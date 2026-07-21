from typing import Any, Iterable, Optional, Union

from brain.context_analyzer import ContextAnalyzer
from brain.context_collector import ContextCollector
from builder.orchestrator import Orchestrator
from builder.runtime import RuntimeManager
from goal.engine import GoalEngine
from goal.models import Goal
from goal.why_assessment import WhyAssessment
from knowledge.memory import MemoryType


class GoalApplicationService:
    """Composes the existing goal-aware application flow."""

    def __init__(
        self,
        runtime: RuntimeManager,
        goal_engine: Optional[GoalEngine] = None,
        context_collector: Optional[ContextCollector] = None,
        context_analyzer: Optional[ContextAnalyzer] = None,
        orchestrator: Optional[Orchestrator] = None,
    ) -> None:
        if runtime.identity_context is None or runtime.goal_engine is None:
            raise RuntimeError("GoalApplicationService requires a booted runtime")

        self.runtime = runtime
        self.goal_engine = (
            goal_engine if goal_engine is not None else runtime.goal_engine
        )
        self.context_collector = (
            context_collector
            if context_collector is not None
            else ContextCollector(runtime)
        )
        self.context_analyzer = (
            context_analyzer
            if context_analyzer is not None
            else ContextAnalyzer()
        )
        self.orchestrator = (
            orchestrator if orchestrator is not None else Orchestrator()
        )

    def run(
        self,
        goal: Goal,
        role: str,
        memory_types: Iterable[Union[MemoryType, str]],
        constitution_rules: Iterable[str],
        why_assessment: Optional[WhyAssessment] = None,
    ) -> dict[str, Any]:
        if not isinstance(goal, Goal):
            raise TypeError("GoalApplicationService requires a Goal instance")

        project_context = self.context_collector.collect()
        technical_context = self.context_analyzer.analyze(project_context)
        goal_context = self.goal_engine.create_context(
            goal=goal,
            role=role,
            memory_types=memory_types,
            constitution_rules=constitution_rules,
            verified_facts=self.runtime.verified_facts,
            project_state=self.runtime.project_state,
        )

        return self.orchestrator.run(
            goal=goal.title,
            context=technical_context,
            goal_context=goal_context,
            identity_context=self.runtime.identity_context,
            why_assessment=why_assessment,
        )
