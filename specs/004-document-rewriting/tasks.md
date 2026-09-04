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

- Implementation baseline is `ad1c28b09b19ea0678f366775102ef51f5e83424`; current implementation is uncommitted on the existing feature branch.
- Current suite: 89 tests pass; `git diff --check` and both draft-bank validators pass.
- Real synthetic UTF-8 file produced complete es-ES and en-GB candidates with automatic acceptance. Local job: `artifacts/document-smoke.rewritten/20260903T225111Z-36a5cd0e29`. Resume verified without regenerating completed work.
- First synthetic attempt under prompt v1 failed on an out-of-range audit confidence; v2 explicitly defines the range, and invalid audits now retain failed evidence instead of claiming acceptance.
- Private-draft preflight: 22439 source bytes, 16902 clean-view bytes, 103 editable spans, 13 batches per language, 48 explicitly recorded removals with the selected preparation cleanup.
- Independent review closed all Important/Critical findings after reference-link rejection and uncached model-identity checks before/after generation were added.
- The actual draft is running in the local job `C:/Users/aitor/Downloads/nlnet-borrador-base-EN-v0.rewritten/20260904T074514Z-8288667699`; active exec session at this handoff is `92751`.
- First actual attempt stopped because LanguageTool was no longer running after the session pause. Started only the existing local LanguageTool installation, hidden, PID 3452; verified `127.0.0.1:8082` and es/en-GB checks, then resumed. Ollama's externally restarted desktop process is PID 9984 on `::11434`; this task did not restart or configure it.
- Added a CLI regression requiring proofreading availability before processing private text. The real job's first Spanish batch completed with two spelling findings, while both model audits passed; it correctly remains review-required.

- Starting implementation checkpoint: `39ee99843ea61f3490943e1381271bce8a9c707c`, branch `naindev/strict-es-quality-gates`; worktree was clean before these design documents.
- The existing service has no file parser, document segmentation, checkpoint orchestration or English translation stage.
- LanguageTool client currently hardcodes Spanish; using it as an English validator would be incorrect.
- The current Ollama client rejects prompts above 12000 UTF-8 bytes and length-limited generation.
- No input document has been sent to a model during this design step. No runtime code or Ollama setting has been changed.
- Baseline re-run: all 58 unit tests passed. LanguageTool's local language inventory lists Spanish (`es`) and British English (`en-GB`). This is availability evidence, not an English quality evaluation.
- Live listeners remain unchanged: Ollama `::11434`, LanguageTool `127.0.0.1:8082`.

### Next

- Implement the approved design with failing-first tests, local implementation and real execution on the user-supplied draft.
- Keep the actual document and all generated outputs outside Git; only synthetic fixtures belong in tests.
- Continue the active local draft run, inspect both outputs and all findings, then complete measured-validation documentation and deliver the files.

### Blocked / not yet delivered

- Runtime implementation is complete and tested; the two private rewritten files are still being generated.
- The earlier strict semantic benchmark still has a known false acceptance; this design must not inherit a claim of production acceptance.
- Ollama must remain unchanged. The latest user request authorizes processing the named document through the existing local model; it does not establish server network isolation or blanket safety for other private documents.
