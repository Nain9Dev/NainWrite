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
