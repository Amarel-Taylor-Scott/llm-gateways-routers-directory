from chronorouter import Budget, ChronoRouter, Freshness, TaskProfile, TemporalSpec
from chronorouter.providers.mock import MockProvider


async def test_graph_judge_mock_router():
    router = ChronoRouter(
        cheap_provider=MockProvider(model="cheap", role="cheap"),
        strong_provider=MockProvider(model="strong", role="judge"),
    )
    result = await router.solve(
        TaskProfile(
            prompt="Design a router",
            temporal=TemporalSpec(deadline_s=60, freshness=Freshness.STATIC),
            budget=Budget(max_parallel_calls=2),
        )
    )
    assert "Selected:" in result.answer
    assert len(result.candidates) == 2
    assert result.audit.selected_candidate_id is not None
