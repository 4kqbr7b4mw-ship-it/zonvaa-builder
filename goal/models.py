from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Tuple, Union

from knowledge.memory import Confidence, MemoryType


class GoalPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class GoalStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class Goal:
    id: str
    title: str
    description: str
    project: str
    priority: Union[GoalPriority, str]
    status: Union[GoalStatus, str]
    owner: str
    created_at: datetime

    def __post_init__(self) -> None:
        for field_name in ("id", "title", "project", "owner"):
            if not getattr(self, field_name).strip():
                raise ValueError("Goal {} must not be empty".format(field_name))

        if self.created_at.tzinfo is None or self.created_at.utcoffset() is None:
            raise ValueError("Goal created_at must include timezone information")

        try:
            priority = GoalPriority(self.priority)
        except ValueError as exc:
            raise ValueError("Unknown goal priority: {}".format(self.priority)) from exc

        try:
            status = GoalStatus(self.status)
        except ValueError as exc:
            raise ValueError("Unknown goal status: {}".format(self.status)) from exc

        object.__setattr__(self, "priority", priority)
        object.__setattr__(self, "status", status)


@dataclass(frozen=True)
class GoalContext:
    goal: Goal
    role: str
    memory_types: Tuple[MemoryType, ...]
    constitution_rules: Tuple[str, ...]
    verified_facts: Dict[str, Any]
    project_state: Dict[str, Any]


@dataclass(frozen=True)
class GoalDecision:
    """Future hand-off result; the Goal Engine does not create decisions yet."""

    goal: Goal
    context: GoalContext
    decision_reason: str
    confidence: Confidence
