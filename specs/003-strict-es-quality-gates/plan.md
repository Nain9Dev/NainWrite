# Strict es-ES Quality Gates Plan

## External prerequisites

- `[A]` Existing loopback Ollama and installed Qwen3.8 writer.
- `[A]` Existing installed `gemma4:latest` candidate for independent audit; it must be benchmarked before adoption.
- `[A]` Side-by-side Java 17 runtime and an official local LanguageTool distribution.
- `[H]` No new account, credential, payment or cloud service is required.

## Tasks

1. Add failing unit tests for a loopback-only LanguageTool client and dual-audit fail-closed behavior.
2. Implement the LanguageTool contracts and client without third-party Python dependencies.
3. Install Java 17 and LanguageTool locally on port `8082`; verify process path, bind address, version and sample findings.
4. Integrate proofreading and dual audit behind explicit service configuration.
5. Raise strict automatic style thresholds to `5/5` and correct the human-review labels.
6. Create and validate an adversarial semantic-mutation bank and runner.
7. Execute unit, structural, real rewrite and mutation benchmarks; compare quality and timing with baseline.
8. Update architecture, runbook, traceability and task handoff.
9. Commit and push the verified branch without generated artifacts or local runtimes.

## Evidence-driven refinements

- Correct draft controls that changed temporal anchoring or invented an explanation, retain their old candidates as invalid regression cases, and evaluate without authored hints by default.
- Save completed cases atomically, reject empty banks/candidates and malformed audits, and require every rewrite result to pass the strict benchmark.
- Add one bounded linguistic repair after observed LanguageTool findings. Preserve initial evidence and repeat every gate; do not apply replacements directly.
- Reject oversized prompts and length-limited generation. Document that unbounded documents are not supported.
- External prerequisites remain unchanged: no new dependency, account, credential, payment or service is needed for these refinements.

## Verification commands

```powershell
python -m unittest discover -s tests -v
python tools/validate_bank.py
python tools/validate_semantic_mutations.py
python tools/rewrite_text.py --text "..."
python tools/run_rewrite_benchmark.py --runs 2
python tools/run_semantic_audit_benchmark.py
git diff --check
```

## Stop conditions

- LanguageTool requires a cloud endpoint or binds outside loopback.
- Java installation changes or removes the existing Java 8 runtime instead of installing side by side.
- The independent auditor rejects valid controls without a defensible reason.
- A quality change improves the benchmark only by weakening a semantic or deterministic gate.
- Existing Docker containers or ports would need modification.
