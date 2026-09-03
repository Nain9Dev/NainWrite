import sys
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spanish_rewriter.local_http import RejectRedirects, open_local
from spanish_rewriter.service import SpanishRewriteService
from spanish_rewriter.evaluator import CandidateEvaluator


class LocalTransportTests(unittest.TestCase):
    @patch("spanish_rewriter.local_http.urllib.request.build_opener")
    def test_proxy_configuration_is_disabled(self, build_opener) -> None:
        request = urllib.request.Request("http://127.0.0.1:8082/v2/check", data=b"local")
        open_local(request, timeout=1)
        handlers = build_opener.call_args.args
        proxy = next(item for item in handlers if isinstance(item, urllib.request.ProxyHandler))
        self.assertEqual({}, proxy.proxies)
        self.assertTrue(any(isinstance(item, RejectRedirects) for item in handlers))

    def test_redirect_is_rejected_without_following_it(self) -> None:
        request = urllib.request.Request("http://127.0.0.1:8082/v2/check", data=b"local")
        with self.assertRaises(urllib.error.HTTPError):
            RejectRedirects().redirect_request(request, None, 307, "Redirect", {}, "https://example.org/check")

    def test_strict_configuration_cannot_disable_required_gates(self) -> None:
        with self.assertRaises(ValueError):
            SpanishRewriteService(Mock(), independent_audit_model=None)
        with self.assertRaises(ValueError):
            SpanishRewriteService(Mock(), require_proofreader=False)
        with self.assertRaises(ValueError):
            CandidateEvaluator(Mock(), ["only-one-model"], Mock())


if __name__ == "__main__":
    unittest.main()
