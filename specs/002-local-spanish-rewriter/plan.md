# Local Spanish Rewriter Plan

## Tasks

1. Confirm the target locale and record the model decision.
2. Write failing unit tests for invariants, prompt isolation and fail-closed service behavior.
3. Implement the domain model, invariant validator, one bounded deterministic repair, Ollama client, prompts and rewrite service.
4. Add a command-line interface and benchmark runner.
5. Run unit tests and a one-case real smoke test.
6. Run the full 30-case benchmark with Qwen3.8.
7. Repeat the benchmark with the same deterministic configuration and compare outputs.
8. Update architecture, runbook, traceability and task handoff with observed evidence.

## Verification commands

```powershell
python -m unittest discover -s tests -v
python tools/validate_bank.py
python tools/rewrite_text.py --text "..."
python tools/run_rewrite_benchmark.py
git diff --check
```

## Stop conditions

- Ollama is unavailable or does not return the required JSON contract.
- The installed model digest changes during the run.
- The benchmark modifies source cases or draft references.
- A repeated infrastructure failure prevents completing the 30 cases.

## Constraints

- No model download is required because the selected Qwen3.8 quantization is already installed.
- No third-party Python dependency is required for the agent core.
- No commit, push, remote service or deployment.
