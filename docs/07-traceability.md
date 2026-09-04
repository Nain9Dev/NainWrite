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
| REQ-059 and REQ-060 | `OllamaLimitTests` | Unit verified; long-document processing intentionally unsupported |
| REQ-061 | `LocalTransportTests`; proxy and redirect regression checks for the shared transport | Unit verified; both clients use the same explicit proxy-free opener |
| REQ-062 | Missing issue-type and invalid offset tests | Unit verified; incomplete findings raise a controlled error |
| REQ-063 | Strict configuration and minimum-auditor tests; service tests now supply both fake auditors | Unit verified; disabled gates cannot produce strict acceptance |
| REQ-064 | `DocumentJobTests.test_unsupported_format_and_invalid_utf8`, original-byte preservation test | Unit verified |
| REQ-065 to REQ-067 | `DocumentTests`, round-trip, spans, stable IDs, long prose and protected-construct regressions | Unit verified for the supported conservative Markdown subset |
| REQ-068 | Complete-prompt byte check, `test_oversized_prompt_is_rejected_before_model_call`, existing Ollama limit tests | Unit verified; no silent truncation |
| REQ-069 | Missing/extra/empty replacement and saved duplicate coverage tests | Unit verified |
| REQ-070 | Bilingual routing unit test; two-paragraph real smoke with unchanged good Spanish sentence | Finite integration evidence; not universal language correctness |
| REQ-071 | Literal mutation tests and dual semantic audits; earlier semantic blind spot remains | Controls implemented; perfect preservation not established |
| REQ-072 and REQ-073 | Cleanup range/disclosure and numbered-heading variant tests | Unit verified; explicit range selection requires editorial judgement |
| REQ-074 and REQ-075 | Versioned glossary, whole bounded neighbours, data-only prompt contract | Implemented; cross-section terminology quality requires human review |
| REQ-076 | Job routing test checks English input is the Spanish output; input/output hash checks | Unit and synthetic real integration verified |
| REQ-077 | Distinct installed digest test, strict locale test and retained per-attempt audits/proofreading | Unit and synthetic real integration verified |
| REQ-078 | Upstream review propagation and evidence-derived status tests | Unit verified |
| REQ-079 | Bounded disagreement repair test and revalidated attempt evidence | Unit verified |
| REQ-080 and REQ-081 | Complete/human approval assertions and interruption/no-English-output test | Unit verified |
| REQ-082 | Atomic checkpoint, process lock and interruption/resume tests | Unit verified; real completed-job resume verified |
| REQ-083 | Source/configuration/tamper/coverage and model/audit/locale evidence mutation tests | Unit verified; checksum is not authentication |
| REQ-084 | Unique jobs, output collision and original preservation tests | Unit verified |
| REQ-085 | File-path CLI help, real smoke execution and resume | Integration verified |
| REQ-086 | Existing loopback proxy-free transport tests; unchanged live listeners | Clients local; server isolation explicitly unverified |
| REQ-087 | Per-span global literal/structure/coverage checks, lexical terminology findings and coverage disclaimer | Implemented; finite batch audits are not exhaustive document semantic proof |
