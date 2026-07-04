# Roadmap

## v0.1 Transparent MVP

- Rule-based temporal policy.
- Provider protocol.
- Mock providers.
- OpenAI-compatible provider.
- Bounded solution graph expansion.
- Strong-model judge prompt.
- Route audit objects.
- Tests and CI.

## v0.2 Provider integrations

- LiteLLM proxy examples.
- Ollama/vLLM examples.
- Provider pricing and cost estimates.
- Configurable model pools.

## v0.3 Evaluation harness

- Compare cheap-only, strong-only, cascade, and graph-judge.
- Track cost, latency, quality, escalation rate, and freshness failures.
- Add coding-agent benchmark tasks.
- Add stale-information test cases.

## v0.4 Learned routing

- Train difficulty and uncertainty classifiers from telemetry.
- Add calibrated escalation thresholds.
- Add budget-aware graph width/depth selection.
- Add bandit policy support.

## v0.5 Agent framework adapters

- LangGraph node wrapper.
- DSPy module wrapper.
- CLI and YAML config.
- OpenAI-compatible service endpoint.
