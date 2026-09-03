import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spanish_rewriter.evaluator import CandidateEvaluator
from spanish_rewriter.models import GenerationResult, ProofreadingResult


class CandidateEvaluatorTests(unittest.TestCase):
    def test_empty_candidate_cannot_pass_even_if_auditors_accept(self) -> None:
        client = Mock()
        client.generate_json.return_value = GenerationResult(
            content={"equivalent": True, "confidence": 1.0, "critical_changes": [],
                     "naturalness_score": 5, "professional_tone_score": 5},
            model="test", model_digest="test", total_duration_seconds=0,
            load_duration_seconds=0, prompt_tokens=0, output_tokens=0,
            tokens_per_second=0,
        )
        proofreader = Mock()
        proofreader.check.return_value = ProofreadingResult("LanguageTool", "test", "es", [], 0)
        evaluator = CandidateEvaluator(client, ["writer", "auditor"], proofreader)
        result = evaluator.evaluate("La propuesta fue aprobada.", "  ")
        self.assertEqual("review_required", result.status)
        self.assertIn("empty_rewrite", result.issues)
        self.assertEqual(2, client.generate_json.call_count)


if __name__ == "__main__":
    unittest.main()
