# Document Rewriting Tasks

## Active task

- `[A]` `TASK-007`: Design the resumable bilingual file-path workflow.
- `[M]` Written design approval is pending before runtime implementation.

## Handoff

### Done

- Read the current repository instructions, task handoff, architecture, runbook and runtime contracts.
- Consolidated interview decisions: professional natural es-ES, wording-only editing, preserved document structure and meaning, unchanged good prose, removal of preparation clutter, no fact investigation, no invented values.
- Recorded the latest request for both Spanish and English candidate files from a supplied path.
- Proposed Markdown/TXT as the first supported formats and en-GB as the consistent English variant.
- Defined a section manifest, bounded context, resumable local state, structural assembly, bilingual audits and separate completion/quality statuses in the specification and plan.

### Verified

- Starting implementation checkpoint: `39ee99843ea61f3490943e1381271bce8a9c707c`, branch `naindev/strict-es-quality-gates`; worktree was clean before these design documents.
- The existing service has no file parser, document segmentation, checkpoint orchestration or English translation stage.
- LanguageTool client currently hardcodes Spanish; using it as an English validator would be incorrect.
- The current Ollama client rejects prompts above 12000 UTF-8 bytes and length-limited generation.
- No input document has been sent to a model during this design step. No runtime code or Ollama setting has been changed.
- Baseline re-run: all 58 unit tests passed. LanguageTool's local language inventory lists Spanish (`es`) and British English (`en-GB`). This is availability evidence, not an English quality evaluation.
- Live listeners remain unchanged: Ollama `::11434`, LanguageTool `127.0.0.1:8082`.

### Next

- Obtain approval of `spec.md` and `plan.md` before implementing the new subsystem.
- Then use the approved design for failing-first tests, local implementation and real execution on the user-supplied draft.
- Keep the actual document and all generated outputs outside Git; only synthetic fixtures belong in tests.

### Blocked / not yet delivered

- Runtime implementation and the two rewritten files are not complete.
- The earlier strict semantic benchmark still has a known false acceptance; this design must not inherit a claim of production acceptance.
- Ollama must remain unchanged. The latest user request authorizes processing the named document through the existing local model; it does not establish server network isolation or blanket safety for other private documents.
