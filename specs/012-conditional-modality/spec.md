# Conditional Modality Regression

The real workbench smoke on 2026-09-09 translated Spanish `Podríamos entregar`
as US English `We can deliver`. Both semantic auditors accepted that candidate.
This is a known missed distinction, not evidence of general equivalence.

- **MOD-001:** When source prose contains conditional ability (`podría` and its
  inflections, or `could`) and candidate prose substitutes unqualified ability
  (`can` or Spanish present-tense `poder`), deterministic checks shall retain a
  conditional-modality finding even when both model auditors accept the text.
- **MOD-002:** When a candidate retains a conditional or possibility expression,
  this narrow rule shall not assert drift. Code, URLs and quoted literals shall
  not trigger prose checks. The rule shall never claim complete semantic coverage.
- **MOD-003:** When deterministic fidelity rules change, configuration identity
  shall change so earlier checkpoints cannot silently inherit the new checks.

No new model, cloud request, dependency or paid service is required. Existing
bounded repairs may use the finding. Broader tense, scope and modal equivalence
remain a human review responsibility. Historical generated files stay retained.
