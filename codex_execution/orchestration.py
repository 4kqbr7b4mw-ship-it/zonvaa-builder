from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import tempfile
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Sequence, Tuple

from architecture_integrator.feedback import (
    ApprovalStatus,
    ArchitectureFeedbackStore,
    ExecutionAuthorization,
)
from architecture_integrator.workflow import ArchitectureWorkflowStore
from codex_execution.errors import (
    ExecutionBridgeError,
    process_failure,
    redact,
)
from codex_execution.models import ExecutionFailure, ExecutionOrigin, ExecutionStep
from codex_execution.runner import CommandResult, SubprocessCommandRunner
from codex_execution.store import ExecutionStore


class CodexExecutionStatus(str, Enum):
    AUTHORIZED = "AUTHORIZED"
    QUEUED = "QUEUED"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    VALIDATING = "VALIDATING"
    VALIDATION_SUCCEEDED = "VALIDATION_SUCCEEDED"
    COMMIT_READY = "COMMIT_READY"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"
    START_FAILED = "START_FAILED"
    EXECUTION_FAILED = "EXECUTION_FAILED"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    COMMIT_FAILED = "COMMIT_FAILED"
    CANCELLED = "CANCELLED"
    RECOVERY_REQUIRED = "RECOVERY_REQUIRED"


class CodexExecutionStep(str, Enum):
    AUTHORIZATION = "AUTHORIZATION"
    REPOSITORY_PREFLIGHT = "REPOSITORY_PREFLIGHT"
    PROCESS_START = "PROCESS_START"
    CODEX_EXECUTION = "CODEX_EXECUTION"
    TESTS = "TESTS"
    DOCTOR = "DOCTOR"
    DIFF_CHECK = "DIFF_CHECK"
    RESULT_VALIDATION = "RESULT_VALIDATION"
    COMMIT = "COMMIT"
    COMPLETE = "COMPLETE"


@dataclass(frozen=True)
class CodexExecutionRequest:
    workflow_id: str

    def __post_init__(self) -> None:
        _identifier(self.workflow_id, "workflow_id", "workflow")


@dataclass(frozen=True)
class CodexExecutionProcessMetadata:
    process_id: Optional[int]
    command: Tuple[str, ...]
    working_directory: str
    exit_code: Optional[int]
    stdout_path: Optional[str]
    stderr_path: Optional[str]

    def __post_init__(self) -> None:
        if self.process_id is not None and (
            isinstance(self.process_id, bool)
            or not isinstance(self.process_id, int)
            or self.process_id < 1
        ):
            raise ValueError("process_id must be a positive integer or None")
        _strings(self.command, "command", required=False)
        _text(self.working_directory, "working_directory")
        if self.exit_code is not None and (
            isinstance(self.exit_code, bool)
            or not isinstance(self.exit_code, int)
        ):
            raise TypeError("exit_code must be an integer or None")
        _optional_text(self.stdout_path, "stdout_path")
        _optional_text(self.stderr_path, "stderr_path")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "process_id": self.process_id,
            "command": list(self.command),
            "working_directory": self.working_directory,
            "exit_code": self.exit_code,
            "stdout_path": self.stdout_path,
            "stderr_path": self.stderr_path,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CodexExecutionProcessMetadata":
        return cls(
            process_id=data["process_id"],
            command=tuple(data["command"]),
            working_directory=data["working_directory"],
            exit_code=data["exit_code"],
            stdout_path=data["stdout_path"],
            stderr_path=data["stderr_path"],
        )


@dataclass(frozen=True)
class CodexExecutionValidationResult:
    tests_passed: bool
    tests_summary: str
    doctor_passed: bool
    doctor_summary: str
    diff_check_passed: bool
    git_status: Tuple[str, ...]
    changed_files: Tuple[str, ...]
    forbidden_changes: Tuple[str, ...]
    branch_unchanged: bool
    head_changed: bool
    push_detected: bool
    diff_summary: str = ""

    def __post_init__(self) -> None:
        for value in (
            self.tests_passed,
            self.doctor_passed,
            self.diff_check_passed,
            self.branch_unchanged,
            self.head_changed,
            self.push_detected,
        ):
            if not isinstance(value, bool):
                raise TypeError("validation flags must be bool")
        if not isinstance(self.tests_summary, str):
            raise TypeError("tests_summary must be a string")
        if not isinstance(self.doctor_summary, str):
            raise TypeError("doctor_summary must be a string")
        if not isinstance(self.diff_summary, str):
            raise TypeError("diff_summary must be a string")
        _status_lines(self.git_status, "git_status")
        _strings(self.changed_files, "changed_files", required=False)
        _strings(self.forbidden_changes, "forbidden_changes", required=False)

    @property
    def passed(self) -> bool:
        return (
            self.tests_passed
            and self.doctor_passed
            and self.diff_check_passed
            and self.branch_unchanged
            and not self.forbidden_changes
            and not self.push_detected
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tests_passed": self.tests_passed,
            "tests_summary": self.tests_summary,
            "doctor_passed": self.doctor_passed,
            "doctor_summary": self.doctor_summary,
            "diff_check_passed": self.diff_check_passed,
            "git_status": list(self.git_status),
            "changed_files": list(self.changed_files),
            "forbidden_changes": list(self.forbidden_changes),
            "branch_unchanged": self.branch_unchanged,
            "head_changed": self.head_changed,
            "push_detected": self.push_detected,
            "diff_summary": self.diff_summary,
            "passed": self.passed,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CodexExecutionValidationResult":
        return cls(
            tests_passed=data["tests_passed"],
            tests_summary=data["tests_summary"],
            doctor_passed=data["doctor_passed"],
            doctor_summary=data["doctor_summary"],
            diff_check_passed=data["diff_check_passed"],
            git_status=tuple(data["git_status"]),
            changed_files=tuple(data["changed_files"]),
            forbidden_changes=tuple(data["forbidden_changes"]),
            branch_unchanged=data["branch_unchanged"],
            head_changed=data["head_changed"],
            push_detected=data["push_detected"],
            diff_summary=data.get("diff_summary", ""),
        )


@dataclass(frozen=True)
class CodexExecutionOrchestrationError:
    status: CodexExecutionStatus
    code: str
    message: str
    failure: Optional[ExecutionFailure] = None

    def __post_init__(self) -> None:
        if self.status not in {
            CodexExecutionStatus.BLOCKED,
            CodexExecutionStatus.START_FAILED,
            CodexExecutionStatus.EXECUTION_FAILED,
            CodexExecutionStatus.VALIDATION_FAILED,
            CodexExecutionStatus.COMMIT_FAILED,
            CodexExecutionStatus.CANCELLED,
            CodexExecutionStatus.RECOVERY_REQUIRED,
        }:
            raise ValueError("error status must be a failure status")
        _text(self.code, "code")
        _text(self.message, "message")
        if self.failure is not None and not isinstance(
            self.failure, ExecutionFailure
        ):
            raise TypeError("failure must be ExecutionFailure or None")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "code": self.code,
            "message": self.message,
            "failure": self.failure.to_dict() if self.failure else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CodexExecutionOrchestrationError":
        return cls(
            status=CodexExecutionStatus(data["status"]),
            code=data.get("code", "LEGACY_ORCHESTRATION_ERROR"),
            message=data["message"],
            failure=(
                ExecutionFailure.from_dict(data["failure"])
                if data["failure"] is not None
                else None
            ),
        )


@dataclass(frozen=True)
class CodexExecutionOrchestration:
    orchestration_id: str
    workflow_id: str
    architecture_run_id: str
    execution_id: str
    authorization_id: str
    prompt_proof_id: str
    repository_path: str
    branch: str
    authorized_branch: Optional[str]
    base_commit: str
    starting_git_status: Tuple[str, ...]
    starting_origin_commit: str
    starting_origin_divergence: str
    status: CodexExecutionStatus
    current_step: CodexExecutionStep
    started_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    process: CodexExecutionProcessMetadata
    result_commit: Optional[str]
    validation_summary: Optional[CodexExecutionValidationResult]
    failure: Optional[CodexExecutionOrchestrationError]
    commit_allowed: bool
    proposed_commit_message: Optional[str]
    commit_attempted: bool = False
    schema_version: str = "1.0"

    def __post_init__(self) -> None:
        if self.schema_version != "1.0":
            raise ValueError("Unsupported orchestration schema")
        for value, name, prefix in (
            (self.orchestration_id, "orchestration_id", "orchestration"),
            (self.workflow_id, "workflow_id", "workflow"),
            (self.architecture_run_id, "architecture_run_id", "architecture-run"),
            (self.execution_id, "execution_id", "execution"),
            (self.authorization_id, "authorization_id", "authorization"),
            (self.prompt_proof_id, "prompt_proof_id", "prompt-proof"),
        ):
            _identifier(value, name, prefix)
        for value, name in (
            (self.repository_path, "repository_path"),
            (self.base_commit, "base_commit"),
            (self.starting_origin_commit, "starting_origin_commit"),
            (self.starting_origin_divergence, "starting_origin_divergence"),
        ):
            _text(value, name)
        if self.branch:
            _text(self.branch, "branch")
        if self.authorized_branch is not None:
            _text(self.authorized_branch, "authorized_branch")
        if re.fullmatch(r"[0-9a-f]{40}", self.base_commit) is None:
            raise ValueError("base_commit must be a full SHA")
        if re.fullmatch(r"[0-9a-f]{40}", self.starting_origin_commit) is None:
            raise ValueError("starting_origin_commit must be a full SHA")
        _status_lines(self.starting_git_status, "starting_git_status")
        if not isinstance(self.status, CodexExecutionStatus):
            raise TypeError("status must be CodexExecutionStatus")
        if not isinstance(self.current_step, CodexExecutionStep):
            raise TypeError("current_step must be CodexExecutionStep")
        _aware(self.started_at, "started_at")
        _aware(self.updated_at, "updated_at")
        if self.completed_at is not None:
            _aware(self.completed_at, "completed_at")
        if not isinstance(self.process, CodexExecutionProcessMetadata):
            raise TypeError("process must be CodexExecutionProcessMetadata")
        _optional_text(self.result_commit, "result_commit")
        if self.validation_summary is not None and not isinstance(
            self.validation_summary, CodexExecutionValidationResult
        ):
            raise TypeError("validation_summary is invalid")
        if self.failure is not None and not isinstance(
            self.failure, CodexExecutionOrchestrationError
        ):
            raise TypeError("failure is invalid")
        if not isinstance(self.commit_allowed, bool):
            raise TypeError("commit_allowed must be bool")
        if not isinstance(self.commit_attempted, bool):
            raise TypeError("commit_attempted must be bool")
        _optional_text(self.proposed_commit_message, "proposed_commit_message")

    @property
    def terminal(self) -> bool:
        return self.status in {
            CodexExecutionStatus.COMPLETED,
            CodexExecutionStatus.BLOCKED,
            CodexExecutionStatus.START_FAILED,
            CodexExecutionStatus.EXECUTION_FAILED,
            CodexExecutionStatus.VALIDATION_FAILED,
            CodexExecutionStatus.COMMIT_FAILED,
            CodexExecutionStatus.CANCELLED,
            CodexExecutionStatus.RECOVERY_REQUIRED,
        } or (
            self.status is CodexExecutionStatus.COMMIT_READY
            and not self.commit_allowed
        )

    def evolve(self, **changes: Any) -> "CodexExecutionOrchestration":
        return replace(self, **changes)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "orchestration_id": self.orchestration_id,
            "workflow_id": self.workflow_id,
            "architecture_run_id": self.architecture_run_id,
            "execution_id": self.execution_id,
            "authorization_id": self.authorization_id,
            "prompt_proof_id": self.prompt_proof_id,
            "repository_path": self.repository_path,
            "branch": self.branch,
            "current_branch": self.branch,
            "authorized_branch": self.authorized_branch,
            "branch_match": (
                self.authorized_branch is not None
                and self.branch == self.authorized_branch
            ),
            "base_commit": self.base_commit,
            "starting_git_status": list(self.starting_git_status),
            "starting_origin_commit": self.starting_origin_commit,
            "starting_origin_divergence": self.starting_origin_divergence,
            "status": self.status.value,
            "current_step": self.current_step.value,
            "started_at": self.started_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "process_id": self.process.process_id,
            "command": list(self.process.command),
            "exit_code": self.process.exit_code,
            "stdout_path": self.process.stdout_path,
            "stderr_path": self.process.stderr_path,
            "process": self.process.to_dict(),
            "result_commit": self.result_commit,
            "validation_summary": (
                self.validation_summary.to_dict()
                if self.validation_summary else None
            ),
            "failure": self.failure.to_dict() if self.failure else None,
            "commit_allowed": self.commit_allowed,
            "create_commit_authorized": self.commit_allowed,
            "commit_attempted": self.commit_attempted,
            "proposed_commit_message": self.proposed_commit_message,
            "next_step": (
                "MANUAL_COMMIT_APPROVAL"
                if self.status is CodexExecutionStatus.COMMIT_READY
                and not self.commit_allowed
                else "COMPLETE"
                if self.status is CodexExecutionStatus.COMPLETED
                else "NONE"
                if self.terminal
                else self.current_step.value
            ),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CodexExecutionOrchestration":
        return cls(
            schema_version=data["schema_version"],
            orchestration_id=data["orchestration_id"],
            workflow_id=data["workflow_id"],
            architecture_run_id=data["architecture_run_id"],
            execution_id=data["execution_id"],
            authorization_id=data["authorization_id"],
            prompt_proof_id=data["prompt_proof_id"],
            repository_path=data["repository_path"],
            branch=data["branch"],
            authorized_branch=data.get("authorized_branch"),
            base_commit=data["base_commit"],
            starting_git_status=tuple(data["starting_git_status"]),
            starting_origin_commit=data["starting_origin_commit"],
            starting_origin_divergence=data["starting_origin_divergence"],
            status=CodexExecutionStatus(data["status"]),
            current_step=CodexExecutionStep(data["current_step"]),
            started_at=datetime.fromisoformat(data["started_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            completed_at=(
                datetime.fromisoformat(data["completed_at"])
                if data["completed_at"] else None
            ),
            process=CodexExecutionProcessMetadata.from_dict(data["process"]),
            result_commit=data["result_commit"],
            validation_summary=(
                CodexExecutionValidationResult.from_dict(
                    data["validation_summary"]
                )
                if data["validation_summary"] else None
            ),
            failure=(
                CodexExecutionOrchestrationError.from_dict(data["failure"])
                if data["failure"] else None
            ),
            commit_allowed=data["commit_allowed"],
            proposed_commit_message=data["proposed_commit_message"],
            commit_attempted=data.get("commit_attempted", False),
        )


@dataclass(frozen=True)
class CodexExecutionResult:
    orchestration: CodexExecutionOrchestration

    def __post_init__(self) -> None:
        if not isinstance(self.orchestration, CodexExecutionOrchestration):
            raise TypeError("orchestration is required")


class CodexExecutionOrchestrationStore:
    def __init__(self, workflows: ArchitectureWorkflowStore) -> None:
        self.workflows = workflows

    def folder(self, workflow_id: str, create: bool = True) -> Path:
        folder = self.workflows.folder(workflow_id) / "executions" / "orchestrations"
        if create:
            folder.mkdir(parents=True, exist_ok=True)
        if folder.is_symlink():
            raise ValueError("Orchestration folder cannot be a symlink")
        return folder

    def path(self, workflow_id: str, orchestration_id: str) -> Path:
        _identifier(orchestration_id, "orchestration_id", "orchestration")
        return self.folder(workflow_id, create=False) / "{}.json".format(
            orchestration_id
        )

    def existing(
        self, workflow_id: str, orchestration_id: str
    ) -> Optional[CodexExecutionOrchestration]:
        path = self.path(workflow_id, orchestration_id)
        if not path.is_file():
            return None
        return CodexExecutionOrchestration.from_dict(
            json.loads(path.read_text(encoding="utf-8"))
        )

    def records(
        self, workflow_id: Optional[str] = None
    ) -> Tuple[CodexExecutionOrchestration, ...]:
        workflow_ids = (
            (workflow_id,)
            if workflow_id is not None
            else tuple(
                path.name for path in sorted(self.workflows.root.glob("workflow-*"))
                if path.is_dir() and not path.is_symlink()
            )
        )
        records = []
        for item in workflow_ids:
            folder = self.workflows.root / item / "executions" / "orchestrations"
            if not folder.is_dir() or folder.is_symlink():
                continue
            for path in sorted(folder.glob("orchestration-*.json")):
                if path.is_file() and not path.is_symlink():
                    records.append(CodexExecutionOrchestration.from_dict(
                        json.loads(path.read_text(encoding="utf-8"))
                    ))
        return tuple(sorted(records, key=lambda item: item.orchestration_id))

    def write(self, record: CodexExecutionOrchestration) -> Path:
        self.folder(record.workflow_id)
        path = self.path(record.workflow_id, record.orchestration_id)
        previous = self.existing(record.workflow_id, record.orchestration_id)
        if previous is not None and previous.terminal and previous != record:
            raise ValueError("Terminal orchestration cannot be changed")
        _atomic_json(path, record.to_dict())
        return path

    def output_path(
        self, record: CodexExecutionOrchestration, stream: str
    ) -> Path:
        if stream not in {"stdout", "stderr"}:
            raise ValueError("stream is invalid")
        return self.folder(record.workflow_id) / "{}.{}.log".format(
            record.orchestration_id, stream
        )

    def write_output(
        self, record: CodexExecutionOrchestration, stream: str, content: str
    ) -> Path:
        path = self.output_path(record, stream)
        _atomic_text(path, redact(content))
        return path


class CodexExecutionOrchestrator:
    CODEX_TIMEOUT_SECONDS = 3600.0

    def __init__(
        self,
        workflows: ArchitectureWorkflowStore,
        repository: Path,
        runner: SubprocessCommandRunner = SubprocessCommandRunner(),
        clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
        codex_resolver: Callable[[], Optional[str]] = lambda: shutil.which("codex"),
    ) -> None:
        self.workflows = workflows
        self.repository = repository.resolve()
        self.runner = runner
        self.clock = clock
        self.codex_resolver = codex_resolver
        self.feedback = ArchitectureFeedbackStore(workflows)
        self.store = CodexExecutionOrchestrationStore(workflows)
        self.executions = ExecutionStore(workflows)

    def orchestration_id(
        self, workflow_id: str, authorization_id: str, prompt_hash: str
    ) -> str:
        digest = hashlib.sha256(
            "{}\0{}\0{}".format(
                workflow_id, authorization_id, prompt_hash
            ).encode("utf-8")
        ).hexdigest()
        return "orchestration-{}".format(digest[:16])

    def run(self, request: CodexExecutionRequest) -> CodexExecutionResult:
        with self.executions.lock(request.workflow_id):
            return self._run_request(request)

    def _run_request(
        self, request: CodexExecutionRequest
    ) -> CodexExecutionResult:
        authorization, proof, prompt = self._authorized_input(
            request.workflow_id
        )
        orchestration_id = self.orchestration_id(
            request.workflow_id,
            authorization.authorization_id,
            proof["prompt_hash"],
        )
        existing = self.store.existing(request.workflow_id, orchestration_id)
        if existing is not None:
            if existing.terminal:
                return CodexExecutionResult(existing)
            return CodexExecutionResult(self._recover(existing))

        now = self.clock()
        branch = self._required(("git", "branch", "--show-current"))
        head = self._required(("git", "rev-parse", "HEAD"))
        status = self._lines(self._required(("git", "status", "--porcelain")))
        divergence = self._required(
            ("git", "rev-list", "--left-right", "--count", "origin/main...HEAD")
        )
        origin_commit = self._required(("git", "rev-parse", "origin/main"))
        process = CodexExecutionProcessMetadata(
            process_id=None,
            command=(),
            working_directory=str(self.repository),
            exit_code=None,
            stdout_path=None,
            stderr_path=None,
        )
        record = CodexExecutionOrchestration(
            orchestration_id=orchestration_id,
            workflow_id=request.workflow_id,
            architecture_run_id=authorization.architecture_run_id,
            execution_id=authorization.expected_execution_id,
            authorization_id=authorization.authorization_id,
            prompt_proof_id="prompt-proof-{}".format(
                proof["prompt_hash"][:16]
            ),
            repository_path=str(self.repository),
            branch=branch,
            authorized_branch=authorization.authorized_branch,
            base_commit=head,
            starting_git_status=status,
            starting_origin_commit=origin_commit,
            starting_origin_divergence=divergence,
            status=CodexExecutionStatus.AUTHORIZED,
            current_step=CodexExecutionStep.AUTHORIZATION,
            started_at=now,
            updated_at=now,
            completed_at=None,
            process=process,
            result_commit=None,
            validation_summary=None,
            failure=None,
            commit_allowed=authorization.create_commit,
            proposed_commit_message=self._commit_message(prompt),
        )
        blocker = self._preflight_blocker(record, authorization)
        if blocker:
            blocked = record.evolve(
                status=CodexExecutionStatus.BLOCKED,
                current_step=CodexExecutionStep.REPOSITORY_PREFLIGHT,
                updated_at=self.clock(),
                completed_at=self.clock(),
                failure=CodexExecutionOrchestrationError(
                    CodexExecutionStatus.BLOCKED,
                    blocker[0],
                    blocker[1],
                ),
            )
            self.store.write(blocked)
            return CodexExecutionResult(blocked)
        self.store.write(record)
        queued = record.evolve(
            status=CodexExecutionStatus.QUEUED,
            current_step=CodexExecutionStep.PROCESS_START,
            updated_at=self.clock(),
        )
        self.store.write(queued)
        return CodexExecutionResult(
            self._execute(queued, authorization, prompt)
        )

    def _execute(
        self,
        record: CodexExecutionOrchestration,
        authorization: ExecutionAuthorization,
        prompt: str,
    ) -> CodexExecutionOrchestration:
        codex = self.codex_resolver()
        if not codex:
            return self._fail(
                record,
                CodexExecutionStatus.START_FAILED,
                CodexExecutionStep.PROCESS_START,
                "Codex CLI executable was not found.",
            )
        command = (
            codex,
            "--ask-for-approval",
            "never",
            "exec",
            "--cd",
            str(self.repository),
            "--sandbox",
            "workspace-write",
            "--add-dir",
            str(self.repository / ".git"),
            "-",
        )
        starting = record.evolve(
            status=CodexExecutionStatus.STARTING,
            current_step=CodexExecutionStep.PROCESS_START,
            updated_at=self.clock(),
            process=replace(record.process, command=command),
        )
        self.store.write(starting)
        running = starting.evolve(
            status=CodexExecutionStatus.RUNNING,
            current_step=CodexExecutionStep.CODEX_EXECUTION,
            updated_at=self.clock(),
        )
        self.store.write(running)
        try:
            run_tracked = getattr(self.runner, "run_tracked", None)
            if run_tracked is not None:
                def process_started(process_id: int) -> None:
                    nonlocal running
                    running = running.evolve(
                        updated_at=self.clock(),
                        process=replace(
                            running.process, process_id=process_id
                        ),
                    )
                    self.store.write(running)

                result = run_tracked(
                    command,
                    cwd=self.repository,
                    process_started=process_started,
                    input_text=prompt,
                    step=ExecutionStep.CODEX_EXECUTION,
                    execution_id=record.execution_id,
                    timeout_seconds=self.CODEX_TIMEOUT_SECONDS,
                    sensitive_values=(prompt,),
                )
            else:
                result = self.runner.run(
                    command,
                    cwd=self.repository,
                    input_text=prompt,
                    step=ExecutionStep.CODEX_EXECUTION,
                    execution_id=record.execution_id,
                    timeout_seconds=self.CODEX_TIMEOUT_SECONDS,
                    sensitive_values=(prompt,),
                )
        except ExecutionBridgeError as error:
            status = (
                CodexExecutionStatus.START_FAILED
                if error.failure.exit_code is None
                else CodexExecutionStatus.EXECUTION_FAILED
            )
            return self._fail(
                running,
                status,
                CodexExecutionStep.CODEX_EXECUTION,
                error.failure.exception_message,
                error.failure,
            )
        stdout_path = self.store.write_output(running, "stdout", result.stdout)
        stderr_path = self.store.write_output(running, "stderr", result.stderr)
        process = replace(
            running.process,
            exit_code=result.exit_code,
            stdout_path=self._relative(stdout_path),
            stderr_path=self._relative(stderr_path),
        )
        if result.exit_code != 0:
            failure = process_failure(
                step=ExecutionStep.CODEX_EXECUTION,
                occurred_at=self.clock(),
                cwd=self.repository,
                arguments=command,
                exit_code=result.exit_code,
                stdout=result.stdout,
                stderr=result.stderr,
                execution_id=record.execution_id,
                sensitive_values=(prompt,),
            )
            return self._fail(
                running.evolve(process=process),
                CodexExecutionStatus.EXECUTION_FAILED,
                CodexExecutionStep.CODEX_EXECUTION,
                "Codex exited with code {}.".format(result.exit_code),
                failure,
            )
        validating = running.evolve(
            status=CodexExecutionStatus.VALIDATING,
            current_step=CodexExecutionStep.TESTS,
            updated_at=self.clock(),
            process=process,
        )
        self.store.write(validating)
        return self._validate(validating, authorization)

    def _validate(
        self,
        record: CodexExecutionOrchestration,
        authorization: ExecutionAuthorization,
    ) -> CodexExecutionOrchestration:
        tests = self._run(("python3", "-m", "pytest", "-q"))
        doctor = self._run(("python3", "-m", "builder.main", "doctor"))
        diff = self._run(("git", "diff", "--check"))
        diff_summary = self._required(("git", "diff", "--stat"))
        branch = self._required(("git", "branch", "--show-current"))
        head = self._required(("git", "rev-parse", "HEAD"))
        status_lines = self._lines(
            self._required(("git", "status", "--porcelain"))
        )
        changed = self._changed_files(status_lines)
        forbidden = self._forbidden_changes(
            changed, record.workflow_id
        )
        remote_after = self._required(("git", "rev-parse", "origin/main"))
        validation = CodexExecutionValidationResult(
            tests_passed=tests.exit_code == 0,
            tests_summary=self._summary(tests),
            doctor_passed=doctor.exit_code == 0,
            doctor_summary=self._summary(doctor),
            diff_check_passed=diff.exit_code == 0,
            git_status=status_lines,
            changed_files=changed,
            forbidden_changes=(
                forbidden
                + (
                    ("premature_result_commit",)
                    if head != record.base_commit
                    else ()
                )
            ),
            branch_unchanged=branch == record.branch,
            head_changed=head != record.base_commit,
            push_detected=remote_after != record.starting_origin_commit,
            diff_summary=diff_summary,
        )
        if not validation.passed:
            return self._fail(
                record.evolve(validation_summary=validation),
                CodexExecutionStatus.VALIDATION_FAILED,
                CodexExecutionStep.RESULT_VALIDATION,
                "Automatic validation failed.",
            )
        validated = record.evolve(
            status=CodexExecutionStatus.VALIDATION_SUCCEEDED,
            current_step=CodexExecutionStep.RESULT_VALIDATION,
            updated_at=self.clock(),
            validation_summary=validation,
        )
        self.store.write(validated)
        ready = validated.evolve(
            status=CodexExecutionStatus.COMMIT_READY,
            current_step=CodexExecutionStep.COMMIT,
            updated_at=self.clock(),
            completed_at=(
                self.clock() if not record.commit_allowed else None
            ),
        )
        self.store.write(ready)
        if not record.commit_allowed:
            return ready
        if validation.changed_files:
            staged = self._run(
                ("git", "add", "--") + validation.changed_files
            )
            if staged.exit_code != 0:
                return self._fail(
                    ready,
                    CodexExecutionStatus.COMMIT_FAILED,
                    CodexExecutionStep.COMMIT,
                    "Authorized staging failed: {}".format(
                        self._summary(staged)
                    ),
                )
        attempting = ready.evolve(
            commit_attempted=True,
            updated_at=self.clock(),
        )
        self.store.write(attempting)
        commit = self._run((
            "git",
            "commit",
            "-m",
            record.proposed_commit_message or "Codex result",
        ))
        if commit.exit_code != 0:
            return self._fail(
                attempting,
                CodexExecutionStatus.COMMIT_FAILED,
                CodexExecutionStep.COMMIT,
                "Authorized commit failed: {}".format(
                    self._summary(commit)
                ),
            )
        result_commit = self._required(("git", "rev-parse", "HEAD"))
        final_status = self._lines(
            self._required(("git", "status", "--porcelain"))
        )
        if final_status:
            return self._fail(
                attempting,
                CodexExecutionStatus.COMMIT_FAILED,
                CodexExecutionStep.COMMIT,
                "Working tree is not clean after commit.",
            )
        completed = attempting.evolve(
            status=CodexExecutionStatus.COMPLETED,
            current_step=CodexExecutionStep.COMPLETE,
            updated_at=self.clock(),
            completed_at=self.clock(),
            result_commit=result_commit,
        )
        self.store.write(completed)
        return completed

    def _authorized_input(
        self, workflow_id: str
    ) -> Tuple[ExecutionAuthorization, Dict[str, Any], str]:
        authorization = self.feedback.authorization(workflow_id)
        if authorization is None:
            raise ValueError("Explicit execution authorization is required")
        if authorization.approval_status is not ApprovalStatus.CONFIRMED:
            raise ValueError("Execution authorization is not confirmed")
        proof = self.workflows.prompt_proof(workflow_id)
        prompt_path = self.workflows.prompt_path(workflow_id)
        if prompt_path.is_symlink():
            raise ValueError("Codex prompt cannot be a symlink")
        prompt = prompt_path.read_text(encoding="utf-8")
        if (
            authorization.workflow_id != workflow_id
            or authorization.prompt_hash != proof["prompt_hash"]
            or authorization.codex_prompt != proof["prompt_path"]
            or Path(authorization.repository).resolve() != self.repository
        ):
            raise ValueError("Authorization, proof and repository differ")
        return authorization, proof, prompt

    def _preflight_blocker(
        self,
        record: CodexExecutionOrchestration,
        authorization: ExecutionAuthorization,
    ) -> Optional[Tuple[str, str]]:
        if authorization.authorized_branch is None:
            return (
                "AUTHORIZED_BRANCH_MISSING",
                "Legacy authorization has no authorized branch.",
            )
        if not record.branch:
            return (
                "DETACHED_HEAD_NOT_ALLOWED",
                "Detached HEAD is not allowed for Codex execution.",
            )
        if record.branch != authorization.authorized_branch:
            return (
                "AUTHORIZED_BRANCH_MISMATCH",
                (
                    "Authorized branch '{}' differs from current branch '{}'; "
                    "workflow={}, authorization={}, repository={}."
                ).format(
                    authorization.authorized_branch,
                    record.branch,
                    record.workflow_id,
                    record.authorization_id,
                    record.repository_path,
                ),
            )
        if record.base_commit != authorization.expected_base_commit:
            return (
                "AUTHORIZED_BASE_COMMIT_MISMATCH",
                "Repository HEAD differs from authorized base commit.",
            )
        if record.starting_git_status:
            return (
                "WORKING_TREE_DIRTY",
                "Execution requires a clean working tree.",
            )
        if self._has_other_active(record):
            return (
                "ACTIVE_ORCHESTRATION_EXISTS",
                "Another active orchestration exists.",
            )
        existing = self.executions.existing(
            record.workflow_id, record.execution_id
        )
        if existing is not None and existing.origin is ExecutionOrigin.RECONSTRUCTED:
            return (
                "RECONSTRUCTED_EXECUTION_NOT_RUNNABLE",
                "Reconstructed historical execution cannot be started.",
            )
        return None

    def _has_other_active(self, record: CodexExecutionOrchestration) -> bool:
        for item in self.store.records():
            if item.orchestration_id == record.orchestration_id or item.terminal:
                continue
            if (
                item.workflow_id == record.workflow_id
                or item.authorization_id == record.authorization_id
            ):
                return True
        return False

    def _recover(
        self, record: CodexExecutionOrchestration
    ) -> CodexExecutionOrchestration:
        if record.process.process_id is not None:
            try:
                os.kill(record.process.process_id, 0)
                return record
            except OSError:
                pass
        recovered = record.evolve(
            status=CodexExecutionStatus.RECOVERY_REQUIRED,
            current_step=CodexExecutionStep.RESULT_VALIDATION,
            updated_at=self.clock(),
            completed_at=self.clock(),
            failure=CodexExecutionOrchestrationError(
                CodexExecutionStatus.RECOVERY_REQUIRED,
                "PROCESS_STATE_UNKNOWN",
                "Persisted active process state cannot be reconstructed.",
            ),
        )
        self.store.write(recovered)
        return recovered

    def _fail(
        self,
        record: CodexExecutionOrchestration,
        status: CodexExecutionStatus,
        step: CodexExecutionStep,
        message: str,
        failure: Optional[ExecutionFailure] = None,
    ) -> CodexExecutionOrchestration:
        failed = record.evolve(
            status=status,
            current_step=step,
            updated_at=self.clock(),
            completed_at=self.clock(),
            failure=CodexExecutionOrchestrationError(
                status,
                "{}_{}".format(status.value, step.value),
                redact(message),
                failure,
            ),
        )
        self.store.write(failed)
        return failed

    def _run(self, arguments: Tuple[str, ...]) -> CommandResult:
        return self.runner.run(arguments, cwd=self.repository)

    def _required(self, arguments: Tuple[str, ...]) -> str:
        result = self._run(arguments)
        if result.exit_code != 0:
            raise RuntimeError(
                "{} failed: {}".format(arguments[0], self._summary(result))
            )
        return result.stdout.rstrip("\r\n")

    def _changed_files(self, lines: Tuple[str, ...]) -> Tuple[str, ...]:
        values = []
        for line in lines:
            path = line[3:] if len(line) >= 4 else line
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            values.append(path)
        return tuple(sorted(set(values)))

    def _forbidden_changes(
        self, paths: Tuple[str, ...], workflow_id: str
    ) -> Tuple[str, ...]:
        protected = (
            "constitution/",
            "governance/",
            "knowledge/architecture_review_decisions/",
            "knowledge/architecture_workflow_supersessions/",
            "knowledge/architecture_workflows/{}/feedback/".format(workflow_id),
            "knowledge/architecture_workflows/{}/prompts/".format(workflow_id),
        )
        return tuple(path for path in paths if path.startswith(protected))

    def _commit_message(self, prompt: str) -> str:
        for line in prompt.splitlines():
            if line.lower().startswith("commit-message:"):
                value = line.split(":", 1)[1].strip()
                if value:
                    return value
        return "Implement authorized Codex architecture task"

    def _summary(self, result: CommandResult) -> str:
        value = result.output.strip() or "no output"
        return redact(value)[:1000]

    def _relative(self, path: Path) -> str:
        return path.resolve().relative_to(self.repository).as_posix()

    def _lines(self, value: str) -> Tuple[str, ...]:
        return tuple(line for line in value.splitlines() if line.strip())


def _identifier(value: object, name: str, prefix: str) -> None:
    _text(value, name)
    if re.fullmatch(r"{}-[0-9a-f]{{16}}".format(prefix), value) is None:
        raise ValueError("{} is invalid".format(name))


def _text(value: object, name: str) -> None:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or "\n" in value
        or "\r" in value
        or "\x00" in value
    ):
        raise ValueError("{} must be trimmed single-line text".format(name))


def _optional_text(value: object, name: str) -> None:
    if value is not None:
        _text(value, name)


def _strings(values: object, name: str, required: bool) -> None:
    if not isinstance(values, tuple) or not all(
        isinstance(item, str) and item and item == item.strip()
        for item in values
    ):
        raise TypeError("{} must contain strings".format(name))
    if required and not values:
        raise ValueError("{} must not be empty".format(name))


def _status_lines(values: object, name: str) -> None:
    if not isinstance(values, tuple) or not all(
        isinstance(item, str)
        and item
        and "\n" not in item
        and "\r" not in item
        and "\x00" not in item
        for item in values
    ):
        raise TypeError("{} must contain git status lines".format(name))


def _aware(value: object, name: str) -> None:
    if not isinstance(value, datetime):
        raise TypeError("{} must be datetime".format(name))
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("{} must be timezone-aware".format(name))


def _atomic_json(path: Path, data: Dict[str, Any]) -> None:
    _atomic_text(
        path,
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    )


def _atomic_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        dir=str(path.parent), prefix=".orchestration-", suffix=".tmp"
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise
