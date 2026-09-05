# Task Handoff

## Completed

- [A] Verified primary references and frozen evaluation protocol. Source and
  suitability decisions are in `docs/12-independent-evaluation.md`.
- [A] Implemented a reproducible pinned import, per-auditor comparison and blinded
  semantic worksheet. Failing tests preceded implementation. Twelve new tests
  and the complete 165-test suite pass, as do both existing bank validators.
- [A] Executed the unchanged local baseline once: 40/40 cases complete, no
  execution errors, no invalid contracts, actual exit 2. Job:
  `artifacts/external-auditors.rewritten/20260905T130759Z-79153014ce`.
- [A] Both auditors detect 20/20 externally labelled non-equivalent pairs. Qwen
  agrees with 5/20 positive labels, Gemma with 6/20; their conservative semantic
  combination agrees with 3/20. Five paired auditor disagreements. Full existing
  pipeline accepts 0/40; style is not independently labelled by this corpus.
- [A] Post-run inspection found material translation/label confounds in positive
  cases. These are not relabelled; original labels and responses remain intact.
  The result cannot rank auditors or establish corporate accuracy/improvement.
- [A] Independent code review and re-review found no outstanding issues after
  closing two Minor findings. Reviewer independently reran all 12 new tests.
- [A] Repeated preparation retained identical evaluation/reserve hashes. The
  40-case reserve was not inspected or submitted to models.

## Publication

- [A] Final source/privacy inspection and authorised commit/push pending.

## Preserved

Writer/auditor prompts, model weights, Ollama configuration, original private
document and all prior outputs remain unchanged. No actual Spanish approval or
English generation is authorised by this evaluation. PyArrow 25.0.1 was installed
only under ignored `.tools/benchmark-deps` to decode the pinned public dataset;
the runtime has no new inference dependency. Original private draft SHA remains
`01e7258c0a59591aa0c9518b36d080ad673f1696d7d09983a57222afde0586cb`.

## Human gate

- [M] Independent reader availability confirmed by Aitor on 2026-09-05. Actual
  ratings remain pending. Give the reader only
  `artifacts/external-pawsx/frozen-v1/independent-review.md`, not labels or model
  results. This is semantic adjudication, not corporate-style certification.
- [M] Next lock previously unseen corporate excerpts and obtain separate meaning,
  naturalness, clarity and es-ES assessments before any tuning/final holdout.
- [M] Actual Spanish revision approval is still required for English generation.

## Resume state: 2026-09-06

Source, completed comparison and unchanged base HEAD were rechecked after the
user requested continuation. No model run remains active. Finish publication;
do not claim maximum quality or weaken gates while human adjudication is pending.
