# Document Rewriting Tasks

## Active task

- `[A]` `TASK-007`: Implement and verify the approved resumable bilingual file-path workflow.
- `[M]` Written design approved by Aitor on 2026-09-04. Human approval of generated documents remains separate.

## Handoff

### Done

- Implemented source-span parser, safe batches, bilingual prompts/transformer, locale-specific proofreading, dual audits, bounded repair, evidence revalidation, atomic job store, resume and file-path CLI.
- Added failing-first parser, locale, transformer and job tests. Corrected five independent parser findings and a saved-evidence validation finding with regressions.
- Updated README, architecture/data diagrams and runbook. Original private source and Ollama configuration remain unchanged.

- Read the current repository instructions, task handoff, architecture, runbook and runtime contracts.
- Consolidated interview decisions: professional natural es-ES, wording-only editing, preserved document structure and meaning, unchanged good prose, removal of preparation clutter, no fact investigation, no invented values.
- Recorded the latest request for both Spanish and English candidate files from a supplied path.
- Proposed Markdown/TXT as the first supported formats and en-GB as the consistent English variant.
- Defined a section manifest, bounded context, resumable local state, structural assembly, bilingual audits and separate completion/quality statuses in the specification and plan.

### Verified

- Runtime baseline is committed and pushed as `b054634b69248b972c8ba8fbd5a6fc6b1646738f` on `naindev/strict-es-quality-gates`. No main-branch change or merge.
- The next editorial refinement is currently uncommitted: parser v2, bilingual prompt v3 and job v2, plus bounded Windows checkpoint-lock retries. Current suite: 100 tests pass; `git diff --check` and both draft-bank validators pass.
- Real synthetic UTF-8 file produced complete es-ES and en-GB candidates with automatic acceptance. Local job: `artifacts/document-smoke.rewritten/20260903T225111Z-36a5cd0e29`. Resume verified without regenerating completed work.
- First synthetic attempt under prompt v1 failed on an out-of-range audit confidence; v2 explicitly defines the range, and invalid audits now retain failed evidence instead of claiming acceptance.
- Private-draft preflight: 22439 source bytes, 16902 clean-view bytes, 103 editable spans, 13 batches per language, 48 explicitly recorded removals with the selected preparation cleanup.
- Independent review closed all Important/Critical findings after reference-link rejection and uncached model-identity checks before/after generation were added.
- The actual draft baseline is running in the local job `C:/Users/aitor/Downloads/nlnet-borrador-base-EN-v0.rewritten/20260904T074514Z-8288667699`. Original session `92751` stopped on Windows access-denied error 5 when replacing the checkpoint. Its saved state retained 13/13 Spanish and 7/13 English batches. Active resumed exec session is `43755`, continuing at English batch 8 with the exact committed b054634 runtime exported under `.tools/document-baseline-b054634/`. Resume command: `python .tools/document-baseline-b054634/tools/rewrite_document.py --resume "C:/Users/aitor/Downloads/nlnet-borrador-base-EN-v0.rewritten/20260904T074514Z-8288667699"`. No checkpoint or prompt migration is allowed.
- First actual attempt stopped because LanguageTool was no longer running after the session pause. Started only the existing local LanguageTool installation, hidden, PID 3452; verified `127.0.0.1:8082` and es/en-GB checks, then resumed. Ollama's externally restarted desktop process is PID 9984 on `::11434`; this task did not restart or configure it.
- Added a CLI regression requiring proofreading availability before processing private text. The real job's first Spanish batch completed with two spelling findings, while both model audits passed; it correctly remains review-required.
- Baseline Spanish inspection found artificial boundaries around removed notes, spacing defects, inconsistent repeated headings and literal technical calques despite positive model scores. Private editorial notes are kept beside the job, not in Git.
- New failing-first tests and scoped independent review closed coherent cleanup, exact raw-source mapping, note groups, ambiguous word joins, inline code/link protection and Markdown hard-break preservation. Repeated original headings now report translation variants in both locales. The enlarged glossary/style calibration keeps the complete request limit; oversized repair diagnostics use an explicit summary, never clipped source text.
- Refined parser preflight on the unchanged original: 92 editable spans, 14 batches per language, 48 removal ranges and exact original reconstruction. Real-model validation of this refinement is pending; the active baseline remains intact.
- Windows error 5 was reproduced with a synthetic checkpoint held open by a reader. New bounded retry tests passed, including persistent failure preserving prior state; an actual Windows reader released after 150 ms verified recovery. The reader responsible for the real incident is not identified. No ACL, security-product or service changes were made.

- Starting implementation checkpoint: `39ee99843ea61f3490943e1381271bce8a9c707c`, branch `naindev/strict-es-quality-gates`; worktree was clean before these design documents.
- At the design baseline, the service had no file parser, document segmentation, checkpoint orchestration or English translation stage.
- At the design baseline, LanguageTool hardcoded Spanish; the implementation now validates both locales explicitly.
- The current Ollama client rejects prompts above 12000 UTF-8 bytes and length-limited generation.
- During the earlier design-only step, no input document was sent to a model and no runtime code was changed. The subsequent approved implementation and real execution are recorded above. Ollama settings remain unchanged.
- Baseline re-run: all 58 unit tests passed. LanguageTool's local language inventory lists Spanish (`es`) and British English (`en-GB`). This is availability evidence, not an English quality evaluation.
- Live listeners remain unchanged: Ollama `::11434`, LanguageTool `127.0.0.1:8082`.

### Next

- Finish the active baseline and inspect both full candidates, preserving all failed evidence.
- Run the synthetic technical-style fixture against the refined version after the baseline releases the local models, then evaluate a fresh private job. Never force old state to resume under changed versions.
- Keep the actual document and all generated outputs outside Git; only synthetic fixtures belong in tests.
- Continue the active local draft run, inspect both outputs and all findings, then complete measured-validation documentation and deliver the files.

### Blocked / not yet delivered

- Baseline runtime is implemented; two private rewritten files are still being generated. Refinement passes unit checks and scoped code review, but its real-model output is not yet verified.
- The earlier strict semantic benchmark still has a known false acceptance; this design must not inherit a claim of production acceptance.
- Ollama must remain unchanged. The latest user request authorizes processing the named document through the existing local model; it does not establish server network isolation or blanket safety for other private documents.
