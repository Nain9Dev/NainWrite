import json
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from spanish_rewriter.benchmark_reporting import (
    all_results_accepted,
    has_semantic_rejection,
    write_json_report,
)
from tools.run_semantic_audit_benchmark import build_parser, main
from spanish_rewriter.ollama_client import OllamaError


class EvidenceIntegrityTests(unittest.TestCase):
    def test_style_rejection_does_not_count_as_semantic_detection(self) -> None:
        self.assertFalse(has_semantic_rejection({
            "issues": ["language_tool:grammar:G1", "audit:model:naturalness_below_threshold:4"],
            "audits": [],
        }))

    def test_valid_semantic_audit_counts_as_detection(self) -> None:
        self.assertTrue(has_semantic_rejection({
            "issues": [],
            "audits": [{"audit": {"equivalent": False, "critical_changes": ["Negation changed."]}}],
        }))

    def test_deterministic_drift_counts_as_detection(self) -> None:
        self.assertTrue(has_semantic_rejection({
            "issues": ["missing_invariant:number:500"], "audits": [],
        }))

    def test_lower_priority_rejection_prevents_rewrite_gate(self) -> None:
        runs = [[{"result": {"status": "accepted"}}, {"result": {"status": "review_required"}}]]
        self.assertFalse(all_results_accepted(runs))
        self.assertFalse(all_results_accepted([]))
        self.assertTrue(all_results_accepted([[{"result": {"status": "accepted"}}]]))

    def test_report_replacement_remains_valid_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "progress.partial.json"
            write_json_report(path, {"complete": False, "results": [1]})
            write_json_report(path, {"complete": False, "results": [1, 2]})
            self.assertEqual([1, 2], json.loads(path.read_text(encoding="utf-8"))["results"])
            self.assertEqual([path], list(Path(directory).iterdir()))

    def test_mutation_runner_is_unassisted_by_default(self) -> None:
        self.assertFalse(build_parser().parse_args([]).with_hints)
        self.assertTrue(build_parser().parse_args(["--with-hints"]).with_hints)

    @patch("tools.run_semantic_audit_benchmark.CandidateEvaluator")
    def test_mutation_bank_without_valid_controls_cannot_pass(self, factory) -> None:
        evaluation = {"status": "review_required", "issues": ["missing_invariant:number:1"], "audits": []}
        factory.return_value.evaluate.return_value = SimpleNamespace(status="review_required", to_dict=lambda: evaluation)
        case = {"id": "TEST-001", "priority": "P0", "phenomenon": "quantity", "source": "1", "candidate": "2", "protected_literals": [], "required_meaning": [], "forbidden_changes": [], "review_status": "draft", "expected_status": "review_required"}
        with tempfile.TemporaryDirectory() as directory:
            bank = Path(directory) / "bank.jsonl"
            output = Path(directory) / "result.json"
            bank.write_text(json.dumps(case) + "\n", encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(2, main(["--bank", str(bank), "--output", str(output)]))


    def test_empty_mutation_bank_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            bank = Path(directory) / "bank.jsonl"
            bank.write_text("", encoding="utf-8")
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(2, main(["--bank", str(bank)]))

    @patch("tools.run_semantic_audit_benchmark.CandidateEvaluator")
    def test_interrupted_mutation_run_keeps_completed_case(self, factory) -> None:
        evaluation = {"status": "accepted", "issues": [], "audits": []}
        factory.return_value.evaluate.side_effect = [
            SimpleNamespace(status="accepted", to_dict=lambda: evaluation),
            OllamaError("Interrupted local service"),
        ]
        case = {
            "id": "TEST-001", "priority": "P0", "phenomenon": "negation",
            "source": "No se aprobó.", "candidate": "No fue aprobado.",
            "protected_literals": [], "required_meaning": ["Author hint"],
            "forbidden_changes": ["Author hint"], "review_status": "draft",
            "expected_status": "accepted",
        }
        with tempfile.TemporaryDirectory() as directory:
            bank = Path(directory) / "bank.jsonl"
            output = Path(directory) / "result.json"
            bank.write_text((json.dumps(case) + "\n") * 2, encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(3, main(["--bank", str(bank), "--output", str(output)]))
            partial = json.loads(output.with_suffix(".partial.json").read_text(encoding="utf-8"))
            self.assertEqual(1, len(partial["results"]))
            self.assertFalse(partial["complete"])
            self.assertFalse(output.exists())
            self.assertEqual([], factory.return_value.evaluate.call_args_list[0].kwargs["required_meaning"])


if __name__ == "__main__":
    unittest.main()
