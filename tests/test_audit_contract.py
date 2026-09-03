import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spanish_rewriter.service import AuditValidationError, parse_audit


class AuditContractTests(unittest.TestCase):
    def test_rejects_non_boolean_equivalence_with_controlled_error(self) -> None:
        for value in ([], {}, 1, "true", None):
            with self.subTest(value=value):
                with self.assertRaises(AuditValidationError):
                    parse_audit({"equivalent": value})

    def test_rejects_missing_critical_changes(self) -> None:
        with self.assertRaises(AuditValidationError):
            parse_audit({
                "equivalent": True,
                "confidence": 1.0,
                "naturalness_score": 5,
                "professional_tone_score": 5,
            })


if __name__ == "__main__":
    unittest.main()
