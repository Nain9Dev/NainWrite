# Requirements

Requirements are maintained in the versioned specifications:

- `specs/001-spanish-rewrite-benchmark/spec.md`: `REQ-001` through `REQ-015`, draft reference bank and human review.
- `specs/002-local-spanish-rewriter/spec.md`: `REQ-016` through `REQ-032`, local rewriting and deterministic/semantic validation.
- `specs/003-strict-es-quality-gates/spec.md`: `REQ-033` through `REQ-063`, independent local quality gates and evidence integrity.
- `specs/004-document-rewriting/spec.md`: `REQ-064` through `REQ-087`, approved bilingual document workflow and resumable local evidence.

## Current requirement status

- Structural dataset requirements: implemented and automatically verified.
- Human naturalness and reference approval requirements: pending Aitor review.
- Runtime and benchmark runners: implemented, unit tested and exercised against the local models.
- Current strict semantic acceptance: failed because both auditors accepted unsupported context in `SEMA-022`; see `docs/10-validation.md`.
- Operational privacy: Ollama isolation remains unverified and unchanged by request. Aitor authorised local processing of the named draft with this limitation understood; other private documents require their own scope decision.
- Translation workflow: implemented for UTF-8 Markdown/TXT, Spanish first and British English second. Automated checks and human approval remain distinct.
