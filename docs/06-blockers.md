# Blockers

## BLK-008: Independent corporate editorial acceptance

- Type: `[M]` independent reader and owner adjudication.
- Status: Actual ratings pending. On 2026-09-09 Aitor confirmed only his own participation; independent reader availability is not a committed dependency. Owner review can proceed but cannot be labelled independent review.
- Evidence: The 40-case external baseline completed without execution or contract
  errors. Both models detect all 20 external non-equivalence labels, but their
  conservative combination disagrees with 17/20 equivalence labels. Inspected
  translations include material meaning changes despite inherited positive labels.
- Impact: Neither high negative-class detection nor these apparent false-positive
  rates establish corporate es-ES accuracy. Labels require independent judgement;
  no prompt or threshold should be tuned to force agreement with disputed labels.
- Next: Complete the blinded external semantic sheet, retain original labels and
  separate adjudications, then lock the corporate wording-only pilot described in
  `docs/12-independent-evaluation.md`. Spanish document approval remains separate.

## BLK-001: Gold reference approval

- Type: `[M]`
- Status: Open
- Impact: The bank can be structurally validated but cannot yet be called a gold benchmark.
- Resolution: Aitor reviews all draft references using `benchmark/review_rubric.md`.

## BLK-002: Target voice confirmation

- Type: `[M]`
- Status: Resolved on 2026-09-03
- Evidence: Aitor confirmed professional Spanish from Spain (`es-ES`).

## BLK-003: Production acceptance

- Type: `[M]`
- Status: Open
- Impact: The historical same-model baseline passed its automated gate, but neither the draft references nor model outputs have received human approval. The independent strict-gate branch has separate evidence and must not inherit that approval.
- Resolution: Review the latest complete human-review sheet and record corrections before calling the bank gold or the model production-safe.

## BLK-004: Independent strict-gate acceptance

- Type: `[A]`, followed by `[M]` reference validation.
- Status: Open.
- Impact: The corrected unassisted 22-case run rejected 16/17 invalid cases and accepted 5/5 valid controls. Both auditors accepted unsupported context in `SEMA-022`. The strict semantic gate failed; the historical 20-case assisted pass cannot override this evidence.
- Resolution: Review the draft semantic labels, preserve the failing regression, and validate any next control on new held-out examples. The final v10 rewrite comparison completed with 28/30 automatically accepted per run; two proofreading rejections and additional editorial defects remain. See `docs/10-validation.md`. Never weaken a gate merely to obtain a pass.

## BLK-005: NainWrite Ollama isolation

- Type: `[A]`, authorised by Aitor on 2026-09-09.
- Status: Dedicated startup and default client routing verified; full offline lifecycle remains unverified.
- Evidence: New default clients use `127.0.0.1:11436`. A dedicated Ollama 0.33.3 process binds only that address and reports cloud disabled. Shared `::11434` remains with the same owner; an occupied-port launch is rejected without changing either owner. Installed model manifests match; no inference was run.
- Limits: This is not global workstation isolation or authentication against local processes. No automatic startup, disconnected full workflow or LanguageTool recovery was tested. Previous jobs with a different endpoint identity require compatible handling; checkpoints must not be edited to bypass guards. See specification 009 and the runbook.

## BLK-006: Bilingual document delivery validation

- Type: `[A]` editorial correction and verification, followed by `[M]` human review. Design approval was already received.
- Status: Implementation, scoped code review and finite execution complete; editorial acceptance open.
- Impact: The refined long document has 92/92 retained spans per locale, preserved structure and an unchanged original. All 14 batches per language require review. Inspection found deliverable-state drift and technical scope narrowing that both semantic auditors missed, alongside unnatural prose. A complete file is not ready for submission.
- Resolution: Preserve the completed local evidence, specify and test source-grounded corrections and negative style/semantic controls, and evaluate the resulting Spanish before its English translation. Do not waive spelling findings or reinterpret model confidence as human approval. See `docs/10-validation.md`.

## BLK-007: Trilingual editorial acceptance

- Type: `[A]` calibration and verification, then `[M]` exact Spanish revision approval.
- Status: Open after finite specification-005 testing.
- Impact: The 12-case draft control experiment detected 5/6 semantic mutations, missed one scope change and had one length-limit execution error on a valid control. The new Spanish document correctly pauses for approval, but still contains a literal calque and unnecessary framing despite maximum model style scores. It is not ready for approval or a claim of perfect writing.
- Resolution: Preserve these failures, specify targeted style/technical-scope calibration with new controls and re-evaluate. Do not authorise actual English generation until Aitor reviews the corrected Spanish revision. Unit-test synthetic approvals do not satisfy that gate.

### Specification-006 follow-up: 2026-09-05

The selected document configuration fixes the three observed Spanish wording defects and detects 6/6 known semantic mutations in the fresh run. The software suite passes 153 tests and reviewed source is published. Editorial acceptance remains open: one valid known control receives spurious audit findings despite the auditor describing the translations as accurate; new style controls can also receive false semantic rejections; the separate short-text unsupported-context failure remains unresolved. Human review and broader independent calibration are still needed. See `specs/006-corporate-calibration/tasks.md` and the selected functional baseline in `docs/10-validation.md`.


## 2026-09-09 operational follow-up

Specifications 010-011 implement local OCR, browser review, queue and PDF/Markdown
export. The launcher started stopped LanguageTool and dedicated Ollama successfully;
the browser exercised extraction and exact Spanish approval, then both English
variants after Aitor's explicit approval of the synthetic text. Shared Ollama PID
8420 remained unchanged. This supersedes the earlier slice's statement that no
inference or LanguageTool restart was tested. A completely disconnected OS test,
40-page endurance run and broad editorial acceptance remain open.

The first US smoke strengthened `podríamos` to `can` despite positive audits.
Specification 012 adds a narrow deterministic review flag; it is not a complete
solution to semantic drift. Final English approval remains pending. Historical
jobs predating `document-fidelity-v2` retain their files but require a new import
to use changed fidelity checks; never edit their checkpoint identities.
