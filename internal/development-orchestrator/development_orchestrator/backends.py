"""Live Agents SDK backend and explicit deterministic offline backend."""

from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from typing import Optional

from .schemas import (
    AgentModelConfiguration,
    AgentResult,
    ContextBundle,
    ResearchReport,
    ReviewOutcome,
    ReviewReport,
    UsageRecord,
    WorkRequest,
)
from .model_configuration import (
    ModelConfigurationError,
    V1_OFFLINE_MODEL_CONFIGURATION,
    require_supported_live_configuration,
)


class BackendConfigurationError(RuntimeError):
    pass


class AgentBackend(ABC):
    model_configuration: AgentModelConfiguration

    @abstractmethod
    def research(
        self,
        request: WorkRequest,
        context: ContextBundle,
        revision_feedback: Optional[list[str]] = None,
    ) -> AgentResult:
        raise NotImplementedError

    @abstractmethod
    def review(
        self,
        request: WorkRequest,
        context: ContextBundle,
        research: ResearchReport,
    ) -> AgentResult:
        raise NotImplementedError


class OfflineContractBackend(AgentBackend):
    """Deterministic non-model backend for contract tests and local evals."""

    def __init__(
        self,
        review_outcomes: Optional[list[ReviewOutcome]] = None,
        force_scope_violation: bool = False,
        force_missing_evidence: bool = False,
        reported_cost_per_call: Optional[float] = None,
    ) -> None:
        self.model_configuration = V1_OFFLINE_MODEL_CONFIGURATION
        self.review_outcomes = list(review_outcomes or [ReviewOutcome.ACCEPT])
        self.force_scope_violation = force_scope_violation
        self.force_missing_evidence = force_missing_evidence
        self.reported_cost_per_call = reported_cost_per_call
        self.review_calls = 0

    def _usage(self) -> UsageRecord:
        return UsageRecord(
            reported_cost=self.reported_cost_per_call,
            cost_status=(
                "synthetic reported cost for offline guard testing"
                if self.reported_cost_per_call is not None
                else "not reliably determined"
            ),
        )

    def research(
        self,
        request: WorkRequest,
        context: ContextBundle,
        revision_feedback: Optional[list[str]] = None,
    ) -> AgentResult:
        evidence = [] if self.force_missing_evidence else context.selected_paths
        findings = [
            "Offline contract analysis completed for the requested scope."
        ]
        if revision_feedback:
            findings.append("Revision feedback was incorporated into the contract result.")
        report = ResearchReport(
            summary="Offline contract result; no model or API call occurred.",
            confirmed_findings=findings,
            open_questions=(
                ["No repository evidence was selected."] if not evidence else []
            ),
            risks=(
                ["Result requires evidence review."] if not evidence else []
            ),
            evidence_paths=evidence,
            unsupported_claims=(
                ["Evidence unavailable in the supplied context."]
                if self.force_missing_evidence
                else []
            ),
            scope_compliant=not self.force_scope_violation,
            customer_facing_summary=(
                "The requested research was reviewed without exposing internal complexity."
            ),
        )
        return AgentResult(output=report.model_dump(mode="json"), usage=self._usage())

    def review(
        self,
        request: WorkRequest,
        context: ContextBundle,
        research: ResearchReport,
    ) -> AgentResult:
        outcome = self.review_outcomes[
            min(self.review_calls, len(self.review_outcomes) - 1)
        ]
        self.review_calls += 1
        evidence_based = bool(research.evidence_paths) and not research.unsupported_claims
        scope_respected = research.scope_compliant
        if not scope_respected or not evidence_based:
            outcome = ReviewOutcome.ESCALATE if outcome is ReviewOutcome.ACCEPT else outcome
        report = ReviewReport(
            outcome=outcome,
            answered_goal=True,
            evidence_based=evidence_based,
            scope_respected=scope_respected,
            facts_separated_from_uncertainty=True,
            complexity_appropriate=True,
            product_principle_respected=True,
            founder_decision_required=outcome is ReviewOutcome.ESCALATE,
            feedback=(
                ["Revise within the original scope."]
                if outcome is ReviewOutcome.REVISE
                else []
            ),
        )
        return AgentResult(output=report.model_dump(mode="json"), usage=self._usage())


class OpenAIAgentsBackend(AgentBackend):
    """Current OpenAI Agents SDK path; loaded only for explicit live runs."""

    RESEARCH_INSTRUCTIONS = """You are the ZONVAA internal Research Agent.
Use only the supplied task and repository context. Separate facts, interpretations,
and uncertainty. Never claim architecture, governance, product approval, commit, or
push authority. Keep customer-facing language simple. Return the required schema."""

    REVIEW_INSTRUCTIONS = """You are the ZONVAA internal Review Agent.
Review the research against the original task and supplied evidence. Check scope,
unsupported claims, usefulness, and the principle 'Innen maximal präzise. Außen
maximal verständlich.' Return ACCEPT, REVISE, or ESCALATE. Do not create decisions,
architecture, governance, commits, pushes, or additional agent roles."""

    def __init__(
        self,
        model_configuration: Optional[AgentModelConfiguration] = None,
        max_turns: int = 4,
    ) -> None:
        try:
            self.model_configuration = require_supported_live_configuration(
                model_configuration
            )
        except ModelConfigurationError as error:
            raise BackendConfigurationError(str(error)) from error
        if not os.environ.get("OPENAI_API_KEY"):
            raise BackendConfigurationError(
                "OPENAI_API_KEY is required for a live Agents SDK run"
            )
        try:
            from agents import Agent, RunConfig, Runner
        except (ImportError, AttributeError) as error:
            raise BackendConfigurationError(
                "openai-agents is unavailable or shadowed; run from the tool directory "
                "with its own installed dependencies"
            ) from error
        self.Agent = Agent
        self.Runner = Runner
        self.RunConfig = RunConfig
        self.max_turns = max_turns

    @staticmethod
    def _usage(result: object) -> UsageRecord:
        usage = result.context_wrapper.usage
        return UsageRecord(
            requests=int(getattr(usage, "requests", 0) or 0),
            input_tokens=int(getattr(usage, "input_tokens", 0) or 0),
            output_tokens=int(getattr(usage, "output_tokens", 0) or 0),
            total_tokens=int(getattr(usage, "total_tokens", 0) or 0),
            cost_status="not reliably determined",
        )

    def _run(
        self,
        name: str,
        instructions: str,
        output_type: type,
        payload: dict,
        model: str,
    ) -> AgentResult:
        agent = self.Agent(
            name=name,
            instructions=instructions,
            output_type=output_type,
            model=model,
        )
        result = self.Runner.run_sync(
            agent,
            json.dumps(payload, ensure_ascii=False),
            max_turns=self.max_turns,
            run_config=self.RunConfig(trace_include_sensitive_data=False),
        )
        output = result.final_output
        if not isinstance(output, output_type):
            output = output_type.model_validate(output)
        return AgentResult(
            output=output.model_dump(mode="json"),
            usage=self._usage(result),
            trace_id=None,
        )

    def research(
        self,
        request: WorkRequest,
        context: ContextBundle,
        revision_feedback: Optional[list[str]] = None,
    ) -> AgentResult:
        return self._run(
            "ZONVAA Research Agent",
            self.RESEARCH_INSTRUCTIONS,
            ResearchReport,
            {
                "request": request.model_dump(mode="json"),
                "context": context.model_dump(mode="json"),
                "revision_feedback": revision_feedback or [],
            },
            self.model_configuration.research_model,
        )

    def review(
        self,
        request: WorkRequest,
        context: ContextBundle,
        research: ResearchReport,
    ) -> AgentResult:
        return self._run(
            "ZONVAA Review Agent",
            self.REVIEW_INSTRUCTIONS,
            ReviewReport,
            {
                "request": request.model_dump(mode="json"),
                "context_paths": context.selected_paths,
                "research": research.model_dump(mode="json"),
            },
            self.model_configuration.review_model,
        )
