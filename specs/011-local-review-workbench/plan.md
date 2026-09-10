# Plan

1. `[A]` Add failing tests for queue transitions, approval gates, export fidelity and request boundaries.
2. `[A]` Implement repository, workbench service, safe export adapter and single worker around existing editorial jobs.
3. `[A]` Add a loopback HTTP presentation adapter and local HTML/CSS/JavaScript review surface.
4. `[A]` Verify service recovery, tampering, pause/resume and both locale paths with synthetic model contracts; inspect real exported PDF and browser states.
5. `[A]` Run a bounded real local-model Spanish smoke up to the human approval gate; never approve real output on Aitor's behalf.
6. `[A]` Document startup, limitations, evidence and handoff. `[M]` Present the actual Spanish candidate for review.

```mermaid
flowchart TD
    Browser[Local browser presentation] --> API[Loopback HTTP adapter]
    API --> Service[Workbench service and domain gates]
    Service --> Repo[Local repository]
    Service --> Worker[Single resumable worker]
    Worker --> Intake[Approved extraction]
    Intake --> Editorial[Existing editorial job service]
    Editorial --> Ollama[Dedicated local models]
    Editorial --> LT[Local proofreading]
    Editorial --> Export[PDF and Markdown exporter]
    Export --> Review[Independent human approval per locale]
```

```mermaid
erDiagram
    WORKBENCH ||--o{ QUEUED_DOCUMENT : owns
    QUEUED_DOCUMENT ||--|| INTAKE : verifies
    QUEUED_DOCUMENT ||--o| EDITORIAL_JOB : runs
    QUEUED_DOCUMENT ||--o{ EXPORT : retains
    EXPORT ||--o| FINAL_APPROVAL : requires
    WORKBENCH {
        boolean paused
        string mode
        boolean night_schedule
    }
    QUEUED_DOCUMENT {
        string id
        string status
        string action
        string progress
    }
    FINAL_APPROVAL {
        string locale
        string revision
        string note
    }
```
