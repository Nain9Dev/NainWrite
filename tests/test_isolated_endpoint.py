"""New operations must not silently use another project's model listener."""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

from spanish_rewriter.ollama_client import OllamaClient, OllamaError
from spanish_rewriter.cli import build_parser
import run_rewrite_benchmark
import run_semantic_audit_benchmark


class IsolatedEndpointTests(unittest.TestCase):
    def test_new_operations_route_to_dedicated_listener(self):
        expected = "http://127.0.0.1:11436"
        self.assertEqual(expected, OllamaClient().base_url)
        for parser in (build_parser(), run_rewrite_benchmark.build_parser(),
                       run_semantic_audit_benchmark.build_parser()):
            with self.subTest(parser=parser.description):
                self.assertEqual(expected, parser.parse_args([]).ollama_url)

    def test_unavailable_dedicated_listener_has_no_shared_fallback(self):
        with patch("spanish_rewriter.ollama_client.open_local", side_effect=TimeoutError) as transport:
            with self.assertRaises(OllamaError):
                OllamaClient().get_model_digest("synthetic-local-model")
        self.assertEqual(1, transport.call_count)
        self.assertEqual("http://127.0.0.1:11436/api/tags",
                         transport.call_args.args[0].full_url)


if __name__ == "__main__":
    unittest.main()
