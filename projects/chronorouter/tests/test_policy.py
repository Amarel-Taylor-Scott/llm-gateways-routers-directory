from chronorouter import Freshness, Risk, TaskProfile, TemporalPolicy, TemporalSpec
from chronorouter.types import ExecutionMode


def test_tight_deadline_routes_direct():
    policy = TemporalPolicy(cheap_model="cheap", strong_model="strong")
    decision = policy.choose(TaskProfile(prompt="x", temporal=TemporalSpec(deadline_s=2)))
    assert decision.mode is ExecutionMode.DIRECT
    assert decision.primary_model == "cheap"


def test_current_routes_evidence_first():
    policy = TemporalPolicy(cheap_model="cheap", strong_model="strong")
    decision = policy.choose(
        TaskProfile(prompt="x", temporal=TemporalSpec(freshness=Freshness.CURRENT))
    )
    assert decision.mode is ExecutionMode.EVIDENCE_FIRST


def test_high_risk_routes_strong():
    policy = TemporalPolicy(cheap_model="cheap", strong_model="strong")
    decision = policy.choose(TaskProfile(prompt="x", risk=Risk.HIGH))
    assert decision.mode is ExecutionMode.DIRECT
    assert decision.primary_model == "strong"


def test_loose_deadline_routes_graph_judge():
    policy = TemporalPolicy(cheap_model="cheap", strong_model="strong")
    decision = policy.choose(TaskProfile(prompt="x", temporal=TemporalSpec(deadline_s=60)))
    assert decision.mode is ExecutionMode.GRAPH_JUDGE
    assert decision.judge_model == "strong"
