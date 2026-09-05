# Approved Trilingual Workflow Tasks

## Current task

- `[A]` TASK-008: Approved design implementation, finite software/local-model evaluation, documentation and independent review are complete. Editorial quality acceptance remains open; this is not a claim that the agent is error-free.
- `[M]` Aitor approved the workflow design on 2026-09-04, not any generated Spanish revision or benchmark gold label.
- No commit, push, merge, deployment, model installation or Ollama configuration change in this iteration.

## Done

- Recorded REQ-088 through REQ-099 before runtime implementation.
- Implemented review-only evidence, conservative editable-span mapping, revision-specific approval, independent en-GB/en-US generation, original-source crosschecks, resumability and immutable history.
- Updated CLI, architecture/data-model diagrams, runbook, traceability and corporate profile.
- Added a synthetic corporate document and 12 draft-labelled semantic controls; no private source text entered Git.
- Closed task-review findings for prose becoming Markdown structure and the actual en-US LanguageTool client rejecting its correct locale. Two fix rounds retained RED/GREEN reports and scoped re-review.
- Closed both whole-change findings in one combined fix wave: empty heading/list markers and the missing CLI outdated-translation notice. The sole final scoped re-review found no remaining Critical/Important findings or new breakage.

## Verified

- Starting branch/HEAD: `naindev/strict-es-quality-gates`, `6553b848fe96fbb6a539c20add5f90e4ec6d5e86`. Changes remain local and uncommitted.
- Baseline 100 tests passed. Recovery 133 passed; corrected task-review checkpoint 137 passed. After the whole-change fixes, the final tree passes 139 tests in 3.431 seconds with `python -X utf8 -m unittest discover -s tests -q`. Both existing draft-bank validators pass (30 rewrite and 22 semantic cases, all draft). Final verification evidence is retained in `.superpowers/sdd/plan/final-verification.md`.
- Independent task and fix reviews have no remaining Important/Critical findings. Recovery report: `.superpowers/sdd/plan/task-1-report.md`; exact correction RED/GREEN: `.superpowers/sdd/plan/fix-1-report.md`. The first worker's closing report was interrupted; its missing exact output was not invented.
- Final whole-change correction evidence is in `.superpowers/sdd/plan/final-fix-report.md` and `final-fix-rereview.md`. Final `git diff --check` passes; HEAD and index remain unchanged. No local review evidence was deleted because these changes have not been committed or merged.
- Existing model identities match the prior record. Ollama remains PID 9984 on `::11434`, untouched. LanguageTool stopped during interruption; only its existing installation was restarted hidden (PID 1784), verified on `127.0.0.1:8082`. Actual en-GB/en-US review controls passed after the client fix.
- Prompt `trilingual-editorial-v5` and evidence contract `trilingual-review-v1` stayed frozen for the finite model experiment. No outcome-based prompt tuning or gate suppression.
- Full attempted-case experiment: `artifacts/corporate-controls.rewritten/20260904T140728Z-9c76f87384/results.json`, plus `review.md` and immutable per-case evidence. Invalid pairs: 5/6 semantically detected, one falsely accepted (CORP-003). Valid controls: 5/6 accepted, one length-limit execution error (CORP-008); no valid semantic rejection. Seven completed cases survived interruption and were not regenerated. Case-8 error was recorded explicitly from the observed exception, not as a fabricated audit.
- A subsequent actual-client en-US error before CORP-010 inference was reproduced and fixed, then the incomplete experiment resumed. This software integration failure remains documented rather than hidden by the passing suite.
- Bank file SHA-256: `5afbbfa42a693c09ca492ffca5add3f8ba3a456e5fb7eba06325cdc1c28d0102`. Synthetic document source SHA-256: `e85043b31ee94451d126961fcd35f8f183e7cec5d0be42c0b54c05b520f2a73c`.
- Real Spanish smoke: `artifacts/corporate-smoke.rewritten/20260904T144219Z-55c9093396`. Spanish revision `51181dd6c83a2683c783acfdbd8be52e7a5c113c3fa9ce54e9e1cd7d23c4ec71`, 8/8 spans, source unchanged, phase `awaiting_spanish_approval`, automatic `review_required`, human approval false, zero English generation results.
- Actual paused-job resume explicitly returned CLI exit 3, with no new model progress and unchanged checkpoint/output/report hashes.
- Spanish inspection found a populated-state calque and unnecessary framing despite equivalence and 5/5 style from both revision auditors. Three LanguageTool flags concern two loanwords and a synthetic proper name. Generated text and flags remain unchanged; separate `editorial-observations.md` contains proposed corrections only.
- Primary profile references were rechecked and documented: Cervantes 2025, GOV.UK and Digital.gov. These are editorial references, not training data or model certification.

## Next

- `[A]` Specify a bounded style/technical-scope calibration iteration using these failures plus new controls. Preserve the frozen experiment; do not silently fix its outputs or labels.
- `[M]` Review a corrected Spanish revision before authorising actual English translations. The current synthetic candidate still has wording defects and is not recommended for approval.
- `[M]` Final editorial review of all three versions remains separate from approval to translate.

## Blocked / not established

- Error-free professional rewriting and complete semantic preservation are not achieved. CORP-003, earlier SEMA-022 and the prior private-draft defects remain open.
- Real three-version document completion remains pending exact Spanish approval. Only unit tests have exercised a synthetic approval event.
- Supported files remain conservative UTF-8 Markdown/TXT; ambiguous structural edits are rejected. This is not arbitrary PDF/DOCX editing.
- Ollama network isolation and unattended service recovery remain unverified. No private draft was reprocessed in this iteration; old documents and generated evidence remain intact.
