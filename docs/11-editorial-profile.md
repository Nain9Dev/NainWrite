# Corporate Editorial Profile

## Approved profile

Aitor approved this profile and the three-language design on 2026-09-04. Intended readers are clients, decision-makers and proposal evaluators, with sufficient precision for technical specialists. The goal is professional, natural, sober and clear prose, not a particular author's imitation, detector evasion or unsupported authorship claims.

1. Preserve meaning, structure, uncertainty, timing, conditions, negation, quantities and disclosures.
2. Leave already suitable wording unchanged. Prefer a precise familiar expression over inflated wording when meaning is identical.
3. Translate technical terms only when the contextual equivalent is reliable. Keep proper names, identifiers and necessary original terms. Flag uncertainty separately rather than inventing a definition.
4. Use es-ES first. Aitor can edit the Spanish and approve an exact reviewed revision for translation.
5. Translate approved Spanish independently into formal natural en-GB and en-US. Also audit each English candidate against the retained original.
6. Keep editorial approval, automatic quality and generation completion separate. Preserve previous revisions and the original.

## Reference basis

Primary pages rechecked on 2026-09-04. These are editorial references, not a downloaded training corpus or a ranking of the best writers.

| Reference | Application | Boundary |
|---|---|---|
| [Montolío and Forment, Cervantes Yearbook 2025](https://cvc.cervantes.es/lengua/anuario/anuario_25/montolio-forment/p02.htm) | Context for Spanish clear institutional communication and established Spanish guides, including Madrid's 2017 guide | Institutional clarity does not authorise simplifying away technical conditions |
| [GOV.UK clear-language guidance](https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/clear-language/) | Precise accessible wording, including for specialists; necessary specialist language is legitimate | Do not mechanically import structure, contraction or modality recommendations that alter the source |
| [Digital.gov plain-language principles](https://digital.gov/guides/plain-language/principles) | Audience-appropriate American English; clarity is not reducing every document to a school reading level | Layout changes and summaries are outside this wording-only workflow |

The profile applies selected principles. No claim is made that these sources approve the software, its outputs, or the local models. No source passages are copied into the test bank.

## Human review sheet

For each section, compare the candidate with the retained original, not only with the intermediate Spanish:

- Meaning: same actor, action, tense/state, certainty, condition, exception, scope and quantities?
- Technical accuracy: same concept; no ungrounded expansion, narrowing or translated proper name?
- Naturalness: would a professional reader in the target locale find the wording ordinary and precise?
- Economy: no empty introduction, needless repetition or literal calque; no removal of meaningful qualifications?
- Continuity: headings, glossary and references consistent across sections?
- Structure: original order, lists, tables, code, links and blank fields retained?

Record pass, correction or uncertainty separately for each dimension. Any substantive uncertainty prevents final editorial approval. A 5/5 model score cannot resolve it by itself.

## Preliminary evaluation

`benchmark/corporate_review_controls.json` contains six deliberately invalid and six valid semantic pairs, all draft labels. Four development examples address previously observed failure classes; eight additional cases were kept out of this iteration's prompt implementation instructions. They are a small development evaluation, not an independently curated benchmark. After being inspected they are no longer unseen for future tuning.

`tests/fixtures/corporate-review-smoke.md` is synthetic and contains no customer text. It tests a previously good sentence, status versus validation, technical scope, conditional timing and a protected product name. Structural/approval tests use synthetic approval events; actual local-model output must still be displayed to Aitor before the workflow continues to English.


## Contextual review follow-up

The owner confirmed that ambiguous terminology must be interpreted from context,
not a universal domain assumption. Specification 013 adds a narrow source-grounded
question for unqualified Spanish lodging terminology. Explicit web/hotel/person
qualification supports matching translations; unrelated keywords and candidate-added
qualifiers do not establish meaning. Reports retain the technical finding and a
plain Spanish question. This is not general word-sense disambiguation; indirect
context and other ambiguous terms still need human review. A changed prompt or
contextual-rule identity requires a new job rather than editing old checkpoints.
