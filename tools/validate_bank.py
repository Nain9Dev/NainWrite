import json
import re
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BANK_PATH = ROOT / "benchmark" / "spanish_rewrite_cases.jsonl"
EXPECTED_FIELDS = {
    "id",
    "title",
    "category",
    "priority",
    "locale",
    "source",
    "draft_reference",
    "protected_literals",
    "required_meaning",
    "forbidden_changes",
    "phenomena",
    "review_status",
}
MINIMUM_CATEGORY_COUNTS = {
    "general": 4,
    "technical": 6,
    "business": 4,
    "legal_administrative": 4,
    "style": 4,
    "ambiguity": 4,
}
CONTROL_CHARACTERS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


class ValidationError(Exception):
    pass


def load_cases(path: Path) -> list[dict]:
    if not path.is_file():
        raise ValidationError(f"Bank not found: {path}")

    cases = []
    with path.open(encoding="utf-8") as bank_file:
        for line_number, raw_line in enumerate(bank_file, start=1):
            if not raw_line.strip():
                continue
            try:
                cases.append(json.loads(raw_line))
            except json.JSONDecodeError as error:
                raise ValidationError(f"Invalid JSON on line {line_number}: {error}") from error
    return cases


def validate_cases(cases: list[dict]) -> None:
    errors = []
    expected_ids = [f"ESRW-{index:03d}" for index in range(1, 31)]
    actual_ids = [case.get("id") for case in cases]

    if len(cases) != 30:
        errors.append(f"Expected 30 cases, found {len(cases)}")
    if actual_ids != expected_ids:
        errors.append("Case identifiers are not unique and sequential from ESRW-001 to ESRW-030")

    for index, case in enumerate(cases, start=1):
        case_id = case.get("id", f"line {index}")
        if set(case) != EXPECTED_FIELDS:
            missing = sorted(EXPECTED_FIELDS - set(case))
            extra = sorted(set(case) - EXPECTED_FIELDS)
            errors.append(f"{case_id}: field mismatch; missing={missing}, extra={extra}")
            continue
        if case["priority"] not in {"P0", "P1", "P2"}:
            errors.append(f"{case_id}: invalid priority")
        if case["locale"] != "es-ES":
            errors.append(f"{case_id}: locale must be es-ES")
        if case["review_status"] != "draft":
            errors.append(f"{case_id}: unapproved reference must remain draft")
        if not case["source"].strip() or not case["draft_reference"].strip():
            errors.append(f"{case_id}: source and draft reference must be non-empty")
        if case["source"] == case["draft_reference"]:
            errors.append(f"{case_id}: source and draft reference must differ")
        if len(case["protected_literals"]) < 1:
            errors.append(f"{case_id}: at least one protected literal is required")
        if len(case["required_meaning"]) < 2:
            errors.append(f"{case_id}: at least two meaning statements are required")
        if len(case["forbidden_changes"]) < 1:
            errors.append(f"{case_id}: at least one forbidden change is required")
        if len(case["phenomena"]) < 1:
            errors.append(f"{case_id}: at least one phenomenon is required")
        for literal in case["protected_literals"]:
            if not literal or literal not in case["source"]:
                errors.append(f"{case_id}: protected literal missing from source: {literal!r}")
            if not literal or literal not in case["draft_reference"]:
                errors.append(f"{case_id}: protected literal missing from draft reference: {literal!r}")
        if CONTROL_CHARACTERS.search(json.dumps(case, ensure_ascii=False)):
            errors.append(f"{case_id}: contains a disallowed control character")

    categories = Counter(case.get("category") for case in cases)
    if set(categories) != set(MINIMUM_CATEGORY_COUNTS):
        errors.append(f"Unexpected category set: {sorted(categories)}")
    for category, minimum in MINIMUM_CATEGORY_COUNTS.items():
        if categories[category] < minimum:
            errors.append(f"Category {category!r} requires at least {minimum} cases")

    observed_phenomena = {
        phenomenon
        for case in cases
        for phenomenon in case.get("phenomena", [])
    }
    required_phenomena = {
        "ambiguity",
        "attribution",
        "causality",
        "condition",
        "date",
        "identifier",
        "modality",
        "negation",
        "number",
        "path",
        "percentage",
        "quotation",
        "uncertainty",
        "url",
        "version",
    }
    missing_phenomena = sorted(required_phenomena - observed_phenomena)
    if missing_phenomena:
        errors.append(f"Missing semantic-risk coverage: {missing_phenomena}")

    if errors:
        raise ValidationError("\n".join(errors))


def main() -> int:
    try:
        cases = load_cases(BANK_PATH)
        validate_cases(cases)
    except ValidationError as error:
        print(f"FAIL\n{error}", file=sys.stderr)
        return 1

    categories = Counter(case["category"] for case in cases)
    priorities = Counter(case["priority"] for case in cases)
    print(f"PASS: validated {len(cases)} draft cases")
    print("Categories: " + ", ".join(f"{key}={categories[key]}" for key in sorted(categories)))
    print("Priorities: " + ", ".join(f"{key}={priorities[key]}" for key in sorted(priorities)))
    print("Human approval required before any reference is treated as gold.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
