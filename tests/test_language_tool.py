import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spanish_rewriter.language_tool import (
    LanguageToolClient,
    LanguageToolError,
    partition_proofreading_issues,
)
from spanish_rewriter.models import LanguageIssue


class FakeHeaders:
    def __init__(self, content_type: str) -> None:
        self.content_type = content_type

    def get_content_type(self) -> str:
        return self.content_type


class FakeResponse:
    def __init__(self, payload: object, content_type: str = "application/json") -> None:
        self.payload = json.dumps(payload).encode("utf-8")
        self.headers = FakeHeaders(content_type)

    def __enter__(self):
        return self

    def __exit__(self, *_args) -> None:
        return None

    def read(self) -> bytes:
        return self.payload


class LanguageToolClientTests(unittest.TestCase):
    @patch("spanish_rewriter.language_tool.open_local")
    def test_rejects_a_match_without_its_issue_type(self, urlopen) -> None:
        urlopen.return_value = FakeResponse({
            "software": {"name": "LanguageTool", "version": "test"},
            "language": {"code": "es"},
            "matches": [{"offset": 0, "length": 5, "rule": {"id": "G1", "category": {"id": "GRAMMAR"}}}],
        })
        with self.assertRaises(LanguageToolError):
            LanguageToolClient().check("Texto de prueba.")

    @patch("spanish_rewriter.language_tool.open_local")
    def test_rejects_invalid_finding_offsets(self, urlopen) -> None:
        for offset in (-1, True, "3", None):
            with self.subTest(offset=offset):
                urlopen.return_value = FakeResponse({
                    "software": {"name": "LanguageTool", "version": "test"},
                    "language": {"code": "es"},
                    "matches": [{"offset": offset, "length": 2, "rule": {"id": "G1", "issueType": "grammar"}}],
                })
                with self.assertRaises(LanguageToolError):
                    LanguageToolClient().check("Texto de prueba.")

    def test_rejects_non_loopback_endpoint(self) -> None:
        for endpoint in (
            "https://api.languagetool.org/v2/check",
            "http://192.168.1.20:8082/v2/check",
            "https://127.0.0.1:8082/v2/check",
        ):
            with self.subTest(endpoint=endpoint):
                with self.assertRaises(ValueError):
                    LanguageToolClient(endpoint=endpoint)

    @patch("spanish_rewriter.language_tool.open_local")
    def test_parses_verified_language_tool_response(self, urlopen) -> None:
        urlopen.return_value = FakeResponse(
            {
                "software": {"name": "LanguageTool", "version": "6.6"},
                "language": {"code": "es"},
                "matches": [
                    {
                        "message": "Possible agreement error.",
                        "offset": 3,
                        "length": 8,
                        "replacements": [{"value": "aprobada"}],
                        "rule": {
                            "id": "ES_AGREEMENT",
                            "issueType": "grammar",
                            "category": {"id": "GRAMMAR"},
                        },
                    }
                ],
            }
        )
        result = LanguageToolClient().check("La propuesta fue aprobado.")
        self.assertEqual("LanguageTool", result.software_name)
        self.assertEqual("6.6", result.software_version)
        self.assertEqual("es", result.language)
        self.assertEqual("ES_AGREEMENT", result.issues[0].rule_id)
        self.assertEqual(["aprobada"], result.issues[0].replacements)

    @patch("spanish_rewriter.language_tool.open_local")
    def test_rejects_non_json_or_wrong_product(self, urlopen) -> None:
        urlopen.return_value = FakeResponse({}, content_type="text/html")
        with self.assertRaises(LanguageToolError):
            LanguageToolClient().check("Texto")

        urlopen.return_value = FakeResponse(
            {"software": {"name": "AnotherService"}, "matches": []}
        )
        with self.assertRaises(LanguageToolError):
            LanguageToolClient().check("Texto")


class LanguageIssueClassificationTests(unittest.TestCase):
    def test_blocks_objective_issues_and_keeps_style_advisory(self) -> None:
        issues = [
            LanguageIssue("G1", "grammar", "GRAMMAR", "Agreement", 3, 4, []),
            LanguageIssue("S1", "style", "STYLE", "Long sentence", 10, 5, []),
        ]
        blocking, advisory, ignored = partition_proofreading_issues(
            "Una frase de prueba.", issues, []
        )
        self.assertEqual(["G1"], [issue.rule_id for issue in blocking])
        self.assertEqual(["S1"], [issue.rule_id for issue in advisory])
        self.assertEqual([], ignored)

    def test_ignores_spelling_finding_on_protected_technical_literal(self) -> None:
        text = "El servicio usa FastAPI 0.115."
        issue = LanguageIssue(
            "MORFOLOGIK_RULE_ES",
            "misspelling",
            "TYPOS",
            "Unknown word",
            text.index("FastAPI"),
            len("FastAPI"),
            [],
        )
        blocking, advisory, ignored = partition_proofreading_issues(
            text, [issue], ["FastAPI 0.115"]
        )
        self.assertEqual([], blocking)
        self.assertEqual([], advisory)
        self.assertEqual(["MORFOLOGIK_RULE_ES"], [item.rule_id for item in ignored])

    def test_ignores_spelling_finding_on_explicit_lowercase_literal(self) -> None:
        issue = LanguageIssue(
            "MORFOLOGIK_RULE_ES",
            "misspelling",
            "TYPOS",
            "Unknown word",
            10,
            7,
            [],
        )
        blocking, advisory, ignored = partition_proofreading_issues(
            "Revisa el backend mañana.",
            [issue],
            ["backend"],
        )
        self.assertEqual([], blocking)
        self.assertEqual([], advisory)
        self.assertEqual(["MORFOLOGIK_RULE_ES"], [item.rule_id for item in ignored])


if __name__ == "__main__":
    unittest.main()
