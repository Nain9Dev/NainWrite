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
