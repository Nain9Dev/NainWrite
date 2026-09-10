# Plan

1. `[A]` Specify immutable intake identity, editable extraction and review authority.
2. `[A]` Add failing tests for full page coverage, OCR, asset confinement, changed approvals and blocked incomplete extraction.
3. `[A]` Implement repository persistence, local PDF/OCR adapters and intake service; CLI remains argument presentation only.
4. `[A]` Test native, scanned, table, multi-column, image, footnote and link fixtures without private data.
5. `[A]` Inspect rendered fixture pages and handoff to the existing parser. Update traceability and handoff before the next slice.

## Architecture

```mermaid
flowchart LR
    CLI[Intake CLI] --> Service[Intake service]
    Service --> Repo[Local intake repository]
    Service --> PDF[PDF and local OCR adapter]
    PDF --> Pages[Page text, assets and findings]
    Pages --> Review[Exact extraction approval]
    Review --> Parser[Existing conservative parser]
```

```mermaid
erDiagram
    INTAKE ||--|{ PAGE : retains
    INTAKE ||--|{ ASSET : hashes
    INTAKE ||--o{ EXTRACTION_APPROVAL : records
    INTAKE ||--o{ EDITORIAL_JOB : supplies
    PAGE {
        int number
        string method
        string preview
        string findings
    }
    EXTRACTION_APPROVAL {
        string source_sha256
        string extraction_sha256
        string note
        boolean complete
    }
```
