# Blockers

## BLK-001: Gold reference approval

- Type: `[M]`
- Status: Open
- Impact: The bank can be structurally validated but cannot yet be called a gold benchmark.
- Resolution: Aitor reviews all draft references using `benchmark/review_rubric.md`.

## BLK-002: Target voice confirmation

- Type: `[M]`
- Status: Resolved on 2026-09-03
- Evidence: Aitor confirmed professional Spanish from Spain (`es-ES`).

## BLK-003: Production acceptance

- Type: `[M]`
- Status: Open
- Impact: The historical same-model baseline passed its automated gate, but neither the draft references nor model outputs have received human approval. The independent strict-gate branch has separate evidence and must not inherit that approval.
- Resolution: Review the latest complete human-review sheet and record corrections before calling the bank gold or the model production-safe.

## BLK-004: Independent strict-gate acceptance

- Type: `[A]`, followed by `[M]` reference validation.
- Status: Open.
- Impact: The initial 20-case assisted mutation pass contained two imperfect draft controls. They were corrected and retained as invalid regression cases in the expanded 22-case bank. The corrected unassisted run is required before an acceptance claim.
- Resolution: Complete the corrected mutation suite and final two-pass rewrite benchmark, disclose every false positive and false negative, and obtain human review. Never weaken a gate merely to obtain a pass.
