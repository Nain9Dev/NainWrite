"""Minimal loopback-only Ollama JSON client."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any
from urllib.parse import urlparse

from .models import GenerationResult
from .local_http import open_local


MAX_PROMPT_BYTES = 12000
MAX_OUTPUT_TOKENS = 2048
DEFAULT_OLLAMA_URL = "http://127.0.0.1:11436"


class OllamaError(RuntimeError):
    """Raised when the local model service returns an invalid response."""


class OllamaClient:
    """Call a local Ollama server without third-party Python dependencies."""

    def __init__(
        self,
        base_url: str = DEFAULT_OLLAMA_URL,
        timeout_seconds: float = 300.0,
    ) -> None:
        parsed = urlparse(base_url)
        if parsed.scheme != "http" or parsed.hostname not in {
            "127.0.0.1",
            "localhost",
            "::1",
        }:
            raise ValueError("Ollama base_url must use HTTP on a loopback host")
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self._digest_cache: dict[str, str] = {}

    def generate_json(
        self,
        *,
        model: str,
        prompt: str,
        schema: dict[str, Any],
        num_predict: int,
    ) -> GenerationResult:
        """Generate and parse one JSON object with deterministic settings."""

        if len(prompt.encode("utf-8")) > MAX_PROMPT_BYTES:
            raise OllamaError(
                f"Prompt exceeds the local safety limit of {MAX_PROMPT_BYTES} UTF-8 bytes; shorten the input without dropping meaning"
            )
        if not 1 <= num_predict <= MAX_OUTPUT_TOKENS:
            raise OllamaError(f"num_predict must be between 1 and {MAX_OUTPUT_TOKENS}")
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "think": False,
            "format": schema,
            "keep_alive": "15m",
            "options": {
                "temperature": 0,
                "seed": 42,
                "num_ctx": 16384,
                "num_predict": num_predict,
            },
        }
        response = self._request("/api/generate", payload)
        if response.get("done_reason") == "length":
            raise OllamaError("Model generation reached its length limit; the candidate is incomplete")
        raw_content = response.get("response")
        if not isinstance(raw_content, str):
            raise OllamaError("Ollama response did not contain a string response")
        try:
            content = json.loads(raw_content)
        except json.JSONDecodeError as error:
            raise OllamaError(f"Model returned invalid JSON: {error}") from error
        if not isinstance(content, dict):
            raise OllamaError("Model JSON response must be an object")

        total_seconds = float(response.get("total_duration", 0)) / 1_000_000_000
        load_seconds = float(response.get("load_duration", 0)) / 1_000_000_000
        output_tokens = int(response.get("eval_count", 0))
        eval_seconds = float(response.get("eval_duration", 0)) / 1_000_000_000
        tokens_per_second = output_tokens / eval_seconds if eval_seconds > 0 else 0.0

        return GenerationResult(
            content=content,
            model=str(response.get("model", model)),
            model_digest=self.get_model_digest(model),
            total_duration_seconds=total_seconds,
            load_duration_seconds=load_seconds,
            prompt_tokens=int(response.get("prompt_eval_count", 0)),
            output_tokens=output_tokens,
            tokens_per_second=tokens_per_second,
        )

    def get_fresh_model_digest(self, model: str) -> str:
        """Resolve current server identity rather than reusing an alias cache."""

        self._digest_cache.pop(model, None)
        return self.get_model_digest(model)

    def get_model_digest(self, model: str) -> str:
        """Resolve and cache the installed model digest."""

        if model in self._digest_cache:
            return self._digest_cache[model]
        response = self._request("/api/tags", None)
        for item in response.get("models", []):
            if item.get("name") == model or item.get("model") == model:
                digest = str(item.get("digest", "unknown"))
                self._digest_cache[model] = digest
                return digest
        self._digest_cache[model] = "unknown"
        return "unknown"

    def _request(self, path: str, payload: dict[str, Any] | None) -> dict[str, Any]:
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=data,
            headers={"Content-Type": "application/json"},
            method="GET" if payload is None else "POST",
        )
        try:
            with open_local(request, timeout=self.timeout_seconds) as response:
                result = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
            raise OllamaError(f"Local Ollama request failed: {error}") from error
        if not isinstance(result, dict):
            raise OllamaError("Ollama returned a non-object response")
        return result
