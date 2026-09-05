# Security Policy

## Supported state

The current project is an experimental local tool. No release is production-approved until the benchmark references and model outputs receive human review.

## Data handling

- Keep Ollama and auxiliary language services bound to loopback interfaces.
- Do not submit confidential, personal, contractual or customer text to remote services.
- Do not commit input documents, generated reports, credentials, tokens, model weights or local runtime installations.
- Inspect staged changes before every commit.

Repository privacy is an access setting, not permission to store secrets or customer text. Keep production inputs outside the checkout; `/private/`, `/inputs/`, `/outputs/`, generated artifacts, local installations and common credential/model files are ignored as a second precaution. Ignore rules do not remove files already tracked by Git. Review the actual staged file list and diff before publication.

The client disables HTTP proxies and refuses redirects, sending text only to configured loopback endpoints. On the current workstation, desktop-managed Ollama listens on `::11434`; server network isolation remains unverified and configuration is unchanged at the owner's request. A loopback client does not restrict incoming connections on other server interfaces.

Checksums detect corruption and inconsistent saved evidence; they are not signatures against a local attacker who can rewrite every artifact. Approval records express local workflow authority, not authenticated identity. Documents are treated as untrusted text; processing does not execute their instructions or open their links.

## Reporting a vulnerability

Report vulnerabilities privately to the repository owner. Do not open a public issue containing sensitive text, credentials or exploit details.
