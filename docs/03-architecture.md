# Architecture

The benchmark is independent of the model runner. This prevents model-specific behavior from changing the evaluation contract. The runtime is a local fail-closed pipeline: no model result bypasses deterministic checks and semantic audit.

```mermaid
flowchart TD
    A[Draft benchmark cases] --> B[Structural validator]
    B -->|Invalid| C[Reject bank change]
    B -->|Valid| D[Human reference review]
    D -->|Corrections required| A
    D -->|Approved| E[Versioned gold benchmark]
    E --> F[Local Qwen rewrite]
    F --> G[Deterministic invariant checks]
    G -->|Drift| H[One constrained repair]
    H --> G
    G -->|Drift after repair| I[review_required]
    G -->|No drift| P[Local LanguageTool proofreading]
    P -->|Unavailable| I
    P -->|Blocking finding, first attempt| R[One constrained linguistic repair]
    R --> S2[Repeat invariants and proofreading]
    S2 -->|Any failure| I
    S2 -->|No failure| J
    P -->|No blocking finding| J[Qwen semantic and style audit]
    J --> N[Independent Gemma semantic and style audit]
    N -->|Either audit fails| I
    N -->|Both audits pass| K[accepted candidate]
    K --> L[Human benchmark review]
    L --> M[Model acceptance report]
    S[Draft semantic mutation candidates] --> T[Candidate evaluator]
    T --> U[Invariant checks, LanguageTool and both audits]
    U --> V[Compare actual and expected outcome]
```

## Layer boundaries

- The benchmark stores inputs, constraints and review state.
- The validator reads the benchmark and reports structural errors.
- The model runner generates candidates but never modifies benchmark inputs or references.
- The rewrite service owns orchestration and status decisions.
- The invariant validator is deterministic and independent of model judgement.
- The loopback-only Ollama client owns local model I/O and JSON decoding.
- The loopback-only LanguageTool client owns proofreading I/O and service-identity validation. Spanish checking uses LanguageTool's `es` rules; the model prompts and human rubric enforce the `es-ES` register.
- Explicit protected literals and automatically detected invariants can suppress overlapping spelling findings, not grammar findings. Callers must not protect ordinary misspellings merely to bypass proofreading.
- The candidate evaluator measures deliberately invalid and valid pairs. It does not generate a rewrite and records all configured audit evidence.
- Human review owns naturalness and final semantic approval.

## Operational boundary

Both services run on the workstation. Ollama uses port `11434`; LanguageTool uses port `8082`. The unrelated Docker service on `8081` is untouched. Neither service requires a cloud account. A different model family is an independent implementation, not proof of statistically independent errors.

The default automatic gate requires semantic confidence of at least `0.95` and both style scores at `5/5` from each auditor. These are uncalibrated model judgements, not probabilities or guarantees of correctness. Rejected candidates remain available for human diagnosis but must not be automatically published.

A linguistic repair never applies LanguageTool replacement suggestions directly. It asks the writer for one new candidate grounded in the original source and preserves the pre-repair evidence. A repaired candidate must pass the same gates; an unavailable proofreader never triggers a repair.

The measured configuration rejects prompts above 12000 UTF-8 bytes and requests at most 2048 output tokens within a 16384-token context. The prompt budget includes instructions, constraints and candidate text, so the source-text allowance is smaller and varies by stage. Length-limited responses are rejected. The document workflow divides content instead of increasing this context.

## Historical bilingual workflow

The following diagram describes specification 004 and its retained artifacts. New CLI jobs use the approval-aware workflow below; old checkpoints are not silently migrated.

```mermaid
flowchart TD
    CLI[File-path CLI] --> Job[Document orchestrator]
    Job --> Store[Local job store and process lock]
    Store --> Input[Read-only source and atomic checkpoint]
    Job --> Parser[Original spans and coherent note-cleaned text]
    Parser --> Batches[Bounded prose batches]
    Batches --> ES[Qwen Spanish generation]
    ES --> Checks[Literal checks and locale-specific LanguageTool]
    Checks --> Audits[Qwen and Gemma audits]
    Audits --> Repair[At most one grounded repair with repeated checks]
    Repair --> Spanish[Complete Spanish candidate]
    Spanish --> EN[English from Spanish with upstream review flags]
    EN --> ChecksEN[Same checks with en-GB proofreading]
    ChecksEN --> Assemble[Coverage, structure and repeated-heading checks]
    Assemble --> Output[Immutable candidate files and separate review]
    Input --> Resume[Validate hashes, configuration and saved evidence]
    Resume --> Job
```

`document.py` owns parsing and deterministic assembly. `document_prompts.py` owns versioned bilingual instructions. `document_transform.py` owns bounded generation/checks/repair; `document_evidence.py` independently revalidates saved evidence. `document_job.py` orchestrates phases and status. Only `document_store.py` reads source files or persists local artifacts. The CLI captures arguments and presents progress; it does not implement editorial rules.

Each batch contains at most 12 source spans and 1800 UTF-8 source bytes. Complete prompts are checked again, including context and candidate text. Whole neighbours up to 256 bytes are included; larger neighbours are explicitly outside context coverage. No text is silently truncated. Cross-section semantic equivalence is not exhaustively established by these bounded audits.

Generated review-required candidates are local review artifacts, not external publication. Source-specific preparation ranges and documents never belong in the repository.

Parser v2 removes approved editorial markers within each prose region before segmentation. Exact original text and cleaned model text have separate hashes. Only spacing directly affected by removal is normalized; protected code/links and existing line-ending suffixes remain intact. Identical original headings are compared across both completed languages; variants require review, not automatic replacement. A new parser/prompt/job version requires a new job instead of migrating prior model evidence.

## Approved trilingual workflow

```mermaid
flowchart TD
    Path[File-path CLI] --> Job[Revision-aware document service]
    Job --> Store[Atomic local store and process lock]
    Store --> Original[Unchanged original and configuration identity]
    Original --> ES[Bounded es-ES generation and checks]
    ES --> Baseline[Immutable generated Spanish baseline]
    Baseline --> Editable[Editable Spanish copy]
    Editable --> Map[Conservative wording-only span mapping]
    Map --> Review[Review exact revision against original]
    Review --> Snapshot[Immutable revision and separate findings]
    Snapshot --> Gate{Explicit approval of exact revision}
    Gate -->|Missing or stale| Wait[Await Spanish approval; no English generation]
    Gate -->|Approved| GB[en-GB from approved Spanish]
    Gate -->|Approved| US[en-US from same approved Spanish]
    GB --> GBCheck[British proofreading and Spanish-grounded audits]
    US --> USCheck[American proofreading and Spanish-grounded audits]
    GBCheck --> OriginalCheck[Separate original-grounded audits]
    USCheck --> OriginalCheck
    Original --> OriginalCheck
    OriginalCheck --> Output[Revision-specific outputs and independent quality status]
    Editable -->|Changed after approval| Invalidate[Invalidate authority; retain outdated outputs]
    Invalidate --> Map
```

Specification 005 adds `document_revision.py` for pure edit mapping, `document_review.py` for evidence-bearing checks without generation, and `editorial_job.py` for revision/approval orchestration. Store code owns filesystem access; the CLI only captures input and presents state. A review-required revision can be authorised for translation only with explicit acknowledgement; its automatic quality does not become accepted.

Edits are scoped to unambiguous retained prose spans. Structural or ambiguous cross-boundary changes fail closed and require smaller wording edits or a new source job. These bounds preserve evidence identity; they are not a claim to support arbitrary document editing. Both English branches consume an immutable Spanish snapshot and are separately compared against the original. Positive audits still do not establish exhaustive cross-section equivalence.

## External auditor baseline

```mermaid
flowchart LR
    Public[Hash-pinned public corpus] --> Import[Offline bounded selection]
    Import --> Sample[40 labelled evaluation pairs]
    Import --> Reserve[40 untouched reserve pairs]
    Sample --> Review[Unchanged review-only service; labels withheld]
    Review --> Store[Immutable per-case evidence]
    Store --> Compare[Offline validation and per-auditor metrics]
    Sample --> Blind[Unlabelled independent human-review sheet]
```

The optional Parquet decoder is isolated from the rewriting runtime. Corpus
selection and comparison live in `independent_evaluation.py`; public snapshot
decoding and CLI argument handling do not alter document-generation services.
The reserve has no inference route in this task. Human review and external
semantic agreement do not automatically approve a Spanish document revision.

## Reproducible editorial calibration

```mermaid
flowchart LR
    Candidate[Exact candidate prose] --> Editorial[Versioned deterministic editorial findings]
    Editorial --> Repair[Bounded generation repair]
    Editorial --> Review[Review-only findings]
    Editorial --> Revalidate[Saved-evidence reconstruction]
    Bank[Draft synthetic pairs] --> Evaluation[Finite local evaluator]
    Evaluation --> Review
    Evaluation --> Evidence[Immutable per-case artifacts and checkpoint]
    Evidence --> Summary[Separate semantic, style and execution outcomes]
```

`document_editorial.py` supplies narrow es-ES wording checks to generation, review and evidence validation. They signal review, never change text automatically or determine its authorship. Model instructions separately compare claims in both directions. `calibration.py` orchestrates bounded synthetic evaluation using the local transformer and atomic store; the CLI renders progress. Authored expectations are used only to score retained results, never included in model input. A changed prompt/editorial version requires a new job.
