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
- Impact: The corrected unassisted 22-case run rejected 16/17 invalid cases and accepted 5/5 valid controls. Both auditors accepted unsupported context in `SEMA-022`. The strict semantic gate failed; the historical 20-case assisted pass cannot override this evidence.
- Resolution: Review the draft semantic labels, preserve the failing regression, and validate any next control on new held-out examples. The final v10 rewrite comparison completed with 28/30 automatically accepted per run; two proofreading rejections and additional editorial defects remain. See `docs/10-validation.md`. Never weaken a gate merely to obtain a pass.

## BLK-005: Desktop-managed Ollama listener

- Type: `[M]`
- Status: Deferred by Aitor on 2026-09-04; isolation not verified.
- Impact: The desktop application's listener is `::` on port `11434`, not loopback-only. Earlier task-terminal settings do not establish the replacement process's configuration. Aitor requested leaving Ollama unchanged and subsequently authorised local-model processing of the named draft. That request is not general approval for other private documents or proof of network isolation.
- Resolution: Do not restart Ollama or change firewall rules under the current instruction. Any later isolation work requires a separately coordinated interruption and listener verification. Current document-workflow calls must continue to use proxy-free loopback transport.

## BLK-006: Bilingual document workflow not implemented

- Type: `[M]` design approval, followed by `[A]` implementation and verification.
- Status: Open.
- Impact: The current short-text service cannot yet accept a document path, preserve its full structure across sections, resume a job or generate a checked English version.
- Resolution: Approve `specs/004-document-rewriting/spec.md` and `plan.md`, then implement with failing-first tests and inspect real local outputs. Do not claim that the two requested files have already been produced.
