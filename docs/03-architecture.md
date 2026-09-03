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

The measured configuration rejects prompts above 12000 UTF-8 bytes and requests at most 2048 output tokens within a 16384-token context. The prompt budget includes instructions, constraints and candidate text, so the source-text allowance is smaller and varies by stage. Length-limited responses are rejected. Whole-document segmentation and long-context acceptance remain unimplemented.
