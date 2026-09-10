# Runbook

## Reproduce the external auditor baseline

This is evaluation-only. It does not rewrite documents or change Ollama. See
`docs/12-independent-evaluation.md` for provenance and interpretation limits.
Use Python 3.12 on this workstation for the isolated optional Parquet reader.

```powershell
python -m pip install --index-url https://pypi.org/simple --only-binary=:all: --no-deps --target .tools/benchmark-deps pyarrow==25.0.1
New-Item -ItemType Directory -Force artifacts/external-pawsx
Invoke-WebRequest -Uri 'https://huggingface.co/datasets/google-research-datasets/paws-x/resolve/4cd8187c404bda33cb1f62b49b001115862acf37/es/test-00000-of-00001.parquet' -OutFile artifacts/external-pawsx/es-test.parquet
python tools/prepare_external_evaluation.py --parquet artifacts/external-pawsx/es-test.parquet --output-dir artifacts/external-pawsx/frozen-v1
python tools/evaluate_corporate.py --bank artifacts/external-pawsx/frozen-v1/evaluation.json --output-dir artifacts/external-auditors.rewritten
python tools/compare_auditors.py --bank artifacts/external-pawsx/frozen-v1/evaluation.json --job artifacts/external-auditors.rewritten/JOB_ID
```

The import checks the exact snapshot hash before decoding. Do not reinstall the
reader if already present. No corpus loading scripts, remote inference or global
Python changes are required. The main rewriting runtime remains standard-library
only. Public network requests above download only public corpus/package files.

Substitute the printed job ID. Existing evaluation exit 2 means its combined
quality gate failed; the external corpus has no corporate-style labels, so use
the separate `auditor-comparison.json` for semantic measurement. Exit 1 means
incomplete/error. Resume interrupted evaluation with the same bank and `--resume
JOB`; do not hand-edit checkpoints or delete failed records to retry them.

`compare_auditors.py` validates completed immutable evidence offline. Changed
source/runtime prompts need a new versioned evaluation, not rewritten evidence.
It cannot compare incomplete jobs or a reserve partition. Keep the reserve
unexamined until a subsequent protocol explicitly freezes its use.

Give the independent reader only `independent-review.md` from the frozen sample
directory. Keep a separate editable copy for their answers; do not overwrite the
generated template. Do not include corpus labels or model decisions until ratings
are recorded. This semantic sheet is not the later corporate-style pilot.

All corpus text, review sheets, reports and decoder files remain ignored. Publish
only source, tests and technical documentation, even in the private repository.

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

On 2026-09-09 Aitor authorised isolation without interrupting other projects.
New default clients use the dedicated endpoint `http://127.0.0.1:11436`. Shared
desktop Ollama on 11434 must remain unchanged. The launcher requires PowerShell
7.4+ and uses child-only environment settings; it does not install dependencies,
download models, preload GPU weights, modify global settings or enable auto-start.

Start dedicated Ollama from the repository root:

```powershell
pwsh -NoProfile -File tools/start-local-ollama.ps1
```

The hidden process remains running after the command returns. Keep its printed PID,
start time and startup-log path. Readiness requires an owned loopback listener and
the `Ollama cloud disabled: true` log marker. An occupied port causes refusal rather
than restart or automatic reuse. Inspect the owner and verify an existing instance
before reusing it. Logs remain under ignored `.tools/nainwrite-ollama/`.

To reverse the startup, first compare the current 11436 listener owner, executable
path and process start time with the launch result, then stop only that matching
process with `Stop-Process -Id VERIFIED_PID`. Do not stop all processes named
Ollama. A mismatch requires inspection, not termination. No global setting needs
restoration. LanguageTool startup remains a separate operation.

Official configuration reference checked on 2026-09-09:
[Ollama FAQ](https://docs.ollama.com/faq), server environment and disabling cloud
features. The verified installed executable was signed and reported version 0.33.3.

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
Invoke-RestMethod -Uri http://127.0.0.1:11436/api/tags -NoProxy -MaximumRedirection 0
Get-NetTCPConnection -State Listen -LocalPort 11436,8082
```

No LanguageTool listener was present in the 2026-09-09 isolation preflight; the
existing installation was left stopped. Dedicated Ollama readiness alone does not
make the complete rewriting pipeline available.

## Repeat the document calibration

The evaluator accepts a draft synthetic JSON bank with at most 100 cases and 1800 UTF-8 bytes per source/candidate. It sends only source, candidate and locale to the auditors, withholding expected outcomes and explanations.

```powershell
python -X utf8 tools/evaluate_corporate.py --bank benchmark/corporate_review_controls.json
python -X utf8 tools/evaluate_corporate.py --bank benchmark/corporate_calibration_controls.json
python -X utf8 tools/evaluate_corporate.py --bank benchmark/corporate_calibration_controls.json --resume "C:/path/to/experiment"
```

Each run prints a unique local directory. Keep the complete directory to resume; changed banks/configurations or inconsistent artifacts are rejected. Complete error records remain failures; a new experiment is needed to retry them. Exit `0` means all finite expected controls passed, `2` means at least one control or execution failed, and `1` means the evaluator stopped before completing. None approves a customer document. Semantic detection, editorial detection and execution failures are scored separately.

Prompt `trilingual-editorial-v10`, editorial rules `corporate-style-v3` and evidence contract `trilingual-review-v2` require fresh document jobs relative to specification 005. Retain old jobs with their compatible runtime; never edit their checkpoint version fields. Narrow editorial flags cover populated-data calques, empty emphasis formulas and the observed redundant conformance-test definition. Quoted expressions, code/links and geographic population uses are excluded; other awkward prose can still escape the checks. Evaluator version `corporate-evaluation-v2` also fails on invalid auditor contracts and semantic false positives among style controls; a published case is recovered if the process stopped before saving its checkpoint.

Both listeners must be loopback-only. A local endpoint is not an authentication boundary against other local applications; do not expose these ports through a proxy or tunnel.

The shared desktop listener remains `::11434`; NainWrite's dedicated instance does
not change its exposure. New default calls no longer use it. Explicit CLI endpoint
overrides require their own listener verification. Historical jobs include endpoint
identity in saved configuration, so switching to 11436 may reject their resumption.
Keep those jobs intact and use a compatible runtime or a separately specified
migration; never edit checkpoints. No private document was processed during the
isolation slice. See `BLK-005` and specification 009 for current evidence and limits.

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

## Rewrite a document with Spanish approval

From the repository root, with the existing local services running:

```powershell
python -X utf8 tools/rewrite_document.py --input "C:/path/draft.md"
```

The supported formats are UTF-8 `.md` and `.txt`. New specification-005 jobs generate and review `es-ES`, publish an editable copy and separate findings, then stop for approval. No English generation is permitted at this stage. The command prints a unique job folder, Spanish revision SHA-256 and a resume command. It does not install, restart or reconfigure Ollama. `-X utf8` keeps Windows console output readable.

Review the Spanish against the original, not merely for fluency. You may edit the printed editable file, preserving its structure. Then resume to review the exact edited text without rewriting your edits:

From another working directory, supply the absolute path to `tools/rewrite_document.py` as well as the input path. The CLI resolves its own package path. Keep quotes around paths containing spaces.

```powershell
python -X utf8 tools/rewrite_document.py --resume "C:/path/draft.rewritten/job-id"
```

Once the displayed revision and findings have actually been reviewed, the operator explicitly authorises that exact Spanish revision for translation:

```powershell
python -X utf8 tools/rewrite_document.py --resume "C:/path/draft.rewritten/job-id" --approve-spanish "EXACT_REVIEWED_SHA256"
```

If automatic review still has findings, the command refuses to continue unless the operator additionally supplies `--acknowledge-review`. This acknowledgement authorises translation of review-required content; it does not clear findings, approve final prose, or assert equivalence. Do not use it to conceal known errors. Design approval is not authorisation to execute this command on an unseen document.

Both `en-GB` and `en-US` are generated independently from the immutable approved Spanish snapshot. Each receives its exact locale's proofreading, audits against Spanish, and separate checks against the retained original. Proper names need not change between variants. If the editable Spanish later changes, current translation authority is invalidated; previous outputs remain retained but outdated. The CLI identifies the older Spanish revision hashes whose translations are outdated; keep those artifacts as history, not as current translations.

Resume with the exact original input and model/prompt configuration. Changed originals, incompatible configuration, corrupted evidence and output collisions are rejected. A running job locks its directory; operating-system process termination releases the lock. Completed validated batches are not regenerated. Keep the entire job directory for recovery; Git excludes `*.rewritten/` and is not a backup of private documents. Historical specification-004 jobs require their original runtime; never edit a checkpoint to force migration to this workflow.

Editing is deliberately conservative: changes must belong unambiguously to retained prose spans. Changed structural markers, code, line separators, unsupported syntax, duplicate-span ambiguity or unresolved long-span boundary crossings stop with guidance to make smaller wording edits or start a new source job. This is not a general document-restructuring editor. The generated baseline and revision snapshots are immutable; edit only the designated copy.

On Windows, a reader holding `checkpoint.json` open can temporarily prevent atomic replacement. Known access/sharing/lock errors receive six bounded attempts (at most 1.55 seconds of backoff); persistent errors remain failures and preserve the prior checkpoint. Avoid keeping the live checkpoint open in tools that deny delete sharing. Use printed CLI progress while processing. Do not weaken filesystem permissions or disable security software to make a run pass.

Optional cleanup must reflect the user's editorial intent:

```powershell
python tools/rewrite_document.py --input "C:/path/draft.md" --clean-notes --omit-lines 3:8
```

`--clean-notes` removes explicit `VERIFY`/`DAVID` bracketed preparation markers; `--omit-lines` removes exact inclusive source-line ranges and rejects numbered headings. All removed text and ranges remain in local evidence. Do not use omitted ranges to delete substantive statements or disclosures. No command or instruction inside the document is executed. Blank fields remain blank, and claims are not investigated.

Note cleanup happens before prose segmentation. It preserves code and link content, except an explicitly editorial marker occupying an entire inline-code span. Original and clean text are stored separately. Ambiguous notes embedded between unspaced word parts stop processing. After a parser, prompt or job-version upgrade, start a fresh job; do not edit checkpoint versions to force resumption of old evidence.

Use `--output-dir "D:/PrivateOutputs"` to choose the parent of the new unique job folder. Do not point it at a versioned folder for customer content. The default folder is beside the source.

Exit codes: `3` = normal pause awaiting Spanish approval; `0` = all three versions complete and automatically accepted; `2` = complete review-required candidates; `1` = incomplete or invalid job. The legacy `--both` option cannot bypass approval. Every generated document remains a candidate until reviewed by a person. Inspect the printed revision-specific report and files; local machine-readable evidence retains actual model digests and findings.

Common Markdown headings, lists, tables with outer pipes, inline code/links and fenced code are covered. Reference-style links, unsupported HTML, unsafe multiline constructs and oversized protected spans stop processing. This is not a universal Markdown renderer or a PDF/DOCX converter. The CLI checks that the configured proofreading languages are available before private generation. If LanguageTool is stopped, start its existing local installation using the separate instructions above; do not restart Ollama.


## Local browser workbench

### Configured workstation

Double-click `Start-NainWrite.cmd` or run `pwsh -NoProfile -File tools/open-workbench.ps1`.
The browser is at `http://127.0.0.1:8765`. Repeated launch checks and reuses the
existing local process. Work continues while the browser is closed and the
computer remains awake. The launcher is manual; it installs no startup task.

1. Add PDF, Markdown or TXT. Markdown images may be supplied as local PNG/JPEG
   files; references must match their names. Remote images are rejected.
2. Inspect every original PDF page and the extraction. Correct OCR, ordering,
   tables and notes. Confirm completeness with a review note. Empty pages need
   an explicit blank-page description; never approve unreadable numbers.
3. Review the entire Spanish, differences and separate findings. Save manual
   wording edits and run review again. Structural changes may require a new
   import because the editorial mapping intentionally refuses ambiguity.
4. Approve the exact Spanish and confirm that meaning doubts are resolved.
   Automatic findings remain recorded; their acknowledgement never erases them.
5. Review both English variants and download PDF, Markdown or ZIP with images.
   Record final approval per exact locale revision. External file edits do not
   update the retained version or its approval; import a revised document to
   process it again. DOCX and an English editing/re-audit screen are deferred.

Use **Pausar cola** to stop at the next model request or stage boundary. An
in-flight request may finish first. **Continuar cola** permits queued work;
paused/failed documents also have their own resume action. A restart recovers
interrupted work as paused. Errors retain originals and checkpoints.

Limited mode requests CPU inference with four threads, and can be slow. Intensive
mode permits available model acceleration. Night mode uses local hours while the
application is running; manual selection overrides it. Modes are request settings,
not GPU/CPU utilisation guarantees. A sleeping computer cannot process the queue.

### Dependencies and private data

`requirements-documents.txt` pins the tested PDF libraries. Core, OCR and export
perform no dependency downloads during processing. The tested installation uses
an existing Python runtime with those libraries and a portable Tesseract under
`.tools/tesseract/`, with `spa`, `eng` and `osd` in `tessdata/`. LanguageTool is under
`.tools/languagetool/LanguageTool-6.9-SNAPSHOT/`; Java 17 is required. Locally
installed custom Qwen and Gemma model aliases must exist before launch.

Optional `.tools/workbench-runtime.json` contains only `python` and `java`
absolute executable paths. Alternatively pass `-Python` and `-Java` to
`tools/start-workbench.ps1`. No credentials are needed. New-machine provisioning
is separate from document processing; the current launcher is not an installer.

Data live under `private/workbench/`: original uploads, intake assets, revision
snapshots, model evidence, queue state and exports. This folder, `.tools/`,
`artifacts/` and `NainWrite-Documents/` are excluded from Git. Retention is indefinite;
there is no automatic deletion or backup. Stop the application before manually
backing up or removing its data. A per-document delete screen is not implemented.

The HTTP service binds loopback and uses Host/Origin checks and a random request
token. It is not authentication against another process running as your Windows
user. Logs stay in `.tools/`. Dedicated Ollama uses `127.0.0.1:11436` with cloud
features disabled; shared `11434` is neither stopped nor reconfigured.

### Verification and limits

The browser upload and approval workflow, real synthetic OCR, local-model Spanish
and exported PDF were exercised on 2026-09-09. The PDF preview was inspected for
clipping and checked for critical extracted text. Synthetic tests exercise both
English variants, exact approvals, tamper rejection and persisted queue recovery.
A fully disconnected operating-system test and sustained 40-page workload have
not been measured. Known semantic benchmark failures remain open; generated
files and high audit scores are not a guarantee of perfect writing or translation.
