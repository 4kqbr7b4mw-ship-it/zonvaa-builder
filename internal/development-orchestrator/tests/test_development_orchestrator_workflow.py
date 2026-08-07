from __future__ import annotations

import json
from pathlib import Path

import pytest

from development_orchestrator.backends import OfflineContractBackend
from development_orchestrator.orchestrator import DevelopmentOrchestrator
from development_orchestrator.schemas import ReviewOutcome, RunStatus, WorkRequest


def request(**changes: object) -> WorkRequest:
    values = {
        "goal": "Review synthetic research",
        "scope": ["research only"],
        "requested_output": "compact decision brief",
        "allowed_context": ["docs/research.md"],
        "approval_constraints": ["no commit", "no push"],
        "max_iterations": 2,
    }
    values.update(changes)
    return WorkRequest.model_validate(values)


def orchestrator(isolated_repository, backend=None) -> DevelopmentOrchestrator:
    repository, tool_root = isolated_repository
    return DevelopmentOrchestrator(
        repository, tool_root, backend or OfflineContractBackend()
    )


def artifacts(isolated_repository, run_id: str) -> set[str]:
    _, tool_root = isolated_repository
    return {
        path.name
        for path in (tool_root / "runs" / run_id).iterdir()
        if path.is_file()
    }


def test_happy_path_persists_compact_complete_run(isolated_repository) -> None:
    result = orchestrator(isolated_repository).run(request())
    assert result.status is RunStatus.COMPLETED
    assert result.review_outcome is ReviewOutcome.ACCEPT
    assert result.founder_decision_required is False
    assert artifacts(isolated_repository, result.run_id) == {
        "request.json",
        "plan.json",
        "research.md",
        "review.md",
        "handover.md",
        "result.json",
        "usage.json",
    }
    _, tool_root = isolated_repository
    stored = json.loads(
        (tool_root / "runs" / result.run_id / "result.json").read_text(encoding="utf-8")
    )
    plan = json.loads(
        (tool_root / "runs" / result.run_id / "plan.json").read_text(encoding="utf-8")
    )
    assert stored["run_id"] == result.run_id
    assert plan["model_configuration"] == {
        "research_model": "offline-contract-v1",
        "review_model": "offline-contract-v1",
    }
    assert "Offline contract result" not in json.dumps(stored["key_results"])


def test_review_can_request_one_revision_then_accept(isolated_repository) -> None:
    backend = OfflineContractBackend(
        review_outcomes=[ReviewOutcome.REVISE, ReviewOutcome.ACCEPT]
    )
    result = orchestrator(isolated_repository, backend).run(request())
    assert result.status is RunStatus.COMPLETED
    assert backend.review_calls == 2
    _, tool_root = isolated_repository
    review = (tool_root / "runs" / result.run_id / "review.md").read_text(encoding="utf-8")
    assert "Cycle 1" in review and "Cycle 2" in review


def test_iteration_exhaustion_escalates_without_loop(isolated_repository) -> None:
    backend = OfflineContractBackend(review_outcomes=[ReviewOutcome.REVISE])
    result = orchestrator(isolated_repository, backend).run(request())
    assert result.status is RunStatus.ESCALATED
    assert result.review_outcome is ReviewOutcome.ESCALATE
    assert result.failure_reason == "maximum review iterations reached"
    assert backend.review_calls == 2


@pytest.mark.parametrize(
    "backend",
    [
        OfflineContractBackend(force_scope_violation=True),
        OfflineContractBackend(force_missing_evidence=True),
    ],
)
def test_scope_or_evidence_failure_escalates(isolated_repository, backend) -> None:
    result = orchestrator(isolated_repository, backend).run(request())
    assert result.status is RunStatus.ESCALATED
    assert result.founder_decision_required is True


@pytest.mark.parametrize("goal", ["Commit this report", "Push this report"])
def test_commit_and_push_requests_stop_before_agents(isolated_repository, goal: str) -> None:
    backend = OfflineContractBackend()
    result = orchestrator(isolated_repository, backend).run(request(goal=goal))
    assert result.status is RunStatus.ESCALATED
    assert backend.review_calls == 0
    assert result.failure_reason == "forbidden Git action requested"


def test_reported_cost_excess_stops_before_review(isolated_repository) -> None:
    backend = OfflineContractBackend(reported_cost_per_call=1.0)
    result = orchestrator(isolated_repository, backend).run(request(max_cost=0.5))
    assert result.status is RunStatus.BUDGET_EXCEEDED
    assert backend.review_calls == 0
    assert result.usage.reported_cost == 1.0


def test_foreign_repository_change_fails_closed_and_reports(isolated_repository) -> None:
    repository, tool_root = isolated_repository
    (repository / "foreign.txt").write_text("outside boundary\n", encoding="utf-8")
    backend = OfflineContractBackend()
    result = DevelopmentOrchestrator(repository, tool_root, backend).run(request())
    assert result.status is RunStatus.FAILED
    assert "out-of-boundary" in (result.failure_reason or "")
    assert backend.review_calls == 0
    assert (tool_root / "runs" / result.run_id / "result.json").is_file()
    assert (repository / "foreign.txt").read_text(encoding="utf-8") == "outside boundary\n"


def test_inputs_are_not_mutated(isolated_repository) -> None:
    item = request()
    before = item.model_dump(mode="json")
    orchestrator(isolated_repository).run(item)
    assert item.model_dump(mode="json") == before
