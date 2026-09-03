# Requirements

Requirements are maintained in the versioned specifications:

- `specs/001-spanish-rewrite-benchmark/spec.md`: `REQ-001` through `REQ-015`, draft reference bank and human review.
- `specs/002-local-spanish-rewriter/spec.md`: `REQ-016` through `REQ-032`, local rewriting and deterministic/semantic validation.
- `specs/003-strict-es-quality-gates/spec.md`: `REQ-033` through `REQ-063`, independent local quality gates and evidence integrity.

## Current requirement status

- Structural dataset requirements: implemented and automatically verified.
- Human naturalness and reference approval requirements: pending Aitor review.
- Runtime and benchmark runners: implemented, unit tested and exercised against the local models.
- Current strict semantic acceptance: failed because both auditors accepted unsupported context in `SEMA-022`; see `docs/10-validation.md`.
- Operational privacy: private-text processing is blocked until the current desktop-managed Ollama listener is verified as loopback-only.
- Translation requirements: intentionally out of scope for this phase.
