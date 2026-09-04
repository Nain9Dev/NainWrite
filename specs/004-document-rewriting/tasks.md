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
- Parser v2, bilingual prompt v3, job v2 and bounded Windows checkpoint-lock retries are committed and pushed as `4e908a113e04043c3a8831509727c820efd3a766`. Prompt v4 adds a contextual manifold-analysis glossary pair and a synthetic fixture extension; these follow-up changes are currently uncommitted. Current suite: 100 tests pass; `git diff --check` and both draft-bank validators pass.
- Real synthetic UTF-8 file produced complete es-ES and en-GB candidates with automatic acceptance. Local job: `artifacts/document-smoke.rewritten/20260903T225111Z-36a5cd0e29`. Resume verified without regenerating completed work.
- First synthetic attempt under prompt v1 failed on an out-of-range audit confidence; v2 explicitly defines the range, and invalid audits now retain failed evidence instead of claiming acceptance.
- Private-draft preflight: 22439 source bytes, 16902 clean-view bytes, 103 editable spans, 13 batches per language, 48 explicitly recorded removals with the selected preparation cleanup.
- Independent review closed all Important/Critical findings after reference-link rejection and uncached model-identity checks before/after generation were added.
- The actual draft baseline completed in `C:/Users/aitor/Downloads/nlnet-borrador-base-EN-v0.rewritten/20260904T074514Z-8288667699`, with 103/103 retained spans in both languages, preserved structure and unchanged original. Both generated files exist and were inspected, but all 13 batches per language require review. Original session `92751` stopped on Windows access-denied error 5; session `43755` resumed using the exact b054634 runtime exported under `.tools/document-baseline-b054634/` and completed. No checkpoint or prompt migration was performed.
- First actual attempt stopped because LanguageTool was no longer running after the session pause. Started only the existing local LanguageTool installation, hidden, PID 3452; verified `127.0.0.1:8082` and es/en-GB checks, then resumed. Ollama's externally restarted desktop process is PID 9984 on `::11434`; this task did not restart or configure it.
- Added a CLI regression requiring proofreading availability before processing private text. The real job's first Spanish batch completed with two spelling findings, while both model audits passed; it correctly remains review-required.
- Baseline Spanish inspection found artificial boundaries around removed notes, spacing defects, inconsistent repeated headings and literal technical calques despite positive model scores. Private editorial notes are kept beside the job, not in Git.
- New failing-first tests and scoped independent review closed coherent cleanup, exact raw-source mapping, note groups, ambiguous word joins, inline code/link protection and Markdown hard-break preservation. Repeated original headings now report translation variants in both locales. The enlarged glossary/style calibration keeps the complete request limit; oversized repair diagnostics use an explicit summary, never clipped source text.
- Refined parser preflight on the unchanged original: 92 editable spans, 14 batches per language, 48 removal ranges and exact original reconstruction. Real-model validation of this refinement is pending; the active baseline remains intact.
- Windows error 5 was reproduced with a synthetic checkpoint held open by a reader. New bounded retry tests passed, including persistent failure preserving prior state; an actual Windows reader released after 150 ms verified recovery. The reader responsible for the real incident is not identified. No ACL, security-product or service changes were made.
- Full baseline English inspection exposed a missed technical round-trip drift (manifold analysis becoming variety analysis). The contextual glossary was extended under prompt v4 with a failing-first test. The first v3 synthetic job was correctly invalidated after the synthetic fixture was extended during execution; it is not acceptance evidence. Fresh v4 smoke completed in `tests/fixtures/document-technical-style.rewritten/20260904T090435Z-30d7572685`: 8/8 spans per language, no global structural/literal findings, coherent cleanup, repeated headings consistent, meaningful qualifiers preserved and the good Spanish sentence unchanged. It remains review-required because LanguageTool flags `manifold`; English inherits that finding. No spelling gate was bypassed.
- Fresh full private job is active in exec session `31367`, directory `C:/Users/aitor/Downloads/nlnet-borrador-base-EN-v0.rewritten/20260904T090725Z-5aeb7aab56`. It uses parser v2, prompt v4 and job v2, with the same local models and exact source/cleanup ranges. Resume with the current `tools/rewrite_document.py`. Do not change its input, parser, prompts, configuration or model identities while it runs; use stdout progress instead of holding its checkpoint open.

- Starting implementation checkpoint: `39ee99843ea61f3490943e1381271bce8a9c707c`, branch `naindev/strict-es-quality-gates`; worktree was clean before these design documents.
- At the design baseline, the service had no file parser, document segmentation, checkpoint orchestration or English translation stage.
- At the design baseline, LanguageTool hardcoded Spanish; the implementation now validates both locales explicitly.
- The current Ollama client rejects prompts above 12000 UTF-8 bytes and length-limited generation.
- During the earlier design-only step, no input document was sent to a model and no runtime code was changed. The subsequent approved implementation and real execution are recorded above. Ollama settings remain unchanged.
- Baseline re-run: all 58 unit tests passed. LanguageTool's local language inventory lists Spanish (`es`) and British English (`en-GB`). This is availability evidence, not an English quality evaluation.
- Live listeners remain unchanged: Ollama `::11434`, LanguageTool `127.0.0.1:8082`.

### Next

- Complete the active fresh private job and inspect both outputs and all findings. Never force old state to resume under changed versions.
- Keep the actual document and all generated outputs outside Git; only synthetic fixtures belong in tests.
- Continue the active local draft run, inspect both outputs and all findings, then complete measured-validation documentation and deliver the files.

### Blocked / not yet delivered

- Baseline files are complete but have confirmed editorial defects. Refinement passes unit checks and scoped code review, and has completed a finite real synthetic evaluation with an unresolved technical-spelling flag. The refined full private-document run is in progress; no final linguistic approval is claimed.
- The earlier strict semantic benchmark still has a known false acceptance; this design must not inherit a claim of production acceptance.
- Ollama must remain unchanged. The latest user request authorizes processing the named document through the existing local model; it does not establish server network isolation or blanket safety for other private documents.
