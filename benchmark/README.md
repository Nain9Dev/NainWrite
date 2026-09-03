# Spanish Rewrite Benchmark

This directory contains the first draft benchmark for professional Spanish rewriting.

## Contents

- `spanish_rewrite_cases.jsonl`: 30 independent cases.
- `review_rubric.md`: human evaluation instructions and acceptance rules.

## Important status boundary

Every `draft_reference` is a candidate written for review. It is not a gold reference and must not be used to train, rank or accept a model as if it had been approved by Aitor.

## Case contract

Each JSONL line contains:

- `id`: stable sequential identifier.
- `title`: concise English label.
- `category`: primary coverage category.
- `priority`: semantic risk priority.
- `locale`: intended Spanish locale.
- `source`: intentionally awkward Spanish input.
- `draft_reference`: candidate natural rewrite.
- `protected_literals`: exact strings that must remain unchanged.
- `required_meaning`: propositions that must survive rewriting.
- `forbidden_changes`: critical drift to reject.
- `phenomena`: semantic and editorial risks represented by the case.
- `review_status`: remains `draft` until human approval.

## Structural validation

From the repository root:

```powershell
python tools/validate_bank.py
python -m unittest discover -s tests -v
```

Structural validation does not assess naturalness or semantic equivalence. Those require the human review described in `review_rubric.md`.
