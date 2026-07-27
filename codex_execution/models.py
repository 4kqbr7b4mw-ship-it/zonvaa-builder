import hashlib
import re
from dataclasses import dataclass, replace
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Tuple


def _text(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError("{} must be a string".format(field_name))
    if (
        not value
        or value != value.strip()
        or "\n" in value
        or "\r" in value
    ):
        raise ValueError(
            "{} must be a trimmed single line".format(field_name)
        )
    return value


def _optional_text(value: object, field_name: str) -> None:
    if value is not None:
        _text(value, field_name)


def _aware(value: object, field_name: str) -> datetime:
    if not isinstance(value, datetime):
        raise TypeError("{} must be a datetime".format(field_name))
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("{} must be timezone-aware".format(field_name))
    return value


class ExecutionStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    WAITING_FOR_CAPACITY = "WAITING_FOR_CAPACITY"
    CANCELLED = "CANCELLED"


class CheckStatus(str, Enum):
    NOT_RUN = "NOT_RUN"
    PASSED = "PASSED"
    FAILED = "FAILED"


class ExecutionFailureKind(str, Enum):
    EXECUTABLE_NOT_FOUND = "EXECUTABLE_NOT_FOUND"
    WORKING_DIRECTORY_NOT_FOUND = "WORKING_DIRECTORY_NOT_FOUND"
    INPUT_NOT_FOUND = "INPUT_NOT_FOUND"
    PROCESS_START_FAILED = "PROCESS_START_FAILED"
    PROCESS_EXIT_NONZERO = "PROCESS_EXIT_NONZERO"
    TIMEOUT = "TIMEOUT"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class ExecutionStep(str, Enum):
    PROMPT_VALIDATION = "PROMPT_VALIDATION"
    REPOSITORY_INSPECTION = "REPOSITORY_INSPECTION"
    CODEX_RESOLUTION = "CODEX_RESOLUTION"
    AUTHENTICATION_CHECK = "AUTHENTICATION_CHECK"
    CODEX_EXECUTION = "CODEX_EXECUTION"
    TEST_EXECUTION = "TEST_EXECUTION"
    DOCTOR_EXECUTION = "DOCTOR_EXECUTION"
    DIFF_CHECK = "DIFF_CHECK"
    RESULT_VERIFICATION = "RESULT_VERIFICATION"
    WATCHER_SCAN = "WATCHER_SCAN"


class AttemptTrigger(str, Enum):
    INITIAL = "INITIAL"
    RETRY = "RETRY"


class RedactionStatus(str, Enum):
    PENDING = "PENDING"
    APPLIED = "APPLIED"


def execution_attempt_id(execution_id: str, attempt_number: int) -> str:
    _text(execution_id, "execution_id")
    if re.fullmatch(r"execution-[0-9a-f]{16}", execution_id) is None:
        raise ValueError("execution_id is invalid")
    if isinstance(attempt_number, bool) or not isinstance(attempt_number, int):
        raise TypeError("attempt_number must be an integer")
    if attempt_number < 1:
        raise ValueError("attempt_number must start at 1")
    digest = hashlib.sha256(
        "{}\0{}".format(execution_id, attempt_number).encode("utf-8")
    ).hexdigest()
    return "attempt-{}".format(digest[:16])


@dataclass(frozen=True)
class ExecutionFailure:
    kind: ExecutionFailureKind
    step: ExecutionStep
    program: Optional[str]
    arguments: Tuple[str, ...]
    working_directory: str
    exit_code: Optional[int]
    stdout: str
    stderr: str
    exception_type: str
    exception_message: str
    technical_cause: str
    occurred_at: datetime
    execution_id: Optional[str]

    def __post_init__(self) -> None:
        if not isinstance(self.kind, ExecutionFailureKind):
            raise TypeError("kind must be ExecutionFailureKind")
        if not isinstance(self.step, ExecutionStep):
            raise TypeError("step must be ExecutionStep")
        _optional_text(self.program, "program")
        if not isinstance(self.arguments, tuple) or not all(
            isinstance(item, str) and item for item in self.arguments
        ):
            raise TypeError("arguments must contain strings")
        for item in self.arguments:
            _text(item, "argument")
        _text(self.working_directory, "working_directory")
        if self.exit_code is not None and (
            isinstance(self.exit_code, bool)
            or not isinstance(self.exit_code, int)
        ):
            raise TypeError("exit_code must be an integer or None")
        for value, name in (
            (self.stdout, "stdout"),
            (self.stderr, "stderr"),
            (self.exception_type, "exception_type"),
            (self.exception_message, "exception_message"),
            (self.technical_cause, "technical_cause"),
        ):
            if not isinstance(value, str):
                raise TypeError("{} must be a string".format(name))
        _text(self.exception_type, "exception_type")
        if not self.exception_message:
            raise ValueError("exception_message must not be empty")
        if not self.technical_cause:
            raise ValueError("technical_cause must not be empty")
        _aware(self.occurred_at, "occurred_at")
        _optional_text(self.execution_id, "execution_id")
        if self.execution_id is not None and re.fullmatch(
            r"execution-[0-9a-f]{16}", self.execution_id
        ) is None:
            raise ValueError("execution_id is invalid")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "kind": self.kind.value,
            "step": self.step.value,
            "program": self.program,
            "arguments": list(self.arguments),
            "working_directory": self.working_directory,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "exception_type": self.exception_type,
            "exception_message": self.exception_message,
            "technical_cause": self.technical_cause,
            "occurred_at": self.occurred_at.isoformat(),
            "execution_id": self.execution_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutionFailure":
        return cls(
            kind=ExecutionFailureKind(data["kind"]),
            step=ExecutionStep(data["step"]),
            program=data["program"],
            arguments=tuple(data["arguments"]),
            working_directory=data["working_directory"],
            exit_code=data["exit_code"],
            stdout=data["stdout"],
            stderr=data["stderr"],
            exception_type=data["exception_type"],
            exception_message=data["exception_message"],
            technical_cause=data["technical_cause"],
            occurred_at=datetime.fromisoformat(data["occurred_at"]),
            execution_id=data["execution_id"],
        )


@dataclass(frozen=True)
class ExecutionAttempt:
    attempt_id: str
    execution_id: str
    attempt_number: int
    started_at: datetime
    completed_at: Optional[datetime]
    status: ExecutionStatus
    trigger: AttemptTrigger
    step: ExecutionStep
    program: Optional[str]
    arguments: Tuple[str, ...]
    working_directory: str
    exit_code: Optional[int]
    stdout: str
    stderr: str
    failure_kind: Optional[ExecutionFailureKind]
    exception_type: Optional[str]
    exception_message: Optional[str]
    technical_cause: Optional[str]
    verification_status: CheckStatus
    verification_result: Optional[str]
    redaction_status: RedactionStatus
    authorization_reference: Optional[str]

    def __post_init__(self) -> None:
        for value, name, pattern in (
            (self.attempt_id, "attempt_id", r"attempt-[0-9a-f]{16}"),
            (self.execution_id, "execution_id", r"execution-[0-9a-f]{16}"),
        ):
            _text(value, name)
            if re.fullmatch(pattern, value) is None:
                raise ValueError("{} is invalid".format(name))
        if isinstance(self.attempt_number, bool) or not isinstance(
            self.attempt_number, int
        ):
            raise TypeError("attempt_number must be an integer")
        if self.attempt_number < 1:
            raise ValueError("attempt_number must start at 1")
        _aware(self.started_at, "started_at")
        if self.completed_at is not None:
            _aware(self.completed_at, "completed_at")
            if self.completed_at < self.started_at:
                raise ValueError("completed_at precedes started_at")
        for value, expected, name in (
            (self.status, ExecutionStatus, "status"),
            (self.trigger, AttemptTrigger, "trigger"),
            (self.step, ExecutionStep, "step"),
            (self.verification_status, CheckStatus, "verification_status"),
            (self.redaction_status, RedactionStatus, "redaction_status"),
        ):
            if not isinstance(value, expected):
                raise TypeError("{} has invalid type".format(name))
        _optional_text(self.program, "program")
        if not isinstance(self.arguments, tuple):
            raise TypeError("arguments must be a tuple")
        for item in self.arguments:
            _text(item, "argument")
        _text(self.working_directory, "working_directory")
        if self.exit_code is not None and (
            isinstance(self.exit_code, bool)
            or not isinstance(self.exit_code, int)
        ):
            raise TypeError("exit_code must be an integer or None")
        for value, name in ((self.stdout, "stdout"), (self.stderr, "stderr")):
            if not isinstance(value, str):
                raise TypeError("{} must be a string".format(name))
        if self.failure_kind is not None and not isinstance(
            self.failure_kind, ExecutionFailureKind
        ):
            raise TypeError("failure_kind must be ExecutionFailureKind or None")
        _optional_text(self.exception_type, "exception_type")
        _optional_text(self.verification_result, "verification_result")
        _optional_text(
            self.authorization_reference,
            "authorization_reference",
        )
        for value, name in (
            (self.exception_message, "exception_message"),
            (self.technical_cause, "technical_cause"),
        ):
            if value is not None and (
                not isinstance(value, str) or not value
            ):
                raise ValueError("{} must be non-empty text".format(name))
        terminal = {
            ExecutionStatus.SUCCEEDED,
            ExecutionStatus.FAILED,
            ExecutionStatus.BLOCKED,
            ExecutionStatus.WAITING_FOR_CAPACITY,
            ExecutionStatus.CANCELLED,
        }
        if self.status in terminal:
            if self.completed_at is None:
                raise ValueError("Terminal attempt requires completed_at")
            if self.redaction_status is not RedactionStatus.APPLIED:
                raise ValueError("Terminal attempt requires applied redaction")
        elif self.completed_at is not None:
            raise ValueError("Non-terminal attempt cannot be completed")
        if self.status is ExecutionStatus.SUCCEEDED:
            if (
                self.exit_code != 0
                or self.failure_kind is not None
                or self.exception_type is not None
                or self.verification_status is not CheckStatus.PASSED
            ):
                raise ValueError("Successful attempt is incomplete")
        if self.status in {
            ExecutionStatus.FAILED,
            ExecutionStatus.BLOCKED,
            ExecutionStatus.WAITING_FOR_CAPACITY,
        } and (
            self.failure_kind is None
            or self.exception_type is None
            or self.exception_message is None
            or self.technical_cause is None
        ):
            raise ValueError("Failed attempt requires complete error data")

    def transition(self, **changes: Any) -> "ExecutionAttempt":
        terminal = {
            ExecutionStatus.SUCCEEDED,
            ExecutionStatus.FAILED,
            ExecutionStatus.BLOCKED,
            ExecutionStatus.WAITING_FOR_CAPACITY,
            ExecutionStatus.CANCELLED,
        }
        if self.status in terminal:
            raise ValueError("Terminal attempt cannot be changed")
        result = replace(self, **changes)
        for name in (
            "attempt_id",
            "execution_id",
            "attempt_number",
            "started_at",
            "trigger",
            "authorization_reference",
        ):
            if getattr(result, name) != getattr(self, name):
                raise ValueError("Attempt identity cannot be changed")
        if self.status is ExecutionStatus.RUNNING and result.status in {
            ExecutionStatus.PENDING,
            ExecutionStatus.RUNNING,
        }:
            raise ValueError("Running attempt cannot move backwards")
        return result

    def to_dict(self) -> Dict[str, Any]:
        return {
            "attempt_id": self.attempt_id,
            "execution_id": self.execution_id,
            "attempt_number": self.attempt_number,
            "started_at": self.started_at.isoformat(),
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "status": self.status.value,
            "trigger": self.trigger.value,
            "step": self.step.value,
            "program": self.program,
            "arguments": list(self.arguments),
            "working_directory": self.working_directory,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "failure_kind": (
                self.failure_kind.value if self.failure_kind else None
            ),
            "exception_type": self.exception_type,
            "exception_message": self.exception_message,
            "technical_cause": self.technical_cause,
            "verification_status": self.verification_status.value,
            "verification_result": self.verification_result,
            "redaction_status": self.redaction_status.value,
            "authorization_reference": self.authorization_reference,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutionAttempt":
        return cls(
            attempt_id=data["attempt_id"],
            execution_id=data["execution_id"],
            attempt_number=data["attempt_number"],
            started_at=datetime.fromisoformat(data["started_at"]),
            completed_at=(
                datetime.fromisoformat(data["completed_at"])
                if data["completed_at"] else None
            ),
            status=ExecutionStatus(data["status"]),
            trigger=AttemptTrigger(data["trigger"]),
            step=ExecutionStep(data["step"]),
            program=data["program"],
            arguments=tuple(data["arguments"]),
            working_directory=data["working_directory"],
            exit_code=data["exit_code"],
            stdout=data["stdout"],
            stderr=data["stderr"],
            failure_kind=(
                ExecutionFailureKind(data["failure_kind"])
                if data["failure_kind"] else None
            ),
            exception_type=data["exception_type"],
            exception_message=data["exception_message"],
            technical_cause=data["technical_cause"],
            verification_status=CheckStatus(data["verification_status"]),
            verification_result=data["verification_result"],
            redaction_status=RedactionStatus(data["redaction_status"]),
            authorization_reference=data["authorization_reference"],
        )


@dataclass(frozen=True)
class ExecutionPolicy:
    schema_version: str = "1.0"
    max_automatic_retries: int = 2
    retry_delay_seconds: int = 900

    def __post_init__(self) -> None:
        if self.schema_version != "1.0":
            raise ValueError("Unsupported execution policy")
        for value, name in (
            (self.max_automatic_retries, "max_automatic_retries"),
            (self.retry_delay_seconds, "retry_delay_seconds"),
        ):
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError("{} must be an integer".format(name))
            if value < 0:
                raise ValueError("{} must not be negative".format(name))


@dataclass(frozen=True)
class ExecutionRecord:
    execution_id: str
    workflow_id: str
    prompt_path: str
    prompt_hash: str
    repository_path: str
    starting_branch: str
    starting_commit: str
    starting_git_status: Tuple[str, ...]
    status: ExecutionStatus
    started_at: datetime
    completed_at: Optional[datetime]
    codex_exit_code: Optional[int]
    test_status: CheckStatus
    test_result: Optional[str]
    doctor_status: CheckStatus
    doctor_result: Optional[str]
    diff_check_status: CheckStatus
    resulting_commit: Optional[str]
    handover_paths: Tuple[str, ...]
    failure: Optional[ExecutionFailure]
    attempts: Tuple[ExecutionAttempt, ...]
    retry_count: int
    push_status: str = "not_pushed"
    schema_version: str = "1.2"

    def __post_init__(self) -> None:
        if self.schema_version != "1.2":
            raise ValueError("Unsupported execution record schema")
        for value, name in (
            (self.execution_id, "execution_id"),
            (self.workflow_id, "workflow_id"),
            (self.prompt_path, "prompt_path"),
            (self.repository_path, "repository_path"),
            (self.starting_branch, "starting_branch"),
            (self.starting_commit, "starting_commit"),
        ):
            _text(value, name)
        if re.fullmatch(r"execution-[0-9a-f]{16}", self.execution_id) is None:
            raise ValueError("execution_id is invalid")
        if re.fullmatch(r"workflow-[0-9a-f]{16}", self.workflow_id) is None:
            raise ValueError("workflow_id is invalid")
        if re.fullmatch(r"[0-9a-f]{64}", self.prompt_hash) is None:
            raise ValueError("prompt_hash must be SHA-256")
        if re.fullmatch(r"[0-9a-f]{7,64}", self.starting_commit) is None:
            raise ValueError("starting_commit is invalid")
        if not isinstance(self.starting_git_status, tuple) or not all(
            isinstance(item, str) and item
            for item in self.starting_git_status
        ):
            raise TypeError("starting_git_status must contain strings")
        if not isinstance(self.status, ExecutionStatus):
            raise TypeError("status must be ExecutionStatus")
        _aware(self.started_at, "started_at")
        if self.completed_at is not None:
            _aware(self.completed_at, "completed_at")
            if self.completed_at < self.started_at:
                raise ValueError("completed_at precedes started_at")
        if self.codex_exit_code is not None and (
            isinstance(self.codex_exit_code, bool)
            or not isinstance(self.codex_exit_code, int)
        ):
            raise TypeError("codex_exit_code must be an integer or None")
        for value, name in (
            (self.test_status, "test_status"),
            (self.doctor_status, "doctor_status"),
            (self.diff_check_status, "diff_check_status"),
        ):
            if not isinstance(value, CheckStatus):
                raise TypeError("{} must be CheckStatus".format(name))
        for value, name in (
            (self.test_result, "test_result"),
            (self.doctor_result, "doctor_result"),
            (self.resulting_commit, "resulting_commit"),
        ):
            _optional_text(value, name)
        if self.failure is not None and not isinstance(
            self.failure, ExecutionFailure
        ):
            raise TypeError("failure must be ExecutionFailure or None")
        if not isinstance(self.attempts, tuple) or not all(
            isinstance(item, ExecutionAttempt) for item in self.attempts
        ):
            raise TypeError("attempts must contain ExecutionAttempt values")
        for number, attempt in enumerate(self.attempts, start=1):
            if attempt.execution_id != self.execution_id:
                raise ValueError("Attempt belongs to another execution")
            if attempt.attempt_number != number:
                raise ValueError("Attempts must be ordered from 1")
            expected_id = execution_attempt_id(self.execution_id, number)
            if attempt.attempt_id != expected_id:
                raise ValueError("Attempt id is not deterministic")
        if self.resulting_commit is not None and re.fullmatch(
            r"[0-9a-f]{7,64}",
            self.resulting_commit,
        ) is None:
            raise ValueError("resulting_commit is invalid")
        if not isinstance(self.handover_paths, tuple) or not all(
            isinstance(item, str) and item
            for item in self.handover_paths
        ):
            raise TypeError("handover_paths must contain strings")
        if isinstance(self.retry_count, bool) or not isinstance(
            self.retry_count,
            int,
        ):
            raise TypeError("retry_count must be an integer")
        if self.retry_count < 0:
            raise ValueError("retry_count must not be negative")
        if self.push_status != "not_pushed":
            raise ValueError("Execution bridge never records a push")
        terminal = {
            ExecutionStatus.SUCCEEDED,
            ExecutionStatus.FAILED,
            ExecutionStatus.BLOCKED,
            ExecutionStatus.WAITING_FOR_CAPACITY,
            ExecutionStatus.CANCELLED,
        }
        if self.status in terminal and self.completed_at is None:
            raise ValueError("Terminal execution requires completed_at")
        if self.status is ExecutionStatus.SUCCEEDED:
            if (
                self.codex_exit_code != 0
                or self.test_status is not CheckStatus.PASSED
                or self.doctor_status is not CheckStatus.PASSED
                or self.diff_check_status is not CheckStatus.PASSED
                or self.resulting_commit is None
                or len(self.handover_paths) < 2
                or self.failure is not None
                or (
                    self.attempts
                    and self.attempts[-1].status
                    is not ExecutionStatus.SUCCEEDED
                )
            ):
                raise ValueError("Successful execution is incomplete")

    def evolve(self, **changes: Any) -> "ExecutionRecord":
        return replace(self, **changes)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "execution_id": self.execution_id,
            "workflow_id": self.workflow_id,
            "prompt_path": self.prompt_path,
            "prompt_hash": self.prompt_hash,
            "repository_path": self.repository_path,
            "starting_branch": self.starting_branch,
            "starting_commit": self.starting_commit,
            "starting_git_status": list(self.starting_git_status),
            "status": self.status.value,
            "started_at": self.started_at.isoformat(),
            "completed_at": (
                self.completed_at.isoformat()
                if self.completed_at is not None
                else None
            ),
            "codex_exit_code": self.codex_exit_code,
            "test_status": self.test_status.value,
            "test_result": self.test_result,
            "doctor_status": self.doctor_status.value,
            "doctor_result": self.doctor_result,
            "diff_check_status": self.diff_check_status.value,
            "resulting_commit": self.resulting_commit,
            "handover_paths": list(self.handover_paths),
            "failure": self.failure.to_dict() if self.failure else None,
            "attempts": [attempt.to_dict() for attempt in self.attempts],
            "retry_count": self.retry_count,
            "push_status": self.push_status,
        }
