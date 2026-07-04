"""Temporal-demand-aware routing policies."""

from __future__ import annotations

from dataclasses import dataclass

from .types import ExecutionMode, Freshness, Risk, RouteDecision, TaskProfile


@dataclass(frozen=True)
class TemporalPolicy:
    """Rule-based MVP policy.

    Later versions can replace this with a learned router, a bandit, or a calibrated uncertainty
    cascade. The rules are intentionally transparent so users can audit why escalation happened.
    """

    cheap_model: str
    strong_model: str
    fast_deadline_s: float = 8.0
    graph_min_deadline_s: float = 25.0
    default_graph_width: int = 3
    default_graph_depth: int = 1

    def choose(self, profile: TaskProfile) -> RouteDecision:
        spec = profile.temporal

        if profile.risk is Risk.HIGH:
            return RouteDecision(
                mode=ExecutionMode.DIRECT,
                primary_model=self.strong_model,
                judge_model=self.strong_model,
                reason="High-risk task: route directly to stronger model and require audit.",
                graph_width=1,
                graph_depth=1,
                require_audit=True,
            )

        if spec.freshness in {Freshness.CURRENT, Freshness.LIVE} or profile.requires_tools:
            return RouteDecision(
                mode=ExecutionMode.EVIDENCE_FIRST,
                primary_model=self.strong_model if spec.freshness is Freshness.LIVE else self.cheap_model,
                judge_model=self.strong_model,
                reason="Fresh/current task: retrieve or validate evidence before generation.",
                graph_width=1,
                graph_depth=1,
                require_audit=True,
            )

        if spec.deadline_s is not None and spec.deadline_s <= self.fast_deadline_s:
            return RouteDecision(
                mode=ExecutionMode.DIRECT,
                primary_model=self.cheap_model,
                judge_model=None,
                reason="Tight deadline: avoid multi-call graph expansion.",
                graph_width=1,
                graph_depth=1,
                require_audit=False,
            )

        if spec.deadline_s is None or spec.deadline_s >= self.graph_min_deadline_s:
            width = max(1, min(profile.budget.max_parallel_calls, self.default_graph_width))
            return RouteDecision(
                mode=ExecutionMode.GRAPH_JUDGE,
                primary_model=self.cheap_model,
                judge_model=self.strong_model,
                reason="Loose/no deadline: explore candidates cheaply, then escalate summaries to judge.",
                graph_width=width,
                graph_depth=self.default_graph_depth,
                require_audit=True,
            )

        return RouteDecision(
            mode=ExecutionMode.CASCADE,
            primary_model=self.cheap_model,
            judge_model=self.strong_model,
            reason="Moderate deadline: try cheap model first, escalate if audit confidence is low.",
            graph_width=1,
            graph_depth=1,
            require_audit=True,
        )


def utility_score(
    *,
    expected_quality: float,
    expected_cost_usd: float,
    expected_latency_s: float,
    staleness_penalty: float,
    risk_penalty: float,
    cost_weight: float = 1.0,
    latency_weight: float = 0.1,
) -> float:
    """A transparent scalar objective useful for learned or grid-searched policies."""
    return (
        expected_quality
        - cost_weight * expected_cost_usd
        - latency_weight * expected_latency_s
        - staleness_penalty
        - risk_penalty
    )
