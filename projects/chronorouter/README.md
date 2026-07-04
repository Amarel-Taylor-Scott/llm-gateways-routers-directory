# ChronoRouter

Temporal-demand-aware model routing and graph-of-solutions orchestration for LLM and agentic workflows.

ChronoRouter is a routing layer that decides not only **which model** to call, but also **when to spend more compute**. It treats time as a first-class constraint: freshness, latency deadlines, answer validity, escalation timing, and long-running workflow checkpoints.

## Core thesis

Many LLM tasks do not need a frontier model to do all of the work. A cheaper/local model can cheaply expand a bounded graph of candidate solution paths, while a stronger model can judge compressed candidates, perform a logic audit, and select or synthesize the best final answer.

ChronoRouter is designed for this pattern:

```text
request -> temporal profile -> policy -> cheap graph expansion -> deterministic audits -> strong judge -> answer + route audit
```

## What makes this different from a normal model router?

Traditional routing tends to optimize across cost, latency, quality, fallback, or provider availability. ChronoRouter adds temporal dimensions:

- Is the answer time-sensitive or evergreen?
- Does the request require current facts, live tools, or source freshness?
- How long is the user willing to wait?
- How long should the answer remain valid?
- Should the agent escalate early, late, or only after a confidence check?
- Should the router generate many cheap candidate plans or route directly?

## MVP capabilities

- Rule-based temporal policy
- Direct routing for tight-deadline tasks
- Evidence-first placeholder for current/live tasks
- Cheap-first cascade for moderate deadlines
- Cheap graph-of-solutions expansion plus strong-model judge for loose deadlines
- Provider interface for local models, OpenAI-compatible APIs, LiteLLM proxy, OpenRouter, vLLM, Ollama, etc.
- Deterministic logic-audit scoring hooks
- SQLite telemetry sink
- Mock providers and tests

## Install locally

```bash
git clone <your-repo-url>
cd chronorouter
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
python examples/mock_demo.py
```

## Basic usage

```python
import asyncio
from chronorouter import Budget, ChronoRouter, Freshness, TaskProfile, TemporalSpec
from chronorouter.providers.mock import MockProvider

async def main():
    router = ChronoRouter(
        cheap_provider=MockProvider(model="local-small", role="cheap"),
        strong_provider=MockProvider(model="frontier-judge", role="judge"),
    )

    result = await router.solve(
        TaskProfile(
            prompt="Design a cost-aware LLM router for agentic workflows.",
            task_type="architecture",
            temporal=TemporalSpec(
                deadline_s=60,
                freshness=Freshness.STATIC,
                validity_ttl_s=30 * 24 * 3600,
            ),
            budget=Budget(max_parallel_calls=3),
        )
    )

    print(result.answer)
    print(result.audit)

asyncio.run(main())
```

## Policy sketch

```python
if high_risk:
    route_to_strong_model_with_audit()
elif freshness in {CURRENT, LIVE} or requires_tools:
    retrieve_or_validate_evidence_first()
elif deadline_s <= fast_deadline_s:
    route_directly_to_fast_model()
elif deadline_s is None or deadline_s >= graph_min_deadline_s:
    cheap_model_expands_solution_graph()
    strong_model_judges_compressed_candidates()
else:
    try_cheap_model_then_escalate_if_audit_low()
```

A future learned policy can optimize this utility:

```text
U(route | request, time) = expected_quality
                         - cost_weight * expected_cost
                         - latency_weight * expected_latency
                         - staleness_penalty
                         - risk_penalty
```

## Recommended roadmap

### 0.1 — Transparent MVP

- Rule-based temporal router
- Provider protocol
- Graph expansion and judge mode
- Route audit object
- Mock providers, examples, tests

### 0.2 — Real provider integrations

- LiteLLM proxy adapter
- OpenAI-compatible adapter examples
- Ollama/vLLM local examples
- Provider pricing table interface
- Cost and latency estimates in audits

### 0.3 — Evaluations

- Compare cheap-only, strong-only, cascade, and graph-judge modes
- Track quality, latency, cost, escalation rate, and staleness failures
- Add coding benchmark with unit tests
- Add research benchmark with source freshness checks

### 0.4 — Learned policies

- Train a difficulty/uncertainty router from telemetry
- Add calibrated escalation thresholds
- Add multi-armed bandit policy for model pools
- Add budget-aware graph width/depth selection

### 0.5 — Agent framework adapters

- LangGraph node wrapper
- DSPy module wrapper
- OpenAI-compatible server endpoint
- CLI and YAML policy config

## Design warning

Do not promise to generate “all possible solutions.” The practical target is a **bounded, diverse, auditable solution graph**. Exhaustiveness should be a configurable aspiration, not a claim.

## License

Apache-2.0
