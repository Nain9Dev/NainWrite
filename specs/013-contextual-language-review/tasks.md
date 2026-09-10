# Task Handoff

## Completed and verified

- `[A]` Added failing tests for unsupported hosting/accommodation choices, unchanged
  ambiguous Spanish, explicit qualified senses, wrong-sense translation, unrelated
  domain words, quoted/code mentions, coordinated senses and evidence suppression.
- `[A]` Added shared `document_ambiguity.py` findings to generation, review and saved
  evidence validation. Positive model audits cannot erase the deterministic question.
- `[A]` Added a separate plain-Spanish context-question section to editorial reports.
  The job still pauses before Spanish approval; no answer or approval is invented.
- `[A]` Versioned contextual rules (`contextual-fidelity-v1`) and prompts
  (`trilingual-editorial-v11`). The first longer prompt failed the existing bounded
  repair-budget regression; shortening the instruction restored the test without
  increasing the request budget or weakening existing literal/modality checks.
- `[A]` Final suite: 201 tests pass. The current retained synthetic es-ES, en-US and
  en-GB exports all produce `source_ambiguity:alojamiento` under the new rule.
  Their saved SHA-256 values were verified; historical files were not changed.

## Limits and pending evidence

- `[M]` The owner confirms meaning depends on context; the isolated synthetic
  example still has no confirmed lodging sense or final English approval.
- `[A]` This is a narrow direct-qualification rule for Spanish lodging terminology.
  Indirect/cross-section context, metaphor, other languages and other polysemous
  terms are not exhaustively classified. Conservative questions can require owner
  judgement even when a broader reader can infer the intended sense.
- `[A]` No new real-model run or live UI restart was performed. Local listeners
  were stopped at inspection. New jobs use the changed rules on the next launch;
  historical checkpoints cannot be resumed under changed configuration identities.
- `[A]` No dependencies, models, paid services or customer documents were added.
- `[A]` Changes are ready for source publication under the existing main authority;
  no existing document approval is extended by implementation or publication.
