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
    failure_reason: Optional[str]
    retry_count: int
    push_status: str = "not_pushed"
    schema_version: str = "1.0"

    def __post_init__(self) -> None:
        if self.schema_version != "1.0":
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
            (self.failure_reason, "failure_reason"),
        ):
            _optional_text(value, name)
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
                or self.failure_reason is not None
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
            "failure_reason": self.failure_reason,
            "retry_count": self.retry_count,
            "push_status": self.push_status,
        }
