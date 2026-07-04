"""Minimal OpenAI-compatible provider demo.

Set OPENAI_API_KEY and point base_url at any OpenAI-compatible endpoint:
OpenAI, LiteLLM proxy, OpenRouter, vLLM, Ollama-compatible gateways, etc.
"""

from __future__ import annotations

import asyncio
import os

from chronorouter import ChronoRouter, Freshness, TaskProfile, TemporalSpec
from chronorouter.providers.openai_compat import OpenAICompatProvider


async def main() -> None:
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    cheap_model = os.environ.get("CHRONOROUTER_CHEAP_MODEL", "gpt-4o-mini")
    strong_model = os.environ.get("CHRONOROUTER_STRONG_MODEL", "gpt-4o")

    router = ChronoRouter(
        cheap_provider=OpenAICompatProvider(model=cheap_model, base_url=base_url),
        strong_provider=OpenAICompatProvider(model=strong_model, base_url=base_url),
    )

    result = await router.solve(
        TaskProfile(
            prompt="Design a graph+judge model routing policy for coding agents.",
            temporal=TemporalSpec(deadline_s=60, freshness=Freshness.STATIC),
        )
    )
    print(result.answer)
    print(result.audit)


if __name__ == "__main__":
    asyncio.run(main())
