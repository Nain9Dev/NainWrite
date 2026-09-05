# Project Tasks

The active handoff is maintained in `specs/007-independent-auditor-evaluation/tasks.md`. Corporate calibration history remains in `specs/006-corporate-calibration/tasks.md`, trilingual implementation evidence in `specs/005-approved-trilingual-workflow/tasks.md`, historical bilingual evidence in `specs/004-document-rewriting/tasks.md`, and earlier strict-gate failures in `specs/003-strict-es-quality-gates/tasks.md`.

## Current task

- `[A]` External semantic baseline and per-auditor comparison: specification 007.
- `[M]` Independent reader availability confirmed; actual blind ratings pending.

- `[A]` Implement and verify the local Qwen3.8 Spanish rewriter: complete.
- `[A]` Implement and execute independent local proofreading and semantic quality gates: implementation and evaluation complete; strict model acceptance failed and remains open.
- `[A]` Resumable bilingual document workflow: implementation, scoped independent review and finite real-document evaluation complete. Both candidate files exist; editorial acceptance failed and remains open.
- `[M]` Written document-workflow design: approved by Aitor on 2026-09-04.
- `[A]` TASK-008: approved corporate profile and revision-gated trilingual workflow implementation, finite evaluation and independent review complete; editorial acceptance remains open. See active handoff.
- `[M]` Three-language design and corporate editorial profile: approved on 2026-09-04. Actual generated Spanish revision approval is still separate.

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
- `[A]` Specify the next source-grounded corporate calibration iteration from specification-005 failures, with new style and technical-scope controls. Preserve historical evidence; never repair by silently editing checkpoints.
- `[M]` Review Spanish before approving either English translation; code-test success and high auditor scores are not linguistic approval.
