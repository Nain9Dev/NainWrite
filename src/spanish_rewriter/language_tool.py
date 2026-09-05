"""Loopback-only LanguageTool client and finding classification."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any
from urllib.parse import urlparse

from .models import LanguageIssue, ProofreadingResult
from .local_http import open_local


DEFAULT_LANGUAGE_TOOL_ENDPOINT = "http://127.0.0.1:8082/v2/check"
_LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}
_BLOCKING_ISSUE_TYPES = {"grammar", "misspelling", "typographical"}


class LanguageToolError(RuntimeError):
    """Raised when a local LanguageTool response cannot be trusted."""


class LanguageToolClient:
    """Call a verified local LanguageTool HTTP endpoint."""

    def __init__(
        self,
        endpoint: str = DEFAULT_LANGUAGE_TOOL_ENDPOINT,
        timeout_seconds: float = 30.0,
        level: str = "default",
        language: str = "es",
    ) -> None:
        parsed = urlparse(endpoint)
        if (
            parsed.scheme != "http"
            or parsed.hostname not in _LOOPBACK_HOSTS
            or parsed.path.rstrip("/") != "/v2/check"
        ):
            raise ValueError(
                "LanguageTool endpoint must use HTTP loopback and the /v2/check path"
            )
        if level not in {"default", "picky"}:
            raise ValueError("LanguageTool level must be 'default' or 'picky'")
        self.endpoint = endpoint
        self.timeout_seconds = timeout_seconds
        self.level = level
        if language not in {"es", "es-ES", "en-GB", "en-US"}:
            raise ValueError("Supported proofreading languages: es, es-ES, en-GB, en-US")
        self.language = "es" if language == "es-ES" else language

    def check(self, text: str) -> ProofreadingResult:
        """Proofread text in the configured language and validate service identity."""

        payload = urllib.parse.urlencode(
            {"language": self.language, "text": text, "level": self.level}
        ).encode("utf-8")
        request = urllib.request.Request(
            self.endpoint,
            data=payload,
            headers={
                "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
                "Accept": "application/json",
            },
            method="POST",
        )
        started = time.perf_counter()
        try:
            with open_local(
                request, timeout=self.timeout_seconds
            ) as response:
                content_type = response.headers.get_content_type()
                if content_type != "application/json":
                    raise LanguageToolError(
                        f"LanguageTool returned unexpected content type: {content_type}"
                    )
                raw = response.read().decode("utf-8")
        except LanguageToolError:
            raise
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            raise LanguageToolError(f"Local LanguageTool request failed: {error}") from error

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as error:
            raise LanguageToolError(f"LanguageTool returned invalid JSON: {error}") from error
        if not isinstance(data, dict):
            raise LanguageToolError("LanguageTool response must be a JSON object")

        software = data.get("software")
        if not isinstance(software, dict) or software.get("name") != "LanguageTool":
            raise LanguageToolError("Endpoint did not identify itself as LanguageTool")
        language = data.get("language")
        allowed = {"es", "es-ES"} if self.language == "es" else {self.language}
        if not isinstance(language, dict) or language.get("code") not in allowed:
            raise LanguageToolError(f"LanguageTool did not confirm {self.language} checking")
        matches = data.get("matches")
        if not isinstance(matches, list):
            raise LanguageToolError("LanguageTool response did not contain a match list")

        issues = [_parse_issue(item) for item in matches]
        return ProofreadingResult(
            software_name="LanguageTool",
            software_version=str(software.get("version", "unknown")),
            language=str(language.get("code")),
            issues=issues,
            duration_seconds=time.perf_counter() - started,
        )


def _parse_issue(value: Any) -> LanguageIssue:
    if not isinstance(value, dict):
        raise LanguageToolError("LanguageTool match must be an object")
    rule = value.get("rule")
    if not isinstance(rule, dict):
        raise LanguageToolError("LanguageTool match did not contain a rule")
    for field in ("id", "issueType"):
        if not isinstance(rule.get(field), str) or not rule[field].strip():
            raise LanguageToolError(f"LanguageTool rule has an invalid {field}")
    for field in ("offset", "length"):
        if type(value.get(field)) is not int or value[field] < 0:
            raise LanguageToolError(f"LanguageTool match has an invalid {field}")
    category = rule.get("category")
    if not isinstance(category, dict):
        category = {}
    replacements = value.get("replacements", [])
    if not isinstance(replacements, list):
        replacements = []
    return LanguageIssue(
        rule_id=rule["id"],
        issue_type=rule["issueType"].lower(),
        category_id=str(category.get("id", "unknown")),
        message=str(value.get("message", "")),
        offset=value["offset"],
        length=value["length"],
        replacements=[
            str(item.get("value"))
            for item in replacements
            if isinstance(item, dict) and item.get("value") is not None
        ],
    )


def partition_proofreading_issues(
    text: str,
    issues: list[LanguageIssue],
    protected_literals: list[str],
) -> tuple[list[LanguageIssue], list[LanguageIssue], list[LanguageIssue]]:
    """Partition objective, advisory and safely ignored technical findings."""

    technical_ranges = _technical_literal_ranges(text, protected_literals)
    blocking: list[LanguageIssue] = []
    advisory: list[LanguageIssue] = []
    ignored: list[LanguageIssue] = []
    for issue in issues:
        issue_range = (issue.offset, issue.offset + issue.length)
        overlaps_technical = any(
            issue_range[0] < literal_range[1]
            and literal_range[0] < issue_range[1]
            for literal_range in technical_ranges
        )
        if issue.issue_type == "misspelling" and overlaps_technical:
            ignored.append(issue)
        elif issue.issue_type in _BLOCKING_ISSUE_TYPES:
            blocking.append(issue)
        else:
            advisory.append(issue)
    return blocking, advisory, ignored


def _technical_literal_ranges(
    text: str, protected_literals: list[str]
) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    for literal in protected_literals:
        start = 0
        while True:
            index = text.find(literal, start)
            if index < 0:
                break
            ranges.append((index, index + len(literal)))
            start = index + max(1, len(literal))
    return ranges
