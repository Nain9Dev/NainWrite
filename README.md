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

The historical document baseline passed 165 software tests. Its known-control run detects all six deliberate meaning changes but requests review for one valid control because an auditor lists correct translations as critical changes. The Spanish smoke corrects the targeted calques and repetition; broader editorial acceptance remains open. The 40-case external semantic baseline exposes substantial disagreement with inherited corpus labels, including questionable translated positive pairs. It does not establish maximum quality or a better model. See [independent evaluation](docs/12-independent-evaluation.md) and its separate human-review gate.

## Local browser application

On the configured Windows workstation, double-click `Start-NainWrite.cmd`, or run:

```powershell
pwsh -NoProfile -File tools/open-workbench.ps1
```

Open **http://127.0.0.1:8765**. Submit PDF, Markdown or TXT; review the extraction;
edit and approve the exact Spanish; then review US and UK English. PDF, Markdown
and a Markdown/images ZIP are available for each candidate. The single queue can
pause and resume, with limited, intensive or optional night operation.

The launcher reuses installed local components. On another machine, install the
pinned optional document dependencies and configure runtimes, OCR, LanguageTool
and the existing model aliases first; see the [runbook](docs/08-runbook.md#local-browser-workbench).
It does not download components or contact a paid service during document work.

New model clients use dedicated Ollama at `127.0.0.1:11436`; the shared Ollama
service is unchanged. Historical jobs with a different endpoint identity cannot
be silently migrated. The original short-text CLI and its quality limitations
remain. Current implementation and verification are recorded in
[specification 011](specs/011-local-review-workbench/tasks.md).

PDF reading is conservative and needs page-by-page confirmation, particularly
for scans, columns, tables and footnotes. Exact PDF layout, DOCX, arbitrary
structural editing and editing text embedded in images are not implemented.
English can be reviewed in full and downloaded for manual editing; external
edits do not receive automatic approval or silently replace retained versions.

The short-text API remains bounded. The document workflow segments UTF-8 Markdown/TXT, produces editable Spanish first and pauses for explicit revision approval. British and American English are then generated independently from the same approved Spanish, with additional original-source checks. Completed batches are checkpointed. Prompts above 12000 UTF-8 bytes and incomplete length-limited responses are rejected. See the [active delivery handoff](specs/007-independent-auditor-evaluation/tasks.md) for verified versus pending work.

## Rewrite a document

```powershell
python tools/rewrite_document.py --input "C:/path/draft.md"
python tools/rewrite_document.py --resume "C:/path/draft.rewritten/job-id"
```

The command creates a unique job folder beside the original and stops with an editable `es-ES` copy and separate review. After reviewing the exact revision, use `--resume JOB --approve-spanish SHA256` to authorise both English variants. Review-required Spanish additionally needs explicit `--acknowledge-review`; that never clears its findings. The original and previous revisions are retained. Later Spanish edits invalidate current approval and mark earlier translations outdated.

Exit `3` is a normal approval pause; `0` means three-version completion and automatic acceptance, `2` means completed candidates require review, and `1` means an error. Human approval is never automatic. Unit tests use synthetic approvals; actual document approval belongs to the user.

Use `--clean-notes` only when removing explicit `VERIFY`/`DAVID` preparation markers is intended; removed spans stay in local evidence. `--omit-lines FIRST:LAST` records an explicit preparation range. Neither option performs fact-checking or fills missing fields. This legacy CLI does not ingest PDF or DOCX; use the browser intake for PDF. HTML blocks and complex Markdown constructs remain unsupported. Editing is wording-only and rejects ambiguous span ownership or structural changes. See the [document runbook](docs/08-runbook.md#rewrite-a-document-with-spanish-approval).

## Requirements

- Windows or another platform with Python 3.12 or later.
- A loopback Ollama service.
- Installed model `qwen3.8-local-fast2:latest` or an explicitly selected compatible model.
- Installed independent auditor `gemma4:latest` or an explicitly selected different model.
- Java 17 and a local LanguageTool server on `127.0.0.1:8082`.

The Python core uses only the standard library. PDF/OCR/browser document delivery additionally uses `requirements-documents.txt`, portable Tesseract and installed local language data.

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
python tools/evaluate_corporate.py --bank benchmark/corporate_review_controls.json
python tools/evaluate_corporate.py --bank benchmark/corporate_calibration_controls.json
python tools/run_semantic_audit_benchmark.py
python tools/run_rewrite_benchmark.py --runs 2
```

Benchmark reports are written under `artifacts/` and intentionally excluded from Git because they are generated and may contain supplied text.

The document path uses its own versioned corporate instructions and reproducible es-ES editorial checks. Its calibration must not be confused with the historical short-text API benchmark. Tests passing establish software behavior; draft synthetic model results do not guarantee flawless writing. The [runbook](docs/08-runbook.md) explains resumption, version compatibility and review-required outputs.

## Documentation

- [Charter](docs/00-charter.md)
- [Requirements](docs/01-requirements.md)
- [Architecture](docs/03-architecture.md)
- [Traceability](docs/07-traceability.md)
- [Runbook](docs/08-runbook.md)
- [Primary-source research](docs/09-research.md)
- [Measured validation results](docs/10-validation.md)
- [Active specifications](specs/)


The first browser translation smoke exposed a conditional-ability change missed
by both model auditors. `document-fidelity-v2` adds a narrow deterministic guard;
see [specification 012](specs/012-conditional-modality/tasks.md). Earlier jobs keep
their outputs but cannot be resumed under changed fidelity rules; use a new import.
