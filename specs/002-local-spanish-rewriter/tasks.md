# Local Spanish Rewriter Tasks

## Active task

- `[M]` `TASK-003`: Review the draft references and generated model outputs.

## Confirmed decisions

- `[M]` `TASK-002`: Target locale confirmed as `es-ES` by Aitor.
- `[M]` Target purpose confirmed: professional, natural Spanish with unchanged meaning.

## Human gates

- `[M]` `TASK-003`: Review benchmark references and model outputs before promoting the bank to gold.
- `[H]` Approve or reject proposed ADR-002.

## Handoff

### Done

- Specification, proposed ADR-002, implementation, CLI and benchmark runner created.
- A bounded deterministic repair was added after failures exposed by `ESRW-006` and `ESRW-018`.
- A human-review Markdown sheet is generated with every benchmark report.

### Verified

- `python -m unittest discover -s tests -v`: 18 tests passed.
- `python tools/validate_bank.py`: 30 draft cases passed structural validation.
- Real loopback Ollama smoke test: accepted with valid structured output.
- Final Qwen3.8 benchmark: 30/30 accepted in each of two runs, 23/23 P0 accepted, no deterministic drift and exact stability across runs.
- Final report: `artifacts/rewrite-benchmark-20260903T120925Z.json`.
- Model digest: `ad4df5727497a8c6c5e2ca7027358fc3f2857d7c9b265fae196b46230406bbaa`.
- Prompt version: `es-es-professional-v6`.

### Next

- Aitor reviews `artifacts/rewrite-benchmark-20260903T120925Z.review.md`.
- Correct and approve the draft references, then re-run the gold benchmark.
- Approve or reject proposed ADR-002.

### Blocked

- Production acceptance remains blocked on human review.
- `ESRW-006` passed the configured threshold but received only 4/5 for naturalness and contains a redundant aggregate before the exact `tres`/`dos` breakdown; it requires explicit human judgement.
- Spanish-to-English translation remains out of scope until the Spanish rewriting gate is human-approved.
