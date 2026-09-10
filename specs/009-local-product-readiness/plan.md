# Delivery Plan

## Current bounded slice

1. `[A]` Record the completed interview and remaining evidence gaps.
2. `[A]` Inspect shared Ollama and a free dedicated port; verify official documentation.
3. `[A]` Add failing default-routing tests before changing runtime behaviour.
4. `[A]` Implement dedicated defaults and a hidden, process-scoped launcher with verified startup and safe cleanup. Preserve old job configuration guards.
5. `[A]` Run routing tests and the existing suite; start and verify the dedicated service using metadata only. Reconcile current docs and handoff.

## Later implementation slices, not executed by this interview

1. `[A]` Source extraction and OCR with page provenance, coverage accounting, uncertainty review and adversarial tables/columns/footnotes.
2. `[A]` Document-wide terminology, cross-section references and coherent bounded rewriting; preserve semantic regressions.
3. `[A]` PDF and portable Markdown/assets export with extraction comparison and visual inspection.
4. `[A]` Local browser review, revision approval and final locale reviews.
5. `[A]` Persistent sequential queue, pause/resume, recovery, resource modes and optional schedule; measure contention before claiming capacity.
6. `[A]` Offline execution checks after dependencies are installed; lifecycle and privacy review.
7. `[M]` Aitor's reference and pilot review, then separate frozen final evaluation. Model comparison follows measured deficiencies, not a presumed ranking.

The future UI only captures input and presents state. Services/domain own editorial
and queue rules; repositories own persistence. Detailed architecture and data model,
including Mermaid diagrams, must precede each implementation slice.

## Rollback and limits

The dedicated service uses a separate port and child environment. Stopping only its
verified process reverses the live startup; no global configuration is changed.
The default endpoint change intentionally makes new jobs require this service.
Existing checkpoint endpoint mismatches remain errors; never rewrite history.
No full UI, OCR, export, scheduler, model inference, service auto-start or OS firewall
configuration is implemented in this slice. No Git publication is authorised.
