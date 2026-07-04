"""Main ChronoRouter orchestration layer."""

from __future__ import annotations

import re
import time

from .evaluators.logic_audit import audit_candidate
from .graph import GraphExplorer, _temporal_summary
from .policies import TemporalPolicy
from .prompts import JUDGE_SYSTEM, judge_prompt
from .providers.base import ModelProvider
from .types import ExecutionMode, RouteAudit, RouteResult, TaskProfile


class ChronoRouter:
    """Temporal-demand-aware model router.

    The MVP supports:
    - direct calls for tight deadlines/high risk
    - cheap-first cascade for medium deadlines
    - cheap graph-of-solutions + strong judge for loose deadlines
    - evidence-first placeholder for current/fresh tasks
    """

    def __init__(
        self,
        *,
        cheap_provider: ModelProvider,
        strong_provider: ModelProvider,
        policy: TemporalPolicy | None = None,
    ) -> None:
        self.cheap_provider = cheap_provider
        self.strong_provider = strong_provider
        self.policy = policy or TemporalPolicy(
            cheap_model=cheap_provider.model,
            strong_model=strong_provider.model,
        )
        self.explorer = GraphExplorer(cheap_provider)

    async def solve(self, profile: TaskProfile) -> RouteResult:
        start = time.perf_counter()
        decision = self.policy.choose(profile)
        notes = [decision.reason]

        if decision.mode is ExecutionMode.DIRECT:
            provider = (
                self.strong_provider
                if decision.primary_model == self.strong_provider.model
                else self.cheap_provider
            )
            response = await provider.complete(profile.prompt)
            audit = RouteAudit(decision=decision, latency_s=time.perf_counter() - start, notes=notes)
            return RouteResult(answer=response.text, audit=audit)

        if decision.mode is ExecutionMode.EVIDENCE_FIRST:
            # MVP behavior: return an explicit audit note instead of pretending retrieval happened.
            # Integrate your search/RAG/tool layer here, then pass evidence to the selected provider.
            notes.append("Evidence-first placeholder: connect retrieval/tool checks before generation.")
            response = await self.strong_provider.complete(profile.prompt)
            audit = RouteAudit(decision=decision, latency_s=time.perf_counter() - start, notes=notes)
            return RouteResult(answer=response.text, audit=audit)

        if decision.mode is ExecutionMode.CASCADE:
            first = await self.cheap_provider.complete(profile.prompt)
            cheap_audit = audit_candidate(first.text)
            notes.extend(cheap_audit.notes)
            if cheap_audit.score >= 0.75:
                audit = RouteAudit(decision=decision, latency_s=time.perf_counter() - start, notes=notes)
                return RouteResult(answer=first.text, audit=audit)
            notes.append("Cheap-model audit score below threshold; escalated to strong model.")
            second = await self.strong_provider.complete(profile.prompt)
            audit = RouteAudit(decision=decision, latency_s=time.perf_counter() - start, notes=notes)
            return RouteResult(answer=second.text, audit=audit)

        if decision.mode is ExecutionMode.GRAPH_JUDGE:
            candidates = await self.explorer.expand(
                profile,
                width=decision.graph_width,
                depth=decision.graph_depth,
            )
            blocks = [
                f"Candidate {node.id}\nAudit score: {node.audit_score:.2f}\n"
                f"Audit notes: {', '.join(node.audit_notes) or 'none'}\n{node.text}"
                for node in candidates
            ]
            judge = await self.strong_provider.complete(
                judge_prompt(profile.prompt, blocks, _temporal_summary(profile)),
                system=JUDGE_SYSTEM,
            )
            selected = _extract_selected(judge.text)
            notes.append(f"Generated {len(candidates)} candidate nodes with {self.cheap_provider.model}.")
            notes.append(f"Judged compressed candidates with {self.strong_provider.model}.")
            audit = RouteAudit(
                decision=decision,
                latency_s=time.perf_counter() - start,
                selected_candidate_id=selected,
                notes=notes,
            )
            return RouteResult(
                answer=judge.text,
                audit=audit,
                candidates=[node.to_dict() for node in candidates],
            )

        raise RuntimeError(f"Unhandled execution mode: {decision.mode}")


def _extract_selected(text: str) -> str | None:
    match = re.search(r"Selected:\s*([^\n]+)", text, flags=re.IGNORECASE)
    return match.group(1).strip() if match else None
