# Local Document Intake

Aitor authorised implementation of the readiness roadmap on 2026-09-09. This
first slice supplies reviewed extraction, not autonomous proof of PDF fidelity.

## Requirements

- **IN-001:** When importing PDF, Markdown or TXT, the service shall retain exact original bytes and a SHA-256 identity in a new local intake folder, reject unsupported, empty, encrypted or oversized input, and never overwrite the original.
- **IN-002:** When importing a PDF, the service shall account for every page, retain a rendered preview and native text/table/image/link evidence, run local Spanish/English OCR for image-only pages, and expose all extraction as requiring human review. Extraction failures shall remain blocking rather than being dropped.
- **IN-003:** When generating editable Markdown, the service shall preserve detected tables and images with local assets and page provenance. Multiple columns, scans, annotations and uncertain structure shall require comparison with the original. Embedded image text is not automatically replaced.
- **IN-004:** When approving extraction, the service shall require the exact current Markdown hash, explicit completeness confirmation and a non-empty reviewer note, validate retained original/assets, and reject an uncorrected blank page. Edits shall invalidate previous approval. Review may correct reading order and transcription but shall never silently waive failed extraction.
- **IN-005:** When handing extraction to the rewriter, the service shall require valid current extraction approval and a manifest accepted by the existing conservative parser. Original PDF, extraction and approval shall remain associated with the downstream job.
- **IN-006:** When handling source Markdown images, the importer shall copy only regular local image assets inside the source directory, reject remote, absolute, traversing or symbolic paths, and never fetch document URLs. It shall preserve text, inline links and code as data.
- **IN-007:** When extracting scans, the OCR adapter shall use a local executable and explicit installed language files, with timeout, bounded pixels and word-level confidence evidence. It shall never download models during processing or present confidence as verified correctness.

## Dependencies and authority

- `[A]` Existing bundled Python libraries: pdfplumber 0.11.9, pypdfium2 5.13.0, Pillow 12.3.0 and ReportLab 4.4.9; runtime capability must be checked explicitly.
- `[A]` Tesseract 5.5.3 portable executable from official project release, extracted under ignored `.tools/`; Spanish and English tessdata_fast files downloaded separately and hashed. No registry/PATH/service changes.
- `[M]` Aitor must review actual extraction. Synthetic test approvals do not satisfy real document approval.
- `[H]` No paid service, client upload, commit, push or model-output approval is authorised by implementation permission.

## Limits

Initial resource guards: 100 MB source, 200 pages and 20 million rendered pixels
per page. These are defensive implementation limits, not throughput promises.
Full-page scanned images remain retained as source evidence. General table and
multi-column interpretation cannot be certified by this extractor; human correction
is mandatory. Final rendering, browser review and background queue follow in the
next slice. All inference continues through the existing Spanish approval gate.
