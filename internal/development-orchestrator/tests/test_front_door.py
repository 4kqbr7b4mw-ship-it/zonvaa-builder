from __future__ import annotations

from pathlib import Path

import pytest

from development_orchestrator.backends import OfflineContractBackend
from development_orchestrator.front_door import (
    ContextCandidate,
    FrontDoorError,
    FrontDoorService,
    FrontDoorStatus,
)
from development_orchestrator.schemas import WorkRequest


def request(**changes: object) -> WorkRequest:
    values = {
        "goal": "Review synthetic research evidence",
        "scope": ["research only"],
        "requested_output": "compact decision brief",
        "allowed_context": [],
        "approval_constraints": ["no commit", "no push"],
        "max_iterations": 2,
    }
    values.update(changes)
    return WorkRequest.model_validate(values)


def service(isolated_repository, factory=None) -> FrontDoorService:
    repository, tool_root = isolated_repository
    return FrontDoorService(
        repository,
        tool_root,
        factory or (lambda: OfflineContractBackend()),
    )


def candidate(path: str = "docs/research.md") -> ContextCandidate:
    return ContextCandidate(path=path, reason="Direct synthetic evidence for the goal.")


def test_submit_proposes_minimized_context_without_running_agents(
    isolated_repository,
) -> None:
    calls = []
    front = service(
        isolated_repository,
        lambda: calls.append(True) or OfflineContractBackend(),
    )
    record = front.submit_work(request(), [candidate()])
    assert record.status is FrontDoorStatus.AWAITING_CONTEXT_APPROVAL
    assert record.open_decision
    assert len(record.context_proposal) == 1
    assert record.context_proposal[0].path == "docs/research.md"
    assert record.context_proposal[0].characters > 0
    assert calls == []


def test_explicit_context_approval_executes_existing_orchestrator(
    isolated_repository,
) -> None:
    front = service(isolated_repository)
    pending = front.submit_work(request(), [candidate(), candidate("README.md")])
    completed = front.approve_context(
        pending.run_id,
        ["docs/research.md"],
        approved=True,
    )
    assert completed.status is FrontDoorStatus.COMPLETED
    assert completed.approved_context == ["docs/research.md"]
    assert completed.review_cycle == 1
    assert completed.decision_brief_available is True
    brief = front.get_decision_brief(completed.run_id)
    assert brief.run_id == completed.run_id


def test_context_rejection_stops_without_backend(isolated_repository) -> None:
    calls = []
    front = service(
        isolated_repository,
        lambda: calls.append(True) or OfflineContractBackend(),
    )
    pending = front.submit_work(request(), [candidate()])
    rejected = front.approve_context(pending.run_id, [], approved=False)
    assert rejected.status is FrontDoorStatus.CONTEXT_REJECTED
    assert calls == []


def test_unproposed_context_is_rejected(isolated_repository) -> None:
    front = service(isolated_repository)
    pending = front.submit_work(request(), [candidate()])
    with pytest.raises(FrontDoorError, match="unproposed"):
        front.approve_context(pending.run_id, ["README.md"], approved=True)


def test_no_context_run_executes_immediately(isolated_repository) -> None:
    calls = []
    completed = service(
        isolated_repository,
        lambda: calls.append(True) or OfflineContractBackend(),
    ).submit_work(request(), [])
    assert completed.status is FrontDoorStatus.ESCALATED
    assert completed.decision_brief_available is True
    assert calls == [True]


@pytest.mark.parametrize("goal", ["Commit this result", "Push this result"])
def test_git_actions_are_rejected_before_backend(isolated_repository, goal: str) -> None:
    calls = []
    front = service(
        isolated_repository,
        lambda: calls.append(True) or OfflineContractBackend(),
    )
    rejected = front.submit_work(request(goal=goal), [])
    assert rejected.status is FrontDoorStatus.REJECTED_POLICY
    assert calls == []


def test_unknown_and_invalid_run_ids_fail_closed(isolated_repository) -> None:
    front = service(isolated_repository)
    with pytest.raises(FrontDoorError, match="unknown"):
        front.get_run_status("run-unknown")
    with pytest.raises(FrontDoorError, match="invalid"):
        front.get_run_status("../escape")


def test_pending_decisions_lists_only_open_records(isolated_repository) -> None:
    front = service(isolated_repository)
    pending = front.submit_work(request(), [candidate()])
    rejected_pending = front.submit_work(request(), [candidate("README.md")])
    rejected = front.approve_context(rejected_pending.run_id, [], approved=False)
    listed = front.list_pending_decisions()
    assert [record.run_id for record in listed] == [pending.run_id]
    assert rejected.run_id not in {record.run_id for record in listed}


def test_foreign_repository_change_fails_closed(isolated_repository) -> None:
    repository, _ = isolated_repository
    (repository / "outside.txt").write_text("foreign\n", encoding="utf-8")
    result = service(isolated_repository).submit_work(request(), [])
    assert result.status is FrontDoorStatus.FAILED
    assert result.decision_brief_available is True


def test_existing_allowed_context_cannot_bypass_proposal(isolated_repository) -> None:
    front = service(isolated_repository)
    with pytest.raises(FrontDoorError, match="controlled"):
        front.submit_work(request(allowed_context=["README.md"]), [])


def test_backend_failure_is_reported_without_propagating_details(
    isolated_repository,
) -> None:
    def failing_backend():
        raise RuntimeError("synthetic provider detail")

    failed = service(isolated_repository, failing_backend).submit_work(request(), [])
    assert failed.status is FrontDoorStatus.FAILED
    assert failed.open_decision == "Run failed; inspect local run evidence."
    assert "provider detail" not in failed.model_dump_json()
