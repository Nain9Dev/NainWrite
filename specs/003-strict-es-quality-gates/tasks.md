# Strict es-ES Quality Gates Tasks

## Active task

- `[A]` `TASK-006`: Add and verify independent local quality gates.

## Human gates

- `[M]` Review model outputs and proposed gold references after automated verification.
- `[H]` Approve or reject proposed ADR-003.

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
- After continuation, both local services were restarted. Ollama 0.33.2 is bound to loopback with cloud inference disabled for this process.
- Completed historical v9 assisted 20-case run: 20/20 expected classifications, all 15 invalid cases rejected by both semantic auditors, duration 276.18 seconds. This is not evidence for the corrected 22-case bank.
- First strict rewrite attempt stopped at case 15 after Ollama reported its model process exited with a CTRL+C signal. The cause of that external interruption is not established; memory exhaustion is not supported by this log.
- A new strict v9 run with atomic checkpoints completed its first pass: 27/30 accepted; three LanguageTool rejections (`ESRW-003`, `ESRW-004`, `ESRW-014`). Its second pass is running.
- Full unit suite: 49 passed before input/output safety tests; both additional safety tests passed separately.
- Complete v9 strict comparison: 27/30 accepted in each of two runs, no deterministic drift, exact stability, 761.75 seconds. The strict acceptance gate failed because of LanguageTool findings in `ESRW-003`, `ESRW-004` and `ESRW-014`.
- V10 focused repair run: `ESRW-014` passed after a bounded linguistic repair; `ESRW-003` and `ESRW-004` still require review. No deterministic drift was observed.
- Full suite after review fixes: 57 tests passed. One additional rewrite-checkpoint regression test was subsequently added and is pending the next full run.
- Latest full suite: 58 passed. Both draft banks passed structural validation; compilation and whitespace checks passed.
- Publication preflight: no credential-pattern match, model weight, runtime archive, generated report or local tool installation staged. Remote privacy reverified.

### Next

- Finish the corrected unassisted 22-case mutation run (currently executing).
- Complete the final strict 30-case rewrite benchmark twice, without weakening failed gates.
- Publish this verified implementation checkpoint to the feature branch while retaining explicit pending acceptance gates.
- Update architecture, runbook, traceability and reproducible evidence before publication.

### Blocked

- Gold and production acceptance remain blocked on human review.
