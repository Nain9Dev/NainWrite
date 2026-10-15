# ADR-0003: Independent Local Language Quality Gates

Status: Proposed

## Context

The baseline uses Qwen3.8 as both writer and auditor. This can reproduce the same blind spots. It also lacks an independent Spanish grammar checker and accepts a `4/5` naturalness score.

## Proposed decision

- Keep Qwen3.8-27B as the writer.
- Require a second audit from a separately configured installed model after it passes valid and invalid control benchmarks.
- Add the open-source LanguageTool local server as a spelling, grammar and typographical gate.
- Bind LanguageTool to loopback port `8082`; port `8081` is owned by another local project.
- Require `5/5` naturalness and professional-tone scores for automatic acceptance.
- Never apply LanguageTool replacements automatically.
- Permit one constrained writer-generated linguistic repair, followed by every validation gate again.
- Save completed benchmark cases atomically and separate semantic detection from style-only rejection.

## Consequences

- A second model family may reduce shared blind spots, but statistical error independence is not established.
- Obvious linguistic errors gain a non-generative detection path.
- Runtime cost and latency increase.
- False positives can increase `review_required` results but cannot silently alter text.
- LanguageTool open source lacks its cloud-only AI rules and cannot prove naturalness or semantic equivalence.
- Model confidence values are not calibrated probabilities. Benchmark cases remain draft until human approval, including corrected temporal and attribution controls.
- Oversized prompts and length-limited outputs are rejected; whole-document rewriting is not yet supported.

## Alternatives considered

- Vale: strong for custom style guides, but no reviewed first-party `es-ES` grammar package was found.
- Public LanguageTool API: rejected because text would leave the workstation.
- Multilingual transformer/NLI stack: potentially useful but adds large dependencies and another model before a mutation benchmark demonstrates need.
- Same-model audit only: retained as one signal but insufficient as the sole semantic judge.

## Approval

`[H]` Only Aitor may change this ADR from `Proposed` to `Accepted`.
