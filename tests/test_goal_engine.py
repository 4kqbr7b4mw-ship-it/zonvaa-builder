from datetime import datetime, timezone

import pytest

from builder.runtime import RuntimeManager
from goal.engine import GoalEngine
from goal.models import Goal, GoalPriority, GoalStatus
from knowledge.memory import MemoryType


def test_goal_creation():
    goal = Goal(
        id="goal-0010",
        title="Goal Engine foundation",
        description="Create structured goal context.",
        project="zonvaa-builder",
        priority="high",
        status="active",
        owner="architect",
        created_at=datetime(2026, 7, 21, tzinfo=timezone.utc),
    )

    assert goal.project == "zonvaa-builder"
    assert goal.priority is GoalPriority.HIGH
    assert goal.status is GoalStatus.ACTIVE


def test_goal_context_contains_runtime_inputs():
    context = GoalEngine().create_context(
        role="architect",
        memory_types=["project_memory", "knowledge_memory"],
        constitution_rules=["Follow the WHY"],
        verified_facts={"tests": "passing"},
        project_state={"git_clean": True},
    )

    assert context.role == "architect"
    assert context.constitution_rules == ("Follow the WHY",)
    assert context.verified_facts == {"tests": "passing"}
    assert context.project_state == {"git_clean": True}


def test_goal_context_classifies_memory_types():
    context = GoalEngine().create_context(
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
            role="architect",
            memory_types=["temporary_memory"],
            constitution_rules=[],
            verified_facts={},
            project_state={},
        )


def test_runtime_loads_goal_engine():
    runtime = RuntimeManager().boot()

    assert isinstance(runtime.goal_engine, GoalEngine)
