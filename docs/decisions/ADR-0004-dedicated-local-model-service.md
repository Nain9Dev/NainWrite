# ADR-0004: Dedicated Local Model Service

Status: Proposed

## Context

Aitor authorised NainWrite isolation on 2026-09-09 while preserving other projects.
The existing desktop-owned Ollama listener was bound to `::11434`. A client using
loopback did not restrict that server's other interfaces. Changing or restarting
the shared service could affect unrelated consumers.

## Proposed decision

Use a dedicated Ollama child process on `127.0.0.1:11436` with cloud features
disabled, reusing installed model storage. Default NainWrite clients target this
endpoint without fallback. Verify listener ownership and cloud-disabled startup.
Refuse occupied ports rather than taking over a process. Leave shared listeners,
global environment, firewall and hardware configuration unchanged.

## Consequences

- Service configuration is scoped and startup is reversible without changing the shared server.
- A second process can compete for GPU memory once models load; resource scheduling remains future work. Verification did not load any model.
- Installed models are shared storage, not a separate security principal or immutable model store. Existing digest checks remain required.
- Old job configuration identities may prevent resumption on the new endpoint. No checkpoint migration is implied.
- Loopback is not authentication against other local processes. Disabling cloud features does not prove complete offline operation or OS-level egress denial.
- Automatic startup and full dependency recovery remain unimplemented.

## Evidence and approval

The authorised bounded slice and verification are recorded in specification 009.
Official [Ollama configuration guidance](https://docs.ollama.com/faq) was checked
on 2026-09-09. The tested binary reported 0.33.3 and a valid Windows signature.

`[H]` Only Aitor may change this ADR from Proposed to Accepted. Operational
authorisation for this slice is not silently treated as ratification of this ADR.
