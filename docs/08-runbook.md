# Runbook

## Validate the draft bank

Run from the repository root:

```powershell
python tools/validate_bank.py
python -m unittest discover -s tests -v
```

Expected structural result:

```text
PASS: validated 30 draft cases
```

## Review a reference

1. Open `benchmark/spanish_rewrite_cases.jsonl`.
2. Select one case identifier.
3. Apply `benchmark/review_rubric.md` without considering authorship.
4. Record any corrected reference and reviewer notes separately.
5. Do not change `review_status` until every protected literal is revalidated.

## Rewrite one text locally

Ollama must be running with `qwen3.8-local-fast2:latest` and `gemma4:latest` installed. LanguageTool must be running separately on loopback port `8082`.

```powershell
python tools/rewrite_text.py --text "Texto de origen" --protected "literal exacto"
```

Use `--plain` only when the caller handles a non-zero exit. Exit code `0` means that every automated gate passed, `2` means `review_required`, and `3` means a local service or response error. An accepted result is not a legal or production approval.

## Start the local services on the measured workstation

Use separate terminals and keep them open. These commands do not configure autostart or change machine-wide environment variables.

Ollama terminal:

```powershell
$env:OLLAMA_HOST = '127.0.0.1:11434'
$env:OLLAMA_NO_CLOUD = '1'
ollama serve
```

LanguageTool terminal, from the repository root:

```powershell
Push-Location '.tools/languagetool/LanguageTool-6.9-SNAPSHOT'
& 'C:/Program Files/Eclipse Adoptium/jre-17.0.20.101-hotspot/bin/java.exe' `
  -cp languagetool-server.jar org.languagetool.server.HTTPServer --port 8082
Pop-Location
```

On another workstation, set the explicit Java path to its verified Java 17 installation. Stop only the service started in that terminal with `Ctrl+C`. If either port is already occupied, identify the existing process rather than terminating it blindly. Port `8081` is reserved for an unrelated existing Docker service on the measured workstation.

Verify before processing a document:

```powershell
ollama list
Get-NetTCPConnection -State Listen -LocalPort 11434,8082
```

Both listeners must be loopback-only. A local endpoint is not an authentication boundary against other local applications; do not expose these ports through a proxy or tunnel.

The latest observed desktop-managed Ollama listener was `::`, not loopback-only. Setting environment variables in a new terminal does not reconfigure an already running application-owned server. On 2026-09-04, Aitor explicitly required leaving that instance unchanged and authorised local processing of the named draft with this limitation understood. This is a narrow exception, not proof of isolation or blanket permission for other private documents. Future isolation work must be separately coordinated; do not run the restart commands above on the current instance. See `BLK-005` and [validation evidence](10-validation.md).

The application HTTP transport explicitly ignores proxies and rejects redirects. The strict Python service rejects configurations that disable proofreading or the second auditor. These controls do not protect against a compromised local service or operating system.

## Installed proofreading dependency

Verified on 2026-09-03:

- Java: Eclipse Temurin JRE 17.0.20.1, installed side by side with Java 8.
- LanguageTool: `6.9-SNAPSHOT`, build `2026-09-02 18:50:18 +0200`.
- Official download: `https://languagetool.org/download/snapshots/LanguageTool-latest-snapshot.zip`.
- Archive length: `263134984` bytes.
- Archive SHA-256: `9FE4B926327B6CD78B23F3F77931D595BEAFBA1E5235DF25F47E9215F747973B`.

The snapshot URL is mutable. A later download is not this verified build unless its digest matches. Keep the local archive for recovery, or treat a different build as a dependency update and rerun the checks. The archive and extracted runtime stay under ignored `.tools/` and are not backed up by Git.

LanguageTool's local Spanish checker uses language code `es`. The `es-ES` editorial register is enforced by the prompts and human rubric, not by a separate LanguageTool regional model. Local open-source LanguageTool does not include all cloud-only rules.

## Run the complete benchmark

```powershell
python tools/run_rewrite_benchmark.py --runs 2
```

The command writes a machine-readable JSON report and a Markdown human-review sheet under `artifacts/`. Draft references always produce a `preliminary` interpretation.

Each completed case is also saved atomically to a `.partial.json` report. A partial report is evidence of completed cases only; it is never a successful full run. Existing runs are not silently resumed across changes in prompts, models or datasets. The final report records the dataset digest and whether authored constraint hints were supplied.

Run the semantic mutation suite without authored hints:

```powershell
python tools/validate_semantic_mutations.py
python tools/run_semantic_audit_benchmark.py
```

Use `--with-hints` only for a separately labelled assisted comparison. Invalid candidates must be rejected for semantic or deterministic drift, not merely for spelling or style. The strict rewrite gate requires every result in every run to be accepted.

## Human-review labels

- `Texto original`: the input supplied to the rewriting agent.
- `Reescritura generada por Qwen`: the local writer's candidate output. Approving it validates that individual result.
- `Referencia propuesta`: a separately authored draft example. It is not automatically the writer's output or a gold reference.
- `Aprobar la referencia propuesta como ejemplo gold`: human approval of the reference after checking meaning and style. It does not train or fine-tune a model.

Review a candidate against the source even if it differs from the proposed reference; more than one rewrite can be valid.

## Failure handling

- Invalid JSON or missing fields: reject the dataset change.
- Missing protected literal: reject the candidate reference.
- Meaning or naturalness disagreement: keep the case in `draft` and record the review note.
- The runtime permits one constrained repair after deterministic drift; a second failure returns `review_required`.
- Blocking proofreading findings permit one additional linguistic repair from the original source. It is rechecked and audited; suggestions are never applied blindly.
- Do not copy a `review_required` rewrite into a document automatically.
- A model confidence value is not a calibrated correctness probability.
- On an Ollama error, retain the partial report and inspect the local service log. Do not convert missing audit evidence into acceptance.
- Prompts above 12000 UTF-8 bytes, including instructions and all constraints, fail before inference. Length-limited outputs also fail. Do not silently crop or split a complex source to bypass this limit; document-level segmentation requires a separate validated design.

## Rewrite a bilingual document

From the repository root, with the existing local services running:

```powershell
python tools/rewrite_document.py --input "C:/path/draft.md" --both
```

The first supported formats are UTF-8 `.md` and `.txt`. Both languages are generated: natural professional `es-ES`, then formal natural `en-GB` from the assembled Spanish candidate. The command prints a unique job folder and a resume command immediately. It does not install, restart or reconfigure Ollama.

```powershell
python tools/rewrite_document.py --resume "C:/path/draft.rewritten/job-id"
```

Resume with the exact original input and model/prompt configuration. Changed inputs, incompatible configuration, corrupted evidence and output collisions are rejected. A running job locks its directory; operating-system process termination releases the lock. Completed batches are not regenerated. Keep the entire job directory for recovery; Git excludes `*.rewritten/` and is not a backup of private documents.

Optional cleanup must reflect the user's editorial intent:

```powershell
python tools/rewrite_document.py --input "C:/path/draft.md" --both --clean-notes --omit-lines 3:8
```

`--clean-notes` removes explicit `VERIFY`/`DAVID` bracketed preparation markers; `--omit-lines` removes exact inclusive source-line ranges and rejects numbered headings. All removed text and ranges remain in local evidence. Do not use omitted ranges to delete substantive statements or disclosures. No command or instruction inside the document is executed. Blank fields remain blank, and claims are not investigated.

Use `--output-dir "D:/PrivateOutputs"` to choose the parent of the new unique job folder. Do not point it at a versioned folder for customer content. The default folder is beside the source.

Exit codes: `0` = complete and automatically accepted; `2` = complete review-required candidates; `1` = incomplete or invalid job. Every generated document remains a candidate until reviewed by a person. Inspect both language files and `review.md`; `review.json` contains full per-attempt findings, actual model digests and cleanup spans.

Common Markdown headings, lists, tables with outer pipes, inline code/links and fenced code are covered. Reference-style links, unsupported HTML, unsafe multiline constructs and oversized protected spans stop processing. This is not a universal Markdown renderer or a PDF/DOCX converter. The CLI checks that both proofreading languages are available before private generation. If LanguageTool is stopped, start its existing local installation using the separate instructions above; do not restart Ollama.
