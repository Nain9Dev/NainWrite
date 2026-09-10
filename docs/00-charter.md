# Project Charter

## Objective

Build a local document rewriting workflow that prioritizes semantic fidelity over stylistic variation, produces reviewed es-ES first, and then en-US and en-GB. Professional publications, commercial proposals and client emails are the priority use cases.

## Current phase

The CLI model runner and revision-gated translation workflow exist, but linguistic acceptance remains open. The completed 2026-09-09 interview defines the broader product in `specs/009-local-product-readiness/spec.md`: PDF/OCR input, PDF/Markdown delivery, local browser review and a background queue are future slices. Only dedicated Ollama isolation is implemented in this slice.

## Success condition

A benchmark version is useful only after its references have been reviewed by Aitor and its structural validation remains green.

## Boundaries

- Local and zero-cost tooling first.
- No confidential client text in the initial benchmark.
- No automatic publication.
- No translation until the Spanish rewriting gate is closed.
