import hashlib
import json
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
import sys

import pytest
from typer.testing import CliRunner

import commands.architecture as architecture_commands
from architecture_integrator import (
    ApprovalStatus,
    ArchitectureFeedbackStore,
    ArchitectureWorkflowStore,
    ExecutionAuthorization,
    validate_local_branch_name,
)
from architecture_integrator.workflow import (
    PromptCommitInstruction,
    analyze_codex_prompt,
)
from builder.main import app
from codex_execution import (
    CodexExecutionOrchestration,
    CodexExecutionOrchestrationStore,
    CodexExecutionOrchestrator,
    CodexExecutionProcessMetadata,
    CodexExecutionRequest,
    CodexExecutionStatus,
    CodexExecutionStep,
    CommandResult,
    ExecutionBridgeError,
    ExecutionFailure,
    ExecutionFailureKind,
    ExecutionStep,
    SubprocessCommandRunner,
)


NOW = datetime(2026, 7, 30, 12, 0, tzinfo=timezone.utc)
WORKFLOW = "workflow-0123456789abcdef"
RUN = "architecture-run-0123456789abcdef"
EXECUTION = "execution-0123456789abcdef"
AUTHORIZATION = "authorization-0123456789abcdef"
BASE = "1" * 40
RESULT = "2" * 40


class OrchestrationRunner:
    def __init__(
        self,
        repository: Path,
        *,
        branch="main",
        head=BASE,
        codex_creates_commit=False,
        initial_status="",
        final_status=" M result.txt\n",
        codex_exit=0,
        tests_exit=0,
        doctor_exit=0,
        diff_exit=0,
        codex_stdout="completed token=secret-value",
        codex_stderr="",
        commit_exit=0,
        pushed=False,
        codex_error=None,
    ):
        self.repository = repository
        self.branch = branch
        self.head = head
        self.codex_creates_commit = codex_creates_commit
        self.initial_status = initial_status
        self.final_status = final_status
        self.codex_exit = codex_exit
        self.tests_exit = tests_exit
        self.doctor_exit = doctor_exit
        self.diff_exit = diff_exit
        self.codex_stdout = codex_stdout
        self.codex_stderr = codex_stderr
        self.commit_exit = commit_exit
        self.pushed = pushed
        self.codex_error = codex_error
        self.codex_called = 0
        self.commit_called = 0
        self.commands = []

    def run(self, arguments, cwd, input_text=None, **kwargs):
        args = tuple(arguments)
        self.commands.append(args)
        assert cwd == self.repository
        if args == ("git", "branch", "--show-current"):
            return CommandResult(0, self.branch + "\n", "")
        if args == ("git", "rev-parse", "HEAD"):
            value = (
                RESULT
                if self.commit_called
                or (self.codex_called and self.codex_creates_commit)
                else self.head
            )
            return CommandResult(0, value + "\n", "")
        if args == ("git", "rev-parse", "origin/main"):
            value = RESULT if self.pushed and self.codex_called else BASE
            return CommandResult(0, value + "\n", "")
        if args[:4] == ("git", "rev-list", "--left-right", "--count"):
            return CommandResult(0, "0\t0\n", "")
        if args == ("git", "status", "--porcelain"):
            return CommandResult(
                0,
                self.final_status if self.codex_called else self.initial_status,
                "",
            )
        if "exec" in args:
            self.codex_called += 1
            if self.codex_error is not None:
                raise self.codex_error
            return CommandResult(
                self.codex_exit, self.codex_stdout, self.codex_stderr
            )
        if args == ("python3", "-m", "pytest", "-q"):
            return CommandResult(
                self.tests_exit,
                "700 passed\n" if self.tests_exit == 0 else "1 failed\n",
                "",
            )
        if args == ("python3", "-m", "builder.main", "doctor"):
            return CommandResult(
                self.doctor_exit,
                "Doctor passed\n" if self.doctor_exit == 0 else "",
                "Doctor failed\n" if self.doctor_exit else "",
            )
        if args == ("git", "diff", "--check"):
            return CommandResult(self.diff_exit, "", "diff error\n")
        if args == ("git", "diff", "--stat"):
            return CommandResult(
                0,
                " commands/architecture.py | 2 ++\n",
                "",
            )
        if args[:3] == ("git", "add", "--"):
            return CommandResult(0, "", "")
        if args[:2] == ("git", "commit"):
            self.commit_called += 1
            if self.commit_exit == 0:
                self.final_status = ""
            return CommandResult(
                self.commit_exit,
                "committed\n" if self.commit_exit == 0 else "",
                "commit failed\n" if self.commit_exit else "",
            )
        raise AssertionError("unexpected command: {}".format(args))


def workflow_fixture(
    repository: Path,
    *,
    authorization=True,
    proof=True,
    allowed_actions=("modify_authorized_repository",),
    authorized_branch="main",
    authorization_schema="1.2",
    create_commit=False,
    prompt_text=None,
    proof_create_commit=None,
    proof_push_forbidden=True,
    proof_schema="1.1",
):
    root = repository / "knowledge" / "architecture_workflows"
    folder = root / WORKFLOW
    for name in ("proposals", "analyses", "decisions", "prompts"):
        (folder / name).mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": "2.0",
        "workflow_id": WORKFLOW,
        "created_at": NOW.isoformat(),
        "proposal_ids": ["proposal-a"],
        "proposal_files": ["proposals/proposal-a.json"],
        "analysis_files": ["analyses/proposal-a.json"],
        "decision_template_files": [],
        "topic": "Orchestration test",
        "decision_template_file": "decision_proposals/decision-proposal.md",
    }
    (folder / "workflow.json").write_text(json.dumps(manifest))
    decision = {
        "decision_id": "decision-a",
        "proposal_id": "proposal-a",
        "decision": "ADOPT",
        "accepted_elements": ["approved"],
        "modified_elements": [],
        "rejected_elements": [],
        "deferred_elements": [],
        "rationale": "approved",
        "decided_by": "Chief Architect",
        "decided_at": NOW.isoformat(),
    }
    (folder / "decisions" / "proposal-a.json").write_text(
        json.dumps(decision)
    )
    prompt = prompt_text or (
        "# Task\n\n"
        + (
            "Create exactly one commit only after all required validations "
            "pass.\n"
            if create_commit
            else (
                "Do not create a commit.\n"
                "Do not stage files.\n"
                "Leave validated changes in the working tree.\n"
            )
        )
        + "Do not push.\n"
    )
    prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
    (folder / "prompts" / "codex-prompt.md").write_text(prompt)
    if proof:
        proof_commit = (
            create_commit
            if proof_create_commit is None else proof_create_commit
        )
        proof_data = {
            "schema_version": proof_schema,
            "workflow_id": WORKFLOW,
            "prompt_path": "prompts/codex-prompt.md",
            "prompt_hash": prompt_hash,
            "decision_ids": ["decision-a"],
        }
        if proof_schema == "1.1":
            proof_data.update(
                {
                    "create_commit_authorized": proof_commit,
                    "commit_instruction": (
                        PromptCommitInstruction
                        .CREATE_EXACTLY_ONE_AFTER_VALIDATION.value
                        if proof_commit
                        else PromptCommitInstruction.DO_NOT_COMMIT.value
                    ),
                    "push_forbidden": proof_push_forbidden,
                }
            )
        (folder / "prompts" / "codex-prompt-proof.json").write_text(
            json.dumps(proof_data)
        )
    workflows = ArchitectureWorkflowStore(root)
    if authorization:
        ArchitectureFeedbackStore(workflows).write_authorization(
            ExecutionAuthorization(
                schema_version=authorization_schema,
                authorization_id=AUTHORIZATION,
                architecture_run_id=RUN,
                workflow_id=WORKFLOW,
                expected_execution_id=EXECUTION,
                decision_artifacts=("decisions/proposal-a.json",),
                approval_status=ApprovalStatus.CONFIRMED,
                codex_prompt="prompts/codex-prompt.md",
                prompt_hash=prompt_hash,
                repository=str(repository),
                expected_base_commit=BASE,
                allowed_actions=allowed_actions,
                expected_completion_artifacts=(
                    "test_result", "doctor_result", "git_status"
                ),
                authorized_at=NOW,
                authorized_branch=authorized_branch,
                create_commit=create_commit,
            )
        )
    return workflows


def orchestrator(tmp_path, runner=None, **fixture_options):
    workflows = workflow_fixture(tmp_path, **fixture_options)
    fake = runner or OrchestrationRunner(tmp_path)
    service = CodexExecutionOrchestrator(
        workflows=workflows,
        repository=tmp_path,
        runner=fake,
        clock=lambda: NOW,
        codex_resolver=lambda: "/usr/local/bin/codex",
    )
    return service, fake


def test_models_are_immutable_and_status_values_are_stable(tmp_path):
    service, runner = orchestrator(tmp_path)
    record = service.run(CodexExecutionRequest(WORKFLOW)).orchestration
    assert record.status is CodexExecutionStatus.COMMIT_READY
    assert record.commit_allowed is False
    assert record.commit_attempted is False
    assert record.result_commit is None
    assert runner.commit_called == 0
    assert "commands/architecture.py" in (
        record.validation_summary.diff_summary
    )
    assert record.to_dict()["next_step"] == "MANUAL_COMMIT_APPROVAL"
    assert record.prompt_commit_instruction == "DO_NOT_COMMIT"
    assert record.prompt_authorization_match is True
    assert record.push_forbidden is True
    with pytest.raises(FrozenInstanceError):
        record.status = CodexExecutionStatus.RUNNING
    assert tuple(item.value for item in CodexExecutionStatus) == (
        "AUTHORIZED", "QUEUED", "STARTING", "RUNNING", "VALIDATING",
        "VALIDATION_SUCCEEDED", "COMMIT_READY", "COMPLETED", "BLOCKED",
        "START_FAILED", "EXECUTION_FAILED", "VALIDATION_FAILED",
        "COMMIT_FAILED", "CANCELLED", "RECOVERY_REQUIRED",
    )


def test_request_rejects_unknown_or_traversing_workflow_ids():
    for value in ("unknown", "../workflow-0123456789abcdef"):
        with pytest.raises(ValueError):
            CodexExecutionRequest(value)


@pytest.mark.parametrize(
    "value",
    (
        "",
        "origin/main",
        "refs/heads/main",
        "feature/*",
        "HEAD",
        "a..b",
        "feature/\nbranch",
    ),
)
def test_authorized_branch_rejects_non_local_or_unsafe_names(value):
    with pytest.raises(ValueError):
        validate_local_branch_name(value)


def test_authorized_branch_accepts_normalized_local_name():
    assert validate_local_branch_name("feature/branch-bound-auth") == (
        "feature/branch-bound-auth"
    )


def test_new_authorization_rejects_commit_in_general_allowed_actions(
    tmp_path,
):
    with pytest.raises(
        ValueError,
        match="must not be derived from allowed_actions",
    ):
        workflow_fixture(
            tmp_path,
            allowed_actions=(
                "modify_authorized_repository",
                "create_commit",
            ),
        )


def test_tracked_runner_reports_process_id_and_separate_output(tmp_path):
    process_ids = []
    result = SubprocessCommandRunner().run_tracked(
        (
            sys.executable,
            "-c",
            "import sys; print('out'); print('err', file=sys.stderr)",
        ),
        cwd=tmp_path,
        process_started=process_ids.append,
        timeout_seconds=5,
    )
    assert len(process_ids) == 1 and process_ids[0] > 0
    assert result.exit_code == 0
    assert result.stdout.strip() == "out"
    assert result.stderr.strip() == "err"


def test_valid_authorized_request_reaches_commit_ready(tmp_path):
    service, fake = orchestrator(tmp_path)
    record = service.run(CodexExecutionRequest(WORKFLOW)).orchestration
    assert record.status is CodexExecutionStatus.COMMIT_READY
    assert record.validation_summary.passed
    assert fake.codex_called == 1
    assert not any(command[:2] == ("git", "push") for command in fake.commands)


@pytest.mark.parametrize(
    "options,message",
    [
        ({"authorization": False}, "authorization"),
        ({"proof": False}, "proof"),
    ],
)
def test_missing_required_authority_blocks_before_codex(
    tmp_path, options, message
):
    service, fake = orchestrator(tmp_path, **options)
    with pytest.raises((FileNotFoundError, ValueError), match=message):
        service.run(CodexExecutionRequest(WORKFLOW))
    assert fake.codex_called == 0


@pytest.mark.parametrize(
    "runner_options,expected",
    [
        ({"initial_status": " M local.txt\n"}, CodexExecutionStatus.BLOCKED),
        ({"branch": "feature"}, CodexExecutionStatus.BLOCKED),
        ({"head": "3" * 40}, CodexExecutionStatus.BLOCKED),
    ],
)
def test_repository_preflight_blocks_unsafe_state(
    tmp_path, runner_options, expected
):
    runner = OrchestrationRunner(tmp_path, **runner_options)
    service, _ = orchestrator(tmp_path, runner)
    record = service.run(CodexExecutionRequest(WORKFLOW)).orchestration
    assert record.status is expected
    assert runner.codex_called == 0


def test_branch_mismatch_has_structured_context_and_no_process(tmp_path):
    runner = OrchestrationRunner(tmp_path, branch="feature/other")
    service, _ = orchestrator(tmp_path, runner)
    record = service.run(CodexExecutionRequest(WORKFLOW)).orchestration
    assert record.status is CodexExecutionStatus.BLOCKED
    assert record.failure.code == "AUTHORIZED_BRANCH_MISMATCH"
    assert "main" in record.failure.message
    assert "feature/other" in record.failure.message
    assert WORKFLOW in record.failure.message
    assert AUTHORIZATION in record.failure.message
    assert str(tmp_path) in record.failure.message
    assert record.process.process_id is None
    assert service.executions.records(WORKFLOW) == ()
    assert runner.codex_called == 0


def test_detached_head_is_blocked_even_when_base_commit_matches(tmp_path):
    runner = OrchestrationRunner(tmp_path, branch="", head=BASE)
    service, _ = orchestrator(tmp_path, runner)
    record = service.run(CodexExecutionRequest(WORKFLOW)).orchestration
    assert record.failure.code == "DETACHED_HEAD_NOT_ALLOWED"
    assert record.process.process_id is None
    assert runner.codex_called == 0


@pytest.mark.parametrize(
    "create_commit,prompt_text,proof_create_commit,proof_push_forbidden",
    (
        (
            False,
            (
                "# Task\n"
                "Create exactly one commit only after all required "
                "validations pass.\n"
                "Do not push.\n"
            ),
            True,
            True,
        ),
        (
            True,
            (
                "# Task\n"
                "Do not create a commit.\n"
                "Do not stage files.\n"
                "Leave validated changes in the working tree.\n"
                "Do not push.\n"
            ),
            False,
            True,
        ),
        (
            False,
            (
                "# Task\n"
                "Do not create a commit.\n"
                "Do not stage files.\n"
                "Leave validated changes in the working tree.\n"
                "Do not push.\n"
                "Push the changes.\n"
            ),
            False,
            False,
        ),
        (
            False,
            (
                "# Task\n"
                "Do not create a commit.\n"
                "Do not stage files.\n"
                "Leave validated changes in the working tree.\n"
                "Create exactly one commit only after all required "
                "validations pass.\n"
                "Do not push.\n"
            ),
            False,
            True,
        ),
    ),
)
def test_prompt_authorization_mismatch_blocks_before_process_or_attempt(
    tmp_path,
    create_commit,
    prompt_text,
    proof_create_commit,
    proof_push_forbidden,
):
    service, runner = orchestrator(
        tmp_path,
        create_commit=create_commit,
        prompt_text=prompt_text,
        proof_create_commit=proof_create_commit,
        proof_push_forbidden=proof_push_forbidden,
    )
    record = service.run(CodexExecutionRequest(WORKFLOW)).orchestration
    assert record.status is CodexExecutionStatus.BLOCKED
    assert record.failure.code == "PROMPT_AUTHORIZATION_MISMATCH"
    assert record.process.process_id is None
    assert service.executions.records(WORKFLOW) == ()
    assert runner.codex_called == 0


def test_historical_inconsistent_prompt_is_blocked_without_mutation(
    tmp_path,
):
    prompt = (
        "# Legacy task\n"
        "Create one commit only after all checks pass.\n"
        "Do not push.\n"
    )
    service, runner = orchestrator(
        tmp_path,
        create_commit=False,
        prompt_text=prompt,
        proof_schema="1.0",
    )
    prompt_path = service.workflows.prompt_path(WORKFLOW)
    proof_path = service.workflows.prompt_proof_path(WORKFLOW)
    before = (prompt_path.read_bytes(), proof_path.read_bytes())
    record = service.run(CodexExecutionRequest(WORKFLOW)).orchestration
    assert record.failure.code == "PROMPT_AUTHORIZATION_MISMATCH"
    assert (prompt_path.read_bytes(), proof_path.read_bytes()) == before
    assert runner.codex_called == 0


def test_legacy_authorization_is_readable_but_not_executable_or_mutated(
    tmp_path,
):
    service, runner = orchestrator(
        tmp_path,
        authorized_branch=None,
        authorization_schema="1.0",
        allowed_actions=(
            "modify_authorized_repository",
            "create_commit",
        ),
    )
    path = service.feedback.authorization_path(WORKFLOW)
    before = path.read_bytes()
    authorization = service.feedback.authorization(WORKFLOW)
    assert authorization.legacy
    assert authorization.authorized_branch is None
    assert authorization.create_commit is False
    record = service.run(CodexExecutionRequest(WORKFLOW)).orchestration
    assert record.failure.code == "AUTHORIZED_BRANCH_MISSING"
    assert path.read_bytes() == before
    assert runner.codex_called == 0


def test_identical_terminal_request_is_idempotent(tmp_path):
    service, fake = orchestrator(tmp_path)
    first = service.run(CodexExecutionRequest(WORKFLOW)).orchestration
    second = service.run(CodexExecutionRequest(WORKFLOW)).orchestration
    assert first == second
    assert fake.codex_called == 1


def test_second_active_authorization_is_blocked(tmp_path):
    service, fake = orchestrator(tmp_path)
    record = service.run(CodexExecutionRequest(WORKFLOW)).orchestration
    service.store.path(WORKFLOW, record.orchestration_id).unlink()
    active = replace(
        record,
        orchestration_id="orchestration-aaaaaaaaaaaaaaaa",
        status=CodexExecutionStatus.RUNNING,
        completed_at=None,
        failure=None,
    )
    service.store.write(active)
    fake.codex_called = 0
    result = service.run(CodexExecutionRequest(WORKFLOW)).orchestration
    assert result.status is CodexExecutionStatus.BLOCKED
    assert fake.codex_called == 0


def test_missing_codex_is_structured_start_failure(tmp_path):
    service, fake = orchestrator(tmp_path)
    service.codex_resolver = lambda: None
    record = service.run(CodexExecutionRequest(WORKFLOW)).orchestration
    assert record.status is CodexExecutionStatus.START_FAILED
    assert record.failure.message == "Codex CLI executable was not found."
    assert fake.codex_called == 0


def test_codex_nonzero_keeps_separate_redacted_outputs(tmp_path):
    runner = OrchestrationRunner(
        tmp_path,
        codex_exit=7,
        codex_stdout="token=topsecret",
        codex_stderr="password=hunter2",
    )
    service, _ = orchestrator(tmp_path, runner)
    record = service.run(CodexExecutionRequest(WORKFLOW)).orchestration
    assert record.status is CodexExecutionStatus.EXECUTION_FAILED
    assert record.failure.failure.exit_code == 7
    assert record.failure.failure.stdout
    assert record.failure.failure.stderr
    stdout = tmp_path / record.process.stdout_path
    stderr = tmp_path / record.process.stderr_path
    assert "[REDACTED]" in stdout.read_text()
    assert "[REDACTED]" in stderr.read_text()
    assert "topsecret" not in stdout.read_text()
    assert "hunter2" not in stderr.read_text()


def test_bridge_start_error_and_timeout_are_preserved(tmp_path):
    failure = ExecutionFailure(
        kind=ExecutionFailureKind.TIMEOUT,
        step=ExecutionStep.CODEX_EXECUTION,
        program="codex",
        arguments=("exec",),
        working_directory=str(tmp_path),
        exit_code=None,
        stdout="",
        stderr="",
        exception_type="TimeoutExpired",
        exception_message="timeout",
        technical_cause="controlled timeout",
        occurred_at=NOW,
        execution_id=EXECUTION,
    )
    runner = OrchestrationRunner(
        tmp_path, codex_error=ExecutionBridgeError(failure)
    )
    service, _ = orchestrator(tmp_path, runner)
    record = service.run(CodexExecutionRequest(WORKFLOW)).orchestration
    assert record.status is CodexExecutionStatus.START_FAILED
    assert record.failure.failure.kind is ExecutionFailureKind.TIMEOUT


@pytest.mark.parametrize(
    "runner_options",
    [
        {"tests_exit": 1},
        {"doctor_exit": 1},
        {"diff_exit": 1},
        {"final_status": " M constitution/constitution.md\n"},
        {"pushed": True},
    ],
)
def test_validation_failures_are_terminal(tmp_path, runner_options):
    runner = OrchestrationRunner(tmp_path, **runner_options)
    service, _ = orchestrator(tmp_path, runner)
    record = service.run(CodexExecutionRequest(WORKFLOW)).orchestration
    assert record.status is CodexExecutionStatus.VALIDATION_FAILED
    assert not record.validation_summary.passed


def test_commit_is_created_only_when_explicitly_allowed(tmp_path):
    runner = OrchestrationRunner(tmp_path)
    service, _ = orchestrator(
        tmp_path,
        runner,
        create_commit=True,
    )
    record = service.run(CodexExecutionRequest(WORKFLOW)).orchestration
    assert record.status is CodexExecutionStatus.COMPLETED
    assert record.result_commit == RESULT
    assert record.commit_allowed is True
    assert record.commit_attempted is True
    assert record.prompt_commit_instruction == (
        "CREATE_EXACTLY_ONE_AFTER_VALIDATION"
    )
    assert record.prompt_authorization_match is True
    assert record.push_forbidden is True
    assert runner.commit_called == 1
    assert not any(command[:2] == ("git", "push") for command in runner.commands)


def test_commit_failure_is_structured(tmp_path):
    runner = OrchestrationRunner(tmp_path, commit_exit=1)
    service, _ = orchestrator(
        tmp_path,
        runner,
        create_commit=True,
    )
    record = service.run(CodexExecutionRequest(WORKFLOW)).orchestration
    assert record.status is CodexExecutionStatus.COMMIT_FAILED
    assert record.commit_attempted is True


def test_explicit_commit_is_not_attempted_after_failed_validation(tmp_path):
    runner = OrchestrationRunner(tmp_path, tests_exit=1)
    service, _ = orchestrator(
        tmp_path,
        runner,
        create_commit=True,
    )
    record = service.run(CodexExecutionRequest(WORKFLOW)).orchestration
    assert record.status is CodexExecutionStatus.VALIDATION_FAILED
    assert record.commit_allowed is True
    assert record.commit_attempted is False
    assert runner.commit_called == 0


def test_codex_created_commit_requires_commit_authority(tmp_path):
    runner = OrchestrationRunner(
        tmp_path, codex_creates_commit=True, final_status=""
    )
    service, _ = orchestrator(tmp_path, runner)
    record = service.run(CodexExecutionRequest(WORKFLOW)).orchestration
    assert record.status is CodexExecutionStatus.VALIDATION_FAILED


def test_codex_created_commit_is_rejected_before_authorized_commit_stage(
    tmp_path,
):
    runner = OrchestrationRunner(
        tmp_path, codex_creates_commit=True, final_status=""
    )
    service, _ = orchestrator(
        tmp_path,
        runner,
        create_commit=True,
    )
    record = service.run(CodexExecutionRequest(WORKFLOW)).orchestration
    assert record.status is CodexExecutionStatus.VALIDATION_FAILED
    assert record.result_commit is None
    assert record.commit_attempted is False
    assert runner.commit_called == 0


def test_reconstructed_execution_cannot_be_started(tmp_path, monkeypatch):
    service, fake = orchestrator(tmp_path)
    monkeypatch.setattr(
        service.executions,
        "existing",
        lambda workflow_id, execution_id: SimpleNamespace(
            origin=__import__(
                "codex_execution", fromlist=["ExecutionOrigin"]
            ).ExecutionOrigin.RECONSTRUCTED
        ),
    )
    record = service.run(CodexExecutionRequest(WORKFLOW)).orchestration
    assert record.status is CodexExecutionStatus.BLOCKED
    assert "Reconstructed" in record.failure.message
    assert fake.codex_called == 0


def test_recovery_required_does_not_restart_unknown_process(tmp_path):
    service, fake = orchestrator(tmp_path)
    auth = service.feedback.authorization(WORKFLOW)
    proof = service.workflows.prompt_proof(WORKFLOW)
    now = NOW
    record = CodexExecutionOrchestration(
        orchestration_id=service.orchestration_id(
            WORKFLOW, auth.authorization_id, proof["prompt_hash"]
        ),
        workflow_id=WORKFLOW,
        architecture_run_id=RUN,
        execution_id=EXECUTION,
        authorization_id=AUTHORIZATION,
        prompt_proof_id="prompt-proof-" + proof["prompt_hash"][:16],
        repository_path=str(tmp_path),
        branch="main",
        authorized_branch="main",
        base_commit=BASE,
        starting_git_status=(),
        starting_origin_commit=BASE,
        starting_origin_divergence="0\t0",
        status=CodexExecutionStatus.RUNNING,
        current_step=CodexExecutionStep.CODEX_EXECUTION,
        started_at=now,
        updated_at=now,
        completed_at=None,
        process=CodexExecutionProcessMetadata(
            None, ("codex", "exec"), str(tmp_path), None, None, None
        ),
        result_commit=None,
        validation_summary=None,
        failure=None,
        commit_allowed=False,
        proposed_commit_message="test",
    )
    service.store.write(record)
    result = service.run(CodexExecutionRequest(WORKFLOW)).orchestration
    assert result.status is CodexExecutionStatus.RECOVERY_REQUIRED
    assert fake.codex_called == 0


def test_terminal_store_record_cannot_be_overwritten(tmp_path):
    service, _ = orchestrator(tmp_path)
    record = service.run(CodexExecutionRequest(WORKFLOW)).orchestration
    with pytest.raises(ValueError, match="Terminal"):
        service.store.write(replace(record, updated_at=NOW.replace(hour=13)))


def test_orchestration_json_round_trip_and_ordered_listing(tmp_path):
    service, _ = orchestrator(tmp_path)
    record = service.run(CodexExecutionRequest(WORKFLOW)).orchestration
    loaded = CodexExecutionOrchestration.from_dict(record.to_dict())
    assert loaded == record
    assert service.store.records() == (record,)


def test_cli_help_and_machine_readable_status(tmp_path, monkeypatch):
    service, _ = orchestrator(tmp_path)
    record = service.run(CodexExecutionRequest(WORKFLOW)).orchestration
    monkeypatch.setattr(
        architecture_commands, "_orchestration_service", lambda: service
    )
    runner = CliRunner()
    help_result = runner.invoke(app, ["architecture", "execution", "run", "--help"])
    workflow_help = runner.invoke(app, ["architecture", "run", "--help"])
    generate_help = runner.invoke(
        app, ["architecture", "workflow", "generate-codex", "--help"]
    )
    status = runner.invoke(app, [
        "architecture", "execution", "status",
        "--orchestration-id", record.orchestration_id,
    ])
    listing = runner.invoke(app, [
        "architecture", "execution", "list",
        "--authorization-id", AUTHORIZATION,
    ])
    assert help_result.exit_code == 0
    assert workflow_help.exit_code == 0
    assert generate_help.exit_code == 0
    assert "--create-commit" in workflow_help.stdout
    assert "--no-create-commit" in workflow_help.stdout
    assert "--create-commit" in generate_help.stdout
    assert "--workflow-id" in help_result.stdout
    assert json.loads(status.stdout)["orchestration_id"] == record.orchestration_id
    assert json.loads(status.stdout)["authorized_branch"] == "main"
    assert json.loads(status.stdout)["current_branch"] == "main"
    assert json.loads(status.stdout)["branch_match"] is True
    assert json.loads(status.stdout)["create_commit_authorized"] is False
    assert json.loads(status.stdout)["commit_attempted"] is False
    assert len(json.loads(listing.stdout)["orchestrations"]) == 1


def test_operations_agent_exposes_orchestration_read_only(tmp_path):
    from architecture_integrator.operations import (
        ArchitectureOperationQuery,
        ArchitectureOperationsAgent,
        render_operation,
    )
    service, fake = orchestrator(tmp_path)
    record = service.run(CodexExecutionRequest(WORKFLOW)).orchestration
    before = service.store.path(WORKFLOW, record.orchestration_id).read_bytes()
    status = ArchitectureOperationsAgent(
        repository=tmp_path,
        workflows=service.workflows,
    ).find(ArchitectureOperationQuery(
        orchestration_id=record.orchestration_id,
        authorization_id=AUTHORIZATION,
        orchestration_status="COMMIT_READY",
    ))[0]
    assert status.orchestration_id == record.orchestration_id
    assert status.orchestration_step == "COMMIT"
    assert status.orchestration_validation is True
    assert status.authorized_branch == "main"
    assert status.current_branch == "main"
    assert status.branch_match is True
    assert status.create_commit_authorized is False
    assert status.commit_attempted is False
    assert status.prompt_commit_instruction == "DO_NOT_COMMIT"
    assert status.prompt_authorization_match is True
    assert status.push_forbidden is True
    rendered = render_operation(status)
    assert "Create Commit Authorized: no" in rendered
    assert "Commit Attempted: no" in rendered
    assert "Prompt Commit Instruction: DO_NOT_COMMIT" in rendered
    assert "Prompt/Authorization Match: yes" in rendered
    assert "Push Forbidden: yes" in rendered
    assert service.store.path(
        WORKFLOW, record.orchestration_id
    ).read_bytes() == before
    assert fake.codex_called == 1


def test_invalid_orchestration_query_status_finds_nothing(tmp_path):
    from architecture_integrator.operations import (
        ArchitectureOperationQuery,
        ArchitectureOperationQueryError,
        ArchitectureOperationsAgent,
    )
    service, _ = orchestrator(tmp_path)
    service.run(CodexExecutionRequest(WORKFLOW))
    agent = ArchitectureOperationsAgent(tmp_path, service.workflows)
    with pytest.raises(ArchitectureOperationQueryError):
        agent.find(ArchitectureOperationQuery(orchestration_status="RUNNING"))
    with pytest.raises(ValueError):
        ArchitectureOperationQuery(orchestration_status="free text")


def test_no_shell_push_or_branch_switch_is_invoked(tmp_path):
    service, fake = orchestrator(tmp_path)
    service.run(CodexExecutionRequest(WORKFLOW))
    flat = tuple(item for command in fake.commands for item in command)
    assert "push" not in flat
    assert "switch" not in flat
    assert "checkout" not in flat
    assert all(isinstance(command, tuple) for command in fake.commands)
