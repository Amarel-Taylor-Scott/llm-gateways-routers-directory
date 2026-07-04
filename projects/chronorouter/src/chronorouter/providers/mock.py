"""Mock providers for tests and demos."""

from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass

from .base import ModelResponse


@dataclass
class MockProvider:
    model: str
    role: str = "cheap"
    latency_s: float = 0.01

    async def complete(self, prompt: str, *, system: str | None = None) -> ModelResponse:
        await asyncio.sleep(self.latency_s)
        text = self._generate(prompt, system=system)
        return ModelResponse(text=text, model=self.model, output_tokens=max(1, len(text.split())))

    def _generate(self, prompt: str, *, system: str | None = None) -> str:
        if self.role == "judge":
            ids = re.findall(r"Candidate ([A-Za-z0-9_.-]+)", prompt)
            chosen = ids[0] if ids else "candidate-1"
            return (
                f"Selected: {chosen}\n"
                "Reason: Chosen by mock judge because it was the first candidate with a clear audit.\n"
                "Answer: Use a bounded graph-of-solutions expansion, then judge compressed candidates."
            )
        return (
            "Candidate Plan:\n"
            "1. Generate diverse solution paths with a cheap/local model.\n"
            "2. Score each path with deterministic checks and a logic audit.\n"
            "3. Escalate only summaries and evidence to a stronger judge model."
        )
