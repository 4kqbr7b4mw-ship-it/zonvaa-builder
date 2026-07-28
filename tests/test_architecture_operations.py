import hashlib
import json
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone
from pathlib import Path

import pytest
from typer.testing import CliRunner

import commands.architecture as architecture_commands
from builder.main import architecture_app
from architecture_integrator import (
    ApprovalStatus,
    ArchitectureFeedbackStore,
    ArchitectureImplementationReview,
    ArchitectureNextStep,
    ArchitectureOperationIssueCode,
    ArchitectureOperationQuery,
    ArchitectureOperationQueryError,
    ArchitectureOperationsAgent,
    ArchitectureWorkflowStore,
    ChiefArchitectDecision,
    CodexHandoverIntake,
    DecisionChoice,
    ExecutionAuthorization,
    FeedbackLoopRecord,
    FeedbackStatus,
    FeedbackTransition,
    HandoverDeviation,
)
from codex_execution import (
    CheckStatus,
    ExecutionOrigin,
    ExecutionRecord,
    ExecutionStatus,
    ExecutionStore,
)


NOW = datetime(2026, 7, 28, 9, 0, tzinfo=timezone.utc)
RESULT = "a" * 40


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def make_workflow(
    repository,
    suffix,
    topic,
    decided=False,
    prompt=False,
    proof=False,
    schema="2.0",
):
    workflow_id = "workflow-{}".format(suffix)
    root = repository / "knowledge" / "architecture_workflows"
    folder = root / workflow_id
    for name in (
        "proposals",
        "analyses",
        "decision_proposals",
        "decisions",
        "prompts",
        "feedback",
        "executions",
    ):
        (folder / name).mkdir(parents=True, exist_ok=True)
    proposal_id = "proposal-{}".format(suffix)
    manifest = {
        "schema_version": schema,
        "workflow_id": workflow_id,
        "created_at": NOW.isoformat(),
        "proposal_ids": [proposal_id],
        "proposal_files": ["proposals/{}.json".format(proposal_id)],
        "analysis_files": ["analyses/{}.json".format(proposal_id)],
        "decision_template_files": [],
    }
    if schema == "2.0":
        manifest.update({
            "topic": topic,
            "decision_template_file": (
                "decision_proposals/decision-proposal.md"
            ),
        })
        (folder / "decision_proposals" / "decision-proposal.md").write_text(
            "# ENTSCHEIDUNGSVORLAGE\n",
            encoding="utf-8",
        )
    else:
        manifest["decision_template_files"] = [
            "decision_proposals/{}.md".format(proposal_id)
        ]
        (
            folder / "decision_proposals" / "{}.md".format(proposal_id)
        ).write_text("# ENTSCHEIDUNGSVORLAGE\n", encoding="utf-8")
    write_json(folder / "workflow.json", manifest)
    write_json(
        folder / "proposals" / "{}.json".format(proposal_id),
        {"title": topic},
    )
    write_json(folder / "analyses" / "{}.json".format(proposal_id), {})
    if decided:
        decision = ChiefArchitectDecision(
            decision_id="decision-{}".format(proposal_id),
            proposal_id=proposal_id,
            decision=DecisionChoice.ADOPT,
            accepted_elements=("Confirmed architecture.",),
            modified_elements=(),
            rejected_elements=(),
            deferred_elements=(),
            rationale="Explicit Chief Architect decision.",
            decided_by="Chief Architect",
            decided_at=NOW,
        )
        write_json(
            folder / "decisions" / "{}.json".format(proposal_id),
            decision.to_dict(),
        )
    if prompt:
        (folder / "prompts" / "codex-prompt.md").write_text(
            "Authorized prompt.\n",
            encoding="utf-8",
        )
    if proof:
        write_json(
            folder / "prompts" / "codex-prompt-proof.json",
            {"proof": "present"},
        )
    return ArchitectureWorkflowStore(root), workflow_id, proposal_id


def authorization(workflows, workflow_id, execution_id):
    item = ExecutionAuthorization(
        authorization_id="authorization-0123456789abcdef",
        architecture_run_id="architecture-run-0123456789abcdef",
        workflow_id=workflow_id,
        expected_execution_id=execution_id,
        decision_artifacts=("decisions/proposal.json",),
        approval_status=ApprovalStatus.CONFIRMED,
        codex_prompt="prompts/codex-prompt.md",
        prompt_hash="b" * 64,
        repository=str(workflows.root.parents[2]),
        expected_base_commit="c" * 40,
        allowed_actions=("create_commit", "create_handover"),
        expected_completion_artifacts=(
            "result_commit",
            "json_handover",
            "markdown_handover",
        ),
        authorized_at=NOW,
    )
    ArchitectureFeedbackStore(workflows).write_authorization(item)
    return item


def running_execution(workflows, workflow_id):
    execution_id = "execution-0123456789abcdef"
    record = ExecutionRecord(
        execution_id=execution_id,
        workflow_id=workflow_id,
        prompt_path="prompts/codex-prompt.md",
        prompt_hash="b" * 64,
        repository_path=str(workflows.root.parents[2]),
        starting_branch="main",
        starting_commit="c" * 40,
        starting_git_status=(),
        status=ExecutionStatus.RUNNING,
        started_at=NOW,
        completed_at=None,
        codex_exit_code=None,
        test_status=CheckStatus.NOT_RUN,
        test_result=None,
        doctor_status=CheckStatus.NOT_RUN,
        doctor_result=None,
        diff_check_status=CheckStatus.NOT_RUN,
        resulting_commit=None,
        handover_paths=(),
        failure=None,
        attempts=(),
        retry_count=0,
    )
    ExecutionStore(workflows).write(record)
    return record


def successful_execution(
    repository,
    workflows,
    workflow_id,
    handovers=True,
):
    execution_id = "execution-0123456789abcdef"
    paths = (
        "knowledge/handovers/result.json",
        "knowledge/handovers/result.md",
    )
    if handovers:
        write_json(
            repository / paths[0],
            {
                "schema_version": "1.0",
                "task": "Completed operation",
                "starting_commit": "c" * 40,
                "ending_commit": RESULT,
                "changed_files": ["result.txt"],
                "checks": [],
                "git_status": ["clean"],
                "open_risks": ["Review remains required."],
                "push_status": "not_pushed",
            },
        )
        (repository / paths[1]).write_text(
            "# Handover\n",
            encoding="utf-8",
        )
    record = ExecutionRecord(
        execution_id=execution_id,
        workflow_id=workflow_id,
        prompt_path="prompts/codex-prompt.md",
        prompt_hash="b" * 64,
        repository_path=str(repository),
        starting_branch="main",
        starting_commit="c" * 40,
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
        handover_paths=paths,
        failure=None,
        attempts=(),
        retry_count=0,
    )
    ExecutionStore(workflows).write(record)
    return record


def complete_review(repository, workflows, workflow_id):
    record = successful_execution(
        repository,
        workflows,
        workflow_id,
    )
    auth = authorization(workflows, workflow_id, record.execution_id)
    intake = CodexHandoverIntake(
        architecture_run_id=auth.architecture_run_id,
        workflow_id=workflow_id,
        execution_id=record.execution_id,
        authorization_id=auth.authorization_id,
        decision_ids=("decision-proposal",),
        attempt_ids=(),
        starting_commit=record.starting_commit,
        result_commit=RESULT,
        handover_path=record.handover_paths[0],
        changed_files=("result.txt",),
        checks=("tests passed",),
        git_status=("clean",),
        open_risks=("Review remains required.",),
        deviations=(),
    )
    review = ArchitectureImplementationReview(
        review_id="review-0123456789abcdef",
        architecture_run_id=auth.architecture_run_id,
        workflow_id=workflow_id,
        execution_id=record.execution_id,
        attempt_ids=(),
        recommendation="ADOPT",
        original_decision_ids=intake.decision_ids,
        codex_prompt="prompts/codex-prompt.md",
        implementation_result="Implementation completed.",
        changed_files=intake.changed_files,
        checks=intake.checks,
        commit=RESULT,
        git_status=intake.git_status,
        deviations=(),
        open_risks=intake.open_risks,
        conflicts=(),
        decision_required=("Chief Architect decision required.",),
    )
    store = ArchitectureFeedbackStore(workflows)
    store.write_intake(intake)
    store.write_review(review)
    statuses = (
        FeedbackStatus.DECISION_CONFIRMED,
        FeedbackStatus.EXECUTION_AUTHORIZED,
        FeedbackStatus.EXECUTION_COMPLETED,
        FeedbackStatus.HANDOVER_DISCOVERED,
        FeedbackStatus.HANDOVER_VALIDATED,
        FeedbackStatus.INTEGRATOR_REVIEW_READY,
        FeedbackStatus.CHIEF_ARCHITECT_DECISION_REQUIRED,
    )
    store.write_record(FeedbackLoopRecord(
        architecture_run_id=auth.architecture_run_id,
        workflow_id=workflow_id,
        expected_execution_id=record.execution_id,
        status=statuses[-1],
        transitions=tuple(
            FeedbackTransition(item, NOW, item.value)
            for item in statuses
        ),
        execution_id=record.execution_id,
        authorization_id=auth.authorization_id,
        handover_path=record.handover_paths[0],
        review_id=review.review_id,
    ))
    return review


def agent(repository, workflows):
    return ArchitectureOperationsAgent(repository, workflows)


def test_status_searches_every_persisted_identifier(tmp_path):
    repository = tmp_path / "repo"
    workflows, workflow_id, proposal_id = make_workflow(
        repository,
        "1111111111111111",
        "Guardian Succession",
        decided=True,
        prompt=True,
        proof=True,
    )
    review = complete_review(repository, workflows, workflow_id)
    operations = agent(repository, workflows)
    status = operations.find(ArchitectureOperationQuery(
        workflow_id=workflow_id,
    ))[0]

    queries = (
        ArchitectureOperationQuery(workflow_id=workflow_id),
        ArchitectureOperationQuery(
            architecture_run_id=status.architecture_run_id
        ),
        ArchitectureOperationQuery(execution_id=status.execution_id),
        ArchitectureOperationQuery(review_id=review.review_id),
        ArchitectureOperationQuery(commit=RESULT),
        ArchitectureOperationQuery(commit=RESULT[:8]),
        ArchitectureOperationQuery(topic="guardian succession"),
        ArchitectureOperationQuery(
            handover_path=status.handover_paths[0]
        ),
        ArchitectureOperationQuery(proposal_id=proposal_id),
        ArchitectureOperationQuery(decision_id=status.decision_ids[0]),
    )
    assert all(
        operations.find(query)[0].workflow_id == workflow_id
        for query in queries
    )


def test_ambiguous_topic_and_short_commit_block(tmp_path):
    repository = tmp_path / "repo"
    first, first_id, _ = make_workflow(
        repository,
        "1111111111111111",
        "Shared Topic One",
        decided=True,
        prompt=True,
        proof=True,
    )
    complete_review(repository, first, first_id)
    second = ArchitectureWorkflowStore(first.root)
    _, second_id, _ = make_workflow(
        repository,
        "2222222222222222",
        "Shared Topic Two",
        decided=True,
        prompt=True,
        proof=True,
    )
    complete_review(repository, second, second_id)
    operations = agent(repository, first)

    for query in (
        ArchitectureOperationQuery(topic="Shared Topic"),
        ArchitectureOperationQuery(commit=RESULT[:7]),
    ):
        with pytest.raises(ArchitectureOperationQueryError) as raised:
            operations.find(query)
        assert raised.value.failure.code.value == "AMBIGUOUS_QUERY"
        assert raised.value.failure.candidates == tuple(sorted(
            (first_id, second_id)
        ))


def test_next_step_engine_covers_workflow_stages(tmp_path):
    repository = tmp_path / "repo"
    workflows, workflow_id, _ = make_workflow(
        repository,
        "1111111111111111",
        "Waiting",
    )
    operations = agent(repository, workflows)
    assert operations.statuses()[0].next_step is (
        ArchitectureNextStep.CHIEF_ARCHITECT_DECISION_REQUIRED
    )

    repository = tmp_path / "decided"
    workflows, _, _ = make_workflow(
        repository,
        "2222222222222222",
        "Decided",
        decided=True,
    )
    assert agent(repository, workflows).statuses()[0].next_step is (
        ArchitectureNextStep.GENERATE_CODEX_PROMPT
    )

    repository = tmp_path / "prompted"
    workflows, _, _ = make_workflow(
        repository,
        "3333333333333333",
        "Prompted",
        decided=True,
        prompt=True,
        proof=True,
    )
    assert agent(repository, workflows).statuses()[0].next_step is (
        ArchitectureNextStep.EXECUTION_AUTHORIZED
    )


def test_execution_and_review_next_steps_are_deterministic(tmp_path):
    repository = tmp_path / "repo"
    workflows, workflow_id, _ = make_workflow(
        repository,
        "1111111111111111",
        "Execution",
        decided=True,
        prompt=True,
        proof=True,
    )
    authorization(
        workflows,
        workflow_id,
        "execution-0123456789abcdef",
    )
    assert agent(repository, workflows).statuses()[0].next_step is (
        ArchitectureNextStep.EXECUTION_REQUIRED
    )
    running_execution(workflows, workflow_id)
    assert agent(repository, workflows).statuses()[0].next_step is (
        ArchitectureNextStep.EXECUTION_RUNNING
    )

    repository = tmp_path / "review"
    workflows, workflow_id, _ = make_workflow(
        repository,
        "2222222222222222",
        "Reviewed",
        decided=True,
        prompt=True,
        proof=True,
    )
    complete_review(repository, workflows, workflow_id)
    status = agent(repository, workflows).statuses()[0]
    assert status.next_step is (
        ArchitectureNextStep.CHIEF_ARCHITECT_DECISION_REQUIRED
    )
    assert status.review_recommendation == "ADOPT"
    assert status.decision_ids == (
        "decision-proposal-2222222222222222",
    )


def test_missing_handover_intake_and_review_are_visible(tmp_path):
    repository = tmp_path / "repo"
    workflows, workflow_id, _ = make_workflow(
        repository,
        "1111111111111111",
        "Missing handover",
        decided=True,
        prompt=True,
        proof=True,
    )
    authorization(
        workflows,
        workflow_id,
        "execution-0123456789abcdef",
    )
    successful_execution(
        repository,
        workflows,
        workflow_id,
        handovers=False,
    )
    status = agent(repository, workflows).statuses()[0]
    assert status.next_step is ArchitectureNextStep.HANDOVER_REQUIRED
    assert ArchitectureOperationIssueCode.SUCCEEDED_EXECUTION_WITHOUT_HANDOVER in {
        item.code for item in status.issues
    }

    repository = tmp_path / "intake"
    workflows, workflow_id, _ = make_workflow(
        repository,
        "2222222222222222",
        "Missing intake",
        decided=True,
        prompt=True,
        proof=True,
    )
    authorization(
        workflows,
        workflow_id,
        "execution-0123456789abcdef",
    )
    successful_execution(repository, workflows, workflow_id)
    assert agent(repository, workflows).statuses()[0].next_step is (
        ArchitectureNextStep.HANDOVER_VALIDATION_REQUIRED
    )


def test_artifacts_are_complete_and_missing_values_are_not_invented(tmp_path):
    repository = tmp_path / "repo"
    workflows, _, _ = make_workflow(
        repository,
        "1111111111111111",
        "Artifact inventory",
    )
    status = agent(repository, workflows).statuses()[0]
    kinds = {item.kind for item in status.artifacts}

    assert {
        "workflow",
        "proposal",
        "analysis",
        "decision",
        "codex_prompt",
        "prompt_proof",
        "execution_authorization",
        "execution_record",
        "attempt_history",
        "json_handover",
        "markdown_handover",
        "handover_intake",
        "integrator_review",
        "decision_proposal",
        "feedback_record",
    }.issubset(kinds)
    assert all(
        item.path is None
        for item in status.artifacts
        if item.availability.value == "MISSING"
        and item.kind in {"execution_record", "json_handover"}
    )


def test_legacy_prompt_without_proof_is_complete_and_not_executable(tmp_path):
    repository = tmp_path / "repo"
    workflows, _, _ = make_workflow(
        repository,
        "1111111111111111",
        "Legacy workflow",
        decided=True,
        prompt=True,
        proof=False,
        schema="1.0",
    )
    status = agent(repository, workflows).statuses()[0]

    assert status.legacy is True
    assert status.executable is False
    assert status.next_step is ArchitectureNextStep.COMPLETE
    assert ArchitectureOperationIssueCode.PROMPT_WITHOUT_PROOF not in {
        item.code for item in status.issues
    }


def test_symlink_and_cross_artifact_inconsistencies_block(tmp_path):
    repository = tmp_path / "repo"
    workflows, workflow_id, _ = make_workflow(
        repository,
        "1111111111111111",
        "Unsafe workflow",
        decided=True,
        prompt=True,
        proof=True,
    )
    prompt = workflows.folder(workflow_id) / "prompts" / "codex-prompt.md"
    prompt.unlink()
    outside = tmp_path / "outside.md"
    outside.write_text("outside\n", encoding="utf-8")
    prompt.symlink_to(outside)
    status = agent(repository, workflows).statuses()[0]

    assert status.next_step is ArchitectureNextStep.BLOCKED
    assert ArchitectureOperationIssueCode.UNSAFE_SYMLINK in {
        item.code for item in status.issues
    }


def test_models_output_and_order_are_immutable_and_stable(tmp_path):
    repository = tmp_path / "repo"
    workflows, _, _ = make_workflow(
        repository,
        "2222222222222222",
        "Second",
    )
    make_workflow(repository, "1111111111111111", "First")
    operations = agent(repository, workflows)
    before = json.dumps(
        [item.to_dict() for item in operations.statuses()],
        sort_keys=True,
    )
    after = json.dumps(
        [item.to_dict() for item in operations.statuses()],
        sort_keys=True,
    )

    assert before == after
    assert tuple(item.workflow_id for item in operations.statuses()) == (
        "workflow-1111111111111111",
        "workflow-2222222222222222",
    )
    with pytest.raises(FrozenInstanceError):
        operations.statuses()[0].topic = "changed"


def test_read_only_calls_change_no_files_or_git_status(tmp_path):
    repository = tmp_path / "repo"
    workflows, _, _ = make_workflow(
        repository,
        "1111111111111111",
        "Read only",
    )
    before = tuple(
        (str(path.relative_to(repository)), path.read_bytes())
        for path in sorted(repository.rglob("*"))
        if path.is_file()
    )
    operations = agent(repository, workflows)

    operations.statuses()
    operations.find(ArchitectureOperationQuery(topic="Read only"))
    operations.reviews()

    after = tuple(
        (str(path.relative_to(repository)), path.read_bytes())
        for path in sorted(repository.rglob("*"))
        if path.is_file()
    )
    assert after == before


def test_reviews_include_only_decision_ready_operations(tmp_path):
    repository = tmp_path / "repo"
    workflows, ready_id, _ = make_workflow(
        repository,
        "1111111111111111",
        "Ready",
        decided=True,
        prompt=True,
        proof=True,
    )
    complete_review(repository, workflows, ready_id)
    make_workflow(repository, "2222222222222222", "Waiting")

    reviews = agent(repository, workflows).reviews()

    assert tuple(item.workflow_id for item in reviews) == (ready_id,)
    assert reviews[0].open_risks == ("Review remains required.",)


def test_cli_human_and_json_outputs_use_read_only_agent(tmp_path, monkeypatch):
    repository = tmp_path / "repo"
    workflows, workflow_id, _ = make_workflow(
        repository,
        "1111111111111111",
        "CLI Topic",
    )
    operations = agent(repository, workflows)
    monkeypatch.setattr(
        architecture_commands,
        "_operations_agent",
        lambda: operations,
    )
    runner = CliRunner()

    human = runner.invoke(
        architecture_app,
        ["status", "--workflow-id", workflow_id],
    )
    machine = runner.invoke(
        architecture_app,
        ["status", "--workflow-id", workflow_id, "--json"],
    )
    next_result = runner.invoke(
        architecture_app,
        ["next", "--workflow-id", workflow_id, "--json"],
    )
    artifacts_result = runner.invoke(
        architecture_app,
        ["artifacts", "--workflow-id", workflow_id, "--json"],
    )
    reviews_result = runner.invoke(
        architecture_app,
        ["reviews", "--workflow-id", workflow_id, "--json"],
    )

    assert human.exit_code == 0
    assert "Thema: CLI Topic" in human.stdout
    assert "Nächster Schritt:" in human.stdout
    assert json.loads(machine.stdout)["operations"][0]["workflow_id"] == (
        workflow_id
    )
    assert json.loads(next_result.stdout)["next_step"] == (
        "CHIEF_ARCHITECT_DECISION_REQUIRED"
    )
    assert artifacts_result.exit_code == 0
    assert any(
        item["kind"] == "workflow"
        for item in json.loads(artifacts_result.stdout)["artifacts"]
    )
    assert reviews_result.exit_code == 0
    assert json.loads(reviews_result.stdout)["reviews"] == []


def test_bridge_and_reconstructed_origins_and_attempt_counts_are_visible(
    tmp_path,
):
    repository = tmp_path / "repo"
    workflows, workflow_id, _ = make_workflow(
        repository,
        "1111111111111111",
        "Bridge",
        decided=True,
        prompt=True,
        proof=True,
    )
    authorization(
        workflows,
        workflow_id,
        "execution-0123456789abcdef",
    )
    running_execution(workflows, workflow_id)
    status = agent(repository, workflows).statuses()[0]

    assert status.execution_origin is ExecutionOrigin.EXECUTION_BRIDGE
    assert status.attempt_count == 0


def test_review_recommendation_never_creates_a_decision(tmp_path):
    repository = tmp_path / "repo"
    workflows, workflow_id, proposal_id = make_workflow(
        repository,
        "1111111111111111",
        "No automatic decision",
        decided=True,
        prompt=True,
        proof=True,
    )
    complete_review(repository, workflows, workflow_id)
    decision_path = (
        workflows.folder(workflow_id)
        / "decisions"
        / "{}.json".format(proposal_id)
    )
    before = decision_path.read_bytes()

    status = agent(repository, workflows).statuses()[0]

    assert status.review_recommendation == "ADOPT"
    assert status.next_step is (
        ArchitectureNextStep.CHIEF_ARCHITECT_DECISION_REQUIRED
    )
    assert decision_path.read_bytes() == before


def test_authorization_and_execution_inconsistencies_are_blocked(tmp_path):
    repository = tmp_path / "authorization"
    workflows, workflow_id, _ = make_workflow(
        repository,
        "1111111111111111",
        "Authorization without prompt",
        decided=True,
    )
    authorization(
        workflows,
        workflow_id,
        "execution-0123456789abcdef",
    )
    status = agent(repository, workflows).statuses()[0]
    assert status.next_step is ArchitectureNextStep.BLOCKED
    assert ArchitectureOperationIssueCode.AUTHORIZATION_WITHOUT_PROMPT in {
        item.code for item in status.issues
    }

    repository = tmp_path / "execution"
    workflows, workflow_id, _ = make_workflow(
        repository,
        "2222222222222222",
        "Execution without authorization",
        decided=True,
        prompt=True,
        proof=True,
    )
    running_execution(workflows, workflow_id)
    status = agent(repository, workflows).statuses()[0]
    assert ArchitectureOperationIssueCode.EXECUTION_WITHOUT_AUTHORIZATION in {
        item.code for item in status.issues
    }


def test_cross_artifact_inconsistencies_are_reported(tmp_path):
    repository = tmp_path / "repo"
    workflows, workflow_id, _ = make_workflow(
        repository,
        "1111111111111111",
        "Cross artifact checks",
        decided=True,
        prompt=True,
        proof=True,
    )
    complete_review(repository, workflows, workflow_id)
    runtime = (
        workflows.folder(workflow_id) / "executions" / "feedback"
    )

    (runtime / "handover-intake.json").unlink()
    status = agent(repository, workflows).statuses()[0]
    assert ArchitectureOperationIssueCode.REVIEW_WITHOUT_INTAKE in {
        item.code for item in status.issues
    }

    review_path = runtime / "integrator-review.json"
    review = json.loads(review_path.read_text(encoding="utf-8"))
    review["commit"] = "d" * 40
    write_json(review_path, review)
    status = agent(repository, workflows).statuses()[0]
    assert ArchitectureOperationIssueCode.RESULT_COMMIT_MISMATCH in {
        item.code for item in status.issues
    }

    (runtime / "feedback-loop.json").unlink()
    status = agent(repository, workflows).statuses()[0]
    assert ArchitectureOperationIssueCode.INVALID_FEEDBACK_TRANSITION in {
        item.code for item in status.issues
    }


def test_duplicate_execution_and_review_are_blocked(tmp_path):
    repository = tmp_path / "repo"
    workflows, workflow_id, _ = make_workflow(
        repository,
        "1111111111111111",
        "Duplicates",
        decided=True,
        prompt=True,
        proof=True,
    )
    first = running_execution(workflows, workflow_id)
    second = replace(
        first,
        execution_id="execution-fedcba9876543210",
    )
    ExecutionStore(workflows).write(second)
    runtime = (
        workflows.folder(workflow_id) / "executions" / "feedback"
    )
    runtime.mkdir(parents=True)
    write_json(
        runtime / "integrator-review.json",
        {
            "schema_version": "1.0",
            "review_id": "review-0123456789abcdef",
            "architecture_run_id": "architecture-run-0123456789abcdef",
            "workflow_id": workflow_id,
            "execution_id": first.execution_id,
            "attempt_ids": [],
            "recommendation": "ADOPT",
            "original_decision_ids": ["decision-proposal"],
            "codex_prompt": "prompts/codex-prompt.md",
            "implementation_result": "Completed.",
            "changed_files": ["file.txt"],
            "checks": ["tests passed"],
            "commit": RESULT,
            "git_status": ["clean"],
            "deviations": [],
            "open_risks": [],
            "conflicts": [],
            "decision_required": ["Chief Architect decision required."],
        },
    )
    write_json(
        runtime / "integrator-review-copy.json",
        json.loads(
            (runtime / "integrator-review.json").read_text(encoding="utf-8")
        ),
    )

    status = agent(repository, workflows).statuses()[0]
    codes = {item.code for item in status.issues}
    assert ArchitectureOperationIssueCode.DUPLICATE_EXECUTION in codes
    assert ArchitectureOperationIssueCode.DUPLICATE_REVIEW in codes
    assert status.next_step is ArchitectureNextStep.BLOCKED
