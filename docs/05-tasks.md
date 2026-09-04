# Project Tasks

The active design handoff is maintained in `specs/004-document-rewriting/tasks.md`. The earlier quality-gate implementation and unresolved acceptance evidence remain in `specs/003-strict-es-quality-gates/tasks.md`.

## Current task

- `[A]` Implement and verify the local Qwen3.8 Spanish rewriter: complete.
- `[A]` Implement and execute independent local proofreading and semantic quality gates: implementation and evaluation complete; strict model acceptance failed and remains open.
- `[A]` Resumable bilingual document workflow: implementation, scoped independent review and finite real-document evaluation complete. Both candidate files exist; editorial acceptance failed and remains open.
- `[M]` Written document-workflow design: approved by Aitor on 2026-09-04.

## Human gates

- `[M]` Confirm target locale and tone: complete (`es-ES`, clear, direct and professional).
- `[M]` Review and correct the 30 draft references.
- `[M]` Review the 30 model outputs in the generated human-review sheet.
- `[M]` Review the corrected semantic draft labels and the observed unsupported-context false acceptance.
- `[M]` Server-isolation work is deferred: Aitor explicitly requested leaving Ollama unchanged. The current named-document request does not establish general network isolation.
- `[H]` Approve ADR-001 if JSONL and fail-closed validation should become canonical.
- `[H]` Approve or reject proposed ADR-002.
- `[H]` Approve or reject proposed ADR-003 after reviewing its measured tradeoffs.

## Later tasks

- `[M]` Promote approved references from draft to gold.
- `[A]` Re-run the versioned gold benchmark after human approval.
- `[A]` Specify a source-grounded editorial correction iteration for the observed deliverable-state drift, narrowed technical meaning and unnatural prose. Add synthetic negative controls before runtime changes; retain the current complete evidence and never repair by silently editing checkpoints.
- `[M]` Review both language candidates after correction; code-test success and high auditor scores are not linguistic approval.
