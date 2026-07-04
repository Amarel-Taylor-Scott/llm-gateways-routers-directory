# Contributing

ChronoRouter is intentionally small and auditable. Contributions should preserve that bias.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check src tests examples
```

## Design principles

1. Treat temporal demand as a first-class routing signal.
2. Prefer transparent policies before learned policies.
3. Never claim exhaustive search; use bounded, diverse, auditable graph expansion.
4. Escalate compressed evidence, candidates, and audit results instead of raw exploration traces.
5. Make route decisions inspectable and replayable.

## Good first issues

- Add pricing/cost estimators for provider adapters.
- Add an Ollama provider adapter.
- Add a LiteLLM proxy example.
- Add benchmark tasks comparing cheap-only, strong-only, cascade, and graph-judge execution.
- Add freshness-aware evidence validators.
