from typing import Any, Iterable, Optional, Union

from brain.context_analyzer import ContextAnalyzer
from brain.context_collector import ContextCollector
from builder.orchestrator import Orchestrator
from builder.preflight import MissionContext, PreflightService
from builder.runtime import RuntimeManager
from execution.models import DocumentArtifact
from goal.engine import GoalEngine
from goal.models import Goal
from goal.why_assessment import WhyAssessment
from knowledge.memory import MemoryType


class GoalApplicationService:
    """Composes the existing goal-aware application flow."""

    def __init__(
        self,
        runtime: RuntimeManager,
        mission_context: Optional[MissionContext] = None,
        goal_engine: Optional[GoalEngine] = None,
        context_collector: Optional[ContextCollector] = None,
        context_analyzer: Optional[ContextAnalyzer] = None,
        orchestrator: Optional[Orchestrator] = None,
    ) -> None:
        if runtime.identity_context is None or runtime.goal_engine is None:
            raise RuntimeError("GoalApplicationService requires a booted runtime")
        self.preflight = PreflightService(runtime)
        self.preflight.validate(mission_context)

        self.runtime = runtime
        self.mission_context = mission_context
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
        document_artifacts: Optional[Iterable[DocumentArtifact]] = None,
        apply: bool = False,
    ) -> dict[str, Any]:
        if not isinstance(goal, Goal):
            raise TypeError("GoalApplicationService requires a Goal instance")
        self.preflight.validate(self.mission_context)

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

        orchestration = {
            "goal": goal.title,
            "context": technical_context,
            "goal_context": goal_context,
            "workflow_context": self.mission_context.for_workflow(),
            "identity_context": self.runtime.identity_context,
            "why_assessment": why_assessment,
        }
        if document_artifacts is not None or apply:
            orchestration.update(
                {
                    "document_artifacts": document_artifacts,
                    "apply": apply,
                }
            )
        return self.orchestrator.run(**orchestration)
