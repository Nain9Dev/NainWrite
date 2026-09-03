"""Validate the structural contract of the semantic mutation bank."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BANK = ROOT / "benchmark" / "semantic_mutations.jsonl"
REQUIRED_FIELDS = {
    "id",
    "priority",
    "phenomenon",
    "source",
    "candidate",
    "protected_literals",
    "required_meaning",
    "forbidden_changes",
    "expected_status",
    "review_status",
}


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    cases: list[dict] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        return [f"cannot_read_bank:{error}"]
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as error:
            errors.append(f"line_{line_number}:invalid_json:{error.msg}")
            continue
        if not isinstance(value, dict):
            errors.append(f"line_{line_number}:not_an_object")
            continue
        cases.append(value)

    if len(cases) != 22:
        errors.append(f"case_count:{len(cases)}")
    for index, case in enumerate(cases, 1):
        case_id = case.get("id", f"line_{index}")
        missing = REQUIRED_FIELDS - set(case)
        if missing:
            errors.append(f"{case_id}:missing_fields:{','.join(sorted(missing))}")
            continue
        if case["id"] != f"SEMA-{index:03d}":
            errors.append(f"{case_id}:unexpected_sequence")
        if case["expected_status"] not in {"accepted", "review_required"}:
            errors.append(f"{case_id}:invalid_expected_status")
        if case["review_status"] != "draft":
            errors.append(f"{case_id}:reference_not_draft")
        for field in ("protected_literals", "required_meaning", "forbidden_changes"):
            if not isinstance(case[field], list):
                errors.append(f"{case_id}:{field}_not_array")

    status_counts = Counter(case.get("expected_status") for case in cases)
    if status_counts["review_required"] < 15:
        errors.append("insufficient_invalid_candidates")
    if status_counts["accepted"] < 3:
        errors.append("insufficient_valid_controls")
    return errors


def main(argv: list[str] | None = None) -> int:
    path = Path(argv[0]).resolve() if argv else DEFAULT_BANK
    errors = validate(path)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    cases = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    counts = Counter(case["expected_status"] for case in cases)
    print(f"PASS: validated {len(cases)} draft semantic mutation cases")
    print(f"Expected outcomes: review_required={counts['review_required']}, accepted={counts['accepted']}")
    print("Human approval required before this bank is treated as gold.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
