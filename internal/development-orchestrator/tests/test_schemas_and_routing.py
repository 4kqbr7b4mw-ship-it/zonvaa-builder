from __future__ import annotations

import pytest
from pydantic import ValidationError

from development_orchestrator.routing import build_plan
from development_orchestrator.model_configuration import V1_LIVE_MODEL_CONFIGURATION
from development_orchestrator.schemas import WorkRequest


def request(**changes: object) -> WorkRequest:
    values = {
        "goal": "Review existing research",
        "scope": ["research only"],
        "requested_output": "decision brief",
        "allowed_context": ["README.md"],
        "approval_constraints": ["no commit", "no push"],
    }
    values.update(changes)
    return WorkRequest.model_validate(values)


def test_request_is_frozen_and_rejects_extra_fields() -> None:
    item = request()
    with pytest.raises(ValidationError):
        item.goal = "changed"
    with pytest.raises(ValidationError):
        request(unknown=True)


@pytest.mark.parametrize("value", [0, 3])
def test_iterations_are_closed_to_v1_limit(value: int) -> None:
    with pytest.raises(ValidationError):
        request(max_iterations=value)


def test_empty_scope_and_blank_items_fail_closed() -> None:
    with pytest.raises(ValidationError):
        request(scope=[])
    with pytest.raises(ValidationError):
        request(scope=[""])


def test_plan_uses_only_closed_agent_sequence_and_expected_artifacts() -> None:
    plan = build_plan("run-fixed", request(), V1_LIVE_MODEL_CONFIGURATION)
    assert plan.agent_sequence == ["research_agent", "review_agent"]
    assert plan.model_configuration.research_model == "gpt-4.1"
    assert plan.model_configuration.review_model == "gpt-4.1"
    assert plan.repository_write_required is True
    assert plan.human_approval_required is False
    assert set(plan.expected_artifacts) == {
        "request.json",
        "plan.json",
        "research.md",
        "review.md",
        "handover.md",
        "result.json",
        "usage.json",
    }


@pytest.mark.parametrize("goal", ["Commit the result", "Push this report"])
def test_git_action_request_routes_to_human_approval(goal: str) -> None:
    assert build_plan(
        "run-fixed", request(goal=goal), V1_LIVE_MODEL_CONFIGURATION
    ).human_approval_required is True


def test_negative_git_constraints_are_not_misread_as_requests() -> None:
    plan = build_plan(
        "run-fixed",
        request(approval_constraints=["kein Commit", "no push"]),
        V1_LIVE_MODEL_CONFIGURATION,
    )
    assert plan.human_approval_required is False
