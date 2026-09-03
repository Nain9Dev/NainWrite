"""Evidence classification and atomic local benchmark report output."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path


def has_semantic_rejection(evaluation: dict) -> bool:
    """Exclude style-only, infrastructure and malformed-response rejections."""
    prefixes = (
        "missing_protected_literal:", "duplicated_protected_literal:",
        "missing_invariant:", "unexpected_invariant:",
    )
    if any(issue.startswith(prefixes) for issue in evaluation.get("issues", [])):
        return True
    return any(
        evidence.get("audit") is not None
        and (
            evidence["audit"].get("equivalent") is False
            or bool(evidence["audit"].get("critical_changes"))
        )
        for evidence in evaluation.get("audits", [])
    )


def all_results_accepted(runs: list[list[dict]]) -> bool:
    """Require a non-empty result set and acceptance across every run."""
    return bool(runs) and all(
        bool(run) and all(entry["result"]["status"] == "accepted" for entry in run)
        for run in runs
    )


def write_json_report(path: Path, report: dict) -> None:
    """Atomically replace one report without exposing a partially written JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        temporary_path.replace(path)
    finally:
        temporary_path.unlink(missing_ok=True)
