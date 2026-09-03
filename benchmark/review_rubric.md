# Human Review Rubric

## Reviewer task

Read the source and draft reference without considering which model or person produced either text. Score the draft reference independently on the dimensions below.

## Critical semantic gate

Mark `critical_drift=true` if any of the following occurs:

- A protected literal is altered or removed.
- A number, date, unit, percentage, currency, version, path, URL, identifier or quotation changes.
- A negation, condition, exception, authorization boundary or sequence changes scope.
- Uncertainty becomes certainty, or certainty becomes uncertainty.
- Correlation becomes causation.
- An actor receives an action, decision or responsibility that belongs to someone else.
- Ambiguity is resolved without evidence.
- A new fact or recommendation is introduced.

Any critical drift rejects the candidate regardless of its other scores.

## Scores

### Meaning preservation

- `5`: All meaning is preserved without detectable drift.
- `4`: Meaning is preserved; only an immaterial nuance differs.
- `3`: The main point remains, but at least one secondary nuance changes.
- `2`: A material proposition changes or disappears.
- `1`: The rewrite substantially contradicts or replaces the source.

### Naturalness

- `5`: Fully natural professional Spanish from Spain.
- `4`: Natural overall, with one minor awkward expression.
- `3`: Understandable but noticeably mechanical or translated.
- `2`: Several unnatural constructions impede reading.
- `1`: Unusable or incoherent Spanish.

### Professional tone

- `5`: Clear, direct and appropriate for professional use.
- `4`: Appropriate with one minor tone issue.
- `3`: Acceptable but inconsistent, cold or unnecessarily ornate.
- `2`: Frequently inappropriate for the intended context.
- `1`: Unprofessional or misleading.

## Per-case review record

Record the following values for every case:

```text
case_id:
critical_drift: true | false
meaning_preservation: 1..5
naturalness: 1..5
professional_tone: 1..5
approved_reference: yes | no
corrected_reference:
reviewer_notes:
```

## Bank approval gate

The benchmark may be promoted from draft to approved only when:

- All 30 cases have been reviewed.
- Every approved reference has `critical_drift=false`.
- Every approved reference scores `5` for meaning preservation.
- Every approved reference scores at least `4` for naturalness and professional tone.
- Any corrected reference still preserves every protected literal.

## Future model acceptance gate

A model run passes only when:

- It introduces zero critical semantic changes.
- At least 95% of outputs score `4` or `5` for naturalness.
- At least 95% of outputs score `4` or `5` for professional tone.
- No P0 case fails.

This gate evaluates a specific model digest, prompt version, inference configuration and benchmark version. Results must not be generalized to a different configuration.
