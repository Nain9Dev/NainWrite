# Spanish Rewrite Benchmark Specification

Status: Draft
Locale assumption: `es-ES`

## Purpose

Define a reproducible benchmark for evaluating local models that rewrite Spanish text so it sounds natural and professional without changing its meaning.

The benchmark evaluates semantic preservation and editorial quality separately. It does not attempt to prove that a text was written by a human or to evade AI detectors.

## Scope

### In scope

- Spanish-to-Spanish rewriting.
- Short professional texts.
- Exact preservation of protected literals.
- Preservation of assertions, negations, modality, conditions, attribution, quantities and uncertainty.
- Draft reference rewrites for human review.
- Machine-verifiable dataset integrity and coverage.

### Out of scope

- Spanish-to-English translation.
- Model installation or fine-tuning.
- Automatic publication of generated text.
- Claims of perfect semantic equivalence.
- AI-detector scoring.

## Requirements

### Dataset

- `REQ-001`: The benchmark shall contain exactly 30 cases in its first version.
- `REQ-002`: Each case shall have a unique sequential identifier from `ESRW-001` through `ESRW-030`.
- `REQ-003`: Each case shall declare its category, priority, locale, source text, draft reference, protected literals, required meaning, forbidden changes, phenomena and review status.
- `REQ-004`: Each source and draft reference shall be non-empty and different.
- `REQ-005`: Each protected literal shall appear unchanged in both the source and the draft reference.
- `REQ-006`: Every draft reference shall remain marked `draft` until Aitor approves it.
- `REQ-007`: The bank shall include general, technical, business, legal/administrative, style and ambiguity cases.

### Semantic safety

- `REQ-008`: When a case contains a number, date, percentage, currency, version, path, URL, identifier or quotation marked as protected, the rewrite shall preserve it exactly.
- `REQ-009`: When a case contains negation or uncertainty, the rewrite shall preserve its scope and strength.
- `REQ-010`: When a case contains a condition, exception, authorization boundary or causal limitation, the rewrite shall preserve it.
- `REQ-011`: If a rewrite cannot preserve all protected constraints, a future runner shall classify it as `review_required`; it shall not silently pass.

### Evaluation

- `REQ-012`: The structural validator shall run without third-party Python dependencies.
- `REQ-013`: The validator shall fail on malformed JSON, missing fields, duplicate identifiers, invalid coverage or missing protected literals.
- `REQ-014`: Naturalness shall be evaluated separately by a human reviewer on a five-point scale.
- `REQ-015`: A model shall not be accepted unless it produces zero critical semantic changes in the approved evaluation set.

## Acceptance criteria

- The structural test suite passes.
- The command-line validator reports 30 valid cases.
- Every requirement is mapped to evidence in the traceability document.
- The test bank remains a draft until the locale, tone and reference rewrites receive human approval.

## Open decision

`[M]` Aitor must confirm that professional Spanish from Spain (`es-ES`) is the target locale and approve or revise the draft references.
