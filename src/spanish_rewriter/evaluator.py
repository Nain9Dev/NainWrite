"""Independent fail-closed evaluation of existing rewrite candidates."""

from __future__ import annotations

from typing import Protocol

from .invariants import extract_invariants, validate_invariants
from .language_tool import LanguageToolError, partition_proofreading_issues
from .models import (
    AuditEvidence,
    CandidateEvaluationResult,
    GenerationResult,
    ProofreadingResult,
)
from .prompts import AUDIT_SCHEMA, build_audit_prompt
from .service import AuditValidationError, audit_issues, parse_audit


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


class CandidateEvaluator:
    """Evaluate candidates with deterministic, linguistic and model gates."""

    def __init__(
        self,
        client: GenerationClient,
        audit_models: list[str],
        proofreader: Proofreader | None,
        semantic_confidence_threshold: float = 0.95,
        minimum_style_score: int = 5,
    ) -> None:
        if len(set(audit_models)) != len(audit_models) or len(audit_models) < 2:
            raise ValueError("audit_models must contain at least two unique model names")
        self.client = client
        self.audit_models = audit_models
        self.proofreader = proofreader
        self.semantic_confidence_threshold = semantic_confidence_threshold
        self.minimum_style_score = minimum_style_score

    def evaluate(
        self,
        source_text: str,
        candidate_text: str,
        *,
        protected_literals: list[str] | None = None,
        required_meaning: list[str] | None = None,
        forbidden_changes: list[str] | None = None,
    ) -> CandidateEvaluationResult:
        protected_literals = list(protected_literals or [])
        required_meaning = list(required_meaning or [])
        forbidden_changes = list(forbidden_changes or [])
        detected_invariants = extract_invariants(source_text)
        issues = validate_invariants(
            source_text, candidate_text, protected_literals
        )
        if not candidate_text.strip():
            issues.append("empty_rewrite")

        proofreading = None
        blocking_language_issues = []
        advisory_language_issues = []
        ignored_language_issues = []
        proofreading_error = None
        if self.proofreader is None:
            issues.append("proofreader_unavailable")
        else:
            try:
                proofreading = self.proofreader.check(candidate_text)
                language_literals = protected_literals + [
                    invariant.value for invariant in detected_invariants
                ]
                (
                    blocking_language_issues,
                    advisory_language_issues,
                    ignored_language_issues,
                ) = partition_proofreading_issues(
                    candidate_text,
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

        audit_evidence: list[AuditEvidence] = []
        for model in self.audit_models:
            generation = self.client.generate_json(
                model=model,
                prompt=build_audit_prompt(
                    source_text,
                    candidate_text,
                    protected_literals,
                    required_meaning,
                    forbidden_changes,
                ),
                schema=AUDIT_SCHEMA,
                num_predict=1536,
            )
            try:
                audit = parse_audit(generation.content)
            except AuditValidationError as error:
                audit = None
                validation_error = error.code
                issues.append(f"audit_invalid:{model}:{error.code}")
            else:
                validation_error = None
                issues.extend(
                    f"audit:{model}:{issue}"
                    for issue in audit_issues(
                        audit,
                        self.semantic_confidence_threshold,
                        self.minimum_style_score,
                    )
                )
            audit_evidence.append(
                AuditEvidence(
                    model=model,
                    generation=generation,
                    audit=audit,
                    validation_error=validation_error,
                )
            )

        return CandidateEvaluationResult(
            status="accepted" if not issues else "review_required",
            source_text=source_text,
            candidate_text=candidate_text,
            issues=list(dict.fromkeys(issues)),
            protected_literals=protected_literals,
            detected_invariants=detected_invariants,
            proofreading=proofreading,
            blocking_language_issues=blocking_language_issues,
            advisory_language_issues=advisory_language_issues,
            ignored_language_issues=ignored_language_issues,
            audits=audit_evidence,
            metadata={"proofreading_error": proofreading_error},
        )
