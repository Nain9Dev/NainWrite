# NainWrite ES

NainWrite ES is a local, fail-closed rewriting agent for natural, clear and professional Spanish from Spain (`es-ES`). It rewrites drafts produced by people or language models while preserving meaning, uncertainty, conditions, negations, attribution and protected literals.

## Current pipeline

1. Qwen3.8-27B produces a structured rewrite through local Ollama.
2. A deterministic validator compares protected and automatically detected invariants.
3. One constrained repair is allowed after deterministic drift.
4. A semantic and stylistic audit classifies the result as `accepted` or `review_required`.

Automated acceptance is not proof of perfect equivalence. Legal, contractual, financial and other high-impact text requires human approval.

## Requirements

- Windows or another platform with Python 3.12 or later.
- A loopback Ollama service.
- Installed model `qwen3.8-local-fast2:latest` or an explicitly selected compatible model.

The Python core uses only the standard library.

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
python tools/run_rewrite_benchmark.py --runs 2
```

Benchmark reports are written under `artifacts/` and intentionally excluded from Git because they are generated and may contain supplied text.

## Documentation

- [Charter](docs/00-charter.md)
- [Requirements](docs/01-requirements.md)
- [Architecture](docs/03-architecture.md)
- [Traceability](docs/07-traceability.md)
- [Runbook](docs/08-runbook.md)
- [Active specifications](specs/)
