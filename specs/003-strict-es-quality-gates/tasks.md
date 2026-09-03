# Strict es-ES Quality Gates Tasks

## Active task

- `[A]` `TASK-006`: Implementation and evaluation checkpoint complete; strict model acceptance has failed and must remain open. Evidence-only publication follows implementation commit `de2dee2` on the same feature branch.

## Human gates

- `[M]` Review model outputs and proposed gold references after automated verification.
- `[H]` Approve or reject proposed ADR-003.
- `[M]` Coordinate a safe interruption of the desktop-managed Ollama application before changing its wildcard listener.

## Handoff

### Done

- Baseline imported into the private repository and published on `main` as `7b20a0c`.
- Official repositories and documentation for Qwen3.8, Ollama structured output, LanguageTool and Vale reviewed.
- Baseline weaknesses recorded in the specification.
- Local LanguageTool client, dual audits, strict audit response ranges and candidate evaluator implemented.
- A 20-case semantic mutation bank and an executable runner added.
- Human-review labels now distinguish the source, the Qwen rewrite and the proposed reference in Spanish.
- Prompt v9 defines concrete style-rating anchors and distinguishes grammatical reformulation from material semantic changes.
- Added strict audit parsing, empty-candidate rejection, semantic-only mutation detection counts, default unassisted evaluation and atomic partial reports.
- Corrected two imperfect draft controls and retained their old candidates as `SEMA-021` and `SEMA-022`; the bank now contains 22 cases.
- Prompt v10 adds one constrained linguistic repair. Invariants and all independent gates are repeated; original proofreading evidence is retained.
- Oversized prompts and length-limited generation now fail closed.
- Independent code review identified four important issues: default HTTP proxy/redirect behavior, malformed proofreading findings treated as advisory, optional independent audit bypass, and mutation gates without valid controls. All four were fixed with regression tests; scoped re-review confirmed all four addressed without new breakage.
- Implementation checkpoint committed and pushed as `de2dee2` on `naindev/strict-es-quality-gates`; `main` was not merged or changed.
- Added curated validation evidence in `docs/10-validation.md`, with failures visible from the README and traceability. Raw reports and local tools remain ignored.

### Verified

- Private remote: `Nain9Dev/nainwrite-es`.
- Baseline unit tests: 18 passed.
- Baseline bank: 30 structurally valid draft cases.
- No credential-shaped value was found in publication preflight.
- Port `8081` belongs to an unrelated Adminer container and shall not be changed.
- Java 17.0.20.1 installed side by side; the existing Java 8 installation was preserved.
- LanguageTool 6.9-SNAPSHOT, build 2026-09-02, verified on `127.0.0.1:8082` with a real Spanish agreement error.
- Initial semantic benchmark: 15/15 invalid cases rejected, 0/5 valid controls accepted. The strict gate failed.
- Prompt v8 benchmark: 15/15 invalid cases rejected, 3/5 valid controls accepted. The strict gate still failed.
- The remaining v8 failures were a grammatical-form false rejection by Gemma and an incorrectly blocked explicitly protected lowercase technical literal.
- Unit tests reproduce the two defects and pass after prompt v9 and protected-literal classification changes.
- The third execution was interrupted before a report was saved. It is not counted as evidence.
- Earlier task-controlled services were restarted with process-local loopback and cloud-disabled settings. This is historical evidence, not a claim about the later desktop-managed replacement process (see below).
- Completed historical v9 assisted 20-case run: 20/20 expected classifications, all 15 invalid cases rejected by both semantic auditors, duration 276.18 seconds. This is not evidence for the corrected 22-case bank.
- First strict rewrite attempt stopped at case 15 after Ollama reported its model process exited with a CTRL+C signal. The cause of that external interruption is not established; memory exhaustion is not supported by this log.
- A strict v9 run with atomic checkpoints completed its first pass with 27/30 accepted; three LanguageTool rejections (`ESRW-003`, `ESRW-004`, `ESRW-014`). Both completed passes are recorded below.
- Full unit suite: 49 passed before input/output safety tests; both additional safety tests passed separately.
- Complete v9 strict comparison: 27/30 accepted in each of two runs, no deterministic drift, exact stability, 761.75 seconds. The strict acceptance gate failed because of LanguageTool findings in `ESRW-003`, `ESRW-004` and `ESRW-014`.
- V10 focused repair run: `ESRW-014` passed after a bounded linguistic repair; `ESRW-003` and `ESRW-004` still require review. No deterministic drift was observed.
- Full suite after review fixes: 57 tests passed, followed by the additional rewrite-checkpoint regression and the complete 58-test run below.
- Latest full suite: 58 passed. Both draft banks passed structural validation; compilation and whitespace checks passed.
- Publication preflight: no credential-pattern match, model weight, runtime archive, generated report or local tool installation staged. Remote privacy reverified.
- Corrected unassisted v10 semantic bank completed: 21/22 expected classifications, 16/17 invalid candidates semantically detected and rejected, 5/5 valid controls accepted, 273.85 seconds. Both auditors falsely accepted the unsupported context in `SEMA-022`. `REQ-046` is not satisfied.
- Latest continuation: all 58 unit tests passed again; both structural validators and Python compilation passed.
- Live service ownership check: Ollama is now managed by `ollama app.exe`, listening on `::` port `11434`. The earlier controlled Ollama terminal has exited. LanguageTool still listens only on `127.0.0.1:8082`. No LAN reachability or firewall test was performed; no desktop application was terminated.
- The full v10 benchmark uses only synthetic bank text through `127.0.0.1`. First-pass editorial inspection found redundancy in accepted `ESRW-006` and an unimproved range construction in accepted `ESRW-011`; automatic acceptance must not be described as flawless writing.
- Full v10 rewrite benchmark completed: 28/30 accepted in each of two runs, `ESRW-003` and `ESRW-004` still require review, exact text/status/issues stability, no deterministic invariant drift, 725.71 seconds. The strict gate failed. Artifact: `artifacts/rewrite-benchmark-20260903T214142Z.json` and its `.review.md` sheet.
- Independent documentation/evidence review found no Critical or Important discrepancies. It verified semantic counts, earlier rewrite results, model/bank digests and the actual listener ownership; it was not a production or merge approval.

### Next

- Start the next session by verifying the remote feature-branch tip and reading `docs/10-validation.md`; do not inherit a production-acceptance claim from this checkpoint.
- After human review of draft labels, specify the next semantic and negative-style control iteration, including held-out examples. Do not keep tuning a prompt solely to pass known examples.
- Aitor subsequently requested leaving Ollama unchanged. Do not restart or reconfigure it. The new document-workflow design and active handoff are in `specs/004-document-rewriting`.

### Blocked

- Gold and production acceptance remain blocked on human review; the current strict semantic gate also has a known false acceptance.
- Server network isolation remains unverified (`BLK-005`). Aitor declined changing Ollama for now and later explicitly requested running the named draft through the existing local model. That request must not be generalised to other documents or treated as proof of isolation.
