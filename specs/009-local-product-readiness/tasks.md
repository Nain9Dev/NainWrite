# Task Handoff

## Completed

- `[A]` Read canonical docs and recorded Aitor's completed decision interview.
- `[A]` Confirmed installed Ollama reports 0.33.3 and shared listener is `::11434`, PID 8420. Dedicated port 11436 was free. No LanguageTool listener was present on 8082.
- `[A]` Checked official Ollama FAQ on 2026-09-09: child environment supports `OLLAMA_HOST` and `OLLAMA_NO_CLOUD=1`; cloud-disabled startup has an explicit log marker.

## Verified

- `[A]` Both new default-routing tests failed against shared port 11434 before implementation, then passed after introducing the dedicated default. Existing proxy/redirect controls remain unchanged.
- `[A]` Final suite: 168 tests pass in 3.650 seconds, including old-endpoint resume rejection with unchanged checkpoint and zero generation calls.
- `[A]` Hidden launcher started dedicated Ollama 0.33.3, PID 47016, at `127.0.0.1:11436`; process start time `2026-09-09T08:48:41.3434330Z`. Signature valid; PowerShell 7.6.5. Cloud-disabled startup marker and version endpoint verified.
- `[A]` Repeated launch refused occupied port without changing listener owners. Shared `::11434` remained PID 8420. Installed model names/digests match both endpoints; dedicated `/api/ps` reported zero loaded models. No model inference or private source processing.
- `[A]` Reconciled current charter, requirements, open questions, task routing, blockers, architecture diagram, runbook and traceability with the interview and observed isolation. ADR-004 remains Proposed.
- `[A]` PowerShell parser and `git diff --check` passed. Startup log ignore status verified. Final listener snapshot retained dedicated 47016 and shared 8420; no LanguageTool listener on 8082.

## Next

- `[A]` Design the first bounded document extraction/OCR slice with page provenance, uncertain-content review and completeness tests before implementation. The larger roadmap remains specified, not implemented.
- `[M]` Present actual reference examples for Aitor's manual review; do not substitute interview answers for labels or document approval.

## Pending / not established

- `[A]` All future READY requirements need implementation-specific evidence; PDF/OCR, general PDF export, browser UI and queue are not delivered.
- `[M]` Actual manual reference and document reviews are pending. No new Spanish revision or translation has been approved.
- `[A]` GPU contention, measured capacity, restart recovery and full offline operation are unverified.
- `[A]` LanguageTool remains stopped. Dedicated Ollama is running but is not automatically restarted after a reboot; the full pipeline is not operationally verified by this slice.
- `[M]` Independent review and English locale competence are not established.
- `[H]` Existing ADRs remain Proposed.

## Preserved

Pre-existing changes to `docs/07-traceability.md`, untracked specification 008 and
`NainWrite-Documents/` were retained. Private inputs and existing generated jobs
were not opened or changed. Shared services, model weights and GPU configuration
remain unchanged. Startup logs are ignored under `.tools/nainwrite-ollama/`.
No commit, push, paid dependency, download or scheduled task was created.

## Stop point

Decision recording and the authorised isolation slice are complete. All broader
product implementation, actual language acceptance and Proposed ADR ratification
remain separate. The dedicated service can be stopped using the runbook's verified
PID/path/start-time check; no global settings require rollback.


## Subsequent authorised delivery

The statements above describe the isolation-only checkpoint. Specifications
010-012 subsequently implement intake, queue, browser review, export and a
conditional-modality regression. LanguageTool was restarted and local synthetic
inference exercised. Aitor explicitly authorised commit and push to main in the
latest follow-up. Current delivery evidence is in specification 011/012 handoffs.
