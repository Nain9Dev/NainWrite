# Requirements

Requirements are maintained in the versioned specifications:

- `specs/001-spanish-rewrite-benchmark/spec.md`: `REQ-001` through `REQ-015`, draft reference bank and human review.
- `specs/002-local-spanish-rewriter/spec.md`: `REQ-016` through `REQ-032`, local rewriting and deterministic/semantic validation.
- `specs/003-strict-es-quality-gates/spec.md`: `REQ-033` through `REQ-063`, independent local quality gates and evidence integrity.
- `specs/004-document-rewriting/spec.md`: `REQ-064` through `REQ-087`, approved bilingual document workflow and resumable local evidence.
- `specs/005-approved-trilingual-workflow/spec.md`: `REQ-088` through `REQ-099`, approved corporate profile, editable Spanish, revision-specific translation authority and independent en-GB/en-US outputs.
- `specs/006-corporate-calibration/spec.md`: `REQ-100` through `REQ-104`, reproducible editorial findings, semantic calibration, finite evaluation and private-repository delivery.
- `specs/007-independent-auditor-evaluation/spec.md`: `REQ-105` through `REQ-109`, independently sourced semantic evaluation, frozen reserve, auditor comparison and separate human editorial gates.
- `specs/009-local-product-readiness/spec.md`: `READY-001` through `READY-011`, confirmed product scope; `ISO-001` through `ISO-004`, dedicated Ollama isolation.

## Current requirement status

- Structural dataset requirements: implemented and automatically verified.
- Human naturalness and reference approval requirements: pending Aitor review.
- Runtime and benchmark runners: implemented, unit tested and exercised against the local models.
- Current strict semantic acceptance: failed because both auditors accepted unsupported context in `SEMA-022`; see `docs/10-validation.md`.
- Operational privacy: dedicated Ollama startup on `127.0.0.1:11436` with cloud disabled was verified on 2026-09-09. New default clients use it; shared `::11434` remains unchanged. Full offline operation, host security and future dependency isolation are not established. No private document was processed in this slice.
- Historical translation workflow: implemented for UTF-8 Markdown/TXT, Spanish first and British English second. Specification 005 replaces automatic progression in new CLI jobs with explicit revision approval and both English variants; see the active handoff for current verification.

- `specs/010-document-intake/spec.md`: `IN-001` through `IN-007`, local PDF/OCR intake and exact extraction approval.
- `specs/011-local-review-workbench/spec.md`: `WB-001` through `WB-012`, local queue, review interface, resource modes, export and launcher.
- `specs/012-conditional-modality/spec.md`: `MOD-001` through `MOD-003`, regression for conditional ability strengthened in translation.

The browser/OCR/export flow is implemented and has finite workstation evidence.
DOCX, editable text inside images, arbitrary layout replication, full disconnected
OS verification, sustained capacity and broad human linguistic acceptance remain
unestablished. Main publication was explicitly authorised in the latest owner message.
