"""Execute the adversarial semantic mutation benchmark."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spanish_rewriter.evaluator import CandidateEvaluator
from spanish_rewriter.benchmark_reporting import has_semantic_rejection, write_json_report
from spanish_rewriter.language_tool import (
    DEFAULT_LANGUAGE_TOOL_ENDPOINT,
    LanguageToolClient,
)
from spanish_rewriter.ollama_client import OllamaClient, OllamaError
from spanish_rewriter.service import DEFAULT_AUDIT_MODEL, DEFAULT_MODEL
from spanish_rewriter.prompts import PROMPT_VERSION


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run intentionally valid and invalid Spanish rewrite candidates."
    )
    parser.add_argument(
        "--bank",
        type=Path,
        default=ROOT / "benchmark" / "semantic_mutations.jsonl",
    )
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--audit-model", default=DEFAULT_AUDIT_MODEL)
    parser.add_argument("--ollama-url", default="http://127.0.0.1:11434")
    parser.add_argument("--language-tool-url", default=DEFAULT_LANGUAGE_TOOL_ENDPOINT)
    parser.add_argument(
        "--language-tool-level", choices=("default", "picky"), default="default"
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--with-hints", action="store_true", help="Supply authored semantic hints; default evaluation uses only source, candidate and protected literals.")
    return parser


def load_cases(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        cases = load_cases(args.bank.resolve())
        bank_sha256 = hashlib.sha256(args.bank.read_bytes()).hexdigest()
    except (OSError, json.JSONDecodeError) as error:
        print(f"Cannot load semantic mutation bank: {error}", file=sys.stderr)
        return 2

    if not cases:
        print("Semantic mutation bank contains no cases.", file=sys.stderr)
        return 2

    evaluator = CandidateEvaluator(
        client=OllamaClient(base_url=args.ollama_url),
        audit_models=[args.model, args.audit_model],
        proofreader=LanguageToolClient(
            endpoint=args.language_tool_url,
            level=args.language_tool_level,
        ),
    )
    started_at = datetime.now(UTC)
    output = (args.output or ROOT / "artifacts" / f"semantic-audit-{started_at.strftime('%Y%m%dT%H%M%SZ')}.json").resolve()
    partial_output = output.with_suffix(".partial.json")
    results = []
    try:
        for index, case in enumerate(cases, 1):
            evaluation = evaluator.evaluate(
                case["source"],
                case["candidate"],
                protected_literals=case["protected_literals"],
                required_meaning=case["required_meaning"] if args.with_hints else [],
                forbidden_changes=case["forbidden_changes"] if args.with_hints else [],
            )
            matches_expected = evaluation.status == case["expected_status"]
            results.append(
                {
                    "case_id": case["id"],
                    "priority": case["priority"],
                    "phenomenon": case["phenomenon"],
                    "review_status": case["review_status"],
                    "expected_status": case["expected_status"],
                    "matches_expected": matches_expected,
                    "evaluation": evaluation.to_dict(),
                }
            )
            write_json_report(partial_output, {
                "complete": False,
                "started_at": started_at.isoformat(),
                "prompt_version": PROMPT_VERSION,
                "bank_sha256": bank_sha256,
                "constraint_hints": args.with_hints,
                "results": results,
            })
            print(
                f"case={index}/{len(cases)} id={case['id']} "
                f"expected={case['expected_status']} actual={evaluation.status} "
                f"match={str(matches_expected).lower()}",
                flush=True,
            )
    except (OllamaError, ValueError, KeyError, OSError) as error:
        print(f"Semantic benchmark stopped: {error}", file=sys.stderr)
        return 3


    completed_at = datetime.now(UTC)
    p0_invalid = [
        item
        for item in results
        if item["priority"] == "P0"
        and item["expected_status"] == "review_required"
    ]
    valid_controls = [
        item for item in results if item["expected_status"] == "accepted"
    ]
    summary = {
        "case_count": len(results),
        "matches_expected": sum(item["matches_expected"] for item in results),
        "p0_invalid_count": len(p0_invalid),
        "p0_invalid_rejected": sum(
            item["evaluation"]["status"] == "review_required"
            for item in p0_invalid
        ),
        "p0_invalid_semantically_detected": sum(
            has_semantic_rejection(item["evaluation"]) for item in p0_invalid
        ),
        "valid_control_count": len(valid_controls),
        "valid_controls_accepted": sum(
            item["evaluation"]["status"] == "accepted"
            for item in valid_controls
        ),
    }
    summary["automated_gate_passed"] = (
        summary["p0_invalid_count"] > 0
        and summary["valid_control_count"] > 0
        and summary["matches_expected"] == summary["case_count"]
        and summary["p0_invalid_rejected"] == summary["p0_invalid_count"]
        and summary["p0_invalid_semantically_detected"] == summary["p0_invalid_count"]
        and summary["valid_controls_accepted"] == summary["valid_control_count"]
    )
    report = {
        "schema_version": 1,
        "complete": True,
        "prompt_version": PROMPT_VERSION,
        "bank_sha256": bank_sha256,
        "constraint_hints": args.with_hints,
        "started_at": started_at.isoformat(),
        "completed_at": completed_at.isoformat(),
        "duration_seconds": (completed_at - started_at).total_seconds(),
        "interpretation": "preliminary",
        "bank": str(args.bank.resolve()),
        "audit_models": [args.model, args.audit_model],
        "proofreader_endpoint": args.language_tool_url,
        "summary": summary,
        "results": results,
    }
    write_json_report(output, report)
    print(json.dumps(summary, ensure_ascii=False), flush=True)
    print(f"report={output}", flush=True)
    return 0 if summary["automated_gate_passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
