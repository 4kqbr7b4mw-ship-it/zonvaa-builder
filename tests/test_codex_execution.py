import hashlib
import json
import os
import plistlib
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
import subprocess
from typer.testing import CliRunner

import commands.architecture as architecture_commands
from architecture_integrator import (
    ApprovalStatus,
    ArchitectureFeedbackStore,
    ArchitectureWorkflowStore,
    ExecutionAuthorization,
)
from codex_execution import (
    ArchitectureExecutionWatcher,
    AttemptTrigger,
    CheckStatus,
    CodexExecutionService,
    CommandResult,
    ExecutionPolicy,
    ExecutionRecord,
    ExecutionBridgeError,
    ExecutionAttempt,
    ExecutionFailureKind,
    ExecutionStep,
    ExecutionStatus,
    ExecutionStore,
    RedactionStatus,
    SubprocessCommandRunner,
)


NOW = datetime(2026, 7, 27, 10, 0, tzinfo=timezone.utc)
START = "1" * 40
RESULT = "2" * 40
WORKFLOW_ID = "workflow-0123456789abcdef"


class FakeRunner:
    def __init__(
        self,
        repository,
        codex_exit=0,
        codex_output="Codex completed.",
        codex_stderr="",
        tests_exit=0,
        doctor_exit=0,
        final_dirty=False,
        initial_status="",
    ):
        self.repository = repository
        self.codex_exit = codex_exit
        self.codex_output = codex_output
        self.codex_stderr = codex_stderr
        self.tests_exit = tests_exit
        self.doctor_exit = doctor_exit
        self.final_dirty = final_dirty
        self.initial_status = initial_status
        self.codex_called = False
        self.commands = []
        self.prompts = []

    def run(self, arguments, cwd, input_text=None, **kwargs):
        args = tuple(arguments)
        self.commands.append(args)
        assert cwd == self.repository
        if input_text is not None:
            self.prompts.append(input_text)
        if args[:3] == ("git", "branch", "--show-current"):
            return CommandResult(0, "main\n", "")
        if args[:3] == ("git", "rev-parse", "--show-toplevel"):
            return CommandResult(0, str(self.repository) + "\n", "")
        if args[:3] == ("git", "rev-parse", "HEAD"):
            value = (
                RESULT
                if self.codex_called and self.codex_exit == 0
                else START
            )
            return CommandResult(0, value + "\n", "")
        if args[:3] == ("git", "status", "--porcelain"):
            dirty = self.final_dirty and self.codex_called
            return CommandResult(
                0,
                " M retained.txt\n"
                if dirty
                else ("" if self.codex_called else self.initial_status),
                "",
            )
        if len(args) >= 3 and args[1:3] == ("login", "status"):
            return CommandResult(0, "Logged in\n", "")
        if "exec" in args:
            self.codex_called = True
            return CommandResult(
                self.codex_exit,
                self.codex_output,
                self.codex_stderr,
            )
        if args[1:4] == ("-m", "pytest", "-q"):
            return CommandResult(
                self.tests_exit,
                "552 passed\n" if self.tests_exit == 0 else "1 failed\n",
                "",
            )
        if args[1:4] == ("-m", "builder.main", "doctor"):
            return CommandResult(
                self.doctor_exit,
                "Doctor passed\n" if self.doctor_exit == 0 else "",
                "Doctor failed\n" if self.doctor_exit else "",
            )
        if args[:3] == ("git", "diff", "--check"):
            return CommandResult(0, "", "")
        if args[:2] == ("git", "diff-tree"):
            return CommandResult(
                0,
                "knowledge/handovers/result.json\n"
                "knowledge/handovers/result.md\n",
                "",
            )
        raise AssertionError("Unexpected command: {}".format(args))


def confirmed_workflow(
    repository: Path,
    workflow_id: str = WORKFLOW_ID,
):
    root = repository / "knowledge" / "architecture_workflows"
    folder = root / workflow_id
    for name in (
        "proposals",
        "analyses",
        "decision_proposals",
        "decisions",
        "prompts",
    ):
        (folder / name).mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": "2.0",
        "workflow_id": workflow_id,
        "created_at": NOW.isoformat(),
        "proposal_ids": ["proposal-a"],
        "proposal_files": ["proposals/proposal-a.json"],
        "analysis_files": ["analyses/proposal-a.json"],
        "decision_template_files": [],
        "topic": "Execution bridge test",
        "decision_template_file": (
            "decision_proposals/decision-proposal.md"
        ),
    }
    (folder / "workflow.json").write_text(
        json.dumps(manifest),
        encoding="utf-8",
    )
    decision = {
        "decision_id": "decision-a",
        "proposal_id": "proposal-a",
        "decision": "ADOPT",
        "accepted_elements": ["Approved test architecture."],
        "modified_elements": [],
        "rejected_elements": [],
        "deferred_elements": [],
        "rationale": "Explicit Chief Architect decision.",
        "decided_by": "Chief Architect",
        "decided_at": NOW.isoformat(),
    }
    (folder / "decisions" / "proposal-a.json").write_text(
        json.dumps(decision),
        encoding="utf-8",
    )
    prompt = "# Confirmed Codex order\n\nDo not push.\n"
    prompt_path = folder / "prompts" / "codex-prompt.md"
    prompt_path.write_text(prompt, encoding="utf-8")
    prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    (folder / "prompts" / "codex-prompt-proof.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "workflow_id": workflow_id,
                "prompt_path": "prompts/codex-prompt.md",
                "prompt_hash": prompt_hash,
                "decision_ids": ["decision-a"],
            }
        ),
        encoding="utf-8",
    )
    workflows = ArchitectureWorkflowStore(root)
    executions = ExecutionStore(workflows)
    return workflows, executions, prompt_path, prompt_hash


def service(repository, runner=None, policy=ExecutionPolicy()):
    workflows, executions, prompt_path, prompt_hash = confirmed_workflow(
        repository
    )
    fake = runner or FakeRunner(repository)
    return (
        CodexExecutionService(
            workflows=workflows,
            executions=executions,
            repository=repository,
            allowed_repository=repository,
            runner=fake,
            clock=lambda: NOW,
            codex_resolver=lambda: "/usr/local/bin/codex",
            policy=policy,
        ),
        fake,
        executions,
        prompt_path,
        prompt_hash,
    )


def feedback_authorization(bridge, prompt_hash, base_commit=START):
    return ExecutionAuthorization(
        authorization_id="authorization-0123456789abcdef",
        architecture_run_id="architecture-run-0123456789abcdef",
        workflow_id=WORKFLOW_ID,
        expected_execution_id=bridge.execution_id(
            WORKFLOW_ID, prompt_hash
        ),
        decision_artifacts=("decisions/proposal-a.json",),
        approval_status=ApprovalStatus.CONFIRMED,
        codex_prompt="prompts/codex-prompt.md",
        prompt_hash=prompt_hash,
        repository=str(bridge.repository),
        expected_base_commit=base_commit,
        allowed_actions=("create_commit", "create_handover"),
        expected_completion_artifacts=("result_commit", "json_handover"),
        authorized_at=NOW,
    )


def test_execution_status_values_are_stable_and_model_is_immutable(tmp_path):
    assert tuple(item.value for item in ExecutionStatus) == (
        "PENDING",
        "RUNNING",
        "SUCCEEDED",
        "FAILED",
        "BLOCKED",
        "WAITING_FOR_CAPACITY",
        "CANCELLED",
    )
    bridge, _, _, _, _ = service(tmp_path)
    record = bridge.execute(WORKFLOW_ID)
    with pytest.raises(FrozenInstanceError):
        record.status = ExecutionStatus.FAILED


def test_execution_identity_changes_only_with_prompt_hash(tmp_path):
    bridge, _, _, _, prompt_hash = service(tmp_path)

    first = bridge.execution_id(WORKFLOW_ID, prompt_hash)
    assert first == bridge.execution_id(WORKFLOW_ID, prompt_hash)
    assert first != bridge.execution_id(WORKFLOW_ID, "0" * 64)


def test_confirmed_workflow_executes_canonical_prompt_and_verifies_result(
    tmp_path,
):
    bridge, runner, executions, prompt_path, prompt_hash = service(tmp_path)

    record = bridge.execute(WORKFLOW_ID)

    assert record.status is ExecutionStatus.SUCCEEDED
    assert record.schema_version == "1.2"
    assert record.failure is None
    assert len(record.attempts) == 1
    attempt = record.attempts[0]
    assert attempt.attempt_number == 1
    assert attempt.attempt_id == bridge.attempt_id(record.execution_id, 1)
    assert attempt.status is ExecutionStatus.SUCCEEDED
    assert attempt.trigger is AttemptTrigger.INITIAL
    assert attempt.completed_at is not None
    assert attempt.verification_status is CheckStatus.PASSED
    assert attempt.redaction_status is RedactionStatus.APPLIED
    assert attempt.authorization_reference.endswith(prompt_hash)
    assert record.prompt_hash == prompt_hash
    assert record.resulting_commit == RESULT
    assert record.test_status is CheckStatus.PASSED
    assert record.doctor_status is CheckStatus.PASSED
    assert len(record.handover_paths) == 2
    assert runner.prompts == [prompt_path.read_text(encoding="utf-8")]
    codex_command = next(
        command for command in runner.commands if "exec" in command
    )
    assert codex_command[:4] == (
        "/usr/local/bin/codex",
        "--ask-for-approval",
        "never",
        "exec",
    )
    assert codex_command[4:] == (
        "--cd",
        str(tmp_path),
        "--sandbox",
        "workspace-write",
        "--add-dir",
        str(tmp_path / ".git"),
        "-",
    )
    assert not any(command[:2] == ("git", "push") for command in runner.commands)
    assert executions.load(
        WORKFLOW_ID,
        record.execution_id,
    ) == record


def test_unconfirmed_workflow_and_missing_decision_do_not_execute(tmp_path):
    bridge, runner, _, prompt_path, _ = service(tmp_path)
    prompt_path.unlink()
    with pytest.raises(RuntimeError, match="confirmed"):
        bridge.execute(WORKFLOW_ID)
    assert not runner.codex_called

    bridge, runner, _, _, _ = service(tmp_path / "second")
    (
        bridge.workflows.folder(WORKFLOW_ID)
        / "decisions"
        / "proposal-a.json"
    ).unlink()
    with pytest.raises(RuntimeError, match="missing"):
        bridge.execute(WORKFLOW_ID)
    assert not runner.codex_called


def test_wrong_prompt_hash_and_symlink_escape_are_blocked(tmp_path):
    bridge, runner, _, prompt_path, _ = service(tmp_path / "hash")
    prompt_path.write_text("changed", encoding="utf-8")
    with pytest.raises(ExecutionBridgeError, match="hash"):
        bridge.execute(WORKFLOW_ID)
    assert not runner.codex_called

    bridge, runner, _, prompt_path, _ = service(tmp_path / "link")
    content = prompt_path.read_text(encoding="utf-8")
    outside = tmp_path / "outside-prompt.md"
    outside.write_text(content, encoding="utf-8")
    prompt_path.unlink()
    prompt_path.symlink_to(outside)
    with pytest.raises(ExecutionBridgeError, match="symlink|escapes"):
        bridge.execute(WORKFLOW_ID)
    assert not runner.codex_called


def test_success_is_idempotent_and_parallel_lock_is_rejected(tmp_path):
    bridge, _, executions, _, prompt_hash = service(tmp_path)
    bridge.execute(WORKFLOW_ID)
    with pytest.raises(RuntimeError, match="already executed"):
        bridge.execute(WORKFLOW_ID)

    second, _, _, _, _ = service(tmp_path / "parallel")
    with second.executions.lock(WORKFLOW_ID):
        with pytest.raises(RuntimeError, match="already running"):
            second.execute(WORKFLOW_ID)


@pytest.mark.parametrize(
    "exit_code,output,status",
    (
        (2, "Codex failed.", ExecutionStatus.FAILED),
        (
            1,
            "Usage limit reached. Try again later.",
            ExecutionStatus.WAITING_FOR_CAPACITY,
        ),
    ),
)
def test_codex_failure_and_capacity_are_classified(
    tmp_path,
    exit_code,
    output,
    status,
):
    fake = FakeRunner(tmp_path, codex_exit=exit_code, codex_output=output)
    bridge, _, _, _, _ = service(tmp_path, runner=fake)

    record = bridge.execute(WORKFLOW_ID)

    assert record.status is status
    assert record.test_status is CheckStatus.NOT_RUN
    assert record.resulting_commit is None


def test_missing_cli_or_authentication_is_blocked_before_codex(tmp_path):
    bridge, runner, _, _, _ = service(tmp_path / "missing")
    bridge.codex_resolver = lambda: None
    missing = bridge.execute(WORKFLOW_ID)
    assert missing.status is ExecutionStatus.BLOCKED
    assert not runner.codex_called

    class AuthFailureRunner(FakeRunner):
        def run(self, arguments, cwd, input_text=None, **kwargs):
            if tuple(arguments)[1:3] == ("login", "status"):
                self.commands.append(tuple(arguments))
                return CommandResult(1, "", "Not logged in")
            return super().run(arguments, cwd, input_text, **kwargs)

    repository = tmp_path / "auth"
    auth_runner = AuthFailureRunner(repository)
    bridge, _, _, _, _ = service(repository, runner=auth_runner)
    blocked = bridge.execute(WORKFLOW_ID)
    assert blocked.status is ExecutionStatus.BLOCKED
    assert not auth_runner.codex_called


def test_retry_keeps_execution_identity_and_increments_counter(tmp_path):
    fake = FakeRunner(
        tmp_path,
        codex_exit=1,
        codex_output="Capacity unavailable.",
        final_dirty=True,
    )
    bridge, _, _, _, _ = service(tmp_path, runner=fake)
    first = bridge.execute(WORKFLOW_ID)
    first_attempt = first.attempts[0]

    second = bridge.execute(WORKFLOW_ID, retry=True)

    assert second.execution_id == first.execution_id
    assert second.retry_count == 1
    assert second.status is ExecutionStatus.WAITING_FOR_CAPACITY
    assert len(second.attempts) == 2
    assert second.attempts[0] == first_attempt
    assert second.attempts[1].attempt_number == 2
    assert second.attempts[1].trigger is AttemptTrigger.RETRY
    assert second.attempts[1].attempt_id == bridge.attempt_id(
        second.execution_id, 2
    )


def test_failed_tests_prevent_result_approval_and_further_commit(tmp_path):
    fake = FakeRunner(tmp_path, tests_exit=1)
    bridge, runner, _, _, _ = service(tmp_path, runner=fake)

    record = bridge.execute(WORKFLOW_ID)

    assert record.status is ExecutionStatus.FAILED
    assert record.test_status is CheckStatus.FAILED
    assert record.resulting_commit is None
    assert not any(
        command[:2] == ("git", "commit") for command in runner.commands
    )


def test_result_verification_failure_retains_redacted_codex_output(tmp_path):
    class NoCommitRunner(FakeRunner):
        def run(self, arguments, cwd, input_text=None, **kwargs):
            args = tuple(arguments)
            if args[:3] == ("git", "rev-parse", "HEAD"):
                self.commands.append(args)
                return CommandResult(0, START + "\n", "")
            return super().run(arguments, cwd, input_text, **kwargs)

    secret = "validation-secret"
    repository = tmp_path / "no-commit"
    runner = NoCommitRunner(
        repository,
        codex_output="read-only complete token={}".format(secret),
        codex_stderr="diagnostic api_key={}".format(secret),
    )
    bridge, _, _, _, _ = service(repository, runner=runner)

    record = bridge.execute(WORKFLOW_ID)

    assert record.status is ExecutionStatus.FAILED
    assert record.failure is not None
    assert record.failure.step is ExecutionStep.RESULT_VERIFICATION
    assert "read-only complete" in record.failure.stdout
    assert "diagnostic" in record.failure.stderr
    assert secret not in json.dumps(record.failure.to_dict())
    assert record.attempts[-1].step is ExecutionStep.RESULT_VERIFICATION
    assert record.attempts[-1].failure_kind is (
        ExecutionFailureKind.INTERNAL_ERROR
    )
    assert record.attempts[-1].program == "/usr/local/bin/codex"
    assert record.attempts[-1].arguments[0:3] == (
        "--ask-for-approval",
        "never",
        "exec",
    )
    assert record.attempts[-1].exit_code == 0
    assert "read-only complete" in record.attempts[-1].stdout
    assert "diagnostic" in record.attempts[-1].stderr
    assert secret not in json.dumps(record.attempts[-1].to_dict())


def test_watcher_is_idempotent_and_retries_capacity_after_delay(tmp_path):
    policy = ExecutionPolicy(
        max_automatic_retries=2,
        retry_delay_seconds=10,
    )
    fake = FakeRunner(
        tmp_path,
        codex_exit=1,
        codex_output="Capacity unavailable.",
    )
    bridge, _, _, _, _ = service(tmp_path, runner=fake, policy=policy)
    watcher = ArchitectureExecutionWatcher(
        bridge,
        clock=lambda: NOW,
    )

    assert watcher.run_once() == (
        "{}:WAITING_FOR_CAPACITY".format(WORKFLOW_ID),
    )
    assert watcher.run_once() == ()
    delayed = ArchitectureExecutionWatcher(
        bridge,
        clock=lambda: NOW + timedelta(seconds=11),
    )
    assert delayed.run_once() == (
        "{}:WAITING_FOR_CAPACITY".format(WORKFLOW_ID),
    )
    watched = bridge.status(WORKFLOW_ID)
    assert watched.retry_count == 1
    assert [attempt.attempt_number for attempt in watched.attempts] == [1, 2]
    assert watched.attempts[0].trigger is AttemptTrigger.INITIAL
    assert watched.attempts[1].trigger is AttemptTrigger.RETRY


def test_watcher_skips_legacy_workflow_without_prompt_proof(tmp_path):
    bridge, runner, _, prompt_path, _ = service(tmp_path)
    proof_path = bridge.workflows.prompt_proof_path(WORKFLOW_ID)
    proof_path.unlink()
    folder = bridge.workflows.folder(WORKFLOW_ID)
    before = {
        path.relative_to(folder): path.read_bytes()
        for path in folder.rglob("*")
        if path.is_file()
    }

    result = ArchitectureExecutionWatcher(
        bridge,
        clock=lambda: NOW,
    ).run_once()

    after = {
        path.relative_to(folder): path.read_bytes()
        for path in folder.rglob("*")
        if path.is_file()
    }
    assert result == ()
    assert runner.commands == []
    assert before == after
    assert prompt_path.read_text(encoding="utf-8") == (
        "# Confirmed Codex order\n\nDo not push.\n"
    )
    assert not (folder / "executions").exists()


def test_watcher_still_executes_workflow_with_valid_prompt_proof(tmp_path):
    bridge, runner, _, _, _ = service(tmp_path)

    result = ArchitectureExecutionWatcher(
        bridge,
        clock=lambda: NOW,
    ).run_once()

    assert result == ("{}:SUCCEEDED".format(WORKFLOW_ID),)
    assert runner.codex_called is True


def test_legacy_workflow_does_not_block_valid_workflow_in_same_scan(
    tmp_path,
):
    legacy_id = "workflow-0000000000000000"
    valid_id = "workflow-ffffffffffffffff"
    workflows, _, _, _ = confirmed_workflow(tmp_path, legacy_id)
    workflows.prompt_proof_path(legacy_id).unlink()
    workflows, executions, _, _ = confirmed_workflow(tmp_path, valid_id)
    runner = FakeRunner(tmp_path)
    bridge = CodexExecutionService(
        workflows=workflows,
        executions=executions,
        repository=tmp_path,
        allowed_repository=tmp_path,
        runner=runner,
        clock=lambda: NOW,
        codex_resolver=lambda: "/usr/local/bin/codex",
    )

    result = ArchitectureExecutionWatcher(
        bridge,
        clock=lambda: NOW,
    ).run_once()

    assert result == ("{}:SUCCEEDED".format(valid_id),)
    assert runner.codex_called is True
    assert not (
        workflows.folder(legacy_id) / "executions"
    ).exists()


def test_watcher_reports_present_but_invalid_prompt_proof(tmp_path):
    bridge, runner, _, _, _ = service(tmp_path)
    proof_path = bridge.workflows.prompt_proof_path(WORKFLOW_ID)
    proof = json.loads(proof_path.read_text(encoding="utf-8"))
    proof["prompt_hash"] = "0" * 64
    proof_path.write_text(json.dumps(proof), encoding="utf-8")

    result = ArchitectureExecutionWatcher(
        bridge,
        clock=lambda: NOW,
    ).run_once()

    prefix = "{}:ERROR:".format(WORKFLOW_ID)
    assert len(result) == 1
    assert result[0].startswith(prefix)
    failure = json.loads(result[0][len(prefix):])
    assert failure["step"] == "WATCHER_SCAN"
    assert failure["exception_type"] == "ValueError"
    assert "hash changed" in failure["exception_message"]
    assert runner.codex_called is False


def test_launchd_template_is_restart_capable_and_runs_finite_scan():
    path = (
        Path(__file__).resolve().parents[1]
        / "automation"
        / "com.zonvaa.codex-execution.plist"
    )
    with path.open("rb") as handle:
        configuration = plistlib.load(handle)

    assert configuration["RunAtLoad"] is True
    assert configuration["StartInterval"] > 0
    assert configuration["ProgramArguments"][-1] == "watch-once"
    assert (
        "/Applications/ChatGPT.app/Contents/Resources"
        in configuration["EnvironmentVariables"]["PATH"]
    )
    assert "while" not in " ".join(configuration["ProgramArguments"])


def test_reports_do_not_duplicate_the_approved_prompt(tmp_path):
    bridge, _, executions, _, _ = service(tmp_path)
    record = bridge.execute(WORKFLOW_ID)
    markdown = executions.path(
        WORKFLOW_ID,
        record.execution_id,
    ).with_suffix(".md").read_text(encoding="utf-8")

    assert "Confirmed Codex order" not in markdown
    assert record.prompt_hash in markdown


def test_service_rejects_every_other_repository(tmp_path):
    workflows = ArchitectureWorkflowStore(tmp_path / "workflows")
    with pytest.raises(ValueError, match="not authorized"):
        CodexExecutionService(
            workflows=workflows,
            executions=ExecutionStore(workflows),
            repository=tmp_path,
            allowed_repository=tmp_path / "other",
        )


def test_runner_classifies_missing_executable_and_working_directory(tmp_path):
    runner = SubprocessCommandRunner()
    with pytest.raises(ExecutionBridgeError) as missing_program:
        runner.run(
            ("zonvaa-command-that-does-not-exist", "--check"),
            cwd=tmp_path,
            step=ExecutionStep.CODEX_EXECUTION,
        )
    assert missing_program.value.failure.kind is (
        ExecutionFailureKind.EXECUTABLE_NOT_FOUND
    )
    assert missing_program.value.failure.program == (
        "zonvaa-command-that-does-not-exist"
    )
    assert missing_program.value.failure.arguments == ("--check",)

    missing_cwd = tmp_path / "missing"
    with pytest.raises(ExecutionBridgeError) as working_directory:
        runner.run(
            ("git", "status"),
            cwd=missing_cwd,
            step=ExecutionStep.REPOSITORY_INSPECTION,
        )
    assert working_directory.value.failure.kind is (
        ExecutionFailureKind.WORKING_DIRECTORY_NOT_FOUND
    )
    assert working_directory.value.failure.working_directory == str(missing_cwd)


def test_runner_classifies_timeout_with_partial_output(tmp_path, monkeypatch):
    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(
            cmd=args[0], timeout=3, output="partial out", stderr="partial err"
        )

    monkeypatch.setattr(subprocess, "run", timeout)
    with pytest.raises(ExecutionBridgeError) as captured:
        SubprocessCommandRunner().run(
            ("codex", "exec"),
            cwd=tmp_path,
            timeout_seconds=3,
            step=ExecutionStep.CODEX_EXECUTION,
        )
    failure = captured.value.failure
    assert failure.kind is ExecutionFailureKind.TIMEOUT
    assert failure.stdout == "partial out"
    assert failure.stderr == "partial err"
    assert failure.exit_code is None
    assert "TimeoutExpired" in failure.technical_cause


def test_nonzero_process_preserves_output_exit_code_and_redacts_secrets(tmp_path):
    secret = "super-secret-token"
    fake = FakeRunner(
        tmp_path,
        codex_exit=7,
        codex_output="progress\napi_key={}".format(secret),
        codex_stderr="failed\nAuthorization: Bearer {}".format(secret),
    )
    bridge, _, executions, _, _ = service(tmp_path, runner=fake)

    record = bridge.execute(WORKFLOW_ID)

    assert record.status is ExecutionStatus.FAILED
    assert record.failure is not None
    assert record.failure.kind is ExecutionFailureKind.PROCESS_EXIT_NONZERO
    assert record.failure.step is ExecutionStep.CODEX_EXECUTION
    assert record.failure.exit_code == 7
    assert "progress" in record.failure.stdout
    assert "failed" in record.failure.stderr
    assert secret not in json.dumps(record.to_dict())
    assert "[REDACTED]" in record.failure.stdout
    assert "[REDACTED]" in record.failure.stderr
    assert record.failure.to_dict() == record.failure.to_dict()
    assert record.attempts[0].stdout == record.failure.stdout
    assert record.attempts[0].stderr == record.failure.stderr
    assert record.attempts[0].exception_type == "ProcessExitError"
    assert record.attempts[0].failure_kind is (
        ExecutionFailureKind.PROCESS_EXIT_NONZERO
    )
    assert executions.load(WORKFLOW_ID, record.execution_id) == record


def test_secret_command_arguments_are_redacted(tmp_path):
    from codex_execution.errors import process_failure

    failure = process_failure(
        step=ExecutionStep.AUTHENTICATION_CHECK,
        occurred_at=NOW,
        cwd=tmp_path,
        arguments=("tool", "--api-key", "clear-secret", "--verbose"),
        exit_code=1,
        stdout="",
        stderr="token=clear-secret",
        execution_id=None,
    )

    serialized = json.dumps(failure.to_dict())
    assert "clear-secret" not in serialized
    assert failure.arguments == ("--api-key", "[REDACTED]", "--verbose")


def test_unexpected_runner_exception_is_structured_and_persisted(tmp_path):
    class ExplodingRunner(FakeRunner):
        def run(self, arguments, cwd, input_text=None, **kwargs):
            if len(arguments) >= 3 and tuple(arguments)[1:3] == (
                "login", "status"
            ):
                raise LookupError("bridge state vanished")
            return super().run(arguments, cwd, input_text, **kwargs)

    repository = tmp_path / "unexpected"
    bridge, _, executions, _, _ = service(
        repository,
        runner=ExplodingRunner(repository),
    )

    record = bridge.execute(WORKFLOW_ID)

    assert record.status is ExecutionStatus.FAILED
    assert record.failure is not None
    assert record.failure.kind is ExecutionFailureKind.INTERNAL_ERROR
    assert record.failure.exception_type == "LookupError"
    assert record.failure.exception_message == "bridge state vanished"
    assert "LookupError" in record.failure.technical_cause
    assert record.failure.execution_id == record.execution_id
    assert executions.load(WORKFLOW_ID, record.execution_id) == record


def test_missing_prompt_is_structured_as_input_failure(tmp_path):
    bridge, _, _, prompt_path, _ = service(tmp_path)
    prompt_path.unlink()

    with pytest.raises(ExecutionBridgeError) as captured:
        bridge.execute(WORKFLOW_ID)

    assert captured.value.failure.kind is ExecutionFailureKind.INPUT_NOT_FOUND
    assert captured.value.failure.step is ExecutionStep.PROMPT_VALIDATION
    assert captured.value.failure.exception_type == "RuntimeError"


def test_watcher_never_reduces_unexpected_error_to_naked_class_name(tmp_path):
    bridge, _, _, _, _ = service(tmp_path)

    def explode(workflow_id):
        raise LookupError("watcher detail")

    bridge.status = explode
    result = ArchitectureExecutionWatcher(bridge, clock=lambda: NOW).run_once()

    prefix = "{}:ERROR:".format(WORKFLOW_ID)
    assert len(result) == 1 and result[0].startswith(prefix)
    failure = json.loads(result[0][len(prefix):])
    assert failure["kind"] == "INTERNAL_ERROR"
    assert failure["step"] == "WATCHER_SCAN"
    assert failure["exception_type"] == "LookupError"
    assert failure["exception_message"] == "watcher detail"
    assert "technical_cause" in failure


def test_missing_watcher_input_is_not_classified_as_missing_executable(
    tmp_path,
):
    bridge, _, _, _, _ = service(tmp_path)

    def missing_input(workflow_id):
        raise FileNotFoundError("missing prompt proof")

    bridge.status = missing_input
    result = ArchitectureExecutionWatcher(bridge, clock=lambda: NOW).run_once()

    prefix = "{}:ERROR:".format(WORKFLOW_ID)
    failure = json.loads(result[0][len(prefix):])
    assert failure["program"] is None
    assert failure["kind"] == "INPUT_NOT_FOUND"


def test_attempt_serialization_order_and_markdown_report(tmp_path):
    fake = FakeRunner(
        tmp_path,
        codex_exit=1,
        codex_output="Capacity unavailable.",
    )
    bridge, _, executions, _, _ = service(tmp_path, runner=fake)
    bridge.execute(WORKFLOW_ID)
    record = bridge.execute(WORKFLOW_ID, retry=True)

    payload = record.to_dict()
    assert [item["attempt_number"] for item in payload["attempts"]] == [1, 2]
    assert [item["status"] for item in payload["attempts"]] == [
        "WAITING_FOR_CAPACITY",
        "WAITING_FOR_CAPACITY",
    ]
    markdown = executions.path(
        WORKFLOW_ID, record.execution_id
    ).with_suffix(".md").read_text(encoding="utf-8")
    assert "- Attempts: `2`" in markdown
    assert markdown.index("### Attempt 1") < markdown.index("### Attempt 2")


def test_terminal_attempt_cannot_be_replaced_in_store(tmp_path):
    bridge, _, executions, _, _ = service(tmp_path)
    record = bridge.execute(WORKFLOW_ID)
    terminal = record.attempts[0]

    with pytest.raises(ValueError, match="Terminal attempt"):
        terminal.transition(stdout="changed")

    tampered = replace(terminal, stdout="changed")
    with pytest.raises(ValueError, match="Terminal attempt"):
        executions.write(record.evolve(attempts=(tampered,)))


@pytest.mark.parametrize("legacy_schema", ("1.0", "1.1"))
def test_legacy_execution_record_loads_without_invented_attempts(
    tmp_path,
    legacy_schema,
):
    bridge, _, executions, _, _ = service(tmp_path)
    record = bridge.execute(WORKFLOW_ID)
    path = executions.path(WORKFLOW_ID, record.execution_id)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload.pop("attempts")
    payload["schema_version"] = legacy_schema
    if legacy_schema == "1.0":
        payload["failure_reason"] = None
        payload.pop("failure")
    path.write_text(json.dumps(payload), encoding="utf-8")

    legacy = executions.load(WORKFLOW_ID, record.execution_id)

    assert legacy.schema_version == "1.2"
    assert legacy.status is ExecutionStatus.SUCCEEDED
    assert legacy.attempts == ()


def test_execution_status_cli_contains_complete_attempt_history(
    tmp_path,
    monkeypatch,
):
    bridge, _, _, _, _ = service(tmp_path)
    record = bridge.execute(WORKFLOW_ID)
    monkeypatch.setattr(
        architecture_commands,
        "_execution_service",
        lambda: bridge,
    )

    result = CliRunner().invoke(
        architecture_commands.execution_app,
        ["status", "--workflow-id", WORKFLOW_ID],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["execution_id"] == record.execution_id
    assert len(payload["attempts"]) == 1
    assert payload["attempts"][0]["attempt_id"] == (
        record.attempts[0].attempt_id
    )


def test_execution_attempt_model_is_frozen_and_rejects_wrong_identity(tmp_path):
    bridge, _, _, _, _ = service(tmp_path)
    record = bridge.execute(WORKFLOW_ID)
    attempt = record.attempts[0]
    assert isinstance(attempt, ExecutionAttempt)
    with pytest.raises(FrozenInstanceError):
        attempt.status = ExecutionStatus.FAILED
    wrong = replace(attempt, execution_id="execution-0000000000000000")
    with pytest.raises(ValueError, match="another execution"):
        record.evolve(attempts=(wrong,))


def test_feedback_authorization_blocks_wrong_repository_base_before_codex(
    tmp_path,
):
    bridge, runner, _, _, prompt_hash = service(tmp_path)
    authorization = feedback_authorization(
        bridge,
        prompt_hash,
        base_commit="f" * 40,
    )
    ArchitectureFeedbackStore(bridge.workflows).write_authorization(
        authorization
    )

    with pytest.raises(ExecutionBridgeError) as raised:
        bridge.execute(WORKFLOW_ID)

    assert raised.value.failure.step is ExecutionStep.PROMPT_VALIDATION
    assert "authorized base commit" in raised.value.failure.exception_message
    assert not runner.codex_called
    assert bridge.status(WORKFLOW_ID) is None


def test_authorized_workflow_artifacts_may_cross_clean_tree_boundary(
    tmp_path,
):
    runner = FakeRunner(
        tmp_path,
        initial_status=(
            "?? knowledge/architecture_workflows/{}/feedback/\n".format(
                WORKFLOW_ID
            )
        ),
    )
    bridge, _, _, _, prompt_hash = service(tmp_path, runner=runner)
    ArchitectureFeedbackStore(bridge.workflows).write_authorization(
        feedback_authorization(bridge, prompt_hash)
    )

    record = bridge.execute(WORKFLOW_ID)

    assert record.status is ExecutionStatus.SUCCEEDED
    assert record.starting_git_status == (
        "?? knowledge/architecture_workflows/{}/feedback/".format(
            WORKFLOW_ID
        ),
    )


def test_authorization_does_not_allow_unrelated_dirty_files(tmp_path):
    runner = FakeRunner(tmp_path, initial_status=" M product.py\n")
    bridge, _, _, _, prompt_hash = service(tmp_path, runner=runner)
    ArchitectureFeedbackStore(bridge.workflows).write_authorization(
        feedback_authorization(bridge, prompt_hash)
    )

    with pytest.raises(ExecutionBridgeError) as raised:
        bridge.execute(WORKFLOW_ID)

    assert "clean working tree" in raised.value.failure.exception_message
    assert not runner.codex_called
