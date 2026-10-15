# ADR-0002: Qwen3.8-27B as the Local Spanish Rewriter

Status: Proposed

## Context

The workstation has an NVIDIA RTX 5080 with 16 GB of VRAM and already contains a 13 GB IQ4_XS quantization of Qwen3.8-27B. A previous live probe produced valid Spanish structured output. The official Q4_K_M package is larger than the available VRAM, while smaller models provide less capacity for nuanced rewriting.

## Proposed decision

- Use `qwen3.8-local-fast2:latest` for the first implementation.
- Pin the observed model digest in every benchmark report.
- Use temperature zero, a fixed seed, structured output and no visible thinking.
- Use a separate audit prompt with the same model plus deterministic invariant validation.
- Keep all processing on the local loopback Ollama endpoint.

## Consequences

- The selected quantization runs on the target GPU without downloading another general model.
- IQ4_XS is an aggressive quantization and may lose subtle linguistic quality compared with higher precision.
- A same-model semantic audit is not independent and can reproduce the writer's blind spots.
- High-impact texts still require human approval.

## Alternatives considered

- Gemma 4 8B: substantially faster in the initial probe, but it introduced a small tense shift and is not the requested Chinese model.
- Official Qwen3.8-27B Q4_K_M: approximately 18 GB and therefore larger than available VRAM.
- Larger Qwen3.8 models: not practical on the available local memory.
- Fine-tuning: premature without an approved gold dataset.

## Approval

`[H]` Only Aitor may change this ADR from `Proposed` to `Accepted`.
