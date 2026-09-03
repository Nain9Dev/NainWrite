# Local Spanish Rewriter Specification

Status: Draft
Target locale: `es-ES` confirmed by Aitor on 2026-09-03
Target voice: clear, direct, professional and natural

## Purpose

Implement a local Spanish rewriting agent that improves fluency without changing meaning. The agent shall use the strongest currently feasible Chinese open model already installed on the target workstation: Qwen3.8-27B IQ4_XS through Ollama.

The product term is *rewriting*, not transcription: wording and syntax may change, while facts, logical scope and certainty must remain stable.

## Scope

### In scope

- Local Spanish-to-Spanish rewriting.
- Qwen3.8 generation through the loopback Ollama API.
- Structured model responses.
- Automatic extraction and comparison of high-risk literals.
- A second semantic-audit pass.
- Fail-closed classification as `accepted` or `review_required`.
- Execution against the 30-case draft benchmark.
- Reproducible reports containing configuration, outputs, checks and timings.

### Out of scope

- Spanish-to-English translation.
- Training or fine-tuning.
- Automatic publication or replacement of source documents.
- A mathematical guarantee of semantic equivalence.
- Remote Ollama endpoints.
- Commit, push or deployment.

## Requirements

### Model and privacy

- `REQ-016`: The agent shall use `qwen3.8-local-fast2:latest` by default.
- `REQ-017`: The agent shall call only an Ollama endpoint on the local loopback interface.
- `REQ-018`: The agent shall use structured JSON output, deterministic sampling settings and disabled thinking output.
- `REQ-019`: Source text shall be treated as untrusted data and shall not be allowed to override the editing contract.

### Rewrite contract

- `REQ-020`: The agent shall target professional Spanish from Spain (`es-ES`).
- `REQ-021`: The rewrite shall not add, remove or change facts, recommendations, conditions, exceptions, actors, attribution, certainty or ambiguity.
- `REQ-022`: The rewrite shall preserve every caller-provided protected literal exactly.
- `REQ-023`: The rewrite shall preserve automatically detected URLs, email addresses, paths, routes, quotations, dates, times, percentages, currencies, versions, identifiers and numerical values.

### Verification

- `REQ-024`: A deterministic validator shall compare protected and automatically extracted invariants.
- `REQ-024A`: When the initial candidate fails deterministic validation, the service shall permit one constrained repair attempt that receives the exact validation issues. If the repaired candidate still fails, the result shall be `review_required` without semantic audit.
- `REQ-025`: A second model call shall assess semantic equivalence, naturalness and professional tone.
- `REQ-026`: The result shall be `review_required` if any deterministic check fails, the auditor reports a critical change, semantic confidence is below `0.95`, or either style score is below `4`.
- `REQ-027`: The agent shall expose every rejection reason in machine-readable form.
- `REQ-028`: An accepted plain-text output shall contain only the rewritten text.

### Benchmark

- `REQ-029`: The benchmark runner shall process every case independently and continue after a rejected case.
- `REQ-030`: The report shall record the model, prompt version, configuration, status, issues, output and timing for every case.
- `REQ-031`: A model configuration shall pass the automated gate only if every P0 case is accepted and no case has deterministic invariant drift.
- `REQ-032`: Benchmark results against draft references shall be labelled preliminary until human review approves the references.

## Exit criteria

- Unit tests for invariant extraction, fail-closed behavior, prompt isolation and service orchestration pass.
- The existing 30-case structural suite remains green.
- A real Ollama smoke test returns valid structured output.
- The complete 30-case benchmark finishes and produces a readable report.
- Repeated deterministic runs are compared and any output drift is disclosed.
- No result is described as perfect or production-safe without human reference approval.

## Safety boundary

The agent assists professional editing but does not replace human approval for legal, contractual, financial or other high-impact text. `accepted` means that the configured automated gates passed; it does not prove absolute equivalence.
