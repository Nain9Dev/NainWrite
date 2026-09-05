# Approved Trilingual Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development to implement this plan. Steps use checkbox syntax for tracking. Repository instructions override skill defaults for paths, publication and private data.

**Goal:** Test a resumable, human-gated es-ES to en-GB/en-US document workflow without modifying prior evidence.

**Architecture:** Preserve the legacy bilingual orchestrator for historical code/tests. Add a revision-aware orchestrator using the existing parser, transformer and atomic store. Extract a reusable review-only contract so edited Spanish and original-grounded English checks carry genuine audit evidence, not fabricated writer output.

**Tech Stack:** Python 3.12 standard library, unittest, local Ollama and LanguageTool.

**Spec:** `specs/005-approved-trilingual-workflow/spec.md`.

Execution closed on 2026-09-04; see `tasks.md` for final evidence and remaining editorial limits. The unchecked initial missing-module-output step is an interrupted historical evidence gap, not a request to recreate or fabricate a RED run after implementation. The recovery report retains what the original worker actually reported; subsequent correction RED/GREEN evidence and the final 139-test run are recorded separately. Real document approval and publication remain outside completed automated tasks.

## Global Constraints

- Only UTF-8 `.md` and `.txt` inputs within the existing conservative parser subset are supported.
- Only loopback inference and proofreading are permitted; Ollama, GPU, firewall and service settings remain unchanged.
- Original documents, historical jobs, model weights and generated reports must not enter Git or be overwritten.
- Retain the existing 12000-byte complete-prompt limit, bounded source batches and at most one generated repair; never truncate source or candidate text to fit.
- Automated acceptance is not human approval or a guarantee of equivalence.
- Changes in code, prompts or evidence contracts require a new configuration identity; do not silently migrate old checkpoints.
- No commit, push, merge, publication or private-document approval is implicit in a test run.

## File responsibilities

- `document_prompts.py`: versioned corporate profile and three locale instructions.
- `language_tool.py`, `document_transform.py`, `document_evidence.py`: exact locale identity, shared validation and generated evidence.
- New `document_review.py`: review-only text checks with saved evidence revalidation.
- New `document_revision.py`: pure editable-span mapping and revision identity validation.
- New `editorial_job.py`: approval/revision state machine and resumable Spanish/English stages; no CLI rendering rules.
- `document_store.py`: any additional file operations stay in this persistence boundary.
- `tools/rewrite_document.py`: argument parsing, progress and next-action messages only.
- New `tests/test_document_review.py`, `test_document_revision.py`, `test_editorial_job.py`; existing locale/CLI tests extended.
- Root controller owns specification, technical docs, traceability, synthetic calibration fixtures and live evidence. Runtime implementer must not edit these shared documents.

### Task 1: Revision-aware three-language vertical slice

**Ownership:** `[A]` One implementation worker owns runtime and tests listed above; no subagents, no commits, no model/service mutations, no live inference. Root performs useful independent reference/fixture/evaluation work. The review gate covers the integrated state machine rather than splitting mutually dependent evidence contracts between workers.

**Interfaces:**

- Consume existing `Manifest`, `make_batches`, `sha`, `DocumentTransformer.transform`, `publish`, `read_state`, `save_state`, `job_lock` and generated-evidence revalidation.
- Produce `DocumentTransformer.review(items, replacements, locale, context)` returning review-only evidence with locale, replacements, hashes, proofreading, both audits, issues and derived status; delegate implementation to `document_review.py` where appropriate.
- Produce `document_revision.map_revision(manifest, baseline_replacements, edited_text)` returning original-ID replacements or a controlled ValueError for ambiguous/structural edits.
- Produce `editorial_job.start_job(input_path, transformer, *, output_dir=None, clean_notes=False, omit_lines=())` and `run_job(job_dir, transformer, *, progress=None, approve_spanish=None, acknowledge_review=False)`.
- Return summary fields `phase`, `generation_complete`, `automatic_status`, `human_approved`, `revision_sha256`, `files`, `editable_file`, `review_file`. `human_approved` means approval of the exact Spanish revision for translation, not final publication.
- CLI stays `python tools/rewrite_document.py --input PATH` / `--resume JOB`. Add `--approve-spanish SHA256` only with resume and `--acknowledge-review`. Existing `--both` must not bypass the new mandatory gate. Explain old checkpoint incompatibility rather than migrating or translating it silently.
- CLI exit codes: `3` for the normal Spanish-approval pause, `0` for complete/accepted, `2` for complete/review-required, `1` for failure. A pause is neither an error nor full completion.

- [x] Add failing tests before runtime behavior changes. Minimum first assertions:

```python
result = run_job(job, service)
self.assertEqual('awaiting_spanish_approval', result['phase'])
self.assertFalse(result['generation_complete'])
self.assertFalse(result['human_approved'])
self.assertFalse(any(call[1]['target_locale'].startswith('en-') for call in service.client.calls))
with self.assertRaises(ValueError):
    run_job(job, service, approve_spanish='0' * 64)
```

- [ ] Run `python -X utf8 -m unittest discover -s tests -p test_editorial_job.py -v`; record the missing-module/interface failure, not an unrelated fixture failure.
- [x] Add US proofreading acceptance and wrong-locale rejection tests; review-only tests must assert zero rewrite calls, genuine audit provenance, invalid confidence rejection, candidate-hash and audit-response tamper rejection.
- [x] Implement locale and shared review contracts. Generated evidence keeps its distinct shape; review-only evidence must never fabricate a generation. Both reviewers use existing strict audit parser/status rules and current model identities. Use target locale for expected proofreading response, not a blanket English fallback.
- [x] Implement pure edit mapping using the generated baseline and original spans. Equal text maps directly. Diff operations may modify only one unambiguous editable region; any operation touching protected/noneditable text or crossing an unresolved span boundary fails. Reassembly must exactly equal edited text. Reject empty prose and unsupported inline structure. Add tests for ordinary sentence edits, unchanged input, CRLF, tables/code, structural deletion, long split-boundary ambiguity and duplicate text.
- [x] Implement a new job-version state machine with original/configuration identity, Spanish generation results, editable file, immutable revisions, review-only results, approval record and per-revision English results. On first Spanish completion publish baseline and create editable copy once, save its SHA and return awaiting approval. Never overwrite user edits when resuming.
- [x] On resume load the editable copy through the store, validate mapping and bytes, create a new immutable revision if needed, and run/resume review-only batches against original source. Preserve the prior revision and mark previous translations outdated. Revision identity binds SHA, source, configuration and evidence. Save after every batch; use the existing job lock.
- [x] Require approval SHA to match the reviewed current Spanish bytes. Refuse approval when evidence is incomplete or stale. Review-required Spanish requires explicit acknowledgement and remains review-required. Check current Spanish bytes again after model work and before publishing so concurrent edits cannot approve or publish a stale revision as current.
- [x] After approval generate each English locale from immutable approved Spanish replacements, then review the English result against original source in a separate review-only call. Persist both evidence types and propagate upstream/crosscheck failures without altering their original audit facts. Validate all saved evidence before trusting resumed progress.
- [x] Publish each revision's three snapshots and report without clobbering earlier artifacts. A changed editable file invalidates current authority even after a previously complete job. Completion must be derived from complete coverage, not a saved boolean alone. Summaries must keep completion, automatic quality, approval and staleness distinct.
- [x] Extend tests to approve a synthetic fixture explicitly, compare both English generation inputs to the same approved Spanish, edit Spanish after completion and assert old outputs retained/new English calls blocked, interrupt mid-English and resume only missing work, reject approval/evidence/hash/configuration tampering, and retain upstream review status. No synthetic approval is Aitor's document approval.
- [x] Run focused tests while iterating; finish with `python -X utf8 -m unittest discover -s tests -v` and `git diff --check`. Write RED/GREEN commands and output, changed files, remaining limits and self-review findings to the assigned report. Do not commit; root packages the uncommitted diff for independent review.

### Task 2: Finite local evaluation and documentation

**Ownership:** `[A]` Root controller; `[M]` actual document editorial approval remains separate. This task uses the reviewed runtime interface from Task 1 and can prepare independent fixtures/documentation while implementation runs.

- [x] Verify existing services and installed model digests without changing settings; verify actual `en-US` LanguageTool response identity.
- [x] Add a small synthetic corporate Markdown fixture containing an already good Spanish sentence, a populated reference set, hosting without a performance qualifier, a conditional delivery and a proper name. Add separate original/candidate semantic controls, labelled draft, with changed state/scope plus unseen condition/negation controls and valid alternatives. Do not include private document passages.
- [x] Invoke the CLI on that fixture, verify it stops with Spanish and no English, inspect actual output/report and source SHA. Human approval is not manufactured. Unit tests exercise the approval event; the real three-language run remains pending Aitor's approval of the displayed Spanish revision.
- [x] Run a finite review-only evaluation of the synthetic semantic controls, persisting raw evidence under ignored `artifacts/`; distinguish semantic detection from a style-only rejection. Do not tune prompts to hide measured failures during this run.
- [x] Update `docs/02-open-questions.md`, architecture/data-model Mermaid diagrams, runbook, traceability and active tasks with verified versus pending results. Document editable-file limitations and exact CLI usage; do not claim arbitrary file support or perfect writing.
- [x] Package the runtime diff and obtain task and whole-change review. Address important findings with the implementer, covering tests and scoped re-review. Keep docs and generated evidence distinct.
- [x] End with paths to Spanish and report, measured outcomes, limitations, and the explicit next approval gate. Update active handoff before ending. Leave changes local unless a separate publication decision is made.
