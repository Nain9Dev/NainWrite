# Data Model

The first version uses one self-contained JSON object per line. Arrays are embedded because each case is independently reviewed and executed.

```mermaid
erDiagram
    BENCHMARK_CASE {
        string id PK
        string title
        string category
        string priority
        string locale
        string source
        string draft_reference
        string review_status
    }
    BENCHMARK_CASE ||--|{ PROTECTED_LITERAL : protects
    BENCHMARK_CASE ||--|{ REQUIRED_MEANING : requires
    BENCHMARK_CASE ||--|{ FORBIDDEN_CHANGE : rejects
    BENCHMARK_CASE ||--|{ PHENOMENON : covers
    PROTECTED_LITERAL {
        string value
    }
    REQUIRED_MEANING {
        string statement
    }
    FORBIDDEN_CHANGE {
        string statement
    }
    PHENOMENON {
        string name
    }
    BENCHMARK_CASE ||--o{ REWRITE_RESULT : produces
    REWRITE_RESULT {
        string status
        string rewritten_text
        string prompt_version
        string model_digest
    }
    REWRITE_RESULT ||--o{ AUDIT_EVIDENCE : requires
    AUDIT_EVIDENCE {
        string model
        string model_digest
        boolean equivalent
        float confidence
        int naturalness_score
        int professional_tone_score
        string validation_error
    }
    REWRITE_RESULT ||--o| PROOFREADING_RESULT : checks
    PROOFREADING_RESULT {
        string software_name
        string software_version
        string language
    }
    PROOFREADING_RESULT ||--o{ LANGUAGE_ISSUE : finds
    LANGUAGE_ISSUE {
        string rule_id
        string issue_type
        string message
        int offset
        int length
    }
    MUTATION_CASE {
        string id PK
        string source
        string candidate
        string expected_status
        string review_status
    }
    MUTATION_CASE ||--o{ CANDIDATE_EVALUATION : evaluates
    CANDIDATE_EVALUATION ||--o{ AUDIT_EVIDENCE : records
    CANDIDATE_EVALUATION ||--o| PROOFREADING_RESULT : records
```

## Status values

- `draft`: generated or edited reference awaiting human approval.
- Future values require an approved ADR before being introduced.

Runtime statuses are separate from reference review state: `accepted` means that configured automatic checks passed; `review_required` means at least one check rejected or could not validate the candidate. Neither changes a reference from `draft` to gold.

Reports also contain detected invariants, blocking/advisory/ignored language findings, generation timing and token counts. Reports are local artifacts and are not repository data or a persistence database.

## Document jobs

```mermaid
erDiagram
    DOCUMENT_JOB ||--|{ SOURCE_PIECE : orders
    DOCUMENT_JOB ||--o{ REMOVAL_RANGE : records
    DOCUMENT_JOB ||--|{ BATCH_RESULT : checkpoints
    BATCH_RESULT ||--|{ ATTEMPT : retains
    ATTEMPT ||--|{ AUDIT_EVIDENCE : requires
    ATTEMPT ||--|| PROOFREADING_RESULT : checks
    DOCUMENT_JOB ||--o{ OUTPUT_FILE : publishes
    DOCUMENT_JOB {
        string source_sha256
        string configuration_sha256
        string phase
        boolean generation_complete
        boolean human_approved
    }
    SOURCE_PIECE {
        string id PK
        int start
        int end
        string role
        string sha256
        string original_sha256
        string original_text
        string text
        boolean editable
        boolean removed
    }
    BATCH_RESULT {
        string locale
        string status
        object input_hashes
        object output_hashes
        object replacements
    }
    OUTPUT_FILE {
        string locale
        string filename
    }
```

Offsets index Unicode source characters; each span and removal retains exact source text locally. The checkpoint envelope contains a SHA-256 of canonical state to detect corruption, not a cryptographic signature or protection against a malicious local writer. Resumption reconstructs the manifest and verifies source/configuration/model identity, coverage, candidate hashes, original audit responses, proofreading classifications and derived statuses. A process lock prevents simultaneous runners from modifying one job.

In parser v2, `original_text` always matches the exact source slice. `text` is the cleaned model input, which can exclude recorded preparation notes inside that slice. Concatenating all original slices reproduces the complete source; assembling replacements produces the cleaned candidate. This prevents artificial sentence fragments while retaining a lossless audit trail. Old manifests are intentionally incompatible.

## Spanish revisions and translation authority

```mermaid
erDiagram
    EDITORIAL_JOB ||--|| EDITABLE_COPY : tracks
    EDITORIAL_JOB ||--|{ SPANISH_REVISION : retains
    SPANISH_REVISION ||--|{ REVISION_REVIEW : requires
    SPANISH_REVISION ||--o| TRANSLATION_APPROVAL : authorises
    TRANSLATION_APPROVAL ||--o{ TRANSLATION_RESULT : permits
    TRANSLATION_RESULT ||--|{ ORIGINAL_CROSSCHECK : requires
    EDITABLE_COPY {
        string current_sha256
        string file_path
    }
    SPANISH_REVISION {
        string sha256 PK
        string source_sha256
        string configuration_sha256
        object replacements
        string automatic_status
    }
    TRANSLATION_APPROVAL {
        string revision_sha256 FK
        string evidence_identity
        boolean review_acknowledged
    }
    TRANSLATION_RESULT {
        string revision_sha256 FK
        string locale
        string automatic_status
        string filename
    }
    REVISION_REVIEW {
        object input_hashes
        object output_hashes
        object proofreading
        object audits
        string status
    }
    ORIGINAL_CROSSCHECK {
        object original_hashes
        object candidate_hashes
        object audits
        string status
    }
```

This is the conceptual specification-005 model; serialized fields are versioned by the runtime. Review-only evidence has no synthetic writer generation: it records actual candidate bytes, checks and audit responses. Approval is local workflow authority tied to a revision, not an authenticated signature or a guarantee that a named person approved it. A local attacker able to rewrite state remains outside the corruption-detection threat model.

An editable-copy change revokes current translation authority. Old snapshots, reviews and translations remain available, but are not the current document version. Completion, automatic quality, human translation approval and stale-history status must not be conflated.

## Calibration evidence

External evaluation adds corpus provenance and partition identity to the retained
bank without changing the existing review evidence contract.

```mermaid
erDiagram
    CORPUS_SNAPSHOT ||--|{ FROZEN_PARTITION : selects
    FROZEN_PARTITION ||--|{ EXTERNAL_CASE : contains
    EXTERNAL_CASE ||--o| CASE_RECORD : evaluates
    CORPUS_SNAPSHOT {
        string source_url
        string revision
        string snapshot_sha256
        string licence_url
    }
    FROZEN_PARTITION {
        string partition
        string bank_sha256
        string seed
        boolean human_approved
    }
    EXTERNAL_CASE {
        integer external_id
        string source
        string candidate
        boolean expected_equivalent
    }
```

External semantic labels have no associated corporate-style approval. Only the
evaluation partition is used in the baseline; the reserve remains unexamined.

```mermaid
erDiagram
    CALIBRATION_RUN ||--|{ CASE_RECORD : retains
    CASE_RECORD ||--o| REVIEW_EVIDENCE : records
    CALIBRATION_RUN {
        string bank_sha256
        object configuration
        string review_status
        boolean complete
        boolean quality_gate_passed
        object summary
    }
    CASE_RECORD {
        string id
        object authored_case
        array deterministic_drift
        string execution_error
    }
    REVIEW_EVIDENCE {
        object candidate_hashes
        array editorial_findings
        object proofreading
        array audits
        string status
    }
```

Each record holds either complete review evidence or an explicit local model execution error. Per-case files are immutable; checkpoint state allows validated completed records to be reused. `complete` means all cases were attempted, whereas `quality_gate_passed` requires all expected semantic/style outcomes and no execution errors. The fixed draft review status is never gold approval. Configuration includes the editorial-rule version as well as prompt/model identities.


## Workbench records

```mermaid
erDiagram
    WORKBENCH ||--o{ DOCUMENT : queues
    DOCUMENT ||--o| INTAKE : retains
    INTAKE ||--o{ PAGE : describes
    INTAKE ||--o{ EXTRACTION_APPROVAL : snapshots
    DOCUMENT ||--o| EDITORIAL_JOB : runs
    DOCUMENT ||--o{ EXPORT : retains
    EXPORT ||--o| FINAL_APPROVAL : identifies
    DOCUMENT {
        string id
        string status
        string action
        string progress
    }
    EXPORT {
        string locale
        string text_sha256
        string pdf_sha256
        string bundle_sha256
    }
    FINAL_APPROVAL {
        string revision
        string note
        string time
    }
```

Workbench state is atomically replaced JSON. Original bytes, page previews,
images, approved snapshots and exports are retained separately. Editing Spanish
invalidates current exports and final approvals; old files remain on disk.
Hashes detect accidental/tampered changes but do not authenticate the local user.
