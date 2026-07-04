"""Optional OpenAI-compatible provider.

Works with OpenAI-compatible APIs, local gateways, LiteLLM proxy, OpenRouter, vLLM, etc.
Install with: pip install chronorouter[openai-compatible]
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass

from .base import ModelResponse


@dataclass
class OpenAICompatProvider:
    model: str
    base_url: str
    api_key_env: str = "OPENAI_API_KEY"
    timeout_s: float = 60.0

    async def complete(self, prompt: str, *, system: str | None = None) -> ModelResponse:
        try:
            import httpx
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("Install httpx or chronorouter[openai-compatible].") from exc

        api_key = os.environ.get(self.api_key_env, "")
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        start = time.perf_counter()
        async with httpx.AsyncClient(timeout=self.timeout_s) as client:
            response = await client.post(
                f"{self.base_url.rstrip('/')}/chat/completions",
                headers=headers,
                json={"model": self.model, "messages": messages},
            )
            response.raise_for_status()
            payload = response.json()

        usage = payload.get("usage", {})
        text = payload["choices"][0]["message"]["content"]
        return ModelResponse(
            text=text,
            model=self.model,
            input_tokens=usage.get("prompt_tokens"),
            output_tokens=usage.get("completion_tokens"),
            latency_s=time.perf_counter() - start,
        )
