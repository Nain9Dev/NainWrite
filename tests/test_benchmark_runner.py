import sys
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.run_rewrite_benchmark import main, render_human_review
from spanish_rewriter.ollama_client import OllamaError


class HumanReviewReportTests(unittest.TestCase):
    @patch("tools.run_rewrite_benchmark.SpanishRewriteService")
    def test_interrupted_rewrite_run_keeps_completed_case(self, factory) -> None:
        factory.return_value.rewrite.side_effect = [
            SimpleNamespace(status="accepted", to_dict=lambda: {"status": "accepted"}),
            OllamaError("Interrupted local service"),
        ]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "result.json"
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(3, main(["--limit", "2", "--runs", "1", "--output", str(output)]))
            partial = json.loads(output.with_suffix(".partial.json").read_text(encoding="utf-8"))
            self.assertFalse(partial["complete"])
            self.assertEqual(1, len(partial["runs"][0]))
            self.assertFalse(output.exists())

    def test_labels_distinguish_source_qwen_output_and_proposed_reference(self) -> None:
        report = {
            "model": "qwen-test",
            "audit_model": "audit-test",
            "interpretation": "preliminary",
            "runs": [
                [
                    {
                        "case_id": "CASE-001",
                        "category": "general",
                        "priority": "P0",
                        "draft_reference": "Referencia propuesta.",
                        "result": {
                            "prompt_version": "test-v1",
                            "status": "accepted",
                            "issues": [],
                            "source_text": "Texto original.",
                            "rewritten_text": "Texto de Qwen.",
                            "audit": {
                                "confidence": 1.0,
                                "naturalness_score": 5,
                                "professional_tone_score": 5,
                            },
                        },
                    }
                ]
            ],
        }
        output = render_human_review(report)
        self.assertIn("### Texto original", output)
        self.assertIn("### Reescritura generada por Qwen", output)
        self.assertIn("### Referencia propuesta", output)
        self.assertIn("Aprobar la reescritura generada por Qwen", output)
        self.assertIn("Aprobar la referencia propuesta como ejemplo gold", output)


if __name__ == "__main__":
    unittest.main()
