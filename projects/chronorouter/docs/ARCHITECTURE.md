# Architecture

ChronoRouter is a policy and orchestration layer for LLM development and agentic workflows. It does not try to replace provider gateways such as LiteLLM or OpenRouter. Instead, it decides how a task should be executed before provider calls are made.

## Request lifecycle

```text
TaskProfile
  -> TemporalPolicy.choose()
  -> ExecutionMode
  -> Provider calls / graph expansion / evidence checks
  -> Logic audit
  -> RouteResult
```

## TemporalSpec

`TemporalSpec` captures time-sensitive properties that normal model routers often ignore:

- `deadline_s`: user-visible latency budget.
- `freshness`: static, recent, current, or live.
- `validity_ttl_s`: how long the answer should remain valid.
- `event_time`: optional date/time referenced by the task.

## Execution modes

### DIRECT

Used when the deadline is tight or risk is high. The router avoids multi-call exploration.

### CASCADE

Used for moderate deadlines. The cheap model answers first, a deterministic audit scores the result, and the strong model is called only if the cheap response is weak.

### GRAPH_JUDGE

Used for loose deadlines or complex work. A cheap/local model expands a bounded set of candidate solution paths. Deterministic checks score each candidate. A stronger model receives compressed candidate summaries and audit details, then selects or synthesizes the final answer.

### EVIDENCE_FIRST

Used for current/live tasks or workflows requiring tools. The MVP contains a placeholder; production integrations should connect retrieval, web search, database reads, or tool calls before generation.

## Why graph + judge can save cost

Exploration is token-heavy and often benefits from breadth. Judging is comparatively compact: the stronger model only needs summaries, evidence, audit scores, and candidate tradeoffs. ChronoRouter makes that separation explicit.

## Non-goals

- Replacing provider gateways.
- Claiming exhaustive search over all possible solutions.
- Hiding route decisions from developers.
- Depending on one LLM provider.
