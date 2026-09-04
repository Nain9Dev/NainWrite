# Local Validation Evidence

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

- Current implementation verification: 89 tests passing, including the original 58; `git diff --check` and both draft-bank validators passing.
- Independent review found five parser gaps, reproduced with synthetic tests and corrected: signs/currency/relative links, nested prefixes/emphasis/setext markers, invalid fence closing, protected-span splitting, and numbered-field cleanup guards.
- A further saved-evidence finding prompted full revalidation of model digests, raw/parsed audit consistency, locale, proofreading classification and derived statuses. A regression also fixed accidental sharing of the final-attempt issue list with downstream upstream-status flags.
- First real synthetic attempt failed with invalid audit confidence under bilingual prompt v1. The failure was not acceptance. Prompt v2 states numeric ranges explicitly and the runtime retains malformed audit responses as failed evidence.
- The complete two-paragraph real smoke job under prompt v2 produced automatically accepted Spanish and British English candidates. It preserved the literal number, written-approval condition and exception. Its previously correct Spanish sentence stayed unchanged.
- Local smoke evidence: `artifacts/document-smoke.rewritten/20260903T225111Z-36a5cd0e29`; successful resume under the stricter evidence validator performed no new generation. Summed model-call duration was 8.95 seconds for Spanish and 13.46 seconds for English, excluding other work and not a performance guarantee.
- Independent review also closed reference-style Markdown link preservation by explicit rejection, and stale model-alias identity by fresh digest checks before and after each generation.
- The named private document passed parsing preflight and is being processed in its own job directory outside Git. First execution stopped when the previously running LanguageTool service was unavailable after a session pause. Only that existing local corrector was started again, its loopback listener and both languages were verified, and the job resumed. Ollama was not restarted or configured by this task.
- A new CLI regression verifies unavailable proofreading stops the job before private generation. Full private-document generation and editorial inspection remain in progress at this checkpoint.

These finite tests do not resolve the earlier semantic benchmark false acceptance or establish human linguistic approval.
