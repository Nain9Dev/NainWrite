# ADR-001: JSONL and Fail-Closed Benchmark Validation

Status: Proposed

## Context

The benchmark needs human-readable diffs, simple streaming, stable identifiers and validation without third-party runtime dependencies. Semantic safety requires uncertain results to remain unapproved.

## Proposed decision

- Store one benchmark case per JSONL line.
- Keep reference rewrites in `draft` state until explicit human approval.
- Reject structural inconsistencies rather than attempting automatic repair.
- Treat any future invariant mismatch as `review_required`.

## Consequences

- Cases are easy to inspect and process independently.
- Multi-line source formatting requires escaped JSON strings.
- JSONL does not enforce a schema by itself, so the repository includes tests and a command-line validator.
- Human review remains necessary for semantic and stylistic quality.

## Approval

`[H]` Only Aitor may change this ADR from `Proposed` to `Accepted`.
