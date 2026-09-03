# Project Tasks

The detailed active handoff is maintained in `specs/003-strict-es-quality-gates/tasks.md`.

## Current task

- `[A]` Implement and verify the local Qwen3.8 Spanish rewriter: complete.
- `[A]` Verify independent local proofreading and semantic quality gates: in progress.

## Human gates

- `[M]` Confirm target locale and tone: complete (`es-ES`, clear, direct and professional).
- `[M]` Review and correct the 30 draft references.
- `[M]` Review the 30 model outputs in the generated human-review sheet.
- `[H]` Approve ADR-001 if JSONL and fail-closed validation should become canonical.
- `[H]` Approve or reject proposed ADR-002.
- `[H]` Approve or reject proposed ADR-003 after reviewing its measured tradeoffs.

## Later tasks

- `[M]` Promote approved references from draft to gold.
- `[A]` Re-run the versioned gold benchmark after human approval.
- `[A]` Design Spanish-to-English translation as a separate specification only after the Spanish gate is approved.
