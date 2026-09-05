# Independent Auditor Evaluation

## Scope

Measure the unchanged local document auditors against externally labelled Spanish
paraphrase pairs. This is an auditor baseline, not evidence that rewriting quality
has improved, an editorial approval, or a best-model ranking.

## Requirements

- REQ-105: When an external corpus is imported, the evaluation tools shall retain
  its publisher, source URL, licence URL, snapshot hashes, original IDs,
  label provenance and known language/domain limitations.
- REQ-106: When selecting an evaluation sample, the importer shall use a fixed
  deterministic rule, balance both semantic classes, exclude invalid/placeholder
  records, and reserve a disjoint sample without inspecting model outcomes.
- REQ-107: When auditing imported cases, the experiment shall withhold corpus
  labels and provenance from both models and preserve the existing prompt,
  sampling, model identity and immutable-resume checks.
- REQ-108: When comparing auditors, the report shall separately count false
  equivalence, false drift, abstentions, invalid contracts, pairwise disagreement
  and strict acceptance, without treating a style finding as semantic detection.
- REQ-109: When the source provides no regional or corporate-style annotation,
  the report shall not claim es-ES editorial gold or human approval; it shall
  retain an explicit independent human-review gate.

## External requirements

- [A] Public PAWS-X download and its permissive publisher licence; no account.
- [A] Existing local Qwen/Gemma and LanguageTool services; no inference installation.
- [M] An independent professional reader is needed to close corporate es-ES
  naturalness validation. Public paraphrase labels do not close this gate.
- [H] Any paid reviewer/service requires separate owner authorisation.

The original Google Storage archive returned HTTP 403 on 2026-09-05. Use the
Google Research Datasets Hugging Face Parquet mirror, revision
`4cd8187c404bda33cb1f62b49b001115862acf37`, Spanish test file SHA-256
`5ba872e113a79c783616e59d3d28ec0e922b6db745d797e5eb95010a32928bee`.
No available runtime includes a Parquet decoder. Install only the official binary
PyArrow 25.0.1 package under ignored `.tools/benchmark-deps`, with no dependencies
or global changes. It decodes the pinned file offline; the rewriting runtime
acquires no new dependency. Do not execute dataset loading scripts or remote code.

## Frozen protocol

Use 40 PAWS-X Spanish test pairs, 20 per class, plus 40 untouched reserve pairs.
Use seed `nainwrite-independent-v1`, SHA-256 ordering, and disjoint normalized
sentences as well as pair IDs. Exclude empty/NS placeholders and texts above the
existing 1,800-byte per-text bound. Do not hand-pick easy examples or relabel
disagreements. PAWS-X is old/public: pretraining contamination cannot be ruled out.

Run the existing v10 Qwen/Gemma review-only path. Compare each model's raw semantic
decision and their conservative combination. Retain full-pipeline acceptance only
as a secondary diagnostic because no corporate-style labels exist. No prompt,
model, threshold, runtime or Ollama changes are part of this task.

Report error counts and Wilson 95% intervals with denominators. The interval is a
finite-sample diagnostic under sampling assumptions, not a deployment guarantee.
Do not claim improvement without paired before/after results on a locked sample.
