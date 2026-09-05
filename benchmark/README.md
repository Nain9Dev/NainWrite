# Spanish Rewrite Benchmark

This directory contains the first draft benchmark for professional Spanish rewriting.

## Contents

- `spanish_rewrite_cases.jsonl`: 30 independent cases.
- `review_rubric.md`: human evaluation instructions and acceptance rules.
- `corporate_review_controls.json`: twelve fixed document-audit regressions from specification 005.
- `corporate_calibration_controls.json`: twelve new paired semantic/style controls for specification 006. The semantic examples were frozen before live evaluation; style examples deliberately test the implemented wording rules. Neither bank is approved gold.

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

## Semantic mutation bank

`semantic_mutations.jsonl` contains intentionally invalid candidates and valid controls. It verifies that semantic gates can reject changed meaning without becoming an always-rejecting classifier.

The current draft has 22 pairs: 17 invalid candidates and 5 valid controls. Two initial controls were corrected after review identified a changed temporal anchor and an unsupported explanation of uncertainty. Their original candidates remain as invalid regression cases `SEMA-021` and `SEMA-022`; earlier 20-case passes must not be presented as passes on the corrected bank.

The semantic runner omits authored semantic hints by default. Use `--with-hints` only for a separately labelled assisted measurement. A style or spelling rejection alone does not count as detecting a semantic mutation.

Validate it with:

```powershell
python tools/validate_semantic_mutations.py
```
