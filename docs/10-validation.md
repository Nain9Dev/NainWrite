# Local Validation Evidence

## External auditor baseline: 2026-09-05

Specification 007 executed the unchanged v10 document review-only path against
40 hash-selected PAWS-X Spanish test pairs, balanced by external label. Another
40 sentence-disjoint pairs remain unexamined. Provenance, selection, exclusions
and primary research references are recorded in `docs/12-independent-evaluation.md`.

Completed local job:
`artifacts/external-auditors.rewritten/20260905T130759Z-79153014ce`.
The offline comparison validates every retained case and the final result before
reporting metrics. No external pair was generated or repaired by the writer.

| Auditor | Detects external non-equivalence | Accepts external equivalence (semantic bit only) | Disagrees on equivalent label | Strict auditor acceptance |
| --- | --- | --- | --- | --- |
| Qwen local fast2 | 20/20 | 5/20 | 15/20 | 5/40 |
| Gemma 4 | 20/20 | 6/20 | 14/20 | 4/40 |
| Conservative semantic pair | 20/20 | 3/20 | 17/20 | Not a production policy |

There were 5/40 pairwise disagreements, no missing decisions, no invalid audit
contracts and no execution errors. The complete existing pipeline accepted 0/40;
all candidates require review. CLI exit 2 correctly retained the failed aggregate
gate. This aggregate is not corporate-style accuracy: that annotation does not
exist in PAWS-X. Model generation durations totalled 254.55 seconds for Qwen and
218.77 seconds for Gemma, including loading; they are not sustained performance
benchmarks or total workflow wall time.

No false equivalence was observed relative to the 20 negative external labels.
The Wilson 95% interval is nevertheless 0–16.1% for each model and their semantic
combination. Equivalent-label disagreement intervals are 53.1–88.8% for Qwen,
48.1–85.5% for Gemma and 64.0–94.8% for the combination. These descriptive intervals
are not corporate deployment guarantees, and annotation uncertainty is additional.

### Label validity finding

The `false_drift` metric means disagreement with an external inherited label,
not a human-verified auditor mistake. Post-run inspection of the first four
externally positive cases identified material confounds: EXT-002 changes an
imperative into a past-tense action and adds an actor; EXT-008 attaches a clock
time to the crimes instead of the execution. Both retain a positive inherited
label. EXT-003 raises a writing-versus-direction attachment ambiguity, and EXT-007
changes aspect/wording. These are observations for adjudication, not relabelled
gold. The original 40 labels and all model outputs remain unchanged.

Consequently this is an external stress baseline, not a reliable estimate of
strict corporate equivalence accuracy and not evidence that one auditor is
better. It gives no before/after improvement estimate. Aitor confirmed an
independent reader is available; their blind judgement of the sample is pending.
Do not weaken the semantic gate to match a questionable inherited label.

### Software and preservation evidence

- 165 unit/integration tests pass; both historical bank validators pass.
- Independent code review found no Critical/Important issues. Two Minor issues
  (recorded comparison thresholds and normalized-duplicate test coverage) were
  corrected and re-reviewed; the reviewer reran all 12 new tests successfully.
- Import preparation was rerun and retained byte-identical evaluation/reserve
  hashes; the blind sheet omits external labels, model names and audit scores.
- The only new dependency is official PyArrow 25.0.1 in ignored
  `.tools/benchmark-deps`, solely for the pinned public Parquet snapshot. No model,
  Ollama, GPU, global Python or inference-service settings were changed.
- The private original still hashes to
  `01e7258c0a59591aa0c9518b36d080ad673f1696d7d09983a57222afde0586cb`.
  No private document was reprocessed and no Spanish approval or English
  generation was performed. Server isolation remains explicitly unverified.

## Historical assessments

Assessment date: 2026-09-03. Interpretation: preliminary, not production approval.

## Current decision

The implementation checkpoint is published as `de2dee2` on `naindev/strict-es-quality-gates`. The independent strict acceptance gate has **not passed**. Keep human review mandatory: two different model families accepted the same unsupported addition in `SEMA-022`.

Passing the unit suite establishes the tested software behavior, not the linguistic correctness of arbitrary model output. `accepted` means that configured checks found no issue; it is not a proof of semantic equivalence or an authorization to publish a document.

## Measured configuration

| Component | Observed configuration |
|---|---|
| Writer and first auditor | `qwen3.8-local-fast2:latest`, Qwen3.8-27B IQ4_XS |
| Writer digest | `ad4df5727497a8c6c5e2ca7027358fc3f2857d7c9b265fae196b46230406bbaa` |
| Second auditor | `gemma4:latest` |
| Second auditor digest | `c6eb396dbd5992bbe3f5cdb947e8bbc0ee413d7c17e2beaae69f5d569cf982eb` |
| Inference | Ollama 0.33.2; client endpoint `127.0.0.1:11434`; current desktop-managed listener is `::`, not loopback-only |
| Proofreader | Local LanguageTool 6.9-SNAPSHOT, build 2026-09-02 |
| Current prompt | `es-es-professional-v10` |
| Sampling | Temperature 0, seed 42, context 16384 |
| Acceptance thresholds | Semantic confidence at least 0.95; both style scores 5/5 for both auditors |

Model scores are not calibrated probabilities. Different model names do not establish statistical independence of their errors. These custom aliases are not guaranteed public download names.

### Service ownership and network limitation

A live check during the final v10 rewrite run found that Ollama was managed by the desktop application, not the earlier controlled terminal session. Its listener used the IPv6 wildcard `::` on port `11434`. The earlier process-local `OLLAMA_HOST` and `OLLAMA_NO_CLOUD` settings must not be assumed to apply to this replacement process. LanguageTool remained bound to `127.0.0.1:8082`.

The benchmark client still sent only synthetic text to `127.0.0.1` and observed the local model digests above. No LAN reachability or firewall test was performed, so a wildcard bind is not proof of external reachability. It does mean loopback-only server isolation was not established for the current Ollama process. Do not process private documents until the desktop application's listener is deliberately reconfigured and verified. Do not terminate an application-owned server as if it were the task's terminal process.

## Completed evidence

| Evaluation | Result | Interpretation |
|---|---|---|
| Current unit suite | 58 passed | Tested contracts and orchestration pass |
| Bank validators | 30 rewrite cases and 22 semantic cases valid | Structure only; all labels and references remain draft |
| Historical same-model baseline, two runs | 30/30 accepted per run | Weaker gate; cannot substitute for independent evaluation |
| Strict v9 rewrite, two runs | 27/30 accepted per run; exact text/status/issues stability; 761.75 s | Strict gate failed |
| Focused v10 linguistic repair | 1/3 accepted; `ESRW-014` repaired; `ESRW-003` and `ESRW-004` require review; 22.09 s | Focused regression evidence, not a full-bank pass |
| Corrected v10 semantic bank, no authored hints | 16/17 invalid candidates semantically detected and rejected; 5/5 valid controls accepted; 273.85 s | One false acceptance; strict semantic gate failed |
| Full v10 rewrite, two runs | 28/30 accepted per run; `ESRW-003` and `ESRW-004` require review; exact text/status/issues stability; 725.71 s | Strict gate failed; no protected-literal/invariant drift detected |

Rewrite evaluation supplies the bank's authored required-meaning and forbidden-change hints. The corrected semantic evaluation does not. The draft reference is never supplied as the writer's target answer. Assisted rewriting results must not be represented as unassisted generalization evidence.

The earlier assisted 20-case semantic pass used two imperfect draft controls. Their candidates were retained as invalid cases `SEMA-021` and `SEMA-022` after correcting the controls. The historical 20/20 result does not validate the corrected bank.

## Observed failures

### Unsupported context accepted by both auditors

`SEMA-022` compares these synthetic benchmark texts:

- Source: "No está claro si debe actualizarse el informe o el anexo."
- Invalid candidate: "La redacción no permite determinar si la actualización corresponde al informe o al anexo."

The candidate attributes uncertainty to the wording, an explanation not stated by the source. Under the draft strict contract, this is unsupported context. Both auditors returned `equivalent=true`, confidence `0.95`, and both style scores `5`. LanguageTool found no language issue. No deterministic literal check can establish this missing semantic relationship.

This is a correlated semantic blind spot, not a transport failure. Do not resolve it by lowering the severity, changing the expected label to fit the models, or interpreting high self-reported scores as human approval. The draft label itself still requires human review.

### Remaining proofreading rejections

- `ESRW-003`: `DIACRITICS_OTHERS` flags the verb `valida` in a condition. Changing it to the adjective `válida` would be incorrect. The bounded repair retained the candidate, so the gate remained closed.
- `ESRW-004`: the dictionary flags the unprotected technical term `endpoint`. No global dictionary exception or automatic substitution was added. An approved terminology policy is still needed.
- `ESRW-014`: `UPPERCASE_SENTENCE_START` flagged lowercase starts in a numbered inline list. The bounded v10 repair capitalized those starts and then passed all gates in the focused run.

### Editorial observations on automatically accepted output

Inspection of the first full v10 pass also found avoidable redundancy in `ESRW-006`: the candidate first says that some clients accepted and others requested changes, then repeats those outcomes with the counts. Both model audits nevertheless assigned 5/5 naturalness. `ESRW-011` retained the source's awkward `entre 10–15 MB` construction instead of improving it while preserving the literal range.

These are editorial observations, not human gold approval. They demonstrate why an automatic acceptance count is not a count of flawless texts. The next quality iteration needs negative style controls as well as semantic mutations; raising a numeric threshold alone does not calibrate an auditor.

## Local artifact index

Generated reports contain supplied text and remain ignored by Git. This document records curated aggregate results, not a backup of those reports.

| Evidence | Local artifact under `artifacts/` |
|---|---|
| Same-model baseline | `rewrite-benchmark-20260903T120925Z.json` |
| Historical assisted semantic pass | `semantic-audit-20260903T210703Z.json` |
| Strict v9 rewrite comparison | `rewrite-benchmark-20260903T211818Z.json` |
| Focused v10 linguistic repair | `rewrite-benchmark-20260903T213329Z.json` |
| Corrected unassisted semantic evaluation | `semantic-audit-20260903T213432Z.json` |
| Complete strict v10 rewrite comparison | `rewrite-benchmark-20260903T214142Z.json` |
| Complete v10 human-review sheet | `rewrite-benchmark-20260903T214142Z.review.md` |

The full v10 run completed on 2026-09-03 at 23:53:47 Europe/Madrid. All 60 entries use prompt v10 and the listed model digests. The `.partial.json` checkpoint remains local for recovery; the complete JSON report is the authoritative execution artifact. Its strict gate is false. The two-run duration is not a latency guarantee for other workloads.

Current bank SHA-256 values:

- Rewrite: `afd77307e84b2d38ad6f4532e796a914e4b07479442e166f1f288e2ebe4d6bd3`.
- Semantic: `e2e242510fe43da12b79d446c91ea6580d882a7faeb7c5398eed4e95f3878a6b`.

Reproduction commands and service setup are in [the runbook](08-runbook.md). Interrupted or partial runs are not counted as completed evaluations.

## Next acceptance steps

1. `[M]` Review the semantic labels, starting with `SEMA-021` and `SEMA-022`, and approve the intended strict treatment of time and unsupported explanations.
2. `[M]` Approve or correct the 30 proposed references and review model outputs independently against their sources. Approving a reference does not train a model.
3. `[M]` Define approved technical terminology, including whether `endpoint` must remain literal in this product's register.
4. `[A]` Specify and test a next semantic-control iteration against the observed blind spot and new held-out examples; do not promote a prompt solely because it passes known development cases.
5. `[H]` Approve or reject ADR-003 only after reviewing the measured failures and added latency.
6. `[M]` Server-isolation changes are deferred by Aitor; leave the current Ollama instance unchanged. The named-draft exception does not establish general network isolation.

Unattended external publication and blanket claims of error-free rewriting remain outside validated scope. GitHub preserves tracked source, synthetic banks and documentation, not local model weights, runtimes, private documents or ignored generated evidence.

## Bilingual document workflow: 2026-09-04

The design was approved before implementation. Failing-first tests cover source-span parsing, protected values, Markdown round trips, cleanup evidence, bilingual routing, independent audits, checkpoints, interrupted execution, incompatible resume and immutable artifact collisions.

- Initial document implementation verification: 89 tests passing, including the original 58; `git diff --check` and both draft-bank validators passing. Refined completion evidence follows below.
- Independent review found five parser gaps, reproduced with synthetic tests and corrected: signs/currency/relative links, nested prefixes/emphasis/setext markers, invalid fence closing, protected-span splitting, and numbered-field cleanup guards.
- A further saved-evidence finding prompted full revalidation of model digests, raw/parsed audit consistency, locale, proofreading classification and derived statuses. A regression also fixed accidental sharing of the final-attempt issue list with downstream upstream-status flags.
- First real synthetic attempt failed with invalid audit confidence under bilingual prompt v1. The failure was not acceptance. Prompt v2 states numeric ranges explicitly and the runtime retains malformed audit responses as failed evidence.
- The complete two-paragraph real smoke job under prompt v2 produced automatically accepted Spanish and British English candidates. It preserved the literal number, written-approval condition and exception. Its previously correct Spanish sentence stayed unchanged.
- Local smoke evidence: `artifacts/document-smoke.rewritten/20260903T225111Z-36a5cd0e29`; successful resume under the stricter evidence validator performed no new generation. Summed model-call duration was 8.95 seconds for Spanish and 13.46 seconds for English, excluding other work and not a performance guarantee.
- Independent review also closed reference-style Markdown link preservation by explicit rejection, and stale model-alias identity by fresh digest checks before and after each generation.
- The named private document passed parsing preflight and is being processed in its own job directory outside Git. First execution stopped when the previously running LanguageTool service was unavailable after a session pause. Only that existing local corrector was started again, its loopback listener and both languages were verified, and the job resumed. Ollama was not restarted or configured by this task.
- A new CLI regression verifies unavailable proofreading stops the job before private generation. Full private-document generation and editorial inspection remain in progress at this checkpoint.

These finite tests do not resolve the earlier semantic benchmark false acceptance or establish human linguistic approval.

### Document editorial refinement

Inspection of the baseline Spanish pass exposed artificial sentence fragments at note-removal boundaries, spacing defects, inconsistent translations of repeated labels and literal technical calques. Positive scores from both auditors did not reliably identify these defects. The baseline job remains immutable evidence, not a flawless language result.

Parser v2 retains original and cleaned text separately and removes preparation notes before segmentation. Failing-first tests cover coherent sentences, exact source reconstruction, adjacent notes, ambiguous word joins, protected inline code/links and preservation of existing Markdown hard breaks. Scoped independent review initially reproduced three remaining cleanup defects; all three were corrected and closed with additional synthetic checks.

Job v2 reports repeated-source-heading translation variants for each locale. Prompt v3 adds a contextual technical glossary and concrete calque examples without changing local models, their sampling configuration or Ollama. Repair diagnostics above 900 bytes use an explicit summary to retain the full 12000-byte request check. At this checkpoint, 100 unit tests and both draft-bank structural validators pass. Real-model validation of the refinement is still pending.

The running baseline encountered Windows access-denied error 5 during atomic checkpoint replacement. Saved evidence retained all 13 Spanish batches and 7 English batches; the job resumed at English batch 8 using an exact export of its committed runtime, not the changed parser. A synthetic held-open reader reproduced error 5, and releasing that reader allowed replacement. This establishes the locking mechanism, not the identity of the reader involved in the real incident. New bounded retries cover Windows errors 5/32/33; unit tests preserve prior state after persistent failure, and a real synthetic Windows reader released after 150 ms demonstrated successful recovery. No permissions, antivirus or Ollama settings were changed.

The complete baseline now has 103/103 retained spans in both languages, structural checks passing and the original digest unchanged. All 13 Spanish and 13 English batches remain review-required (49 and 52 final batch issue entries, including upstream flags). Inspection found that a technical manifold-analysis term became generic variety analysis in the English round trip despite favourable model scores. Prompt v4 adds an explicit contextual glossary pair and the synthetic fixture now includes optionality and negation around that term. This is a development correction, not a held-out accuracy claim.

The first refined synthetic job under prompt v3 was invalidated because its synthetic input fixture was extended while that job was still running. The end-of-job source check rejected the changed input; no complete output was published or counted as accepted. The private original was not involved in that modification. A fresh v4 fixture job is being evaluated with its source frozen.

The completed v4 synthetic job `tests/fixtures/document-technical-style.rewritten/20260904T090435Z-30d7572685` covers all 8 retained spans in both locales, with no global literal or structural findings. Inspection confirmed coherent note removal, matching repeated headings, the retained technical manifold term, the literal 12, incomplete-dataset qualification, optionality/negation and an unchanged acceptable Spanish sentence. The automatic result remains review-required: Spanish LanguageTool flags the borrowed technical word `manifold`, and English inherits that unresolved flag. Both model audits gave their highest style scores; this is not a human-equivalence approval. A separate fresh v4 full-document run subsequently completed as recorded below.

### Completed refined private-document evaluation

The second complete job finished on 2026-09-04 at 11:51:48 Europe/Madrid. Its private directory is recorded in the active specification handoff, not published as a document fixture. The original, outputs, raw audits and editorial observations remain outside Git. It used `document-spans-v2`, `bilingual-document-v4`, `bilingual-job-v2` and the unchanged model digests listed above; runtime commit `937eacd93835fa0f26b7bf20772d69c7407f09d7` is pushed to the existing feature branch.

| Check | Observed result | Interpretation |
|---|---|---|
| Generation | 14/14 batches per locale; both complete candidate files exist | Workflow complete, not approved prose |
| Coverage and structure | 92/92 retained editable spans per locale; structural integrity true | Supported structural assembly verified |
| Source and cleanup | Original digest unchanged; 48 recorded removal ranges | No original-file modification; omitted preparation content remains in local evidence |
| Automatic status | 0/14 accepted per locale; 46 final batch issue entries per locale | Review required; issue counts include repeated/upstream findings and are not independent errors |
| Global literal checks | Seven Spanish findings, one English finding | Acronym translation/expansion needs individual review, not a blanket exemption |
| Global terminology checks | One Spanish lexical flag; no repeated-heading translation variants | Lexical checks are not a complete terminology or style audit |
| Audit validity | Two English final Gemma audits have out-of-range confidence | Retained as invalid; not converted to acceptance |
| Completed-job resume | Exit 2; no new batch generation; checkpoint, candidate and report hashes unchanged | Idempotent completion and saved evidence revalidated |
| Current local tests | 100 unit tests pass; 30 rewrite and 22 semantic draft cases structurally valid | Software contracts pass; draft references remain unapproved |

Full inspection of both candidates found improved note-removal spacing, consistent repeated labels and preservation of the corrected technical manifold-analysis term through English. It also found a change from a populated deliverable to one being populated, and narrowing of a general benchmark-hosting concept to performance testing. Both Spanish final model audits for these batches reported equivalence, top style scores and confidence 0.98/1.0. English faithfully propagated the flawed Spanish concepts. This is a semantic-control blind spot despite the overall job already being review-required for other findings.

Further Spanish defects include colloquial agreement, redundant processing terminology, vague technical destinations and overly literal glossary application. English retains some redundancies. A source-language label remains in the Spanish title. Private editorial notes identify exact passages without overwriting model-generated evidence. The retained disclosure and factual assertions were not externally verified; empty fields remain empty. No submission, publication or human approval is implied.

The 165 retained model calls comprise 110 Qwen calls (2362.21 seconds total model-call duration) and 55 Gemma calls (283.20 seconds), including writing, audits and repairs. Their summed duration is about 44.1 minutes, excluding non-model work. This one run is not a performance guarantee or a controlled model-speed comparison.

After a later task interruption, completed-job revalidation first returned exit 1 because LanguageTool was no longer listening. The complete artifacts remained intact. Only the existing local corrector was started again, hidden, and its `127.0.0.1:8082` listener was verified; a second revalidation returned exit 2 without artifact changes. Ollama's existing process and `::11434` listener were unchanged. This recovery does not establish unattended service startup or server network isolation.

The finite implementation/evaluation task is complete, but REQ-070/REQ-071 editorial acceptance and BLK-006 remain open. The next iteration needs specified source-grounded corrections and negative style/semantic controls, including held-out examples. Preserve failures and original evidence; do not silently edit checkpoints, suppress terminology rules or equate confident model scores with linguistic correctness.

## Approved trilingual workflow evaluation: 2026-09-04

Specification 005 records the approved corporate profile, editable Spanish and explicit revision-specific translation authority. Both English variants consume the same approved Spanish snapshot and have separate original-source crosschecks. The unit suite exercises synthetic approval events; no actual newly generated Spanish document has been approved by Aitor.

### Software verification and integration findings

The original 100-test baseline passed. After interruption, 133 tests passed on the recovered implementation. Independent review found that an editable paragraph could become a Markdown horizontal rule. The first correction covered long markers but missed short Setext underlines, which the reviewer reproduced. The applicable syntax is documented in [CommonMark 0.31.2 section 4.3](https://spec.commonmark.org/0.31.2/#setext-headings), checked on 2026-09-04. The second correction passed focused regressions and independent scoped re-review; that checkpoint passed 137 tests in 3.485 seconds with no remaining Important/Critical task-review findings.

The whole-change review then identified empty heading/list markers still accepted as prose and a missing user-visible outdated-translation notice. Failing regressions reproduced both defects, including empty constructs inside retained heading/list prefixes. A bounded correction preserves normal wording edits, table-cell symbols and hashtags, rejects those structural edits, and displays the application service's stale revision identities without changing approval rules. The corrected full suite passes 139 tests in 3.431 seconds. The final scoped review is recorded in the active handoff. These software fixes do not change the frozen model experiment below.

Live integration also exposed a gap in the original mocked transformer tests: the actual LanguageTool client accepted `en-US` as a requested locale but still validated every English response against `en-GB`. A failing real-client/mock-HTTP test reproduced it; exact configured-locale validation fixed it. The resumed actual `en-US` control then passed. This failure is not hidden by the earlier unit-test count.

The user interrupted the running evaluation. Seven complete case artifacts survived. The old process was gone and LanguageTool had stopped; only its existing installation was restarted hidden and verified at `127.0.0.1:8082`. Ollama PID 9984 and its `::11434` listener were unchanged. Saved bank/configuration/review evidence was revalidated before continuing; completed cases were not regenerated.

### Frozen review-only controls

The draft bank contains six invalid and six valid semantic pairs. Four development cases target prior failure classes; eight cases were excluded from this iteration's prompt implementation instructions. This small self-authored bank is neither approved gold nor a representative accuracy estimate.

| Result | Count | Interpretation |
|---|---|---|
| Invalid pairs semantically detected | 5/6 | Both-model agreement is not required to reject; Qwen alone caught two of these changes |
| Invalid pairs falsely accepted | 1/6 | CORP-003 narrowed conformance-test hosting to performance tests; both auditors accepted it |
| Valid controls automatically accepted | 5/6 | Includes real en-GB and en-US proofreading plus local model audits |
| Valid controls semantically rejected | 0/6 | The remaining valid case was an execution failure, not a semantic rejection |
| Execution failures | 1/12 | CORP-008 reached the model output-length limit; incomplete output was rejected |

CORP-008's error was explicitly recorded from the observed exception after resumption; no complete/raw audit response was fabricated. The experiment finished evaluating the remaining cases. Complete attempted-case coverage does not mean all calls succeeded. Spelling/style rejections and invalid responses are not counted as semantic detection.

Evidence: `artifacts/corporate-controls.rewritten/20260904T140728Z-9c76f87384/results.json` and `review.md`, with immutable per-case files. Prompt `trilingual-editorial-v5`, evidence contract `trilingual-review-v1`, and the existing model identities stayed fixed. Bank file SHA-256: `5afbbfa42a693c09ca492ffca5add3f8ba3a456e5fb7eba06325cdc1c28d0102`. No prompt tuning occurred in response to the measured control outcomes.

### Real Spanish document pause

The synthetic corporate fixture produced an es-ES candidate in `artifacts/corporate-smoke.rewritten/20260904T144219Z-55c9093396`. All 8 retained prose spans were assembled; the good Spanish sentence, headings, number, written-approval condition and protected product name were preserved on inspection. Source SHA-256 remains `e85043b31ee94451d126961fcd35f8f183e7cec5d0be42c0b54c05b520f2a73c`.

The workflow stopped at `awaiting_spanish_approval`, `human_approved=false`, with zero British/American generation results. Spanish revision SHA-256: `51181dd6c83a2683c783acfdbd8be52e7a5c113c3fa9ce54e9e1cd7d23c4ec71`. Resume returned the explicit CLI exit code 3 without model progress or changed checkpoint/output/report hashes. Human approval was not simulated for this real-model run.

Automatic status remains `review_required`: LanguageTool flags two technical loanword occurrences and one synthetic proper name. No exception was introduced to obtain acceptance. Editorial inspection also found a literal populated-state calque and retention of an unnecessary framing clause. Both revision auditors nevertheless returned positive equivalence and maximum style scores. The proposed corrections remain in separate local editorial observations; generated text is unchanged.

The approval mechanism is exercised, but the requested editorial quality is not fully achieved. Real English document generation remains pending an actually reviewed and approved Spanish revision. Earlier strict-benchmark and private-draft semantic/style failures remain open.

## Corporate calibration and repository delivery: 2026-09-05

Specification 006 adds deterministic es-ES editorial findings to generation, bounded repair, exact revision review and saved-evidence reconstruction. Initial regressions reproduced automatic acceptance of the populated-data calque and empty emphasis despite perfect fake model scores. The new findings flag wording for review; they do not rewrite text themselves or turn style objections into semantic drift.

Prompt v6 made all six known semantic mutations detectable, including the previously missed scope narrowing. It also introduced a false rejection of the valid 'not all' / 'some not' pair. The retained run `artifacts/corporate-controls.rewritten/20260905T000255Z-bc7d0a4147` records 6/6 invalid detections, 5/6 valid acceptances and zero execution errors. Prompt v7 explicitly distinguished literal quantifier meaning from inferred pragmatic implications: the new full run `artifacts/corporate-calibration.rewritten/20260905T000555Z-86ea57246c` detected 6/6 invalid cases and accepted 6/6 valid controls without errors. These are development regressions, not held-out accuracy estimates.

The v7 synthetic document replaced the populated-data calque and removed empty emphasis, while retaining the unchanged good sentence and original constraints. It still produced a redundant conformance-test definition. That new defect was added as a failing regression and corrected through prompt v8 and editorial-rule v3. The v7 generated output remains unchanged in `artifacts/corporate-v7-smoke.rewritten/20260905T000848Z-fc8dff0d55`.

Independent code review found that the evaluator could hide semantic false positives on style controls, pass with one invalid auditor contract, and regenerate a published case after a checkpoint interruption. It also found an unhandled single-quoted expression. All four were reproduced before correction. Re-review closed them; the evaluator now counts these failures explicitly and recovers validated published records before inference. At that checkpoint, the full suite passed 153 tests in 3.622 seconds. Final live evaluation uses prompt v8, editorial rules v3, evidence contract v2 and evaluator v2. Its final results are recorded in the active specification-006 handoff.

Private repository visibility was rechecked before delivery. The pending tracked/untracked source set was inspected for common credential patterns and oversized files; generated artifacts, private input/output folders, credential file types, weights and local review scratch are ignored. This bounded scan is not an exhaustive security audit and does not make repository privacy equivalent to safe secret storage. Ollama configuration was unchanged; only the stopped existing LanguageTool installation was restarted hidden. No cloud inference, new dependency or paid service was used.

### Selected functional baseline

The v8 new-control run completed with 4/4 factual mutations detected, 6/6 suitable controls accepted and 2/2 editorial defects flagged. Both editorial cases were also incorrectly classified as semantic changes, so the stricter calibration gate failed. Separating the audit instructions in v9 reduced one of those false positives but regressed the known-control bank to 5/6 semantic detections and 2/6 good acceptances. It also failed to semantically detect the separate unsupported-context regression. All of these completed results are retained; no failure was relabelled or hidden by overall review-required status.

The selected version is `trilingual-editorial-v10`, which restores the better v8 prompt content under a fresh identity. The 24 retained audit prompt hashes in the v8 new-control run match the restored instructions exactly. This establishes prompt identity, not a new execution or a guarantee of repeatability.

A fresh v10 known-control run, `artifacts/corporate-calibration.rewritten/20260905T124605Z-32a9abe957`, detected 6/6 semantic mutations and accepted 5/6 valid controls. There were no false semantic rejections, execution errors or invalid auditor contracts; the remaining valid case was rejected because Gemma listed correct, equivalent translations in `critical_changes` despite describing them as accurate. The strict calibration gate still failed because a good control was not automatically accepted.

The fresh v10 Spanish fixture, `artifacts/corporate-v10-smoke.rewritten/20260905T124819Z-8c2c935b03`, produced revision `81ab4b4ec1e69371dad8ba64b397acbc06e6c4a32fb7a9c2c5dcf54fd04f5e3f`, byte-identical to the inspected v8 Spanish candidate. It preserves 8/8 spans and the original source, corrects all three targeted wording defects and stops at the Spanish approval phase (actual CLI exit 3). The proper-name spelling finding remains, and Gemma also lists correct wording improvements as critical changes in the revision review. These spurious findings are retained rather than waived. No user-document approval or English generation was performed. Both English workflow branches remain covered by synthetic unit approvals and live locale review controls.

Selected-runtime verification: 153 tests pass; both historical bank validators and whitespace checks pass. The reviewed implementation was committed as `e1c21bdd8fb084207176a3f276efbb49ddf241a2` and pushed to `naindev/strict-es-quality-gates`; the remote SHA was independently checked. Publication reviewed 44 staged files and excluded all generated reports, private documents, credentials and local installations. This is a functional local review workflow with documented limitations, not production editorial certification or proof that further improvement is impossible.
