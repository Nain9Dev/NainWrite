# Task Handoff

## Completed and verified

- `[A]` Implemented local PDF/Markdown/TXT intake, extraction approval, conservative
  Spanish review, complete locale previews, differences, separate review evidence,
  exact Spanish approval, both English variants and per-locale final approval.
- `[A]` Added persisted single-worker queue, pause/resume, limited/intensive/night
  request modes, loopback Host/Origin/token checks and confined repositories.
- `[A]` Added clean PDF, Markdown and asset ZIP export with artifact hash checks.
  A document becomes ready only after all three exact final approvals; Spanish
  edits invalidate that readiness. Repeated approval is idempotent.
- `[A]` Added a double-click launcher that starts stopped local dependencies or
  reuses the verified application. Cold-start readiness retries and occupied-port
  refusal were checked; shared Ollama remained unchanged.
- `[A]` Browser upload, extraction review and Spanish pause were exercised with
  synthetic text. Aitor explicitly approved that exact Spanish in the conversation;
  real local generation then produced both English variants.
- `[A]` The first US output strengthened conditional ability. Specification 012
  reproduced the missed distinction and introduced a deterministic check. The
  second real execution retained the finding in attempt one and repaired to
  `We could deliver` in attempt two. British currency formatting still raises a
  literal alert. No final English approval was fabricated.
- `[A]` Mixed PDF export was rendered and visually inspected; critical extracted
  text, table and image retention passed. Portable real OCR and native PDF layout
  checks are recorded in specification 010.
- `[A]` Final verification on 2026-09-10: 193 software tests passed; JavaScript
  syntax passed. PowerShell parsing and both draft-bank structural validators
  passed during implementation. A separately invoked corporate model experiment
  was interrupted after CORP-001; it is retained and is not a completed benchmark.

## Retained evidence

Synthetic jobs under ignored `private/workbench/jobs/` include
`20260909T205445Z-7c43bfb476` (original miss) and
`20260909T210414Z-8680350057` (modality repair). Spanish revision:
`227ccc3ed6d2c300d99e4c085edc37cbe9e3ef11be3fbe6206d742bff8f44dbd`.
Mixed PDF/OCR/export previews remain under ignored `artifacts/`.

## Remaining limits and human actions

- `[M]` Final English and actual customer-document approval remain explicit owner
  actions. Reference, broader naturalness and regional-language acceptance remain open.
- `[A]` Disconnected OS lifecycle and sustained 40-page capacity remain unmeasured.
- `[A]` DOCX, arbitrary structural editing, embedded image text editing and an
  English edit/re-audit screen remain deferred; manual Markdown editing is available.
- `[A]` Original scans remain source evidence; isolated figures inside scans are
  not automatically segmented for reflow. Complex PDF layouts require correction.
- `[H]` ADRs remain Proposed. No paid service, client upload or hardware changes.

## Publication

Aitor explicitly authorised publishing all eligible changes to main, reaffirmed
on 2026-09-10. Source, tests and technical documentation are eligible; private
inputs, generated results, local installations and models are excluded. Remote
main was fetched and is an ancestor of the implementation branch. Publication
and remote SHA verification are the final delivery steps.
