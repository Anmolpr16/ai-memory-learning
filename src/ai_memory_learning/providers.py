from __future__ import annotations

import json
import os
from dataclasses import dataclass
from urllib.request import Request, urlopen
from typing import Protocol


class ModelProvider(Protocol):
    name: str

    def generate(self, prompt: str, *, system: str | None = None) -> str: ...


@dataclass(frozen=True)
class OpenAICompatibleProvider:
    """Minimal dependency-free adapter for OpenAI-compatible chat endpoints."""

    base_url: str
    model: str
    api_key: str | None = None
    timeout: float = 60.0
    name: str = "openai-compatible"

    def generate(self, prompt: str, *, system: str | None = None) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        body = json.dumps({"model": self.model, "messages": messages}).encode()
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        url = self.base_url.rstrip("/") + "/chat/completions"
        req = Request(url, data=body, headers=headers, method="POST")
        with urlopen(req, timeout=self.timeout) as response:
            data = json.load(response)
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError("provider response did not contain chat completion content") from exc


def provider_from_env() -> OpenAICompatibleProvider:
    """Build the adapter from AI_MEMORY_BASE_URL / AI_MEMORY_MODEL / AI_MEMORY_API_KEY."""
    base_url = os.environ.get("AI_MEMORY_BASE_URL")
    model = os.environ.get("AI_MEMORY_MODEL")
    if not base_url or not model:
        raise ValueError("AI_MEMORY_BASE_URL and AI_MEMORY_MODEL are required")
    return OpenAICompatibleProvider(base_url, model, os.environ.get("AI_MEMORY_API_KEY"))
