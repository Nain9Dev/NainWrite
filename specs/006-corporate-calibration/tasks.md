# Corporate calibration and delivery handoff

## Current

- `[A]` Implementation and independent review complete. Final selected configuration is `trilingual-editorial-v10`, `corporate-style-v3`, `trilingual-review-v2`, evaluator `corporate-evaluation-v2`.
- Publication explicitly authorized by Aitor on 2026-09-05 is complete for the implementation: commit `e1c21bdd8fb084207176a3f276efbb49ddf241a2` pushed to `naindev/strict-es-quality-gates`; local and remote SHA verified identical. Final validation is recorded below and in `docs/10-validation.md`, delivered in the subsequent documentation-only commit.
- Editorial acceptance is still open. No evidence establishes maximum possible quality or error-free rewriting.

## Done

- Preserved and integrated the prior specification-005 trilingual workflow.
- Added reproducible editorial findings for populated-data calques, empty emphasis and the observed redundant conformance definition. These reach repair and both saved-evidence validators.
- Added quote/code/link and geographic-use exclusions; apostrophes do not conceal unquoted findings.
- Added a reusable finite evaluator with withheld labels, immutable records, explicit semantic/style/contract/transport outcomes and recovery of published records after a checkpoint interruption.
- Added two paired corporate banks and a document-path regression for the separate short-text unsupported-context failure.
- Strengthened repository exclusions and documented the operating, data and security boundaries.

## Verified

- Failing-first editorial regressions reproduced acceptance with perfect fake audits; evaluator regressions reproduced three review findings and the publication/checkpoint crash window.
- Independent review closed all three Important evaluator findings and the quote-exclusion finding; subsequent review accepted the bounded conformance-rule addition and checked ignored publication paths.
- Full selected-runtime suite: 153 tests passed in 4.015 seconds. Both existing draft-bank validators pass (30 rewrite and 22 semantic cases). These are software/data-contract checks, not linguistic approval.
- v6 known controls: 6/6 invalid detected, 5/6 valid accepted; CORP-008 falsely rejected. Local run: `artifacts/corporate-controls.rewritten/20260905T000255Z-bc7d0a4147`.
- v7 known controls: 6/6 invalid detected, 6/6 valid accepted, no execution errors. Local run: `artifacts/corporate-calibration.rewritten/20260905T000555Z-86ea57246c`.
- v8 new controls: 4/4 invalid detected, 6/6 good controls accepted, 2/2 style defects flagged. Both style cases were also incorrectly classified as semantic drift, so the strict gate FAILED. No execution/contract errors. Local run: `artifacts/corporate-calibration.rewritten/20260905T001228Z-b21ec38651`.
- v8 Spanish fixture removes all three targeted wording defects and retains good Spanish, scope, condition, number and protected name on inspection. Automatic review remains required for the synthetic proper name Northbridge. Local run: `artifacts/corporate-v8-smoke.rewritten/20260905T001507Z-19bf123e6f`.
- v9 separated audit/writer instructions but regressed. New controls: one remaining semantic false positive; known controls: only 5/6 semantic detections and 2/6 good acceptances; unsupported-context regression: 0/1 semantic detections. All runs completed without execution/contract errors. Evidence directories: `20260905T001648Z-652786ff0e`, `20260905T001902Z-01533b96e9`, `20260905T002115Z-1ba0ba62fb` under `artifacts/corporate-calibration.rewritten/`.
- v10 restores the better v8 prompt content under a fresh version identity. All 24 retained v8 audit prompt hashes match the restored instructions; old evidence remains historical, not fabricated as a new run.
- Original private draft and prior artifacts remain unchanged. Only the stopped existing LanguageTool installation was restarted; Ollama settings and existing process were not modified.
- GitHub identity and private visibility verified. Reviewed publication paths have no detected common credential patterns or oversized files. Inputs, outputs, weights, credentials, local tools and generated reports are excluded. This is a bounded inspection, not an exhaustive security certification.

## Final live verification

- Fresh v10 evaluation is complete: 6/6 invalid detected, 5/6 good controls accepted, no semantic false positives or execution/contract errors; spurious Gemma critical-change comments on accurate translations keep the strict gate failed. Run: `artifacts/corporate-calibration.rewritten/20260905T124605Z-32a9abe957`.
- Fresh v10 Spanish smoke is complete and paused normally (CLI exit 3), 8/8 spans. Revision `81ab4b4ec1e69371dad8ba64b397acbc06e6c4a32fb7a9c2c5dcf54fd04f5e3f` matches the inspected v8 wording; the revision review retains the proper-name spelling finding and spurious Gemma critical-change comments on correct wording improvements. Run: `artifacts/corporate-v10-smoke.rewritten/20260905T124819Z-8c2c935b03`.

## Next

- `[A]` Before further prompt/model changes, specify a separately reviewed evaluation corpus and compare alternatives. Current evidence supports improvement and functional review, not maximum possible quality.
- `[M]` Obtain actual Spanish revision approval before translating a user document. Synthetic unit approvals exercise both English branches but do not count as Aitor's approval.

## Remaining limits

- Stable software behavior does not establish flawless language. False semantic rejections on style controls remain measured; broader semantic blind spots and the separate short-text SEMA-022 failure remain unresolved.
- Do not continue tuning the same small bank as if it were independent evidence. The next quality decision needs a separately reviewed corpus and comparison of approaches/models under the same protocol.
- Only the supported UTF-8 Markdown/TXT subset is covered. No PDF/DOCX pipeline or arbitrary document restructuring.
- Ollama's listener is not certified as isolated; the owner requested leaving it unchanged. LanguageTool may need its existing startup procedure after session interruption.
- The private long draft has not been reprocessed in this iteration. No new user-document English translation, human approval, main-branch merge or release certification has occurred.
