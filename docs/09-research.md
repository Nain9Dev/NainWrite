# Technical Research

Verified on 2026-09-03 against primary project documentation.

## Qwen3.8

The official Qwen repository and model card confirm the Qwen3.8 family and the Apache-2.0 Qwen3.8-27B model. The installed IQ4_XS package is the current measured writer on the target 16 GB GPU. This is a hardware-specific feasibility decision, not a comparative ranking or a claim that one model is best for every Spanish task.

- https://github.com/QwenLM/Qwen3.8
- https://huggingface.co/Qwen/Qwen3.8-27B

## Ollama

Ollama supports JSON Schema structured output and recommends grounding the schema in the prompt. The current client already uses a schema, zero temperature and loopback HTTP.

- https://github.com/ollama/ollama/blob/main/docs/capabilities/structured-outputs.mdx
- https://github.com/ollama/ollama/blob/main/docs/openapi.yaml

## LanguageTool

LanguageTool is an LGPL open-source proofreading system with Spanish support and an embedded local HTTP server. Its local open-source server does not include the cloud-only AI rules. It is suitable as an independent spelling, grammar and typographical signal, but not as a semantic judge.

- https://github.com/languagetool-org/languagetool
- https://github.com/languagetool-org/languagetool-org.github.io/blob/master/http-server.md
- https://github.com/languagetool-org/languagetool-org.github.io/blob/master/roadmap.md

## Vale

Vale is a fast, extensible prose linter. Its value depends on a curated style package. The reviewed official and community packages primarily implement English-language corporate guides, so Vale is not adopted as an `es-ES` grammar gate in this slice.

- https://github.com/vale-cli/vale
- https://docs.vale.sh/

## Decision summary

- Keep Qwen3.8 as writer.
- Keep Ollama structured output.
- Add local LanguageTool for independent proofreading.
- Evaluate the already installed Gemma model only as a second conservative auditor.
- Do not add a transformer/NLI stack until the mutation benchmark proves that the lighter controls are insufficient.
