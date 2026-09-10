# Project Tasks

The active handoff is maintained in `specs/009-local-product-readiness/tasks.md`. Independent-evaluation history remains in `specs/007-independent-auditor-evaluation/tasks.md`; the separate private sample remains pending approval in `specs/008-proposal-reading-sample/tasks.md`. Corporate calibration and earlier implementation evidence remain in their original specification handoffs.

## Current task

- `[A]` Local intake, browser queue/export and observed modality regression: specifications 010-012. Active handoff: `specs/012-conditional-modality/tasks.md`; full product evidence: `specs/011-local-review-workbench/tasks.md`.
- `[M]` Aitor confirms manual review availability; actual ratings remain pending and an independent reader is no longer a committed dependency.

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
- `[A]` Dedicated NainWrite listener and cloud-disabled startup verified after explicit authorisation on 2026-09-09. Shared Ollama remains unchanged; complete offline lifecycle and private-document workflow are not verified by this slice.
- `[H]` Approve ADR-001 if JSONL and fail-closed validation should become canonical.
- `[H]` Approve or reject proposed ADR-002.
- `[H]` Approve or reject proposed ADR-003 after reviewing its measured tradeoffs.

## Later tasks

- `[M]` Promote approved references from draft to gold.
- `[A]` Re-run the versioned gold benchmark after human approval.
- `[A]` Specify the next source-grounded corporate calibration iteration from specification-005 failures, with new style and technical-scope controls. Preserve historical evidence; never repair by silently editing checkpoints.
- `[M]` Review Spanish before approving either English translation; code-test success and high auditor scores are not linguistic approval.
