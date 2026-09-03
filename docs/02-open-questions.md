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
- Current state: the editorial interview is complete enough for the proposal in `specs/004-document-rewriting`.
- Decision needed: approve the initial Markdown/TXT workflow, proposed `en-GB` variant, local resumable outputs and explicit draft/quality status before implementation.
