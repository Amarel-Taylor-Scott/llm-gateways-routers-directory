"""Prompt templates used by the default graph+judge strategy."""

EXPLORER_SYSTEM = """You are a cheap exploration model.
Generate one diverse, testable solution path. Avoid final polish.
Focus on assumptions, dependencies, temporal risks, and failure modes.
"""

JUDGE_SYSTEM = """You are a senior logic auditor and route judge.
Select or synthesize the best candidate using only the candidate summaries and audits.
Prefer candidates that satisfy temporal constraints, have low hidden risk, and expose uncertainty.
Return a concise final answer plus an audit.
"""


def explorer_prompt(user_prompt: str, branch_id: int, temporal_summary: str) -> str:
    return f"""User task:
{user_prompt}

Temporal constraints:
{temporal_summary}

Generate candidate solution path #{branch_id}. Include:
- approach summary
- assumptions
- temporal/freshness risks
- validation plan
- expected cost/latency profile
"""


def judge_prompt(user_prompt: str, candidate_blocks: list[str], temporal_summary: str) -> str:
    joined = "\n\n---\n\n".join(candidate_blocks)
    return f"""User task:
{user_prompt}

Temporal constraints:
{temporal_summary}

Candidates:
{joined}

Choose the best candidate or synthesize a better final plan.
Return:
Selected: <candidate id or synthesis>
Reason: <logic audit>
Answer: <final answer>
"""
