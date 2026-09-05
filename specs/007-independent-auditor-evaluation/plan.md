# Plan

1. Verify primary corpus, human-evaluation and auditor-method sources; document
   applicability, licensing and exclusions.
2. Add failing tests, then a bounded offline PAWS-X importer and audit comparison
   tool reusing the existing validated review-only experiment.
3. Freeze and hash the sample/reserve before inference. Execute the 40-case local
   baseline once without tuning. Keep external text and generated reports ignored.
4. Verify metrics, tests, privacy boundaries and document measured limitations.
5. Preserve the human editorial-review gate and publish only source, tests and
   technical documentation within the previously authorised repository scope.
