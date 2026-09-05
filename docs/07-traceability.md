# Traceability

| Requirement | Evidence | Status |
|---|---|---|
| REQ-001 | Dataset length test | Verified |
| REQ-002 | Sequential identifier test | Verified |
| REQ-003 | Required field contract test | Verified |
| REQ-004 | Non-empty and distinct text test | Verified |
| REQ-005 | Protected literal test | Verified |
| REQ-006 | Draft status test | Verified |
| REQ-007 | Category coverage test | Verified |
| REQ-008 | Protected literals across P0 cases | Structurally verified; semantic review pending |
| REQ-009 | Negation, modality and uncertainty cases | Coverage verified; semantic review pending |
| REQ-010 | Condition, exception, authorization and causality cases | Coverage verified; semantic review pending |
| REQ-011 | Fail-closed behavior | Verified by service unit tests |
| REQ-012 | Python standard-library validator | Verified |
| REQ-013 | Unit tests and CLI validation | Verified |
| REQ-014 | Human review rubric | Documented; execution pending |
| REQ-015 | Model acceptance gate | Historical same-model gate passed; current independent strict gate failed; human approval pending |
| REQ-016 to REQ-019 | Local model, structured output and prompt isolation | Implemented; unit and real Ollama tests passed |
| REQ-020 to REQ-023 | es-ES rewrite and literal preservation contract | Implemented; deterministic benchmark checks passed |
| REQ-024 and REQ-024A | Deterministic validation and bounded repair | Verified by unit tests and two real repairs across 60 results |
| REQ-025 to REQ-028 | Semantic audit, fail-closed status and CLI output | Verified by unit tests and real Ollama execution |
| REQ-029 to REQ-032 | Complete reproducible preliminary benchmark | `artifacts/rewrite-benchmark-20260903T120925Z.json`; human approval pending |
| REQ-033 to REQ-037 | `test_language_tool.LanguageToolClientTests`; live loopback check and identity | Unit and local integration verified |
| REQ-038 and REQ-039 | `LanguageIssueClassificationTests` including explicit lowercase protected literals | Unit verified; rule false positives remain possible |
| REQ-040 | `test_fails_closed_when_required_proofreader_is_missing` | Unit verified |
| REQ-041 to REQ-043 | Independent disagreement, invalid audit range and strict acceptance service tests; complete v10 comparison | Orchestration verified; 28/30 accepted in both runs, strict benchmark failed; model scores do not establish linguistic correctness |
| REQ-044 | GenerationResult model/digest in every observed generation; report fields | Implemented; observed in local artifacts |
| REQ-045 | `SemanticMutationBankTests` | 22 draft cases structurally verified; human labels pending |
| REQ-046 | Corrected unassisted 22-case bank, `semantic-audit-20260903T213432Z.json` | Not satisfied: 16/17 invalid candidates detected; `SEMA-022` falsely accepted |
| REQ-047 | Same corrected unassisted bank | 5/5 valid controls accepted; preliminary labels await human review |
| REQ-048 | Candidate runner and interruption persistence test | Unit verified |
| REQ-049 and REQ-050 | `HumanReviewReportTests` and unchanged draft references | Labels unit verified; human approval pending |
| REQ-051 | `AuditContractTests` | Unit verified |
| REQ-052 | Empty bank and empty candidate tests | Unit verified |
| REQ-053 | `test_style_rejection_does_not_count_as_semantic_detection` and semantic/invariant positive controls | Unit verified |
| REQ-054 | Atomic JSON replacement and interrupted mutation-run checkpoint tests | Unit verified; local partial report observed |
| REQ-055 | Default-unassisted parser and evaluator call assertions | Unit verified |
| REQ-056 | `test_lower_priority_rejection_prevents_rewrite_gate` | Unit verified |
| REQ-057 and REQ-058 | `LanguageRepairTests`; unavailable-proofreader test; focused v10 run | Unit verified; real bounded repair fixed `ESRW-014`, retained review for `ESRW-003` and `ESRW-004` |
| REQ-059 and REQ-060 | `OllamaLimitTests` | Unit verified; direct oversized requests remain unsupported; the document workflow uses separate bounded segmentation |
| REQ-061 | `LocalTransportTests`; proxy and redirect regression checks for the shared transport | Unit verified; both clients use the same explicit proxy-free opener |
| REQ-062 | Missing issue-type and invalid offset tests | Unit verified; incomplete findings raise a controlled error |
| REQ-063 | Strict configuration and minimum-auditor tests; service tests now supply both fake auditors | Unit verified; disabled gates cannot produce strict acceptance |
| REQ-064 | `DocumentJobTests.test_unsupported_format_and_invalid_utf8`, original-byte preservation test | Unit verified |
| REQ-065 to REQ-067 | `DocumentTests`, round-trip, spans, stable IDs, long prose and protected-construct regressions | Unit verified for the supported conservative Markdown subset |
| REQ-068 | Complete-prompt byte check, `test_oversized_prompt_is_rejected_before_model_call`, existing Ollama limit tests | Unit verified; no silent truncation |
| REQ-069 | Missing/extra/empty replacement and saved duplicate coverage tests | Unit verified |
| REQ-070 | Bilingual routing unit test; real synthetic unchanged-Spanish controls; complete refined private-document inspection | Routing verified; professional-naturalness target not fully satisfied in the actual draft |
| REQ-071 | Literal mutation tests, dual semantic audits and complete refined private-document inspection | Not fully satisfied: observed deliverable-state drift and technical scope narrowing missed by both auditors; earlier semantic blind spot remains |
| REQ-072 and REQ-073 | Cleanup range/disclosure, coherent note removal, hard-break/code/link protection and numbered-heading variant tests | Unit verified; explicit range selection requires editorial judgement |
| REQ-074 and REQ-075 | Versioned glossary, whole bounded neighbours, data-only prompt contract; complete v4 evaluation | Mechanisms verified; corrected technical round trip but literal glossary application and inconsistent terminology still impair prose; no authorship claim |
| REQ-076 | Job routing test checks English input is the Spanish output; input/output hash checks | Unit, synthetic and complete private-document evidence revalidation verified; English also inherits upstream semantic errors |
| REQ-077 | Distinct installed digest test, strict locale test and retained per-attempt audits/proofreading | Unit and synthetic real integration verified |
| REQ-078 | Upstream review propagation and evidence-derived status tests | Unit verified |
| REQ-079 | Bounded disagreement repair test and revalidated attempt evidence | Unit verified |
| REQ-080 and REQ-081 | Complete/human approval assertions and interruption/no-English-output test | Unit verified |
| REQ-082 | Atomic checkpoint, bounded Windows reader-lock retries, process lock and interruption/resume tests | Unit verified; real completed private-job resume returned 2 without generation or changed artifact hashes; synthetic Windows reader-lock recovery verified |
| REQ-083 | Source/configuration/tamper/coverage and model/audit/locale evidence mutation tests | Unit verified; checksum is not authentication |
| REQ-084 | Unique jobs, output collision and original preservation tests | Unit verified |
| REQ-085 | File-path CLI help, real smoke execution and resume | Integration verified |
| REQ-086 | Existing loopback proxy-free transport tests; unchanged live listeners | Clients local; server isolation explicitly unverified |
| REQ-087 | Per-span global literal/structure/coverage checks, lexical terminology findings, repeated-source-heading variant test and coverage disclaimer | Refined private run: 92/92 per locale, structural integrity true, repeated headings consistent; literal/terminology findings remain. These checks did not detect all editorial and semantic defects |
| REQ-088 | `test_first_completion_requires_exact_spanish_approval`, `test_both_still_pauses_for_revision_specific_approval`; real corporate smoke | Unit and real local-model pause verified, no English calls/results before approval |
| REQ-089 | `DocumentRevisionTests`, ordinary edits/CRLF/table/code/structural/split/duplicate cases, empty block-marker and short-Setext regressions | Unit verified for conservative wording-only mapping; arbitrary editing is unsupported |
| REQ-090 | `test_review_only_has_genuine_audits_and_no_rewrite`, candidate/hash/audit/prompt tamper tests; complete corporate experiment | Unit verified; 11 complete local dual-audit pairs and one retained length-limit error; no invented writer generation |
| REQ-091 | Exact-hash, review-required acknowledgement, unreviewed revision, altered report and forged-state tests | Unit verified; synthetic approval is not Aitor's document approval |
| REQ-092 | `test_explicit_synthetic_approval_generates_both_from_same_spanish`, actual-client American/wrong-locale HTTP test | Routing unit verified; real en-GB/en-US review controls pass after fixing a client identity bug; actual three-output document completion pending revision approval |
| REQ-093 | `test_original_crosscheck_failure_is_separate_from_generation`, saved crosscheck identity | Unit verified; an original-grounded audit is not a complete semantic proof |
| REQ-094 | Edit/revert/invalid-edit authority revocation, edit-during-English and `test_outdated_revisions_are_visible_to_the_user` | Unit verified; previous snapshots retained and CLI lists outdated revision identities |
| REQ-095 | Multibatch and mid-English recovery, configuration/source/evidence tampering tests; actual paused-job resume | Unit verified; interrupted audit cases retained; actual Spanish-job resume returned 3 without generation or artifact hash changes |
| REQ-096 | Snapshot collision/tamper, completion-boolean and original-change regressions; CLI exit code tests | Unit verified; normal approval pause is exit 3; final editorial approval remains separate |
| REQ-097 | Versioned corporate profile, preserved-literal controls, paired semantic experiment and actual Spanish inspection | Not fully satisfied: CORP-003 falsely accepted; calque and unnecessary framing remain despite 5/5 style scores; older false acceptance remains open |
| REQ-098 | Versioned locale prompts and exact proofreading identity tests | Mechanism verified; no overall naturalness or regional-quality certification |
| REQ-099 | 139 passing tests, two draft-bank validators, 12 synthetic paired controls, actual Spanish pause and independent fix re-review | Finite checks complete: 5/6 semantic mutations detected, 5/6 valid accepted, one length-limit error. Scope quality not certified; whole-change review tracked in active handoff |
| REQ-100 | Versioned document prompt and original/new paired controls | Local evaluation in specification 006; results and limitations in validation history |
| REQ-101 | `DocumentEditorialTests`: calque, empty framing, good prose, geography, quoted/code/link exclusions and repair feedback | Unit verified; findings remain separate from semantic audit decisions |
| REQ-102 | Editorial evidence recomputation, suppression rejection and configuration-change resume tests | Unit verified; prior prompt/evidence jobs require their original runtime |
| REQ-103 | `CalibrationTests`: label isolation, immutable records, changed bank/configuration, interruption, error and style/semantic classification | Unit verified; finite model run evidence recorded in active handoff |
| REQ-104 | Explicit staged-file review, privacy exclusions, full suite, bank validators and remote commit verification | Publication evidence recorded in specification-006 handoff |
