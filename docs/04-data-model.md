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
```

## Status values

- `draft`: generated or edited reference awaiting human approval.
- Future values require an approved ADR before being introduced.
