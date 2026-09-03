"""Fail-closed orchestration for professional Spanish rewriting."""

from __future__ import annotations

from typing import Protocol

from .invariants import extract_invariants, validate_invariants
from .models import AuditResult, GenerationResult, RewriteResult
from .prompts import (
    AUDIT_SCHEMA,
    PROMPT_VERSION,
    REWRITE_SCHEMA,
    build_audit_prompt,
    build_repair_prompt,
    build_rewrite_prompt,
)


DEFAULT_MODEL = "qwen3.8-local-fast2:latest"


class GenerationClient(Protocol):
    def generate_json(
        self,
        *,
        model: str,
        prompt: str,
        schema: dict,
        num_predict: int,
    ) -> GenerationResult: ...


class SpanishRewriteService:
    """Rewrite and audit Spanish locally, returning review_required on doubt."""

    def __init__(
        self,
        client: GenerationClient,
        model: str = DEFAULT_MODEL,
        semantic_confidence_threshold: float = 0.95,
        minimum_style_score: int = 4,
    ) -> None:
        self.client = client
        self.model = model
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
        audit = _parse_audit(audit_generation.content)

        if writer_uncertain:
            issues.append("writer_reported_uncertainty")
        if not audit.equivalent:
            issues.append("semantic_equivalence_failed")
        if audit.confidence < self.semantic_confidence_threshold:
            issues.append(f"semantic_confidence_below_threshold:{audit.confidence:.3f}")
        for change in audit.critical_changes:
            issues.append(f"critical_change:{change}")
        if audit.naturalness_score < self.minimum_style_score:
            issues.append(f"naturalness_below_threshold:{audit.naturalness_score}")
        if audit.professional_tone_score < self.minimum_style_score:
            issues.append(
                f"professional_tone_below_threshold:{audit.professional_tone_score}"
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
            audit=audit,
            audit_generation=audit_generation,
            metadata={
                "writer_uncertain": writer_uncertain,
                "writer_attempts": 2 if repair_generation else 1,
            },
        )


def _parse_audit(content: dict) -> AuditResult:
    """Convert model JSON into a strict audit contract."""

    critical_changes = content.get("critical_changes", [])
    if not isinstance(critical_changes, list):
        critical_changes = ["Invalid critical_changes response"]
    return AuditResult(
        equivalent=content.get("equivalent") is True,
        confidence=float(content.get("confidence", 0)),
        critical_changes=[str(value) for value in critical_changes],
        naturalness_score=int(content.get("naturalness_score", 0)),
        professional_tone_score=int(content.get("professional_tone_score", 0)),
    )
