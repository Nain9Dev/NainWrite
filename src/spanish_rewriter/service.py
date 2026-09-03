"""Fail-closed orchestration for professional Spanish rewriting."""

from __future__ import annotations

from dataclasses import asdict
from typing import Protocol

from .invariants import extract_invariants, validate_invariants
from .language_tool import LanguageToolError, partition_proofreading_issues
from .models import (
    AuditResult,
    GenerationResult,
    ProofreadingResult,
    RewriteResult,
)
from .prompts import (
    AUDIT_SCHEMA,
    PROMPT_VERSION,
    REWRITE_SCHEMA,
    build_audit_prompt,
    build_language_repair_prompt,
    build_repair_prompt,
    build_rewrite_prompt,
)


DEFAULT_MODEL = "qwen3.8-local-fast2:latest"
DEFAULT_AUDIT_MODEL = "gemma4:latest"


class AuditValidationError(ValueError):
    """Raised when a model audit violates its strict response contract."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


class GenerationClient(Protocol):
    def generate_json(
        self,
        *,
        model: str,
        prompt: str,
        schema: dict,
        num_predict: int,
    ) -> GenerationResult: ...


class Proofreader(Protocol):
    def check(self, text: str) -> ProofreadingResult: ...


class SpanishRewriteService:
    """Rewrite and audit Spanish locally, returning review_required on doubt."""

    def __init__(
        self,
        client: GenerationClient,
        model: str = DEFAULT_MODEL,
        independent_audit_model: str | None = DEFAULT_AUDIT_MODEL,
        proofreader: Proofreader | None = None,
        require_proofreader: bool = True,
        semantic_confidence_threshold: float = 0.95,
        minimum_style_score: int = 5,
    ) -> None:
        if not isinstance(independent_audit_model, str) or not independent_audit_model.strip():
            raise ValueError("The strict profile requires an independent auditor")
        if not require_proofreader:
            raise ValueError("The strict profile requires proofreading")
        if independent_audit_model == model:
            raise ValueError("Independent audit model must differ from the writer model")
        self.client = client
        self.model = model
        self.independent_audit_model = independent_audit_model
        self.proofreader = proofreader
        self.require_proofreader = require_proofreader
        self.semantic_confidence_threshold = semantic_confidence_threshold
        self.minimum_style_score = minimum_style_score

    def rewrite(
        self,
        source_text: str,
        *,
        protected_literals: list[str] | None = None,
        required_meaning: list[str] | None = None,
        forbidden_changes: list[str] | None = None,
    ) -> RewriteResult:
        protected_literals = list(protected_literals or [])
        required_meaning = list(required_meaning or [])
        forbidden_changes = list(forbidden_changes or [])

        writer_generation = self.client.generate_json(
            model=self.model,
            prompt=build_rewrite_prompt(
                source_text,
                protected_literals,
                required_meaning,
                forbidden_changes,
            ),
            schema=REWRITE_SCHEMA,
            num_predict=2048,
        )
        rewritten_text = str(writer_generation.content.get("rewritten_text", "")).strip()
        writer_uncertain = writer_generation.content.get("uncertain") is not False
        issues = validate_invariants(source_text, rewritten_text, protected_literals)
        if not rewritten_text:
            issues.append("empty_rewrite")

        detected_invariants = extract_invariants(source_text)
        repair_generation: GenerationResult | None = None
        if issues:
            repair_generation = self.client.generate_json(
                model=self.model,
                prompt=build_repair_prompt(
                    source_text,
                    rewritten_text,
                    issues,
                    protected_literals,
                    required_meaning,
                    forbidden_changes,
                ),
                schema=REWRITE_SCHEMA,
                num_predict=2048,
            )
            rewritten_text = str(
                repair_generation.content.get("rewritten_text", "")
            ).strip()
            writer_uncertain = (
                writer_uncertain
                or repair_generation.content.get("uncertain") is not False
            )
            issues = validate_invariants(source_text, rewritten_text, protected_literals)
            if not rewritten_text:
                issues.append("empty_rewrite")

        if issues:
            return RewriteResult(
                status="review_required",
                source_text=source_text,
                rewritten_text=rewritten_text,
                issues=list(dict.fromkeys(issues)),
                protected_literals=protected_literals,
                detected_invariants=detected_invariants,
                model=writer_generation.model,
                model_digest=writer_generation.model_digest,
                prompt_version=PROMPT_VERSION,
                writer_generation=writer_generation,
                repair_generation=repair_generation,
                metadata={
                    "writer_uncertain": writer_uncertain,
                    "writer_attempts": 2 if repair_generation else 1,
                },
            )

        proofreading: ProofreadingResult | None = None
        pre_repair_proofreading: ProofreadingResult | None = None
        language_repair_generation: GenerationResult | None = None
        proofreading_error = None
        blocking_language_issues = []
        advisory_language_issues = []
        ignored_language_issues = []
        for language_attempt in range(2):
            if self.proofreader is None:
                if self.require_proofreader:
                    issues.append("proofreader_unavailable")
                break
            try:
                proofreading = self.proofreader.check(rewritten_text)
                language_literals = protected_literals + [
                    invariant.value for invariant in detected_invariants
                ]
                (
                    blocking_language_issues,
                    advisory_language_issues,
                    ignored_language_issues,
                ) = partition_proofreading_issues(
                    rewritten_text,
                    proofreading.issues,
                    language_literals,
                )
                issues.extend(
                    f"language_tool:{item.issue_type}:{item.rule_id}"
                    for item in blocking_language_issues
                )
            except (LanguageToolError, OSError, ValueError) as error:
                issues.append("proofreader_unavailable")
                proofreading_error = str(error)
                break

            if not blocking_language_issues or language_attempt == 1:
                break

            pre_repair_proofreading = proofreading
            language_repair_generation = self.client.generate_json(
                model=self.model,
                prompt=build_language_repair_prompt(
                    source_text,
                    rewritten_text,
                    [asdict(item) for item in blocking_language_issues],
                    protected_literals,
                    required_meaning,
                    forbidden_changes,
                ),
                schema=REWRITE_SCHEMA,
                num_predict=2048,
            )
            rewritten_text = str(
                language_repair_generation.content.get("rewritten_text", "")
            ).strip()
            writer_uncertain = (
                writer_uncertain
                or language_repair_generation.content.get("uncertain") is not False
            )
            issues = validate_invariants(source_text, rewritten_text, protected_literals)
            if not rewritten_text:
                issues.append("empty_rewrite")
            proofreading = None
            blocking_language_issues = []
            advisory_language_issues = []
            ignored_language_issues = []
            if issues:
                break

        if issues:
            return RewriteResult(
                status="review_required",
                source_text=source_text,
                rewritten_text=rewritten_text,
                issues=list(dict.fromkeys(issues)),
                protected_literals=protected_literals,
                detected_invariants=detected_invariants,
                model=writer_generation.model,
                model_digest=writer_generation.model_digest,
                prompt_version=PROMPT_VERSION,
                writer_generation=writer_generation,
                repair_generation=repair_generation,
                proofreading=proofreading,
                pre_repair_proofreading=pre_repair_proofreading,
                language_repair_generation=language_repair_generation,
                blocking_language_issues=blocking_language_issues,
                advisory_language_issues=advisory_language_issues,
                ignored_language_issues=ignored_language_issues,
                metadata={
                    "writer_uncertain": writer_uncertain,
                    "writer_attempts": 1 + bool(repair_generation) + bool(language_repair_generation),
                    "proofreading_error": proofreading_error
                    if self.proofreader is not None
                    else None,
                },
            )

        audit_generation = self.client.generate_json(
            model=self.model,
            prompt=build_audit_prompt(
                source_text,
                rewritten_text,
                protected_literals,
                required_meaning,
                forbidden_changes,
            ),
            schema=AUDIT_SCHEMA,
            num_predict=1536,
        )
        try:
            audit = parse_audit(audit_generation.content)
        except AuditValidationError as error:
            audit = None
            issues.append(f"primary_audit_invalid:{error.code}")
        independent_audit_generation: GenerationResult | None = None
        independent_audit: AuditResult | None = None
        if self.independent_audit_model is not None:
            independent_audit_generation = self.client.generate_json(
                model=self.independent_audit_model,
                prompt=build_audit_prompt(
                    source_text,
                    rewritten_text,
                    protected_literals,
                    required_meaning,
                    forbidden_changes,
                ),
                schema=AUDIT_SCHEMA,
                num_predict=1536,
            )
            try:
                independent_audit = parse_audit(
                    independent_audit_generation.content
                )
            except AuditValidationError as error:
                independent_audit = None
                issues.append(f"independent_audit_invalid:{error.code}")

        if writer_uncertain:
            issues.append("writer_reported_uncertainty")
        if audit is not None:
            issues.extend(
                audit_issues(
                    audit,
                    self.semantic_confidence_threshold,
                    self.minimum_style_score,
                )
            )
        if independent_audit is not None:
            issues.extend(
                audit_issues(
                    independent_audit,
                    self.semantic_confidence_threshold,
                    self.minimum_style_score,
                    prefix="independent_",
                )
            )

        return RewriteResult(
            status="accepted" if not issues else "review_required",
            source_text=source_text,
            rewritten_text=rewritten_text,
            issues=list(dict.fromkeys(issues)),
            protected_literals=protected_literals,
            detected_invariants=detected_invariants,
            model=writer_generation.model,
            model_digest=writer_generation.model_digest,
            prompt_version=PROMPT_VERSION,
            writer_generation=writer_generation,
            repair_generation=repair_generation,
            proofreading=proofreading,
            pre_repair_proofreading=pre_repair_proofreading,
            language_repair_generation=language_repair_generation,
            blocking_language_issues=blocking_language_issues,
            advisory_language_issues=advisory_language_issues,
            ignored_language_issues=ignored_language_issues,
            audit=audit,
            audit_generation=audit_generation,
            independent_audit=independent_audit,
            independent_audit_generation=independent_audit_generation,
            metadata={
                "writer_uncertain": writer_uncertain,
                "writer_attempts": 1 + bool(repair_generation) + bool(language_repair_generation),
                "audit_models": [
                    model
                    for model in (self.model, self.independent_audit_model)
                    if model is not None
                ],
            },
        )


def parse_audit(content: dict) -> AuditResult:
    """Convert model JSON into a strict audit contract."""

    if not isinstance(content.get("equivalent"), bool):
        raise AuditValidationError("equivalent_not_boolean")
    confidence = content.get("confidence")
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
        raise AuditValidationError("confidence_not_number")
    if not 0 <= float(confidence) <= 1:
        raise AuditValidationError("confidence_out_of_range")
    critical_changes = content.get("critical_changes")
    if not isinstance(critical_changes, list) or not all(
        isinstance(value, str) for value in critical_changes
    ):
        raise AuditValidationError("critical_changes_not_string_array")
    naturalness = content.get("naturalness_score")
    professional_tone = content.get("professional_tone_score")
    if isinstance(naturalness, bool) or not isinstance(naturalness, int):
        raise AuditValidationError("naturalness_not_integer")
    if not 1 <= naturalness <= 5:
        raise AuditValidationError("naturalness_out_of_range")
    if isinstance(professional_tone, bool) or not isinstance(
        professional_tone, int
    ):
        raise AuditValidationError("professional_tone_not_integer")
    if not 1 <= professional_tone <= 5:
        raise AuditValidationError("professional_tone_out_of_range")
    return AuditResult(
        equivalent=content["equivalent"],
        confidence=float(confidence),
        critical_changes=critical_changes,
        naturalness_score=naturalness,
        professional_tone_score=professional_tone,
    )


def audit_issues(
    audit: AuditResult,
    confidence_threshold: float,
    minimum_style_score: int,
    prefix: str = "",
) -> list[str]:
    issues: list[str] = []
    if not audit.equivalent:
        issues.append(f"{prefix}semantic_equivalence_failed")
    if audit.confidence < confidence_threshold:
        issues.append(
            f"{prefix}semantic_confidence_below_threshold:{audit.confidence:.3f}"
        )
    for change in audit.critical_changes:
        issues.append(f"{prefix}critical_change:{change}")
    if audit.naturalness_score < minimum_style_score:
        issues.append(
            f"{prefix}naturalness_below_threshold:{audit.naturalness_score}"
        )
    if audit.professional_tone_score < minimum_style_score:
        issues.append(
            f"{prefix}professional_tone_below_threshold:"
            f"{audit.professional_tone_score}"
        )
    return issues
