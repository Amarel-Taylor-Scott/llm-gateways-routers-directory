"""Simple deterministic candidate audit helpers.

These are intentionally lightweight. Real deployments should replace or extend them with
unit tests, retrieval checks, policy checks, static analyzers, or human review.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AuditScore:
    score: float
    notes: list[str]


def audit_candidate(text: str) -> AuditScore:
    score = 0.5
    notes: list[str] = []
    lowered = text.lower()

    for keyword, note in [
        ("assumption", "mentions assumptions"),
        ("validation", "includes validation plan"),
        ("risk", "mentions risks"),
        ("temporal", "mentions temporal/freshness issues"),
        ("cost", "mentions cost"),
        ("latency", "mentions latency"),
    ]:
        if keyword in lowered:
            score += 0.08
            notes.append(note)

    if "all possible" in lowered:
        score -= 0.15
        notes.append("overclaims exhaustive coverage")

    return AuditScore(score=max(0.0, min(1.0, score)), notes=notes)
