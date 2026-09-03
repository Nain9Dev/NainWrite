"""Data contracts for local Spanish rewriting."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class Invariant:
    """A literal whose addition, removal, or mutation can alter meaning."""

    kind: str
    value: str


@dataclass(frozen=True)
class GenerationResult:
    """Structured result and timing information returned by a model call."""

    content: dict[str, Any]
    model: str
    model_digest: str
    total_duration_seconds: float
    load_duration_seconds: float
    prompt_tokens: int
    output_tokens: int
    tokens_per_second: float


@dataclass(frozen=True)
class AuditResult:
    """Semantic and stylistic assessment of one rewrite."""

    equivalent: bool
    confidence: float
    critical_changes: list[str]
    naturalness_score: int
    professional_tone_score: int


@dataclass
class RewriteResult:
    """Complete fail-closed result for a rewrite request."""

    status: str
    source_text: str
    rewritten_text: str
    issues: list[str]
    protected_literals: list[str]
    detected_invariants: list[Invariant]
    model: str
    model_digest: str
    prompt_version: str
    writer_generation: GenerationResult
    repair_generation: GenerationResult | None = None
    audit: AuditResult | None = None
    audit_generation: GenerationResult | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""

        return asdict(self)
