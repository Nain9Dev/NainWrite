# Runbook

## Validate the draft bank

Run from the repository root:

```powershell
python tools/validate_bank.py
python -m unittest discover -s tests -v
```

Expected structural result:

```text
PASS: validated 30 draft cases
```

## Review a reference

1. Open `benchmark/spanish_rewrite_cases.jsonl`.
2. Select one case identifier.
3. Apply `benchmark/review_rubric.md` without considering authorship.
4. Record any corrected reference and reviewer notes separately.
5. Do not change `review_status` until every protected literal is revalidated.

## Rewrite one text locally

Ollama must be running with `qwen3.8-local-fast2:latest` installed.

```powershell
python tools/rewrite_text.py --text "Texto de origen" --protected "literal exacto"
```

Use `--plain` only when the caller handles a non-zero exit. Exit code `0` means that every automated gate passed, `2` means `review_required`, and `3` means a local service or response error. An accepted result is not a legal or production approval.

## Run the complete benchmark

```powershell
python tools/run_rewrite_benchmark.py --runs 2
```

The command writes a machine-readable JSON report and a Markdown human-review sheet under `artifacts/`. Draft references always produce a `preliminary` interpretation.

## Failure handling

- Invalid JSON or missing fields: reject the dataset change.
- Missing protected literal: reject the candidate reference.
- Meaning or naturalness disagreement: keep the case in `draft` and record the review note.
- The runtime permits one constrained repair after deterministic drift; a second failure returns `review_required`.
- Do not copy a `review_required` rewrite into a document automatically.
