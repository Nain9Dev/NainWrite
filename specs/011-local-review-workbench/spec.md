# Local Review Workbench

Implementation authorised by Aitor on 2026-09-09, following specification 010.

- **WB-001:** When opening the local application, the user shall be able to submit PDF/MD/TXT, view queue and progress, inspect original pages/extraction, edit text and approve an exact complete extraction with a review note.
- **WB-002:** When extraction is approved, a single background worker shall run the existing conservative Spanish workflow, preserve evidence and pause before English. The UI shall show original and Spanish text, a server-generated diff and separate findings, and allow edits followed by review-only execution.
- **WB-003:** When translating, the service shall require current exact Spanish revision approval and explicit confirmation that all meaning doubts have been resolved. It shall retain automatic findings and their acknowledgement independently. It shall produce en-US first and en-GB second, and record final approval separately for each exact exported locale revision.
- **WB-004:** When exporting a reviewed candidate, the service shall provide PDF, Markdown and a portable Markdown/assets ZIP, retain image/table structure and use a clean local-font template. Export is generation, not final linguistic approval. Unsupported rendering constructs shall fail visibly instead of disappearing.
- **WB-005:** When queue work is interrupted, the service shall retain jobs and checkpoints, recover running work as paused after restart and permit explicit resumption. Pause shall take effect at the next safe request/stage boundary without killing inference or changing other processes.
- **WB-006:** When resource mode changes, the service shall offer limited CPU-only inference with at most four CPU threads, or intensive mode using the model service's available acceleration. Optional local night hours may select intensive mode; manual selection overrides the schedule. These modes are request options, not hardware settings or a measured performance guarantee.
- **WB-007:** When handling browser requests, the server shall bind loopback only, reject unexpected Host/Origin and require a random per-process token for API mutations and private reads. It shall confine paths to its data root, reject arbitrary file access, escape all source text and serve no remote dependencies or document URLs.
- **WB-008:** When resuming or approving a document, the service shall verify intake identity and extraction approval and preserve source-to-job association. Source/extraction changes shall invalidate downstream actions; saved old outputs shall remain retained.
- **WB-009:** When reporting readiness, the UI shall distinguish extraction review, Spanish approval, translation generation, automatic findings and final human approval. It shall not present generated or automatically accepted documents as human-approved.
- **WB-010:** When reviewing exports, the interface shall display every complete locale text before its approval controls. Repeating approval of the same immutable revision shall preserve the first recorded approval. Changed export bytes shall prevent viewing, downloading or approving that artifact.
- **WB-011:** When launching from the repository shortcut, the launcher shall open the existing verified local workbench or start the stopped application and its local dependencies without creating a duplicate worker.
- **WB-012:** When all three current locale revisions have explicit final approvals, the service shall mark the document ready. Partial approval or generation alone shall not mark it ready; editing Spanish shall revoke readiness.

## Scope and limits

Use a Python standard-library local server and filesystem repository; no distributed
system, database service or paid dependency. Browser JavaScript only renders state
and captures actions. Local Tesseract and optional PDF libraries were inventoried in
specification 010. Reuse existing loopback Ollama and LanguageTool; start only stopped,
project-scoped instances after ownership checks. Do not load client text for tests.

Human reference/locale acceptance remains `[M]`. English regional competence and
maximum-quality claims cannot be established by unit tests. Model comparison and
advanced document-wide semantic calibration remain separate measured work after
the owner review gate; do not weaken known failures to finish the application.

## Dependency and operation notes

Limited mode runs models on CPU and may be very slow; it avoids requesting GPU
offload but does not reclaim other processes' memory or cap their load. Switching
mode applies at the next model request. Night hours are application settings, not
an OS automation, and work only while the process is running. Reboots do not approve
or automatically resume interrupted work. Browser localhost is not a boundary
against a compromised local account.
