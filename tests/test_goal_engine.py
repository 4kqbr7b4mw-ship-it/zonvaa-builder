from datetime import datetime, timezone

import pytest

from builder.runtime import RuntimeManager
from goal.engine import GoalEngine
from goal.models import Goal, GoalPriority, GoalStatus
from knowledge.memory import MemoryType


def create_goal(goal_id="goal-0010", title="Goal Engine foundation"):
    return Goal(
        id=goal_id,
        title=title,
        description="Create structured goal context.",
        project="zonvaa-builder",
        priority="high",
        status="active",
        owner="architect",
        created_at=datetime(2026, 7, 21, tzinfo=timezone.utc),
    )


def test_goal_creation():
    goal = create_goal()

    assert goal.project == "zonvaa-builder"
    assert goal.priority is GoalPriority.HIGH
    assert goal.status is GoalStatus.ACTIVE


def test_goal_context_contains_runtime_inputs():
    goal = create_goal()
    context = GoalEngine().create_context(
        goal=goal,
        role="architect",
        memory_types=["project_memory", "knowledge_memory"],
        constitution_rules=["Follow the WHY"],
        verified_facts={"tests": "passing"},
        project_state={"git_clean": True},
    )

    assert context.goal is goal
    assert context.role == "architect"
    assert context.constitution_rules == ("Follow the WHY",)
    assert context.verified_facts == {"tests": "passing"}
    assert context.project_state == {"git_clean": True}


def test_goal_context_classifies_memory_types():
    context = GoalEngine().create_context(
        goal=create_goal(),
        role="architect",
        memory_types=["working_memory", MemoryType.HERITAGE],
        constitution_rules=[],
        verified_facts={},
        project_state={},
    )

    assert context.memory_types == (
        MemoryType.WORKING,
        MemoryType.HERITAGE,
    )


def test_goal_context_rejects_unknown_memory_type():
    with pytest.raises(ValueError, match="unknown memory type"):
        GoalEngine().create_context(
            goal=create_goal(),
            role="architect",
            memory_types=["temporary_memory"],
            constitution_rules=[],
            verified_facts={},
            project_state={},
        )


def test_goal_context_preserves_goal_fields_unchanged():
    goal = create_goal()

    context = GoalEngine().create_context(
        goal=goal,
        role="architect",
        memory_types=["project_memory"],
        constitution_rules=[],
        verified_facts={},
        project_state={},
    )

    assert context.goal is goal
    assert context.goal == goal


def test_different_goals_create_different_goal_contexts():
    first_goal = create_goal("goal-first", "First goal")
    second_goal = create_goal("goal-second", "Second goal")
    engine = GoalEngine()
    context_data = {
        "role": "architect",
        "memory_types": ["project_memory"],
        "constitution_rules": [],
        "verified_facts": {},
        "project_state": {},
    }

    first_context = engine.create_context(goal=first_goal, **context_data)
    second_context = engine.create_context(goal=second_goal, **context_data)

    assert first_context.goal is first_goal
    assert second_context.goal is second_goal
    assert first_context != second_context


def test_goal_engine_requires_goal():
    with pytest.raises(TypeError):
        GoalEngine().create_context(
            role="architect",
            memory_types=["project_memory"],
            constitution_rules=[],
            verified_facts={},
            project_state={},
        )


@pytest.mark.parametrize("invalid_goal", [None, "placeholder", {}])
def test_goal_engine_rejects_non_goal_values(invalid_goal):
    with pytest.raises(TypeError, match="Goal instance"):
        GoalEngine().create_context(
            goal=invalid_goal,
            role="architect",
            memory_types=["project_memory"],
            constitution_rules=[],
            verified_facts={},
            project_state={},
        )


def test_runtime_loads_goal_engine():
    runtime = RuntimeManager().boot()

    assert isinstance(runtime.goal_engine, GoalEngine)
