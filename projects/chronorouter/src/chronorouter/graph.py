"""Bounded solution graph expansion."""

from __future__ import annotations

import asyncio
from dataclasses import asdict, dataclass, field
from typing import Any

from .evaluators.logic_audit import audit_candidate
from .prompts import EXPLORER_SYSTEM, explorer_prompt
from .providers.base import ModelProvider
from .types import TaskProfile


@dataclass(frozen=True)
class SolutionNode:
    id: str
    text: str
    parent_id: str | None = None
    depth: int = 0
    audit_score: float = 0.0
    audit_notes: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class GraphExplorer:
    """Uses a cheaper/local model to generate a bounded graph of candidate solutions."""

    def __init__(self, provider: ModelProvider):
        self.provider = provider

    async def expand(self, profile: TaskProfile, *, width: int = 3, depth: int = 1) -> list[SolutionNode]:
        nodes: list[SolutionNode] = []
        frontier: list[SolutionNode | None] = [None]

        for d in range(depth):
            tasks = []
            for parent in frontier:
                for b in range(width):
                    node_id = f"d{d + 1}.b{b + 1}"
                    prompt = explorer_prompt(
                        profile.prompt,
                        branch_id=b + 1,
                        temporal_summary=_temporal_summary(profile),
                    )
                    tasks.append((node_id, parent, self.provider.complete(prompt, system=EXPLORER_SYSTEM)))

            responses = await asyncio.gather(*(task[2] for task in tasks))
            next_frontier: list[SolutionNode] = []
            for (node_id, parent, _), response in zip(tasks, responses):
                audit = audit_candidate(response.text)
                node = SolutionNode(
                    id=node_id,
                    text=response.text,
                    parent_id=parent.id if parent else None,
                    depth=d + 1,
                    audit_score=audit.score,
                    audit_notes=audit.notes,
                    metadata={"model": response.model},
                )
                nodes.append(node)
                next_frontier.append(node)
            frontier = next_frontier

        return nodes


def _temporal_summary(profile: TaskProfile) -> str:
    spec = profile.temporal
    return (
        f"freshness={spec.freshness.value}; "
        f"deadline_s={spec.deadline_s}; "
        f"validity_ttl_s={spec.validity_ttl_s}; "
        f"event_time={spec.event_time}"
    )
