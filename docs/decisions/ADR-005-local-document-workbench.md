# ADR-005: Local Document Workbench

Status: Proposed

## Context

The owner requires local, no-paid-service PDF/Markdown/TXT intake, conservative
Spanish editing, exact human approval, two English variants, persisted queue
control and a browser interface. Implementation and main publication are explicitly
authorised; ADR ratification remains a separate owner decision.

## Proposed decision

Use a Python standard-library HTTP adapter bound to loopback, one worker, JSON
filesystem repositories, local Tesseract and bounded PDF adapters. Presentation
renders service state; service/domain code owns approvals and transitions. Keep
the existing editorial job checkpoints and dedicated Ollama endpoint. Retain
original bytes and independent revision identities throughout delivery.

## Consequences

No database service, frontend build stack, cloud inference or paid API is required.
Local dependencies must be provisioned before offline document work. Native PDF
extraction cannot guarantee reading order or fidelity; every page requires human
review. PDF/Markdown delivery uses a clean template and rejects unsupported
constructs. DOCX, full PDF layout replication and in-image text editing remain
outside this implementation. A compromised local account can access local data.

Known semantic model failures remain visible. A narrow versioned modality guard
addresses one observed miss without claiming exhaustive semantic equivalence.
