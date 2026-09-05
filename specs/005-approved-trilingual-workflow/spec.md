# Approved Trilingual Editorial Workflow

## Approval and scope

Aitor approved this design and requested testing on 2026-09-04. Approval covers the workflow, not any generated document, benchmark reference, or automatic equivalence claim. This specification supersedes the automatic Spanish-to-British-English progression for new CLI jobs. Historical jobs and evidence remain unchanged.

The editorial profile is clear, sober, precise, professional and natural for corporate readers: clients, decision-makers and proposal evaluators, with technical precision for specialists. Spanish from Spain is reviewed first. British and American English are independent translations of the exact approved Spanish revision. No new UI, document format, model installation or service configuration is included.

## External dependencies

- `[A]` Existing Python standard library, local Qwen writer, independent Gemma auditor and loopback LanguageTool with `es`, `en-GB` and `en-US` checking. Verify availability before model work; install nothing if already available.
- `[M]` Aitor reviews the exact Spanish revision and authorises translation. Design approval does not satisfy this gate.
- `[M]` Human editorial review remains necessary for all three outputs; model scores and synthetic fixtures are not approved gold.
- `[H]` No accounts, payments, credentials, cloud inference or deployment are required.

## Requirements

- **REQ-088:** When a new document job finishes Spanish generation, the system shall persist an editable es-ES copy and a separate review report, and shall stop before any English generation until explicit revision-specific approval is recorded.
- **REQ-089:** When the user edits the Spanish copy, the system shall preserve the generated baseline, map wording-only edits to the original manifest, and reject structural or ambiguous edits without silently dropping or moving content.
- **REQ-090:** When a Spanish revision is submitted for review, the system shall check the exact edited text against the original retained source using literal checks, Spanish proofreading and both configured semantic/style auditors, without rewriting the user's edits or presenting them as model generations.
- **REQ-091:** When approval is requested, the system shall require the exact current revision SHA-256 and completed review evidence; review-required text shall require explicit acknowledgement and shall retain that quality status independently of approval to translate.
- **REQ-092:** When an approved Spanish revision is translated, the system shall generate en-GB and en-US independently from the same immutable Spanish snapshot and validate the exact requested proofreading locale.
- **REQ-093:** When either English candidate is produced, the system shall also audit it against the retained original source, preserve this distinct evidence, and require review if either the Spanish-grounded or original-grounded checks fail.
- **REQ-094:** When the editable Spanish file changes after approval, the system shall invalidate current translation authority, retain all prior revision artifacts, report earlier translations as outdated, and require review and approval of the new revision.
- **REQ-095:** When a job resumes, the system shall verify original, configuration, revision, approval and saved quality evidence before additional model work; interrupted batches shall resume without regenerating validated completed batches.
- **REQ-096:** When files are published, the system shall retain the original and historical outputs unchanged, publish revision-specific Spanish/English artifacts and separate reports, and distinguish generation completeness, automatic quality and human translation approval.
- **REQ-097:** While editing or auditing prose, the system shall preserve statement state, modality, negation, conditions, quantities, proper names, technical scope and structure; it shall leave already suitable prose unchanged and shall not invent definitions or factual verification.
- **REQ-098:** When English variants are requested, prompts shall specify formal natural British or American usage respectively, without modifying proper names, protected literals or source meaning to force locale differences.
- **REQ-099:** When the workflow is evaluated, tests shall cover the approval barrier, editing/revision invalidation, both locale routes, interrupted recovery, tampered evidence and deliberate semantic mutations; live synthetic results shall remain separately labelled preliminary, never human approval or production acceptance.

## Global constraints

- Only UTF-8 `.md` and `.txt` inputs within the existing conservative parser subset are supported.
- Only loopback inference and proofreading are permitted; Ollama, GPU, firewall and service settings remain unchanged.
- Original documents, historical jobs, model weights and generated reports must not enter Git or be overwritten.
- Retain the existing 12000-byte complete-prompt limit, bounded source batches and at most one generated repair; never truncate source or candidate text to fit.
- Automated acceptance is not human approval or a guarantee of equivalence.
- Changes in code, prompts or evidence contracts require a new configuration identity; do not silently migrate old checkpoints.
- No commit, push, merge, publication or private-document approval is implicit in a test run.

## Conservative editing boundary

The initial editable-file implementation accepts unambiguous edits inside retained prose spans. It rejects changed structural prefixes, separators, code, unsupported syntax, removed regions or edits whose ownership crosses split boundaries ambiguously. The message must explain that smaller wording edits or a new source job are needed. Full document restructuring is outside the approved wording-only goal. This limitation must be visible in the runbook.

## Evidence and stopping point

First establish deterministic safety behavior, then run a finite synthetic local-model evaluation. Deliberately invalid semantic pairs test the auditors separately from prose generation. No percentage from these preliminary examples represents overall quality. A real document may stop at its Spanish review gate; the agent must not approve its own candidate on Aitor's behalf. Known strict-benchmark false acceptance remains open until separately re-evaluated.
