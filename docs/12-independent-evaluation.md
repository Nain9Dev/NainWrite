# Independent Evaluation

Research checked on 2026-09-05. The decision is to measure external semantic
agreement now and obtain a separate blind human assessment of corporate es-ES.
No reviewed source establishes a single best local model for this product.

## Primary references and applicability

| Resource | Evidence and intended use | Boundary |
| --- | --- | --- |
| [PAWS-X, Yang et al., EMNLP 2019](https://aclanthology.org/D19-1382/) and [publisher dataset](https://github.com/google-research-datasets/paws/tree/master/pawsx) | Adversarial paraphrase pairs translated by native professional translators; a subset received second-worker validation. Semantic labels are inherited from human-labelled English PAWS pairs. Selected for an externally labelled semantic baseline. | Wikipedia-derived, not corporate prose; regional Spanish unspecified. Translation artefacts and inherited-label errors are possible. It is public and old, so model-training contamination cannot be excluded. |
| [Google WMT MQM human evaluation](https://github.com/google/wmt-mqm-human-evaluation) | Useful error taxonomy: accuracy, fluency, terminology, style and locale, with severity and document context. The project separately records errors rather than relying on one overall score. | Released pairs there are principally English-German and Chinese-English, not an es-ES editorial gold set. Our simplified review sheet is not a certified/full MQM implementation. |
| [Contrastive ESA, July 2026](https://arxiv.org/abs/2607.26640) | Current research compares multiple translations of the same source with error-span annotations. Useful design reference for a future blind A/B corporate revision comparison. | Its reported experiment is English-Japanese. It does not validate es-ES or this agent. Do not copy its reported improvement rates into this project's results. |
| [Pearmut](https://github.com/zouharvi/pearmut) and [WMT26 campaign](https://github.com/wmt-conference/wmt26-general-mt) | MIT-licensed human evaluation platform with several protocols; WMT26 documents its use. Consider only if multiple reviewers or larger campaigns justify a server. | Not installed. WMT26 instructions still contain incomplete annotation links; Spanish coverage and redistribution terms were not established for a direct corpus import. A local Markdown sheet is sufficient for the present reader. |
| [CLARA-MeD](https://huggingface.co/datasets/CLARA-MeD/claramed5000), [UNED project](https://clara-nlp.uned.es/open-results/) and [CSIC catalogue](https://datos.gob.es/es/catalogo/ea0041268-clara-med-corpus) | Spanish medical simplification with linguist-revised and manually simplified material. Relevant to understanding terminology/readability evaluation. | Medical/patient register is not corporate wording-only rewriting. The catalogue lists non-commercial share-alike terms; no corpus was imported or embedded into the product. |
| [FEINA, 2023](https://arxiv.org/html/2312.09897v1) and [iDEM corpus, 2026](https://arxiv.org/html/2603.05345v1) | Human simplification resources for financial education and democratic participation respectively. | Simplification can deliberately remove information, explain concepts or change structure. Their targets cannot be treated automatically as our strict-preservation gold; not imported. |
| [COMET](https://github.com/Unbabel/COMET) and [XCOMET-XL](https://huggingface.co/Unbabel/XCOMET-XL) | Translation-quality metrics; XCOMET reports error spans/severity. Candidate method for the later English translation stage. | XCOMET-XL's model card specifies CC-BY-NC-SA, access conditions and separate commercial permission. Not installed, no account agreement, no commercial-use clearance, and no measured local result. Translation quality is not proof of monolingual equivalence. |
| [GEMBA-MQM](https://github.com/MicrosoftTranslator/GEMBA) | Useful reference for structured LLM translation error assessment. | The documented setup requires OpenAI/Azure credentials and uses GPT-4. Not used for inference; no text sent to these services. Reimplementing the idea locally does not reproduce its research scores. |
| [Multilingual NLI model card](https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-mnli-xnli) | A different potential auditor architecture: test whether each sentence entails the other instead of relying only on generative judgements. | Future experiment only. One-way entailment is not equivalence; thresholds and local compatibility require measurement. Its historical ranking is not a current best-model claim. |

Searches stopped after establishing a downloadable externally labelled Spanish
source, primary evaluation methods, and the relevant domain/licensing gaps. More
repository stars or unrelated model rankings would not close those gaps.

## Corpus provenance and frozen selection

The original publisher's Google Storage download returned access denied. The
[Google Research Datasets Hugging Face mirror](https://huggingface.co/datasets/google-research-datasets/paws-x)
was downloaded at revision `4cd8187c404bda33cb1f62b49b001115862acf37`.
The publisher [licence](https://github.com/google-research-datasets/paws/blob/master/LICENSE)
permits use for any purpose and disclaims warranties. Google Research is credited
as the source; no assertion of endorsement is made.

- Snapshot: Spanish test Parquet, 345,485 bytes, SHA-256
  `5ba872e113a79c783616e59d3d28ec0e922b6db745d797e5eb95010a32928bee`.
- The mirror contains 2,000 rows. The importer excludes one placeholder row,
  leaving 1,999 eligible rows, consistent with the paper's usable Spanish count.
- Fixed seed `nainwrite-independent-v1`, SHA-256 ordering by external ID; select
  20 equivalent and 20 non-equivalent pairs without inspecting model outcomes.
- Reserve another balanced 40 pairs. No normalized sentence is shared within or
  between the selected partitions. Reserve contents are not presented to the
  models or manually inspected in this iteration.
- Evaluation hash: `8c3ff545d250a70f6cef1304c4356fed9a687938c76970887e71da7369e2c923`.
- Reserve hash: `b7f2528d8f0d1a6a9324fae145f79df293b126bd8cc9e8e95305cf5345d69239`.

The existing evaluator's `review_status=draft` remains local editorial status.
It does not erase external provenance or claim that these labels were invented
here. Conversely, external labels do not imply locally approved references.
`locale=es-ES` selects the existing production review policy; the corpus itself
is only labelled `es`. Regional/style scores are not validated by this experiment.

## Comparison and interpretation

Freeze the existing document prompt v10, editorial v3 and installed model digests.
Each exact external candidate receives the same review-only prompt from Qwen and
Gemma. Neither model receives corpus name, label, original ID, annotation rationale
or the other auditor's response. No candidate is generated or repaired here.

Compare separately:

1. Raw semantic decisions: false equivalence on non-equivalent pairs; false drift
   on equivalent pairs; missing decisions remain abstentions.
2. Conservative semantic pair: any explicit drift decision means drift; two true
   decisions mean equivalent; otherwise abstain. This is a diagnostic combination,
   not a new production acceptance policy.
3. Strict individual auditor acceptance: existing confidence/style/critical-change
   rules also apply. A style objection alone is never counted as semantic success.
4. Full pipeline acceptance including literal, editorial and proofreading checks.
   This is secondary and is not accuracy against absent corporate-style labels.
5. Pairwise disagreements, invalid contracts, execution errors and measured model
   generation duration. Durations include loading and are not deployment SLAs.

Report Wilson 95% intervals against each class denominator and show abstentions
alongside them. The sample is small, balanced and sentence-disjoint, not a random
sample of customer traffic. These intervals are descriptive, not guaranteed error
bounds. Errors with disputed external labels stay in the primary result; append
separate human adjudication instead of relabelling the benchmark to improve scores.

This baseline cannot establish improvement: no previous agent version has been
measured on this same locked sample. Once inspected, these cases become known
development evidence. Do not repeatedly tune against the reserve.

## Human review: available, not yet completed

Aitor confirmed on 2026-09-05 that another person can review the sample. Export
`independent-review.md` for that person; do not supply the bank JSON or model report
before they record their own judgement. The sheet omits dataset labels, model
identities, confidence and model comments. It contains external sentence pairs,
not newly generated corporate revisions.

For the subsequent corporate pilot, use 20 previously unseen, owner-authorised
excerpts covering reports, client communication, proposals, technical documentation
and delivery conditions. Include good prose that should remain unchanged. Select
and lock whole-document groups before generation; do not split the same document
between tuning and final evaluation. Preserve originals and do not publish them.

Have Aitor and the independent reader judge separately before discussing answers:

- Meaning: same facts, actor, time, certainty, obligations, conditions and scope;
  label equivalent/different/uncertain and cite exact offending words.
- Naturalness, clarity and professional tone: rate each separately, with a reason
  for required changes; do not reward needless rewriting of good prose.
- Spain-specific usage and technical terminology: record actual examples, not
  assumptions based on a generic Spanish language tag.
- Structure/literals: unchanged order, headings, lists, links, identifiers and
  numbers; wording preferences do not authorise semantic deletion.

For a before/after comparison, anonymise candidate identities and counterbalance
their positions. Report paired outcomes, ties, reviewer disagreement and unresolved
meaning changes. This campaign is still pending; the external semantic worksheet
does not certify corporate naturalness. Actual Spanish revision approval remains
required before en-GB and en-US, which need separate locale-competent review.
