# Interactive Web Demo

- **DEMO-001:** When accessed in a static hosting environment (GitHub Pages at `write.naindev.com` or without a local loopback server), the web workbench shall operate autonomously using an in-browser deterministic engine, preserving all UI element contracts and API semantics without broken network requests.
- **DEMO-002:** When initialized in standalone demo mode, the workbench shall pre-seed representative documents covering all review stages: extraction review with page inspection, Spanish rewrite with semantic invariant verification and diff comparison, and final trilingual export review (`es-ES`, `en-US`, `en-GB`).
- **DEMO-003:** When a user submits custom text or uploads a `.md`/`.txt` file in demo mode, the in-browser engine shall execute a deterministic pass detecting invariants (numbers, dates, currency, negations, protected literals) and correcting frequent English calques into natural Spanish from Spain with real-time diff reporting.
- **DEMO-004:** When interacting with editorial gates, all actions (`accept_extraction`, `edit_spanish`, `translate`, `approve_final`) shall preserve state locally in `localStorage`, maintaining complete fidelity to the documented human-in-the-loop approval workflow.
- **DEMO-005:** When code is pushed to `main`, a GitHub Actions workflow shall deploy the static web assets to GitHub Pages with custom domain `write.naindev.com`.

No paid cloud dependencies, remote inference, or tracking services are used `[A]`. Automated acceptance in the demo is illustrative; final legal or editorial approval remains `[M]`.
