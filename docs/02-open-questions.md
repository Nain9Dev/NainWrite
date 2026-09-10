# Open Questions

## OQ-001: Target locale

- Owner: `[M]` Aitor
- Status: Resolved on 2026-09-03.
- Decision: professional Spanish from Spain (`es-ES`).

## OQ-002: Voice profile

- Owner: `[M]` Aitor
- Status: Resolved for the first benchmark.
- Decision: clear, direct, professional, natural and non-ornate.

## OQ-003: Reference approval

- Owner: `[M]` Aitor
- Current state: all 30 references are drafts.
- Decision needed: approve or correct each reference using the human review rubric.

## OQ-004: Model comparison set

- Owner: `[H]` Aitor
- Status: Partially resolved.
- Current measured candidate: the installed Qwen3.8-27B IQ4_XS writer. No comparative evidence establishes that it is the strongest available model for this task.
- Update on 2026-09-09: Aitor's constraint is no paid expenditure, with local professional-use-compatible tooling. Candidate selection is a technical evaluation task after live hardware, licence and quality checks; no new download or best-model ranking was established by the interview.

## OQ-005: Strict semantic draft labels

- Owner: `[M]` Aitor
- Current state: the corrected bank has 17 invalid candidates and 5 valid controls, all draft.
- Decision needed: review temporal anchoring and unsupported-context cases, especially `SEMA-021` and `SEMA-022`, before using the bank as gold. Model disagreement does not authorize changing a label.

## OQ-006: Desktop service interruption

- Owner: `[M]` Aitor
- Historical decision on 2026-09-04: leave shared Ollama unchanged.
- Update on 2026-09-09: Aitor explicitly authorised isolation without interrupting other projects. A dedicated `127.0.0.1:11436` instance with cloud disabled was verified; the shared `::11434` instance remains unchanged. New default jobs use the dedicated endpoint; old checkpoint configuration guards remain enforced.

## OQ-007: Written bilingual document design

- Owner: `[M]` Aitor
- Status: Resolved; Aitor approved the initial design on 2026-09-04. Implemented evaluation and unresolved editorial failures are recorded in `specs/004-document-rewriting/tasks.md`.

## OQ-008: Corporate profile and three-language approval flow

- Owner: `[M]` Aitor
- Status: Design approved on 2026-09-04; implementation/testing requested.
- Decision: editable es-ES first, explicit approval of the reviewed revision, then independent en-GB and en-US translations with original-source crosschecks. See `specs/005-approved-trilingual-workflow/spec.md` and `docs/11-editorial-profile.md`.
- Separate pending action: review and approve an actual Spanish revision. Design approval is not document approval.

## OQ-009: Independent reader and corporate holdout

- Owner: `[M]` Aitor and an independent reader.
- Availability confirmed by Aitor on 2026-09-05. Actual ratings remain pending.
- PAWS-X closes external semantic-label sourcing, not corporate es-ES naturalness.
  The blind sheet and subsequent corporate pilot protocol are described in
  `docs/12-independent-evaluation.md`.
- Update on 2026-09-09: Aitor is the only committed reviewer and confirms manual review availability. Do not depend on the colleague's participation or describe owner review as independent. Actual ratings and English locale competence remain unverified.

## OQ-010: Local product readiness interview

- Owner: `[H]` Aitor; scope decisions recorded on 2026-09-09.
- Decision: see `specs/009-local-product-readiness/spec.md` for all confirmed requirements. Volume is 5-10 pages/day with peaks of 40 pages, not 40 documents/day. One hour is guidance, not a hard timeout.
- Remaining technical work `[A]`: sustained capacity, broader layout coverage and a disconnected OS lifecycle test. OCR/export/UI/queue are now implemented with finite tests; software dependency and local runtime evidence are in specifications 010-012. Aitor's agents' compute location remains unanswered; inspect before resource-intensive work.
- Remaining evidence `[M]`: actual reference and document reviews, including separate English locale assessment. Interview approval does not approve any generated document or existing Proposed ADR.


## OQ-011: Current synthetic language review

- `[M]` On 2026-09-09 Aitor explicitly approved the displayed synthetic Spanish
  proposal for both English translations. This approval does not cover customer
  documents, final English or historical samples.
- The first actual US translation changed conditional ability to `can`, missed by
  both auditors; specification 012 adds a deterministic regression. British
  currency formatting raised an existing literal alert. Both outputs are retained.
- No new product decision blocks using the review interface. Actual document
  acceptance and Proposed ADR ratification remain the owner's actions.
