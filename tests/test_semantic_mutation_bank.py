import json
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "benchmark" / "semantic_mutations.jsonl"


class SemanticMutationBankTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = [
            json.loads(line)
            for line in BANK.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def test_contains_twenty_two_sequential_cases(self) -> None:
        self.assertEqual(22, len(self.cases))
        self.assertEqual(
            [f"SEMA-{number:03d}" for number in range(1, 23)],
            [case["id"] for case in self.cases],
        )

    def test_contract_is_complete(self) -> None:
        required = {
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
        for case in self.cases:
            with self.subTest(case=case.get("id")):
                self.assertEqual(set(), required - set(case))
                self.assertIn(case["priority"], {"P0", "P1", "P2"})
                self.assertIn(case["expected_status"], {"accepted", "review_required"})
                self.assertEqual("draft", case["review_status"])
                self.assertTrue(case["source"].strip())
                self.assertTrue(case["candidate"].strip())

    def test_has_invalid_and_valid_controls(self) -> None:
        statuses = Counter(case["expected_status"] for case in self.cases)
        self.assertGreaterEqual(statuses["review_required"], 15)
        self.assertGreaterEqual(statuses["accepted"], 3)
        for case in self.cases:
            if case["expected_status"] == "review_required":
                self.assertNotEqual(case["source"], case["candidate"])

    def test_valid_technical_terms_are_explicitly_protected(self) -> None:
        case = next(item for item in self.cases if item["id"] == "SEMA-019")
        self.assertIn("backend", case["protected_literals"])

    def test_covers_critical_semantic_phenomena(self) -> None:
        required = {
            "negation",
            "modality",
            "actor",
            "condition",
            "quantity",
            "date",
            "causality",
            "ambiguity",
            "exception",
            "scope",
            "tense",
            "unsupported_context",
        }
        observed = {case["phenomenon"] for case in self.cases}
        self.assertEqual(set(), required - observed)


if __name__ == "__main__":
    unittest.main()
