# Task Handoff

## Completed

- `[A]` Implement the authorised document intake slice before broader UI work.
- `[A]` Canonical docs and current dirty tree read; pre-existing work retained.
- `[A]` Portable Tesseract extracted from hash-verified official release; no global installation. Existing bundled PDF libraries will be reused.
- `[A]` Added failing intake tests before implementation. The first live adapter run exposed unsupported PdfPage context management; explicit resource closure fixed it.
- `[A]` Implemented original/asset hashes, every-page previews, native text/table/image/link extraction, local spa+eng OCR with per-word confidence, exact extraction approvals and guarded downstream source snapshots.
- `[A]` Real three-page synthetic fixture passed native table/image/link and real OCR checks; all three rendered pages were inspected. The observed column interleaving prompted a failing regression and a conservative two-column correction. Complex layouts still require owner review.
- `[A]` Full initial suite passed 176 tests before the added column regression; final count recorded after that regression below.

## Evidence

- Portable Tesseract 5.5.3.20260724; release package SHA-256 `bee9e3434bd94fd65387d9be28cd467a41f61b1275383b55b0f59a1331270ae4`.
- tessdata_fast pinned revision `87416418657359cb625c412a48b6e1d6d41c29bd`; local model hashes retained in `.tools/tesseract/model-manifest.json`.
- Synthetic evidence: `artifacts/document-intake-smoke/`; no human extraction approval or private inference performed.

## Pending

- `[A]` Browser integration, clean PDF output and background queue are the next slice.
- `[M]` Actual document extraction and editorial approval remain Aitor's actions.

No private text, model inference, commit or push in this slice.


## Subsequent verification

- `[A]` All nine intake regressions pass in the current 193-test suite.
- `[A]` Browser, clean PDF/Markdown/ZIP export and queue implemented in specification 011.
- `[A]` The three original preview pages and subsequent clean export were visually
  inspected. The older mixed fixture retains the pre-fix column reading; the new
  column regression verifies the correction without rewriting old evidence.
- `[M]` Actual customer-document extraction approval remains required.
