import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spanish_rewriter.models import GenerationResult, LanguageIssue, ProofreadingResult
from spanish_rewriter.service import SpanishRewriteService


def generation(content: dict) -> GenerationResult:
    return GenerationResult(content, "writer", "digest", 0, 0, 0, 0, 0)


def proofread(issues: list[LanguageIssue]) -> ProofreadingResult:
    return ProofreadingResult("LanguageTool", "test", "es", issues, 0)


class LanguageRepairTests(unittest.TestCase):
    def make_service(self, responses, findings):
        if "equivalent" in responses[-1]:
            responses.append(dict(responses[-1]))
        client = Mock()
        client.generate_json.side_effect = [generation(item) for item in responses]
        proofreader = Mock()
        proofreader.check.side_effect = [proofread(items) for items in findings]
        service = SpanishRewriteService(client, independent_audit_model="independent-test", proofreader=proofreader)
        return service, client, proofreader

    def test_language_repair_is_rechecked_and_audited(self) -> None:
        issue = LanguageIssue("G1", "grammar", "GRAMMAR", "Agreement", 16, 8, [])
        service, client, proofreader = self.make_service([
            {"rewritten_text": "La propuesta fue aprobado.", "uncertain": False},
            {"rewritten_text": "La propuesta fue aprobada.", "uncertain": False},
            {"equivalent": True, "confidence": 1.0, "critical_changes": [], "naturalness_score": 5, "professional_tone_score": 5},
        ], [[issue], []])
        result = service.rewrite("La propuesta fue aprobada.")
        self.assertEqual("accepted", result.status)
        self.assertEqual(2, proofreader.check.call_count)
        self.assertEqual(4, client.generate_json.call_count)
        self.assertIsNotNone(result.language_repair_generation)
        self.assertEqual([issue], result.pre_repair_proofreading.issues)

    def test_language_repair_cannot_bypass_invariants(self) -> None:
        issue = LanguageIssue("S1", "misspelling", "TYPOS", "Unknown word", 23, 8, [])
        service, client, proofreader = self.make_service([
            {"rewritten_text": "La tasa fue del 1 % en el endpoint.", "uncertain": False},
            {"rewritten_text": "La tasa fue del 2 % en la ruta.", "uncertain": False},
        ], [[issue]])
        result = service.rewrite("La tasa fue del 1 % en el endpoint.")
        self.assertEqual("review_required", result.status)
        self.assertIn("missing_invariant:percentage:1 %", result.issues)
        self.assertEqual(2, client.generate_json.call_count)
        self.assertEqual(1, proofreader.check.call_count)
        self.assertIsNone(result.audit)

    def test_linguistic_repair_is_bounded_to_one_attempt(self) -> None:
        issue = LanguageIssue("G1", "grammar", "GRAMMAR", "Agreement", 16, 8, [])
        service, client, proofreader = self.make_service([
            {"rewritten_text": "La propuesta fue aprobado.", "uncertain": False},
            {"rewritten_text": "La propuesta fue aprobado.", "uncertain": False},
        ], [[issue], [issue]])
        result = service.rewrite("La propuesta fue aprobada.")
        self.assertEqual("review_required", result.status)
        self.assertEqual(2, client.generate_json.call_count)
        self.assertEqual(2, proofreader.check.call_count)


if __name__ == "__main__":
    unittest.main()
