import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from typer.testing import CliRunner

import commands.architecture as architecture_commands
from architecture_integrator import (
    ArchitectureContextLoader,
    ArchitectureFeedbackLoop,
    ArchitectureFeedbackStore,
    ArchitectureIntegrator,
    ArchitectureLayer,
    ArchitectureProposal,
    ArchitectureWorkflowOrchestrator,
    ArchitectureWorkflowStore,
    ChiefArchitectDecision,
    DecisionChoice,
    FeedbackStatus,
    SourceRole,
)
from codex_execution import (
    CheckStatus,
    ExecutionRecord,
    ExecutionStatus,
)
from builder.runtime import RuntimeManager
from builder.main import app


BASE = "a" * 40
RESULT = "b" * 40
NOW = datetime(2026, 7, 27, 10, 30, tzinfo=timezone.utc)


@pytest.fixture(scope="module")
def runtime():
    return RuntimeManager().boot()


class FakeExecutionService:
    def __init__(self, record=None, pending_start=False):
        self.record = record
        self.execute_count = 0
        self.repository = None
        self.pending_start = pending_start

    def execution_id(self, workflow_id, prompt_hash):
        import hashlib
        digest = hashlib.sha256(
            "{}\0{}".format(workflow_id, prompt_hash).encode("utf-8")
        ).hexdigest()
        return "execution-{}".format(digest[:16])

    def status(self, workflow_id):
        if self.pending_start:
            self.pending_start = False
            return None
        return self.record

    def execute(self, workflow_id):
        self.execute_count += 1
        if self.record is None:
            raise RuntimeError("Fake execution result is missing")
        return self.record


def _proposal():
    return ArchitectureProposal(
        proposal_id="proposal-feedback",
        title="Feedback architecture",
        source="internal test",
        source_role=SourceRole.INTERNAL,
        submitted_at=NOW,
        content="- Add a deterministic implementation feedback loop.",
        requested_scope="Architecture automation",
        related_layers=(ArchitectureLayer.CROSS_LAYER,),
        known_constraints=("Chief Architect remains authoritative.",),
        source_references=(),
    )


def _decision():
    return ChiefArchitectDecision(
        decision_id="decision-feedback",
        proposal_id="proposal-feedback",
        decision=DecisionChoice.ADOPT,
        accepted_elements=("Deterministic feedback is accepted.",),
        modified_elements=(),
        rejected_elements=(),
        deferred_elements=(),
        rationale="Explicit test authority.",
        decided_by="Chief Architect",
        decided_at=NOW,
    )


def _setup(runtime, tmp_path, create_commit=False):
    repository = tmp_path / "repository"
    repository.mkdir(parents=True)
    workflows = ArchitectureWorkflowStore(
        repository / "knowledge" / "architecture_workflows"
    )
    integrator = ArchitectureIntegrator(ArchitectureContextLoader(runtime))
    orchestrator = ArchitectureWorkflowOrchestrator(integrator, workflows)
    workflow = orchestrator.analyze((_proposal(),), topic="Feedback loop")
    orchestrator.decide(workflow.workflow_id, _decision())
    orchestrator.generate_codex(
        workflow.workflow_id,
        create_commit=create_commit,
    )
    service = FakeExecutionService()
    loop = ArchitectureFeedbackLoop(
        workflows,
        service,
        integrator,
        repository,
        branch_resolver=lambda: "main",
    )
    service.repository = repository
    authorization = loop.authorize(
        workflow.workflow_id,
        expected_base_commit=BASE,
        create_commit=create_commit,
    )
    return repository, workflow, workflows, service, loop, authorization


def _handover(repository, execution_id, missing=()):
    relative = "knowledge/handovers/result.json"
    path = repository / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "1.0",
        "timestamp": NOW.isoformat(),
        "task": "Authorized feedback implementation",
        "starting_commit": BASE,
        "ending_commit": RESULT,
        "changed_files": ["architecture_integrator/feedback.py"],
        "functional_changes": ["Closed local transport gap."],
        "technical_changes": ["Added deterministic intake."],
        "decisions": ["No architecture decision was made by Codex."],
        "relevant_adrs": ["ADR-0035"],
        "checks": [
            {
                "command": "python3 -m pytest -q",
                "status": "passed",
                "result": "tests passed",
            },
            {
                "command": "python3 -m builder.main doctor",
                "status": "passed",
                "result": "doctor passed",
            },
            {
                "command": "git diff --check",
                "status": "passed",
                "result": "clean",
            },
        ],
        "open_risks": ["Chief Architect review remains required."],
        "intentionally_not_implemented": ["No automatic approval."],
        "recommended_next_step": "Chief Architect review.",
        "git_status": ["clean after commit"],
        "push_status": "not_pushed",
    }
    for field in missing:
        payload.pop(field)
    path.write_text(json.dumps(payload), encoding="utf-8")
    path.with_suffix(".md").write_text("# Handover\n", encoding="utf-8")
    return relative


def _record(workflow_id, authorization, handover_path):
    return ExecutionRecord(
        execution_id=authorization.expected_execution_id,
        workflow_id=workflow_id,
        prompt_path="prompts/codex-prompt.md",
        prompt_hash=authorization.prompt_hash,
        repository_path=authorization.repository,
        starting_branch="main",
        starting_commit=BASE,
        starting_git_status=(),
        status=ExecutionStatus.SUCCEEDED,
        started_at=NOW,
        completed_at=NOW,
        codex_exit_code=0,
        test_status=CheckStatus.PASSED,
        test_result="tests passed",
        doctor_status=CheckStatus.PASSED,
        doctor_result="doctor passed",
        diff_check_status=CheckStatus.PASSED,
        resulting_commit=RESULT,
        handover_paths=(handover_path, handover_path[:-5] + ".md"),
        failure=None,
        attempts=(),
        retry_count=0,
    )


def test_confirmed_decision_creates_authorized_execution_artifact(
    runtime,
    tmp_path,
):
    _, workflow, _, _, _, authorization = _setup(runtime, tmp_path)

    assert authorization.workflow_id == workflow.workflow_id
    assert authorization.approval_status.value == "CONFIRMED"
    assert authorization.expected_base_commit == BASE
    assert authorization.schema_version == "1.2"
    assert authorization.authorized_branch == "main"
    assert authorization.create_commit is False
    assert "create_commit" not in authorization.allowed_actions
    assert "create_handover" in authorization.allowed_actions
    assert "push" not in authorization.allowed_actions


def test_commit_authority_is_explicit_and_changes_authorization_identity(
    runtime,
    tmp_path,
):
    false_authorization = _setup(
        runtime, tmp_path / "false", create_commit=False
    )[-1]
    true_authorization = _setup(
        runtime, tmp_path / "true", create_commit=True
    )[-1]
    assert false_authorization.create_commit is False
    assert true_authorization.create_commit is True
    assert false_authorization.authorization_id != (
        true_authorization.authorization_id
    )
    assert "create_commit" not in true_authorization.allowed_actions


def test_unconfirmed_workflow_cannot_authorize_or_start(runtime, tmp_path):
    repository = tmp_path / "repository"
    workflows = ArchitectureWorkflowStore(repository / "workflows")
    integrator = ArchitectureIntegrator(ArchitectureContextLoader(runtime))
    orchestrator = ArchitectureWorkflowOrchestrator(integrator, workflows)
    workflow = orchestrator.analyze((_proposal(),))
    service = FakeExecutionService()
    loop = ArchitectureFeedbackLoop(
        workflows, service, integrator, repository
    )

    with pytest.raises(RuntimeError, match="Confirmed decisions"):
        loop.authorize(workflow.workflow_id, BASE)
    assert service.execute_count == 0


def test_complete_feedback_flow_is_idempotent_and_requires_decision(
    runtime,
    tmp_path,
):
    repository, workflow, workflows, service, loop, authorization = _setup(
        runtime, tmp_path
    )
    handover = _handover(
        repository,
        authorization.expected_execution_id,
    )
    service.record = _record(
        workflow.workflow_id,
        authorization,
        handover,
    )

    first = loop.advance(workflow.workflow_id)
    second = loop.advance(workflow.workflow_id)

    assert first == second
    assert first.status is FeedbackStatus.CHIEF_ARCHITECT_DECISION_REQUIRED
    assert service.execute_count == 0
    store = ArchitectureFeedbackStore(workflows)
    review = json.loads(
        (
            store.runtime_folder(workflow.workflow_id)
            / "integrator-review.json"
        )
        .read_text(encoding="utf-8")
    )
    assert review["execution_id"] == authorization.expected_execution_id
    assert review["recommendation"] == "ADOPT"
    assert "decision" not in review
    assert len(tuple(
        store.runtime_folder(workflow.workflow_id).glob(
            "integrator-review.json"
        )
    )) == 1


def test_handover_is_assigned_by_execution_and_commit(runtime, tmp_path):
    repository, workflow, _, service, loop, authorization = _setup(
        runtime, tmp_path
    )
    handover = _handover(
        repository,
        authorization.expected_execution_id,
    )
    record = _record(workflow.workflow_id, authorization, handover)

    intake = loop.validate_handover(authorization, record, handover)

    assert intake.execution_id == record.execution_id
    assert intake.starting_commit == BASE
    assert intake.result_commit == RESULT
    assert intake.deviations == ()


def test_schema_1_handover_without_self_referential_commit_is_unambiguous(
    runtime,
    tmp_path,
):
    repository, workflow, _, _, loop, authorization = _setup(
        runtime, tmp_path
    )
    handover = _handover(repository, authorization.expected_execution_id)
    payload = json.loads((repository / handover).read_text(encoding="utf-8"))
    payload["ending_commit"] = None
    (repository / handover).write_text(json.dumps(payload), encoding="utf-8")
    record = _record(workflow.workflow_id, authorization, handover)

    intake = loop.validate_handover(authorization, record, handover)

    assert intake.result_commit == RESULT
    assert intake.deviations == ()


def test_foreign_or_incomplete_handover_creates_deviations(runtime, tmp_path):
    repository, workflow, _, _, loop, authorization = _setup(
        runtime, tmp_path
    )
    handover = _handover(
        repository,
        authorization.expected_execution_id,
        missing=("checks", "git_status"),
    )
    payload = json.loads((repository / handover).read_text(encoding="utf-8"))
    payload["ending_commit"] = "c" * 40
    (repository / handover).write_text(json.dumps(payload), encoding="utf-8")
    record = _record(workflow.workflow_id, authorization, handover)

    intake = loop.validate_handover(authorization, record, handover)
    codes = {item.code for item in intake.deviations}

    assert "HANDOVER_RESULT_MISMATCH" in codes
    assert "MISSING_CHECKS" in codes
    assert "MISSING_GIT_STATUS" in codes
    assert "CHECKS_MISSING" in codes


def test_feedback_models_and_output_are_deterministic(runtime, tmp_path):
    repository, workflow, _, service, loop, authorization = _setup(
        runtime, tmp_path
    )
    handover = _handover(repository, authorization.expected_execution_id)
    service.record = _record(workflow.workflow_id, authorization, handover)

    left = loop.advance(workflow.workflow_id).to_dict()
    right = loop.advance(workflow.workflow_id).to_dict()

    assert left == right
    assert [
        item["status"] for item in left["transitions"]
    ][-3:] == [
        "HANDOVER_VALIDATED",
        "INTEGRATOR_REVIEW_READY",
        "CHIEF_ARCHITECT_DECISION_REQUIRED",
    ]


def test_controlled_end_to_end_starts_once_and_preserves_execution_evidence(
    runtime,
    tmp_path,
):
    repository, workflow, _, service, loop, authorization = _setup(
        runtime, tmp_path
    )
    handover = _handover(repository, authorization.expected_execution_id)
    service.record = _record(workflow.workflow_id, authorization, handover)
    service.pending_start = True

    result = loop.advance(workflow.workflow_id)

    assert service.execute_count == 1
    assert result.status is FeedbackStatus.CHIEF_ARCHITECT_DECISION_REQUIRED
    intake = json.loads(
        (
            loop.store.runtime_folder(workflow.workflow_id)
            / "handover-intake.json"
        ).read_text(encoding="utf-8")
    )
    assert intake["execution_id"] == authorization.expected_execution_id
    assert intake["attempt_ids"] == []
    assert intake["result_commit"] == RESULT


def test_cli_exposes_machine_readable_pipeline_status(
    runtime,
    tmp_path,
    monkeypatch,
):
    repository, workflow, workflows, _, _, _ = _setup(runtime, tmp_path)
    store = ArchitectureFeedbackStore(workflows)
    monkeypatch.setattr(
        architecture_commands,
        "ArchitectureWorkflowStore",
        lambda: workflows,
    )
    monkeypatch.setattr(
        architecture_commands,
        "ArchitectureFeedbackStore",
        lambda value: store,
    )

    result = CliRunner().invoke(
        app,
        [
            "architecture",
            "workflow",
            "feedback-status",
            "--workflow-id",
            workflow.workflow_id,
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert payload["workflow_id"] == workflow.workflow_id
    assert payload["status"] == "EXECUTION_AUTHORIZED"
    assert "executions/feedback" in str(store.record_path(workflow.workflow_id))


def test_handover_intake_redacts_sensitive_metadata(runtime, tmp_path):
    repository, workflow, _, _, loop, authorization = _setup(
        runtime, tmp_path
    )
    handover = _handover(repository, authorization.expected_execution_id)
    payload = json.loads((repository / handover).read_text(encoding="utf-8"))
    payload["open_risks"] = ["Authorization: Bearer secret-value"]
    (repository / handover).write_text(json.dumps(payload), encoding="utf-8")

    intake = loop.validate_handover(
        authorization,
        _record(workflow.workflow_id, authorization, handover),
        handover,
    )

    serialized = json.dumps(intake.to_dict())
    assert "secret-value" not in serialized
    assert "[REDACTED]" in serialized
