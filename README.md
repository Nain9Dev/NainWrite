# NainWrite ES

NainWrite ES is a local, fail-closed rewriting agent for natural, clear and professional Spanish from Spain (`es-ES`). It rewrites drafts produced by people or language models while preserving meaning, uncertainty, conditions, negations, attribution and protected literals.

## Current pipeline

1. Qwen3.8-27B produces a structured rewrite through local Ollama.
2. A deterministic validator compares protected and automatically detected invariants.
3. One constrained repair is allowed after deterministic drift.
4. Local LanguageTool checks spelling, grammar and typography. One constrained linguistic repair is allowed; it repeats the invariant and language checks.
5. Qwen and a separately configured Gemma auditor assess meaning and style. Both must pass before the result is `accepted`; otherwise it is `review_required`.

Automated acceptance is not proof of perfect equivalence. Legal, contractual, financial and other high-impact text requires human approval.

Current validation is preliminary: the corrected unassisted semantic bank exposes one false acceptance (`SEMA-022`), and some valid rewrites still trigger proofreading review. The strict acceptance gate has not passed. See [measured validation results](docs/10-validation.md) before using the agent.

Before supplying private text, verify both service listeners are loopback-only. The latest desktop-managed Ollama instance did not meet this check; the client using `127.0.0.1` does not by itself restrict the server's other interfaces.

This version is intended for bounded text passages. It rejects prompts above 12000 UTF-8 bytes and incomplete length-limited responses. Long documents and automatic translation are not yet validated.

## Requirements

- Windows or another platform with Python 3.12 or later.
- A loopback Ollama service.
- Installed model `qwen3.8-local-fast2:latest` or an explicitly selected compatible model.
- Installed independent auditor `gemma4:latest` or an explicitly selected different model.
- Java 17 and a local LanguageTool server on `127.0.0.1:8082`.

The Python core uses only the standard library.

These are the measured workstation model aliases, not public download names. A new installation must resolve the original model package and verify its digest; do not assume that `ollama pull` can retrieve these custom aliases.

## Rewrite one text

```powershell
python tools/rewrite_text.py --text "El texto original necesita una redacción más clara." --plain
```

Protect exact literals by repeating `--protected`:

```powershell
python tools/rewrite_text.py `
  --text "La entrega podría realizarse si Aitor aprueba ADR-007." `
  --protected "Aitor" `
  --protected "ADR-007"
```

Exit code `0` means every configured automated gate passed. Exit code `2` means human review is required. See [the runbook](docs/08-runbook.md) for full operation and failure handling.

## Verification

```powershell
python -m unittest discover -s tests -v
python tools/validate_bank.py
python tools/validate_semantic_mutations.py
python tools/run_semantic_audit_benchmark.py
python tools/run_rewrite_benchmark.py --runs 2
```

Benchmark reports are written under `artifacts/` and intentionally excluded from Git because they are generated and may contain supplied text.

## Documentation

- [Charter](docs/00-charter.md)
- [Requirements](docs/01-requirements.md)
- [Architecture](docs/03-architecture.md)
- [Traceability](docs/07-traceability.md)
- [Runbook](docs/08-runbook.md)
- [Primary-source research](docs/09-research.md)
- [Measured validation results](docs/10-validation.md)
- [Active specifications](specs/)
