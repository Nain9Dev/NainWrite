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
- Remaining question: which additional candidate, if any, merits a controlled comparison after the semantic and style evaluation gaps are addressed? Any candidate must fit the local hardware and preserve the no-paid-service constraint.

## OQ-005: Strict semantic draft labels

- Owner: `[M]` Aitor
- Current state: the corrected bank has 17 invalid candidates and 5 valid controls, all draft.
- Decision needed: review temporal anchoring and unsupported-context cases, especially `SEMA-021` and `SEMA-022`, before using the bank as gold. Model disagreement does not authorize changing a label.

## OQ-006: Desktop service interruption

- Owner: `[M]` Aitor
- Current state: the desktop-managed Ollama listener is `::` on port `11434`.
- Decision on 2026-09-04: leave Ollama unchanged. Service-isolation work is deferred, not verified complete.

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
