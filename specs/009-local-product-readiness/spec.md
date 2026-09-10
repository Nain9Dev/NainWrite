# Local Product Readiness

## Authority and scope

Aitor completed the decision interview on 2026-09-09. These product requirements
record his answers; they do not establish implementation or linguistic acceptance.
The immediate delivery is the decision record and the explicitly authorised
Ollama isolation slice. It does not authorise implementation of the entire roadmap,
document approval, paid services, publication, commits or pushes.

## Confirmed product requirements

- **READY-001:** When an existing Spanish or English document is submitted, the system shall first produce conservative, formal, natural es-ES, preserving meaning and suitable wording. Professional publications, commercial proposals and client emails are the priority use cases, in that order. Reorganisation shall require explicit selection.
- **READY-002:** When PDF, Markdown or TXT is submitted, the system shall account for the entire document, including scanned pages, reading order, tables, images, footnotes, links and multiple columns. Unsupported or uncertain content shall remain visibly unresolved, never silently omitted.
- **READY-003:** When extraction is uncertain, the system shall present the original page and doubtful extraction for correction or replacement. Independent sections may continue, but missing content or unreadable quantities shall prevent final document approval.
- **READY-004:** When generating a deliverable, the system shall preserve headings, order, lists, tables, images and their relationships using a clean template, and shall provide PDF and editable Markdown with required local assets. Exact source layout replication and DOCX are deferred.
- **READY-005:** When images contain text, the system shall retain the original image, translate editable captions and legends, and flag relevant untranslated image text with a separate transcription or translation. Image text replacement is deferred.
- **READY-006:** When reviewing Spanish, the system shall display the full document, highlighted changes and separate questions, allow manual editing and renewed review, and require explicit approval of the exact reviewed revision before English generation. Unresolved meaning questions shall block final approval.
- **READY-007:** When Spanish is approved, the system shall generate independent en-US and en-GB versions from that revision, with checks against the retained original and separate final human review. en-US has priority if delivery must be staged. Units, amounts, obligations and names shall not be converted merely to force regional differences.
- **READY-008:** When processing private content, the system shall use local inference, OCR, review and export without Internet after component installation, retain originals and job history until user-directed deletion, and keep updates separate. No paid service, model or hardware purchase is authorised; existing-machine electricity consumption is not a measured zero-cost claim.
- **READY-009:** When multiple documents are submitted, the system shall expose a local browser queue with progress, pause and resume, limited and intensive modes, optional night scheduling and a manual mode override. Intensive mode shall use available resources without changing hardware settings or interrupting other projects.
- **READY-010:** When documenting capacity, the project shall use 5-10 pages per day with peaks of 40 pages as the workload target. Larger project documents commonly have 25-30 pages and may reach 40. One hour is guidance, not an execution cutoff or measured throughput promise.
- **READY-011:** When evaluating quality, the project shall separate completeness, fidelity, naturalness, professional tone and locale findings, retain known false acceptances/rejections, and obtain Aitor's actual reviews before claiming editorial acceptance. Aitor is the only committed reviewer; independent and locale-specific English competence are not established by availability alone.

## Immediate isolation requirements

- **ISO-001:** When a new client or CLI uses default configuration, it shall target the dedicated NainWrite endpoint `http://127.0.0.1:11436`, with no fallback to shared port 11434.
- **ISO-002:** When starting dedicated Ollama, the launcher shall bind only `127.0.0.1:11436`, disable cloud features through its child environment, reuse installed model storage, launch hidden and verify its own listener and cloud-disabled startup evidence before reporting success.
- **ISO-003:** If the dedicated port is occupied or verification fails, the launcher shall fail without terminating an existing service. Cleanup may terminate only the process it launched. Shared listeners, global environment, firewall, model weights and GPU settings shall remain unchanged.
- **ISO-004:** When an old job contains a different endpoint identity, the existing configuration guard shall reject incompatible resumption rather than editing checkpoints or claiming a seamless migration.

## External dependencies and human actions

- `[A]` Reuse installed Python, PowerShell and Ollama; verify executable identity and official isolation configuration. No download needed for this slice.
- `[A]` Later investigate local OCR, PDF extraction/rendering, browser UI and model licences before selecting dependencies; no component is selected by this interview.
- `[A]` Later inventory local GPU contention before resource scheduling; other agents' compute location is unanswered.
- `[M]` Aitor can manually review examples; actual reference labels and document approvals remain pending. A proposed 12-fragment pilot does not replace existing reference obligations or the separate final evaluation.
- `[M]` English meaning/locale reviewing competence remains to be established through actual review, not assumed.
- `[H]` Existing Proposed ADRs remain Proposed; product answers do not silently approve their technical details.

## Acceptance boundaries

The isolation slice requires a failing routing regression first, a passing software
suite, live listener ownership and cloud-disabled evidence, an unchanged shared
process and read-only local API checks. No private inference or network-disconnection
test is needed for this slice. Loopback binding is not a security boundary against
other local processes or proof that every future dependency works offline.
All READY requirements require their own implementation evidence before closure.
