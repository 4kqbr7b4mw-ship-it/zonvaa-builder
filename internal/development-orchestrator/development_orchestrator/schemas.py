"""Typed, serializable contracts for the v1 development workflow."""

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ReviewOutcome(str, Enum):
    ACCEPT = "ACCEPT"
    REVISE = "REVISE"
    ESCALATE = "ESCALATE"


class RunStatus(str, Enum):
    COMPLETED = "COMPLETED"
    ESCALATED = "ESCALATED"
    FAILED = "FAILED"
    BLOCKED_CONFIGURATION = "BLOCKED_CONFIGURATION"
    BUDGET_EXCEEDED = "BUDGET_EXCEEDED"


class WorkRequest(FrozenModel):
    goal: str = Field(min_length=1)
    scope: List[str] = Field(min_length=1)
    requested_output: str = Field(min_length=1)
    allowed_context: List[str] = Field(default_factory=list)
    approval_constraints: List[str] = Field(default_factory=list)
    max_cost: Optional[float] = Field(default=None, ge=0)
    max_iterations: int = Field(default=2, ge=1, le=2)

    @field_validator("goal", "requested_output")
    @classmethod
    def no_blank_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value

    @field_validator("scope", "allowed_context", "approval_constraints")
    @classmethod
    def no_blank_items(cls, values: List[str]) -> List[str]:
        if any(not value.strip() for value in values):
            raise ValueError("items must not be blank")
        return values


class ContextDocument(FrozenModel):
    path: str
    content: str
    truncated: bool = False


class ContextBundle(FrozenModel):
    documents: List[ContextDocument] = Field(default_factory=list)
    selected_paths: List[str] = Field(default_factory=list)
    total_characters: int = Field(ge=0)


class AgentModelConfiguration(FrozenModel):
    research_model: str = Field(min_length=1)
    review_model: str = Field(min_length=1)

    @field_validator("research_model", "review_model")
    @classmethod
    def no_blank_model(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("model identifier must not be blank")
        return value


class RunPlan(FrozenModel):
    run_id: str
    goal: str
    agent_sequence: List[str]
    model_configuration: AgentModelConfiguration
    context_sources: List[str]
    stop_conditions: List[str]
    human_approval_required: bool
    repository_write_required: bool
    max_iterations: int
    max_cost: Optional[float]
    expected_artifacts: List[str]


class ResearchReport(FrozenModel):
    summary: str
    confirmed_findings: List[str] = Field(default_factory=list)
    refuted_findings: List[str] = Field(default_factory=list)
    open_questions: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    evidence_paths: List[str] = Field(default_factory=list)
    unsupported_claims: List[str] = Field(default_factory=list)
    scope_compliant: bool = True
    customer_facing_summary: str = ""


class ReviewReport(FrozenModel):
    outcome: ReviewOutcome
    answered_goal: bool
    evidence_based: bool
    scope_respected: bool
    facts_separated_from_uncertainty: bool
    complexity_appropriate: bool
    product_principle_respected: bool
    founder_decision_required: bool
    feedback: List[str] = Field(default_factory=list)


class UsageRecord(FrozenModel):
    requests: int = Field(default=0, ge=0)
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    total_tokens: int = Field(default=0, ge=0)
    reported_cost: Optional[float] = Field(default=None, ge=0)
    cost_status: str = "not reliably determined"


class AgentResult(FrozenModel):
    output: dict
    usage: UsageRecord = Field(default_factory=UsageRecord)
    trace_id: Optional[str] = None


class DecisionBrief(FrozenModel):
    run_id: str
    status: RunStatus
    goal: str
    key_results: List[str]
    confirmed_findings: List[str]
    refuted_findings: List[str]
    open_risks: List[str]
    open_questions: List[str]
    review_outcome: ReviewOutcome
    founder_decision_required: bool
    recommended_next_step: str
    generated_files: List[str]
    usage: UsageRecord
    trace_ids: List[str] = Field(default_factory=list)
    failure_reason: Optional[str] = None
