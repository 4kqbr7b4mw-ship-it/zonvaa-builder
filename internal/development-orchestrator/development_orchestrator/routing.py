"""Deterministic v1 routing; no dynamic agent creation."""

from __future__ import annotations

from .policies import (
    AGENT_SEQUENCE,
    EXPECTED_ARTIFACTS,
    requested_forbidden_git_action,
    stop_conditions,
)
from .schemas import AgentModelConfiguration, RunPlan, WorkRequest


def build_plan(
    run_id: str,
    request: WorkRequest,
    model_configuration: AgentModelConfiguration,
) -> RunPlan:
    inputs = [request.goal, *request.scope, *request.approval_constraints]
    forbidden_git = requested_forbidden_git_action(inputs)
    return RunPlan(
        run_id=run_id,
        goal=request.goal,
        agent_sequence=AGENT_SEQUENCE,
        model_configuration=model_configuration,
        context_sources=request.allowed_context,
        stop_conditions=stop_conditions(),
        human_approval_required=forbidden_git,
        repository_write_required=True,
        max_iterations=request.max_iterations,
        max_cost=request.max_cost,
        expected_artifacts=EXPECTED_ARTIFACTS,
    )
