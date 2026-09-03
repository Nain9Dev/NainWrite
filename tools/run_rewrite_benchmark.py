"""Run the local Spanish rewriter against the versioned JSONL bank."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spanish_rewriter.ollama_client import OllamaClient, OllamaError
from spanish_rewriter.service import DEFAULT_MODEL, SpanishRewriteService


DETERMINISTIC_ISSUE_PREFIXES = (
    "missing_protected_literal:",
    "duplicated_protected_literal:",
    "missing_invariant:",
    "unexpected_invariant:",
    "empty_rewrite",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the local Spanish rewrite bank.")
    parser.add_argument(
        "--bank",
        type=Path,
        default=ROOT / "benchmark" / "spanish_rewrite_cases.jsonl",
    )
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--ollama-url", default="http://127.0.0.1:11434")
    parser.add_argument("--runs", type=int, default=2)
    parser.add_argument(
        "--case",
        action="append",
        dest="case_ids",
        help="Run only this case ID. May be specified more than once.",
    )
    parser.add_argument("--limit", type=int)
    parser.add_argument("--output", type=Path)
    return parser


def load_cases(path: Path) -> list[dict]:
    cases: list[dict] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"Line {line_number} must contain a JSON object")
        cases.append(value)
    return cases


def is_deterministic_issue(issue: str) -> bool:
    return issue.startswith(DETERMINISTIC_ISSUE_PREFIXES)


def render_human_review(report: dict) -> str:
    """Render a readable approval sheet for the first benchmark run."""

    lines = [
        "# Human Review: Spanish Rewrite Benchmark",
        "",
        f"- Model: `{report['model']}`",
        f"- Prompt: `{report['runs'][0][0]['result']['prompt_version']}`",
        f"- Interpretation: `{report['interpretation']}`",
        "- Locale: `es-ES`",
        "",
        "Automated acceptance is not human approval. Review meaning, naturalness and professional tone.",
        "",
    ]
    for entry in report["runs"][0]:
        result = entry["result"]
        audit = result.get("audit") or {}
        lines.extend(
            [
                f"## {entry['case_id']} - {entry['category']} - {entry['priority']}",
                "",
                f"- Automated status: `{result['status']}`",
                f"- Semantic confidence: `{audit.get('confidence', 'not_audited')}`",
                f"- Naturalness: `{audit.get('naturalness_score', 'not_audited')}/5`",
                f"- Professional tone: `{audit.get('professional_tone_score', 'not_audited')}/5`",
                f"- Issues: `{', '.join(result['issues']) if result['issues'] else 'none'}`",
                "",
                "### Source",
                "",
                result["source_text"],
                "",
                "### Model output",
                "",
                result["rewritten_text"],
                "",
                "### Draft reference",
                "",
                entry["draft_reference"],
                "",
                "### Human decision",
                "",
                "- [ ] Approve model output",
                "- [ ] Reject model output",
                "- [ ] Approve draft reference as gold",
                "- Notes:",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.runs < 1:
        print("--runs must be at least 1", file=sys.stderr)
        return 2

    try:
        cases = load_cases(args.bank.resolve())
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"Cannot load benchmark: {error}", file=sys.stderr)
        return 2
    if args.case_ids:
        selected_ids = set(args.case_ids)
        cases = [case for case in cases if case.get("id") in selected_ids]
        missing_ids = selected_ids - {case.get("id") for case in cases}
        if missing_ids:
            print(f"Unknown case IDs: {', '.join(sorted(missing_ids))}", file=sys.stderr)
            return 2
    if args.limit is not None:
        cases = cases[: args.limit]
    if not cases:
        print("Benchmark contains no cases.", file=sys.stderr)
        return 2

    client = OllamaClient(base_url=args.ollama_url)
    service = SpanishRewriteService(client=client, model=args.model)
    started_at = datetime.now(UTC)
    run_results: list[list[dict]] = []

    try:
        for run_number in range(1, args.runs + 1):
            current_run: list[dict] = []
            for case_number, case in enumerate(cases, 1):
                result = service.rewrite(
                    str(case["source"]),
                    protected_literals=list(case.get("protected_literals", [])),
                    required_meaning=list(case.get("required_meaning", [])),
                    forbidden_changes=list(case.get("forbidden_changes", [])),
                )
                current_run.append(
                    {
                        "case_id": case["id"],
                        "priority": case["priority"],
                        "category": case["category"],
                        "review_status": case["review_status"],
                        "draft_reference": case["draft_reference"],
                        "result": result.to_dict(),
                    }
                )
                print(
                    f"run={run_number}/{args.runs} "
                    f"case={case_number}/{len(cases)} "
                    f"id={case['id']} status={result.status}",
                    flush=True,
                )
            run_results.append(current_run)
    except (OllamaError, ValueError, KeyError, OSError) as error:
        print(f"Benchmark stopped: {error}", file=sys.stderr)
        return 3

    first_run = run_results[0]
    deterministic_comparisons: list[dict] = []
    if len(run_results) > 1:
        for index, case in enumerate(cases):
            observed = [run[index]["result"] for run in run_results]
            deterministic_comparisons.append(
                {
                    "case_id": case["id"],
                    "same_rewritten_text": len(
                        {item["rewritten_text"] for item in observed}
                    )
                    == 1,
                    "same_status": len({item["status"] for item in observed}) == 1,
                    "same_issues": len(
                        {json.dumps(item["issues"], ensure_ascii=False) for item in observed}
                    )
                    == 1,
                }
            )

    p0_results = [entry for entry in first_run if entry["priority"] == "P0"]
    all_p0_accepted = all(entry["result"]["status"] == "accepted" for entry in p0_results)
    no_deterministic_drift = all(
        not any(is_deterministic_issue(issue) for issue in entry["result"]["issues"])
        for run in run_results
        for entry in run
    )
    stable_across_runs = all(
        item["same_rewritten_text"] and item["same_status"] and item["same_issues"]
        for item in deterministic_comparisons
    ) if deterministic_comparisons else None
    automated_gate_passed = (
        all_p0_accepted
        and no_deterministic_drift
        and stable_across_runs is not False
    )
    completed_at = datetime.now(UTC)

    report = {
        "schema_version": 1,
        "started_at": started_at.isoformat(),
        "completed_at": completed_at.isoformat(),
        "duration_seconds": (completed_at - started_at).total_seconds(),
        "bank": str(args.bank.resolve()),
        "bank_is_draft": any(case.get("review_status") != "approved" for case in cases),
        "interpretation": "preliminary" if any(
            case.get("review_status") != "approved" for case in cases
        ) else "gold",
        "model": args.model,
        "model_digest": first_run[0]["result"]["model_digest"],
        "settings": {
            "locale": "es-ES",
            "temperature": 0,
            "seed": 42,
            "num_ctx": 16384,
            "semantic_confidence_threshold": service.semantic_confidence_threshold,
            "minimum_style_score": service.minimum_style_score,
            "runs": args.runs,
        },
        "summary": {
            "case_count": len(cases),
            "accepted_first_run": sum(
                entry["result"]["status"] == "accepted" for entry in first_run
            ),
            "review_required_first_run": sum(
                entry["result"]["status"] != "accepted" for entry in first_run
            ),
            "p0_count": len(p0_results),
            "all_p0_accepted": all_p0_accepted,
            "no_deterministic_drift": no_deterministic_drift,
            "stable_across_runs": stable_across_runs,
            "automated_gate_passed": automated_gate_passed,
        },
        "deterministic_comparisons": deterministic_comparisons,
        "runs": run_results,
    }

    output = args.output
    if output is None:
        timestamp = started_at.strftime("%Y%m%dT%H%M%SZ")
        output = ROOT / "artifacts" / f"rewrite-benchmark-{timestamp}.json"
    output = output.resolve()
    review_output = output.with_suffix(".review.md")
    report["human_review_file"] = str(review_output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    review_output.write_text(render_human_review(report), encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False), flush=True)
    print(f"report={output}", flush=True)
    print(f"human_review={review_output}", flush=True)
    return 0 if automated_gate_passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
