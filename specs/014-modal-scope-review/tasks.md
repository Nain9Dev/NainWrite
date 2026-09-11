# Task Handoff

## Completed and verified

- `[A]` Read repository instructions and the current linguistic-review baseline.
- `[A]` Added failing regressions for another sentence masking stronger commitment,
  swapped sentence scope, merged sentences and English month/modal `May` confusion.
- `[A]` Added shared sentence/count checks and recognised-date exclusion in the
  existing literal-fidelity path. Version is now `document-fidelity-v3`.
- `[A]` Valid controls preserve conditional alternatives, compatible multiple
  sentences, dates, quoted/code mentions and unqualified original ability.
- `[A]` Generation with positive synthetic audits still retains the scope finding
  across both bounded attempts. Removing it from saved evidence is rejected.
- `[A]` Final suite on 2026-09-11: 207 tests passed; `git diff --check` passed.

## Limits and remaining evidence

- `[A]` Sentence alignment is positional and only used when sentence counts match.
  Counts also supply a conservative fallback. Complex scope sharing, sentence
  reordering, abbreviations and paraphrases may produce review questions or escape
  this narrow rule. This is not a full parser or a proof of semantic equivalence.
- `[A]` No new real-model benchmark or live UI execution was performed in this
  slice. Synthetic auditors verify software contracts, not model quality.
- `[M]` Actual document approval and broader regional/naturalness evaluation remain
  pending. Existing findings and historical document files are retained.
- `[A]` No dependencies, downloads, paid services or hardware changes were needed.
  Changed fidelity configuration applies to new jobs, not silently to old checkpoints.

## Publication

The owner has authorised continued implementation and saving eligible changes to
main. The full suite is green; source publication and remote verification complete
this slice. Private inputs, outputs, model files and local installations are excluded.
