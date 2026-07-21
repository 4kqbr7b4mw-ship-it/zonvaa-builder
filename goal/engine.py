from typing import Any, Dict, Iterable, Union

from goal.models import GoalContext
from knowledge.memory import MemoryType


class GoalEngine:
    """Builds validated goal context without making a decision."""

    def create_context(
        self,
        role: str,
        memory_types: Iterable[Union[MemoryType, str]],
        constitution_rules: Iterable[str],
        verified_facts: Dict[str, Any],
        project_state: Dict[str, Any],
    ) -> GoalContext:
        if not role.strip():
            raise ValueError("Goal context role must not be empty")

        try:
            classified_memory = tuple(
                MemoryType(memory_type) for memory_type in memory_types
            )
        except ValueError as exc:
            raise ValueError("Goal context contains an unknown memory type") from exc

        if not classified_memory:
            raise ValueError("Goal context requires at least one memory type")

        rules = tuple(rule for rule in constitution_rules if rule.strip())

        return GoalContext(
            role=role,
            memory_types=classified_memory,
            constitution_rules=rules,
            verified_facts=dict(verified_facts),
            project_state=dict(project_state),
        )
