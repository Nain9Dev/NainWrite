# Spanish Rewrite Benchmark Plan

## Delivery slices

1. Specify the benchmark contract and acceptance criteria.
2. Add a failing structural test before the dataset exists.
3. Add 30 draft cases covering the required semantic risks.
4. Add a dependency-free validator and make the tests pass.
5. Record coverage, verification evidence and the human-review gate.

## Verification

- Run `python -m unittest discover -s tests -v`.
- Run `python tools/validate_bank.py`.
- Run `git diff --check`.
- Inspect the coverage summary and review every case identifier.

## Constraints

- No model downloads.
- No network-dependent validation.
- No commit, push or deployment.
- Spanish is allowed only in benchmark inputs and candidate user-facing rewrites; repository documentation and identifiers remain in English.
