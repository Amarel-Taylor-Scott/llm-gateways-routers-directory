"""Core data types for ChronoRouter."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Freshness(str, Enum):
    """How time-sensitive the answer is."""

    STATIC = "static"      # math, stable code, evergreen concepts
    RECENT = "recent"      # should prefer recent evidence, but not live
    CURRENT = "current"    # must retrieve/check current state before answering
    LIVE = "live"          # low-latency/current-state action, e.g. trading/support/ops


class Risk(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ExecutionMode(str, Enum):
    DIRECT = "direct"
    CASCADE = "cascade"
    GRAPH_JUDGE = "graph_judge"
    EVIDENCE_FIRST = "evidence_first"


@dataclass(frozen=True)
class TemporalSpec:
    """Temporal constraints for a request.

    deadline_s: User-visible latency/deadline budget. None means no explicit deadline.
    freshness: Whether the answer depends on current/recent facts.
    validity_ttl_s: How long the returned answer should be considered valid.
    event_time: Optional ISO-8601 time/date the prompt refers to.
    """

    deadline_s: float | None = None
    freshness: Freshness = Freshness.STATIC
    validity_ttl_s: int | None = None
    event_time: str | None = None


@dataclass(frozen=True)
class Budget:
    """Request-level budget constraints."""

    max_cost_usd: float | None = None
    max_tokens: int | None = None
    max_parallel_calls: int = 4


@dataclass(frozen=True)
class TaskProfile:
    """Normalized task description consumed by policies and routers."""

    prompt: str
    task_type: str = "general"
    temporal: TemporalSpec = field(default_factory=TemporalSpec)
    budget: Budget = field(default_factory=Budget)
    risk: Risk = Risk.LOW
    requires_tools: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RouteDecision:
    """Policy output describing how a request should be handled."""

    mode: ExecutionMode
    primary_model: str
    judge_model: str | None = None
    reason: str = ""
    graph_width: int = 3
    graph_depth: int = 1
    require_audit: bool = True


@dataclass(frozen=True)
class RouteAudit:
    """Human-readable explanation of routing behavior."""

    decision: RouteDecision
    estimated_cost_usd: float | None = None
    latency_s: float | None = None
    selected_candidate_id: str | None = None
    notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RouteResult:
    """Final router result."""

    answer: str
    audit: RouteAudit
    candidates: list[dict[str, Any]] = field(default_factory=list)
