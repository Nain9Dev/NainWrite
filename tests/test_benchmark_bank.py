import json
import re
import unittest
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


def load_cases() -> list[dict]:
    cases = []
    with BANK_PATH.open(encoding="utf-8") as bank_file:
        for line_number, raw_line in enumerate(bank_file, start=1):
            if not raw_line.strip():
                continue
            try:
                cases.append(json.loads(raw_line))
            except json.JSONDecodeError as error:
                raise AssertionError(f"Invalid JSON on line {line_number}: {error}") from error
    return cases


class BenchmarkBankTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = load_cases()

    def test_contains_exactly_thirty_sequential_cases(self) -> None:
        self.assertEqual(30, len(self.cases))
        self.assertEqual(
            [f"ESRW-{index:03d}" for index in range(1, 31)],
            [case["id"] for case in self.cases],
        )

    def test_each_case_has_the_required_contract(self) -> None:
        for case in self.cases:
            with self.subTest(case=case.get("id")):
                self.assertEqual(EXPECTED_FIELDS, set(case))
                self.assertRegex(case["id"], r"^ESRW-\d{3}$")
                self.assertIn(case["priority"], {"P0", "P1", "P2"})
                self.assertEqual("es-ES", case["locale"])
                self.assertEqual("draft", case["review_status"])
                self.assertTrue(case["title"].strip())
                self.assertTrue(case["source"].strip())
                self.assertTrue(case["draft_reference"].strip())
                self.assertNotEqual(case["source"], case["draft_reference"])
                self.assertGreaterEqual(len(case["protected_literals"]), 1)
                self.assertGreaterEqual(len(case["required_meaning"]), 2)
                self.assertGreaterEqual(len(case["forbidden_changes"]), 1)
                self.assertGreaterEqual(len(case["phenomena"]), 1)

    def test_protected_literals_are_preserved_in_draft_references(self) -> None:
        for case in self.cases:
            for literal in case["protected_literals"]:
                with self.subTest(case=case["id"], literal=literal):
                    self.assertTrue(literal)
                    self.assertIn(literal, case["source"])
                    self.assertIn(literal, case["draft_reference"])

    def test_cases_do_not_contain_control_characters(self) -> None:
        control_characters = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
        for case in self.cases:
            serialized = json.dumps(case, ensure_ascii=False)
            with self.subTest(case=case["id"]):
                self.assertIsNone(control_characters.search(serialized))

    def test_category_coverage_meets_minimums(self) -> None:
        counts = Counter(case["category"] for case in self.cases)
        self.assertEqual(set(MINIMUM_CATEGORY_COUNTS), set(counts))
        for category, minimum in MINIMUM_CATEGORY_COUNTS.items():
            with self.subTest(category=category):
                self.assertGreaterEqual(counts[category], minimum)

    def test_semantic_risk_coverage(self) -> None:
        observed = {phenomenon for case in self.cases for phenomenon in case["phenomena"]}
        required = {
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
        self.assertTrue(required.issubset(observed), required - observed)


if __name__ == "__main__":
    unittest.main()
