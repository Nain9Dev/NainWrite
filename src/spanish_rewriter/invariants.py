"""Deterministic extraction and comparison of meaning-critical literals."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass

from .models import Invariant


@dataclass(frozen=True)
class _Match:
    start: int
    end: int
    priority: int
    invariant: Invariant


_FLAGS = re.UNICODE | re.IGNORECASE

# Earlier patterns take precedence over their constituent numbers or fragments.
_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("url", re.compile(r"https?://[^\s<>\]\[\)\(\{\}\"']+[^\s<>\]\[\)\(\{\}\"'.,;:!?]", _FLAGS)),
    ("email", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", _FLAGS)),
    ("windows_path", re.compile(r"\b[A-Z]:\\(?:[^\s\\/:*?\"<>|]+\\)*[^\s\\/:*?\"<>|]+", _FLAGS)),
    ("quoted_text", re.compile(r"(?:\"[^\"\r\n]+\"|«[^»\r\n]+»|'[^'\r\n]+')", _FLAGS)),
    ("route", re.compile(r"(?<![\w:])/(?:[A-Z0-9._~-]+/)*[A-Z0-9._~-]+", _FLAGS)),
    ("date", re.compile(r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2})\b", _FLAGS)),
    ("time", re.compile(r"\b(?:[01]?\d|2[0-3]):[0-5]\d\b", _FLAGS)),
    ("currency", re.compile(r"(?<!\w)(?:\d+(?:[.,]\d+)?\s?(?:€|EUR|USD)|(?:€|\$)\s?\d+(?:[.,]\d+)?)", _FLAGS)),
    ("percentage", re.compile(r"(?<!\w)\d+(?:[.,]\d+)?\s?%", _FLAGS)),
    (
        "version",
        re.compile(
            r"(?:\b(?:PostgreSQL|Python|Windows|Ubuntu|Ollama|Qwen|FastAPI|Pydantic|Docker|Node(?:\.js)?|TypeScript|React|Vue|Angular|Godot|Blender|CUDA)\s+v?\d+(?:\.\d+){0,3}\b|(?<!\w)\.NET\s+v?\d+(?:\.\d+){0,3}\b|\b[A-Z][A-Z0-9.+#-]*\s+v?\d+(?:\.\d+){1,3}\b)",
            _FLAGS,
        ),
    ),
    ("identifier", re.compile(r"\b(?:ADR|REQ|BR|FR|NFR|TC|P)[-_ ]?\d{1,5}\b", _FLAGS)),
    ("short_identifier", re.compile(r"\b[A-Z]\d{1,4}[A-Z]?\b")),
    ("number", re.compile(r"(?<![\w])[-+]?\d+(?:[.,]\d+)?(?![\w])", _FLAGS)),
)


def extract_invariants(text: str) -> list[Invariant]:
    """Extract non-overlapping high-risk literals in source order."""

    candidates: list[_Match] = []
    for priority, (kind, pattern) in enumerate(_PATTERNS):
        for match in pattern.finditer(text):
            value = match.group(0)
            end = match.end()
            if kind in {"url", "windows_path"}:
                trimmed = value.rstrip(".,;:!?")
                end -= len(value) - len(trimmed)
                value = trimmed
            candidates.append(
                _Match(
                    start=match.start(),
                    end=end,
                    priority=priority,
                    invariant=Invariant(kind=kind, value=value),
                )
            )

    selected: list[_Match] = []
    for candidate in sorted(
        candidates,
        key=lambda item: (item.priority, item.start, -(item.end - item.start)),
    ):
        if any(
            candidate.start < existing.end and existing.start < candidate.end
            for existing in selected
        ):
            continue
        selected.append(candidate)

    return [item.invariant for item in sorted(selected, key=lambda item: item.start)]


def validate_invariants(
    source_text: str,
    rewritten_text: str,
    protected_literals: list[str] | None = None,
) -> list[str]:
    """Return deterministic drift reasons; an empty list means no drift found."""

    issues: list[str] = []
    protected_literals = protected_literals or []

    for literal in protected_literals:
        source_count = _literal_count(source_text, literal)
        rewritten_count = _literal_count(rewritten_text, literal)
        if rewritten_count < max(1, source_count):
            issues.append(f"missing_protected_literal:{literal}")
        elif rewritten_count > source_count and source_count > 0:
            issues.append(f"duplicated_protected_literal:{literal}")

    source_counts = Counter(
        (invariant.kind, invariant.value) for invariant in extract_invariants(source_text)
    )
    rewritten_counts = Counter(
        (invariant.kind, invariant.value) for invariant in extract_invariants(rewritten_text)
    )

    for (kind, value), count in source_counts.items():
        if rewritten_counts[(kind, value)] < count:
            issues.append(f"missing_invariant:{kind}:{value}")
    for (kind, value), count in rewritten_counts.items():
        if source_counts[(kind, value)] < count:
            issues.append(f"unexpected_invariant:{kind}:{value}")

    return list(dict.fromkeys(issues))


def _literal_count(text: str, literal: str) -> int:
    """Count an exact literal without treating it as part of a larger word."""

    if not literal:
        return 0
    prefix = r"(?<!\w)" if literal[0].isalnum() or literal[0] == "_" else ""
    suffix = r"(?!\w)" if literal[-1].isalnum() or literal[-1] == "_" else ""
    return sum(1 for _ in re.finditer(f"{prefix}{re.escape(literal)}{suffix}", text))
