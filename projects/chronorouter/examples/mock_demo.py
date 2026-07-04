"""Run with: python examples/mock_demo.py"""

from __future__ import annotations

import asyncio

from chronorouter import Budget, ChronoRouter, Freshness, TaskProfile, TemporalSpec
from chronorouter.providers.mock import MockProvider


async def main() -> None:
    router = ChronoRouter(
        cheap_provider=MockProvider(model="local-small", role="cheap"),
        strong_provider=MockProvider(model="frontier-judge", role="judge"),
    )

    profile = TaskProfile(
        prompt="Design a cost-aware LLM router for agentic workflows.",
        task_type="architecture",
        temporal=TemporalSpec(deadline_s=60, freshness=Freshness.STATIC, validity_ttl_s=30 * 24 * 3600),
        budget=Budget(max_parallel_calls=3),
    )
    result = await router.solve(profile)
    print(result.answer)
    print("\nAudit:", result.audit)


if __name__ == "__main__":
    asyncio.run(main())
