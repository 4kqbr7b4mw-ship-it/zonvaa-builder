from datetime import datetime, timezone

from brain.decision_engine import DecisionEngine
from goal.engine import GoalEngine
from goal.models import Goal


def test_decision_engine_returns_decision():
    engine = DecisionEngine()

    context = {
        "summary": {
            "git_dirty": False,
        },
        "risks": [],
    }

    decision = engine.decide(
        goal="Decision Engine entwickeln",
        context=context,
    )

    assert decision["goal"] == "Decision Engine entwickeln"
    assert decision["status"] == "approved"
    assert decision["next_action"] == "plan"


def test_decision_engine_blocks_dirty_repository():
    engine = DecisionEngine()

    context = {
        "summary": {
            "git_dirty": True,
        },
        "risks": [
            "Der aktuelle Arbeitsstand ist noch nicht vollständig versioniert."
        ],
    }

    decision = engine.decide(
        goal="Decision Engine entwickeln",
        context=context,
    )

    assert decision["status"] == "blocked"
    assert decision["next_action"] == "clean_repository"
    assert decision["reasons"]


def test_decision_engine_behavior_with_goal_context_remains_unchanged():
    goal = Goal(
        id="goal-decision-context",
        title="Preserve Decision Engine behavior",
        description="Pass structured goal context without assessment.",
        project="zonvaa-builder",
        priority="high",
        status="active",
        owner="architect",
        created_at=datetime(2026, 7, 21, tzinfo=timezone.utc),
    )
    goal_context = GoalEngine().create_context(
        goal=goal,
        role="architect",
        memory_types=["project_memory"],
        constitution_rules=["Follow the WHY"],
        verified_facts={"tests": "passing"},
        project_state={"git_clean": True},
    )

    decision = DecisionEngine().decide(
        goal=goal.title,
        context={"summary": {"git_dirty": False}, "risks": []},
        goal_context=goal_context,
    )

    assert decision == {
        "goal": goal.title,
        "status": "approved",
        "next_action": "plan",
        "reasons": [],
    }
