"""Provider interface for LLM backends."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ModelResponse:
    text: str
    model: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: float | None = None
    latency_s: float | None = None


class ModelProvider(Protocol):
    """A minimal interface that can wrap OpenAI-compatible APIs, LiteLLM, Ollama, etc."""

    model: str

    async def complete(self, prompt: str, *, system: str | None = None) -> ModelResponse:
        """Return a text completion for the prompt."""
        ...
