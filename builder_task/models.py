from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


class VetoClassification(str, Enum):
    NO_VETO = "NO_VETO"
    VETO_REQUIRED = "VETO_REQUIRED"
    HUMAN_CLASSIFICATION_REQUIRED = "HUMAN_CLASSIFICATION_REQUIRED"


class GuardStatus(str, Enum):
    ALLOWED = "ALLOWED"
    BLOCKED = "BLOCKED"


class RunResult(str, Enum):
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    INTERRUPTED = "INTERRUPTED"


class GateStatus(str, Enum):
    READY_FOR_HUMAN_REVIEW = "READY_FOR_HUMAN_REVIEW"
    BLOCKED = "BLOCKED"


class ApprovalAction(str, Enum):
    COMMIT = "COMMIT"
    PUSH = "PUSH"


@dataclass(frozen=True)
class ImmutableTask:
    task_id: str
    repository: str
    branch: str
    start_head: str
    goal: str
    allowed_paths: Tuple[str, ...]
    non_goals: Tuple[str, ...]
    veto_classification: VetoClassification
    commit_permitted: bool = False
    push_permitted: bool = False
    plan_approved_by: Optional[str] = None
    plan_approved_at: Optional[datetime] = None
    schema_version: str = "2.0"

    def __post_init__(self) -> None:
        if self.schema_version != "2.0":
            raise ValueError("Unsupported task schema")
        _id(self.task_id, "task_id", "task")
        _text(self.repository, "repository")
        if not Path(self.repository).is_absolute():
            raise ValueError("repository must be absolute")
        _branch(self.branch)
        _sha(self.start_head, "start_head")
        _text(self.goal, "goal")
        _paths(self.allowed_paths, "allowed_paths", required=True)
        _strings(self.non_goals, "non_goals")
        if not isinstance(self.veto_classification, VetoClassification):
            raise TypeError("veto_classification is invalid")
        for value, name in (
            (self.commit_permitted, "commit_permitted"),
            (self.push_permitted, "push_permitted"),
        ):
            if not isinstance(value, bool):
                raise TypeError("{} must be bool".format(name))
        if self.veto_classification is VetoClassification.VETO_REQUIRED:
            _text(self.plan_approved_by, "plan_approved_by")
            _aware(self.plan_approved_at, "plan_approved_at")
        elif self.plan_approved_by is not None or self.plan_approved_at is not None:
            raise ValueError("Plan approval is only valid for VETO_REQUIRED")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "task_id": self.task_id,
            "repository": self.repository,
            "branch": self.branch,
            "start_head": self.start_head,
            "goal": self.goal,
            "allowed_paths": list(self.allowed_paths),
            "non_goals": list(self.non_goals),
            "veto_classification": self.veto_classification.value,
            "commit_permitted": self.commit_permitted,
            "push_permitted": self.push_permitted,
            "plan_approved_by": self.plan_approved_by,
            "plan_approved_at": (
                self.plan_approved_at.isoformat()
                if self.plan_approved_at else None
            ),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ImmutableTask":
        required = {
            "schema_version", "task_id", "repository", "branch", "start_head",
            "goal", "allowed_paths", "non_goals", "veto_classification",
            "commit_permitted", "push_permitted",
        }
        missing = sorted(required.difference(data))
        if missing:
            raise ValueError("Task is missing required fields: {}".format(", ".join(missing)))
        return cls(
            schema_version=data["schema_version"],
            task_id=data["task_id"],
            repository=data["repository"],
            branch=data["branch"],
            start_head=data["start_head"],
            goal=data["goal"],
            allowed_paths=tuple(data["allowed_paths"]),
            non_goals=tuple(data["non_goals"]),
            veto_classification=VetoClassification(
                data["veto_classification"]
            ),
            commit_permitted=data["commit_permitted"],
            push_permitted=data["push_permitted"],
            plan_approved_by=data.get("plan_approved_by"),
            plan_approved_at=(
                datetime.fromisoformat(data["plan_approved_at"])
                if data.get("plan_approved_at") else None
            ),
        )


@dataclass(frozen=True)
class GuardResult:
    status: GuardStatus
    blockers: Tuple[str, ...]
    branch: str
    head: str
    git_status: Tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.status, GuardStatus):
            raise TypeError("status is invalid")
        _strings(self.blockers, "blockers")
        _text(self.branch, "branch")
        _sha(self.head, "head")
        _strings(self.git_status, "git_status")
        if self.status is GuardStatus.ALLOWED and self.blockers:
            raise ValueError("Allowed guard cannot contain blockers")
        if self.status is GuardStatus.BLOCKED and not self.blockers:
            raise ValueError("Blocked guard needs blockers")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "blockers": list(self.blockers),
            "branch": self.branch,
            "head": self.head,
            "git_status": list(self.git_status),
        }


@dataclass(frozen=True)
class RepositoryLock:
    task_id: str
    pid: int
    started_at: datetime
    repository: str

    def __post_init__(self) -> None:
        _id(self.task_id, "task_id", "task")
        if not isinstance(self.pid, int) or isinstance(self.pid, bool) or self.pid < 1:
            raise ValueError("pid must be positive")
        _aware(self.started_at, "started_at")
        _text(self.repository, "repository")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "pid": self.pid,
            "started_at": self.started_at.isoformat(),
            "repository": self.repository,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RepositoryLock":
        return cls(
            task_id=data["task_id"],
            pid=data["pid"],
            started_at=datetime.fromisoformat(data["started_at"]),
            repository=data["repository"],
        )


@dataclass(frozen=True)
class ExecutionResult:
    process_started: bool
    exit_code: Optional[int]
    stdout: str
    stderr: str
    started_at: datetime
    ended_at: datetime
    result: RunResult

    def __post_init__(self) -> None:
        if not isinstance(self.process_started, bool):
            raise TypeError("process_started must be bool")
        if self.exit_code is not None and (
            not isinstance(self.exit_code, int) or isinstance(self.exit_code, bool)
        ):
            raise TypeError("exit_code must be int or None")
        for value, name in ((self.stdout, "stdout"), (self.stderr, "stderr")):
            if not isinstance(value, str):
                raise TypeError("{} must be text".format(name))
        _aware(self.started_at, "started_at")
        _aware(self.ended_at, "ended_at")
        if not isinstance(self.result, RunResult):
            raise TypeError("result is invalid")


@dataclass(frozen=True)
class CheckResult:
    command: Tuple[str, ...]
    passed: bool
    summary: str

    def __post_init__(self) -> None:
        _strings(self.command, "command", required=True)
        if not isinstance(self.passed, bool):
            raise TypeError("passed must be bool")
        _text(self.summary, "summary")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "command": list(self.command),
            "passed": self.passed,
            "summary": self.summary,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CheckResult":
        return cls(
            command=tuple(data["command"]),
            passed=data["passed"],
            summary=data["summary"],
        )


@dataclass(frozen=True)
class GitGateResult:
    status: GateStatus
    branch_unchanged: bool
    head_unchanged: bool
    staged_paths: Tuple[str, ...]
    changed_paths: Tuple[str, ...]
    out_of_scope_paths: Tuple[str, ...]
    push_detected: bool
    diff_hash: str
    checks: Tuple[CheckResult, ...]
    blockers: Tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.status, GateStatus):
            raise TypeError("status is invalid")
        for value in (
            self.branch_unchanged,
            self.head_unchanged,
            self.push_detected,
        ):
            if not isinstance(value, bool):
                raise TypeError("gate flags must be bool")
        for values, name in (
            (self.staged_paths, "staged_paths"),
            (self.changed_paths, "changed_paths"),
            (self.out_of_scope_paths, "out_of_scope_paths"),
            (self.blockers, "blockers"),
        ):
            _strings(values, name)
        _sha256(self.diff_hash, "diff_hash")
        if not isinstance(self.checks, tuple) or not all(
            isinstance(item, CheckResult) for item in self.checks
        ):
            raise TypeError("checks must contain CheckResult")

    @property
    def passed(self) -> bool:
        return self.status is GateStatus.READY_FOR_HUMAN_REVIEW

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "branch_unchanged": self.branch_unchanged,
            "head_unchanged": self.head_unchanged,
            "staged_paths": list(self.staged_paths),
            "changed_paths": list(self.changed_paths),
            "out_of_scope_paths": list(self.out_of_scope_paths),
            "push_detected": self.push_detected,
            "diff_hash": self.diff_hash,
            "checks": [item.to_dict() for item in self.checks],
            "blockers": list(self.blockers),
            "passed": self.passed,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GitGateResult":
        return cls(
            status=GateStatus(data["status"]),
            branch_unchanged=data["branch_unchanged"],
            head_unchanged=data["head_unchanged"],
            staged_paths=tuple(data["staged_paths"]),
            changed_paths=tuple(data["changed_paths"]),
            out_of_scope_paths=tuple(data["out_of_scope_paths"]),
            push_detected=data["push_detected"],
            diff_hash=data["diff_hash"],
            checks=tuple(CheckResult.from_dict(item) for item in data["checks"]),
            blockers=tuple(data["blockers"]),
        )


@dataclass(frozen=True)
class RunReceipt:
    task_id: str
    branch: str
    start_head: str
    started_at: datetime
    ended_at: datetime
    process_started: bool
    exit_code: Optional[int]
    result: RunResult
    checks: Tuple[CheckResult, ...]
    commit_status: str
    push_status: str
    git_gate: GitGateResult
    schema_version: str = "2.0"

    def __post_init__(self) -> None:
        if self.schema_version != "2.0":
            raise ValueError("Unsupported receipt schema")
        _id(self.task_id, "task_id", "task")
        _branch(self.branch)
        _sha(self.start_head, "start_head")
        _aware(self.started_at, "started_at")
        _aware(self.ended_at, "ended_at")
        if not isinstance(self.process_started, bool):
            raise TypeError("process_started must be bool")
        if self.exit_code is not None and (
            not isinstance(self.exit_code, int) or isinstance(self.exit_code, bool)
        ):
            raise TypeError("exit_code must be int or None")
        if not isinstance(self.result, RunResult):
            raise TypeError("result is invalid")
        if not isinstance(self.checks, tuple) or not all(
            isinstance(item, CheckResult) for item in self.checks
        ):
            raise TypeError("checks must contain CheckResult")
        _text(self.commit_status, "commit_status")
        _text(self.push_status, "push_status")
        if not isinstance(self.git_gate, GitGateResult):
            raise TypeError("git_gate is required")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "task_id": self.task_id,
            "branch": self.branch,
            "start_head": self.start_head,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat(),
            "process_started": self.process_started,
            "exit_code": self.exit_code if self.exit_code is not None else "unknown",
            "result": self.result.value,
            "checks": [item.to_dict() for item in self.checks],
            "commit_status": self.commit_status,
            "push_status": self.push_status,
            "git_gate": self.git_gate.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RunReceipt":
        exit_code = data["exit_code"]
        return cls(
            schema_version=data["schema_version"],
            task_id=data["task_id"],
            branch=data["branch"],
            start_head=data["start_head"],
            started_at=datetime.fromisoformat(data["started_at"]),
            ended_at=datetime.fromisoformat(data["ended_at"]),
            process_started=data["process_started"],
            exit_code=None if exit_code == "unknown" else exit_code,
            result=RunResult(data["result"]),
            checks=tuple(CheckResult.from_dict(item) for item in data["checks"]),
            commit_status=data["commit_status"],
            push_status=data["push_status"],
            git_gate=GitGateResult.from_dict(data["git_gate"]),
        )


@dataclass(frozen=True)
class CommitApproval:
    task_id: str
    branch: str
    head: str
    diff_hash: str
    action: ApprovalAction
    approved_at: datetime
    approved_by: str

    def __post_init__(self) -> None:
        _id(self.task_id, "task_id", "task")
        _branch(self.branch)
        _sha(self.head, "head")
        _sha256(self.diff_hash, "diff_hash")
        if self.action is not ApprovalAction.COMMIT:
            raise ValueError("Commit approval action must be COMMIT")
        _aware(self.approved_at, "approved_at")
        _text(self.approved_by, "approved_by")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CommitApproval":
        return cls(
            task_id=data["task_id"],
            branch=data["branch"],
            head=data["head"],
            diff_hash=data["diff_hash"],
            action=ApprovalAction(data["action"]),
            approved_at=datetime.fromisoformat(data["approved_at"]),
            approved_by=data["approved_by"],
        )


@dataclass(frozen=True)
class PushApproval:
    task_id: str
    branch: str
    commit: str
    remote: str
    remote_branch: str
    action: ApprovalAction
    approved_at: datetime
    approved_by: str

    def __post_init__(self) -> None:
        _id(self.task_id, "task_id", "task")
        _branch(self.branch)
        _sha(self.commit, "commit")
        _text(self.remote, "remote")
        _branch(self.remote_branch)
        if self.action is not ApprovalAction.PUSH:
            raise ValueError("Push approval action must be PUSH")
        _aware(self.approved_at, "approved_at")
        _text(self.approved_by, "approved_by")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PushApproval":
        return cls(
            task_id=data["task_id"],
            branch=data["branch"],
            commit=data["commit"],
            remote=data["remote"],
            remote_branch=data["remote_branch"],
            action=ApprovalAction(data["action"]),
            approved_at=datetime.fromisoformat(data["approved_at"]),
            approved_by=data["approved_by"],
        )


def _text(value: object, name: str) -> None:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or "\x00" in value
    ):
        raise ValueError("{} must be non-empty trimmed text".format(name))


def _id(value: object, name: str, prefix: str) -> None:
    _text(value, name)
    if re.fullmatch(r"{}-[A-Za-z0-9][A-Za-z0-9._-]*".format(prefix), value) is None:
        raise ValueError("{} is invalid".format(name))


def _sha(value: object, name: str) -> None:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{40}", value) is None:
        raise ValueError("{} must be a full lowercase Git SHA".format(name))


def _sha256(value: object, name: str) -> None:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise ValueError("{} must be a lowercase SHA-256".format(name))


def _branch(value: object) -> None:
    _text(value, "branch")
    if (
        value.startswith("-")
        or value.startswith("origin/")
        or ".." in value
        or value.endswith(".")
        or any(item in value for item in ("*", "?", "[", "\\", " ", "~", "^", ":"))
    ):
        raise ValueError("branch is invalid")


def _strings(value: object, name: str, required: bool = False) -> None:
    if not isinstance(value, tuple) or not all(
        isinstance(item, str) and item and item == item.strip()
        for item in value
    ):
        raise TypeError("{} must contain strings".format(name))
    if required and not value:
        raise ValueError("{} must not be empty".format(name))


def _paths(value: object, name: str, required: bool = False) -> None:
    _strings(value, name, required)
    if tuple(sorted(set(value))) != value:
        raise ValueError("{} must be unique and sorted".format(name))
    for item in value:
        path = Path(item)
        if path.is_absolute() or ".." in path.parts or path.as_posix() != item:
            raise ValueError("{} contains unsafe path".format(name))


def _aware(value: object, name: str) -> None:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise ValueError("{} must be timezone-aware".format(name))
