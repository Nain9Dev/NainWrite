# Spanish Rewrite Benchmark Tasks

## Active task

- `[A]` `TASK-001`: Create and structurally validate a 30-case draft benchmark for `es-ES` rewriting.

## External actions

- `[M]` `TASK-002`: Confirm the `es-ES` locale and desired professional tone.
- `[M]` `TASK-003`: Review and approve or correct every draft reference before it becomes a gold reference.
- `[H]` `TASK-004`: Approve any future ADR that changes the benchmark acceptance policy.

## Handoff

### Done

- Specification and implementation plan created.
- Added 30 draft cases across six categories.
- Added a dependency-free command-line validator and unit tests.
- Added the human review rubric and lifecycle documentation.

### Verified

- `python -m unittest discover -s tests -v`: 6 tests passed.
- `python tools/validate_bank.py`: 30 draft cases passed structural validation.

### Next

- `[M]` Aitor confirms the locale and tone, then reviews the 30 draft references.
- After approval, create the first versioned gold benchmark and implement the local model runner.

### Blocked

- Gold-reference status is blocked on Aitor's review.
- Model comparison is intentionally blocked until reference approval.
