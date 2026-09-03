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
    G -->|No drift| J[Semantic and style audit]
    J -->|Gate failure| I
    J -->|Gate pass| K[accepted candidate]
    K --> L[Human benchmark review]
    L --> M[Model acceptance report]
```

## Layer boundaries

- The benchmark stores inputs, constraints and review state.
- The validator reads the benchmark and reports structural errors.
- The model runner generates candidates but never modifies benchmark inputs or references.
- The rewrite service owns orchestration and status decisions.
- The invariant validator is deterministic and independent of model judgement.
- The loopback-only Ollama client owns local model I/O and JSON decoding.
- Human review owns naturalness and final semantic approval.
