# Corporate calibration and repository delivery

## Scope and authorization

Aitor requested correction, repeated evaluation and repository publication on 2026-09-05. This authorizes committing and pushing reviewed source, synthetic tests and documentation to the existing private repository. It does not approve any Spanish document revision or change the instruction to leave Ollama and original documents unchanged.

## External dependencies

- `[A]` Existing Python, local Qwen/Gemma, Java/LanguageTool, Git and authenticated GitHub CLI. Restart only the existing corrector if stopped. No installation, paid service or cloud inference is needed.
- `[M]` Exact Spanish revision approval precedes translation of user documents. Synthetic end-to-end verification can exercise approval explicitly as test data.
- `[H]` No new account, credential or payment is needed.

## Requirements

- **REQ-100:** When document prose is written or audited, the versioned instructions shall distinguish data state, scope and unsupported interpretation, request direct corporate prose and preserve good wording, meaning and structure.
- **REQ-101:** When es-ES prose contains a documented populated-data calque, unnecessary emphasis formula or the observed redundant conformance-test definition, deterministic editorial checks shall retain an explicit review finding and bounded repair feedback even if both model style scores pass; protected code, links, quoted expressions and geographic population uses shall not trigger these checks.
- **REQ-102:** When saved generated or review-only evidence resumes, editorial findings shall be recomputed under the saved-compatible configuration; changing editorial rules or prompts shall change configuration identity and reject incompatible jobs.
- **REQ-103:** When a finite calibration experiment runs, it shall withhold authored labels from models, persist per-case evidence, distinguish semantic/style/operational outcomes, and resume only validated results for unchanged bank and configuration.
- **REQ-104:** When preparing repository publication, the delivery shall exclude private documents, generated reports, credentials, model weights and installed tools, include reproducible verification and operating instructions, and verify the published commit identity.

## Evaluation boundary

The original twelve controls remain unchanged as regressions, not new held-out evidence. Add fresh paired semantic and editorial controls before running the updated prompt. Record results including failures; do not promote a general accuracy claim from a small draft bank. Compare the unchanged synthetic Spanish fixture, then run a synthetic three-locale route with explicitly labelled test approval if its Spanish is suitable. The private long draft waits until this calibration is assessed. Software stability, linguistic quality and human approval remain separate.
