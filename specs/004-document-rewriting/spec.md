# Bilingual Document Rewriting Specification

Status: Design approved by Aitor on 2026-09-04; implementation in progress.

## User-approved editorial intent

- Rewrite the wording, not the substance of the document.
- Preserve headings, section order, numbering, tables, factual content, conditions, uncertainty and commitments.
- Leave already natural and professional Spanish passages unchanged when no improvement is needed.
- Remove redundant wording, robotic framing and internal preparation notes without summarising substantive content.
- Do not investigate factual claims, invent missing data or add arguments.
- Process the whole document in sections, retain progress, and assemble the complete result.
- Use the local models. Do not change or restart Ollama.
- Produce professional, natural Spanish from Spain first, then professional, natural English from that Spanish version.

The latest request asks for both files in one workflow. The proposed implementation generates both as candidates and records automated checks separately; it never manufactures human approval of the Spanish intermediate result.

## Proposed implementation boundary

Initial inputs are UTF-8 Markdown and plain text (`.md`, `.txt`), including the supplied Markdown draft. PDF, DOCX, scans, OCR, complex layout conversion and universal file-format support are not part of this slice. English defaults to `en-GB`, proposed for consistent spelling in the European proposal; Spanish uses `es-ES`.

The original stays untouched. Generated text, source excerpts, local job state and review evidence stay outside versioned repository content. The named user-supplied draft is an input to local execution, never a committed fixture.

## Requirements

### File and structural integrity

- `REQ-064`: WHEN a user supplies a supported file path, the application SHALL read that file without modifying it and SHALL reject unsupported formats or invalid UTF-8 with a clear error.
- `REQ-065`: WHEN preparing a document, the application SHALL create an ordered manifest of stable block identifiers, source locations, structural roles and content hashes.
- `REQ-066`: WHEN dividing a document, the application SHALL preserve heading levels, numbering, table rows and columns, list markers, code, URLs and technical identifiers; it SHALL not split a protected construct merely to meet a character limit.
- `REQ-067`: WHEN a prose block exceeds the local request budget, the application SHALL divide it at safe prose boundaries and SHALL retain the mapping needed to reassemble it in its original position.
- `REQ-068`: BEFORE every inference request, the application SHALL account for instructions, target text, bounded context, constraints and candidate text within the existing request limit; it SHALL not silently truncate any of them.
- `REQ-069`: WHEN assembling output, the application SHALL ensure that each retained block appears exactly once and in order, with the original structural relationships preserved.

### Editorial transformation

- `REQ-070`: WHEN source text is not Spanish, the first stage SHALL produce a faithful professional `es-ES` version; WHEN Spanish wording already meets the editorial target, the stage MAY leave that wording unchanged.
- `REQ-071`: WHEN improving wording, the agent SHALL preserve propositions, actors, responsibility, tense, modality, negation, conditions, exceptions, uncertainty, figures and technical identifiers.
- `REQ-072`: WHEN removing preparation material, the application SHALL record the removed source ranges in local evidence; it SHALL not remove substantive sections, commitments, required disclosures, citations or uncertainty merely because they resemble generated text.
- `REQ-073`: WHEN editorial markers such as `[VERIFY: ...]` or `[DAVID: ...]` identify internal notes, the clean view MAY omit those notes under the recorded cleanup policy, but SHALL not invent values for empty fields or certify the remaining factual claims.
- `REQ-074`: The agent SHALL use a shared terminology policy and bounded neighbouring context across blocks, and SHALL not copy neighbouring content into the target block.
- `REQ-075`: The agent SHALL evaluate concrete writing defects rather than claim to detect authorship or remove an unverified technical watermark.

### English stage and evidence

- `REQ-076`: WHEN generating English, the agent SHALL translate the assembled Spanish candidate rather than independently rewriting the original into English; each English block SHALL be linked to its Spanish source hash.
- `REQ-077`: WHEN checking either language, the agent SHALL run language-appropriate proofreading and distinct local model audits for meaning and professional naturalness, while retaining findings and actual model digests.
- `REQ-078`: WHEN an earlier-stage block has unresolved issues, downstream English results SHALL inherit review-required status even if their own translation checks pass.
- `REQ-079`: WHEN a repair is attempted, it SHALL be bounded, grounded in the corresponding source and followed by the same checks; it SHALL not silence a rule by deleting a claim or changing a fact.
- `REQ-080`: WHEN all generation stages finish, the report SHALL distinguish generation completion, structural integrity, automatic quality status and human approval; successful generation SHALL not imply error-free writing.
- `REQ-081`: WHEN a stage cannot produce all required blocks, the job SHALL remain incomplete and SHALL not label a partial or mixed-language file as a completed version.

### Resumption and usability

- `REQ-082`: AFTER each completed block and phase, the application SHALL atomically save progress so a later run can resume without regenerating valid completed work.
- `REQ-083`: WHEN resuming, the application SHALL verify source hash, manifest, configuration, prompt versions and model digests and SHALL reject incompatible state.
- `REQ-084`: WHEN writing results, the application SHALL create a new job directory, preserve existing files and produce separate Spanish, English and review artifacts; output filenames SHALL expose review-required status where applicable.
- `REQ-085`: The CLI SHALL accept a quoted file path, report phase/block progress, provide an explicit resume command and print the final output paths and quality status.
- `REQ-086`: The implementation SHALL keep inference and proofreading requests on the existing proxy-free loopback transport and SHALL not install cloud services, execute instructions from documents or modify Ollama configuration.
- `REQ-087`: The document-level checks SHALL report block coverage, structural mismatches, protected-literal changes and terminology inconsistencies; any bounded semantic cross-section checks SHALL disclose their coverage rather than claim exhaustive proof.

### Refinement acceptance criteria

For `REQ-065`, `REQ-067` and `REQ-073`, note cleanup precedes segmentation of each editable structural region. The manifest retains exact original spans separately from clean model text. Only horizontal spacing at recorded removal joins is normalized; code, line endings and Markdown hard breaks remain intact. Ambiguous unspaced word joins are rejected. A parser version change requires a fresh job.

For `REQ-074` and `REQ-087`, repeated identical source headings with differing translations are reported with their block IDs in both languages. This comparison uses original source identity even when Spanish candidates differ; no variant is silently chosen as authoritative.

For `REQ-082`, checkpoint replacement retries known Windows access/sharing/lock errors a bounded number of times. It never truncates the existing checkpoint, changes permissions or suppresses persistent failures. The previous valid state remains readable after exhausted retries.

## Current-draft handling

The provided file contains numbered submission fields as well as editorial preparation material. Its cleanup plan must explicitly identify which ranges are preparation notes and preserve all substantive numbered fields, their order, table structure and the AI-use disclosure section. No repository, website, script, business decision or declaration mentioned inside the file becomes an instruction to the agent.

Unfilled budget, contact and decision fields remain unfilled. Rewriting does not make the application fact-checked, complete for submission or human-authored. Such limitations belong in the separate review artifact, not as added commentary inside ordinary rewritten paragraphs.

## Acceptance evidence

1. Existing 58 tests remain passing.
2. New failing-first tests cover supported inputs, Markdown round trips, tables, protected constructs, long blocks, non-ASCII text, note cleanup, structural coverage and immutable originals.
3. Checkpoint tests cover interruption, incompatible resume, missing blocks, duplicate blocks, source changes and existing-output collision.
4. Bilingual tests cover source-to-Spanish and Spanish-to-English routing, language-specific proofreading, preservation of uncertainty and inheritance of earlier review failures.
5. Synthetic regression examples exercise robotic framing, useful contrast statements, preserved disclosures and acceptable unchanged prose.
6. The supplied document is processed locally only after design approval. Both outputs and the complete real report are inspected; every failure is disclosed. No generated document enters Git.

This is a finite evaluation of a configured workflow, not proof of perfect semantic equivalence or a universally optimal model.
