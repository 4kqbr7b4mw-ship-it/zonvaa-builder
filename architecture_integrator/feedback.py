from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple

from architecture_integrator.io import write_json, write_text_atomic

if TYPE_CHECKING:
    from architecture_integrator.workflow import ArchitectureWorkflowStore


class FeedbackStatus(str, Enum):
    DECISION_CONFIRMED = "DECISION_CONFIRMED"
    EXECUTION_AUTHORIZED = "EXECUTION_AUTHORIZED"
    EXECUTION_RUNNING = "EXECUTION_RUNNING"
    EXECUTION_COMPLETED = "EXECUTION_COMPLETED"
    HANDOVER_DISCOVERED = "HANDOVER_DISCOVERED"
    HANDOVER_VALIDATED = "HANDOVER_VALIDATED"
    INTEGRATOR_REVIEW_READY = "INTEGRATOR_REVIEW_READY"
    CHIEF_ARCHITECT_DECISION_REQUIRED = (
        "CHIEF_ARCHITECT_DECISION_REQUIRED"
    )
    FAILED = "FAILED"


class ApprovalStatus(str, Enum):
    CONFIRMED = "CONFIRMED"


@dataclass(frozen=True)
class FeedbackTransition:
    status: FeedbackStatus
    occurred_at: datetime
    reference: str

    def __post_init__(self) -> None:
        if not isinstance(self.status, FeedbackStatus):
            raise TypeError("status must be FeedbackStatus")
        _aware(self.occurred_at, "occurred_at")
        _text(self.reference, "reference")

    def to_dict(self) -> Dict[str, str]:
        return {
            "status": self.status.value,
            "occurred_at": self.occurred_at.isoformat(),
            "reference": self.reference,
        }


@dataclass(frozen=True)
class FeedbackLoopRecord:
    architecture_run_id: str
    workflow_id: str
    expected_execution_id: str
    status: FeedbackStatus
    transitions: Tuple[FeedbackTransition, ...]
    execution_id: Optional[str] = None
    authorization_id: Optional[str] = None
    handover_path: Optional[str] = None
    review_id: Optional[str] = None
    schema_version: str = "1.0"

    def __post_init__(self) -> None:
        if self.schema_version != "1.0":
            raise ValueError("Unsupported feedback record schema")
        _identifier(
            self.architecture_run_id,
            "architecture_run_id",
            "architecture-run",
        )
        _identifier(self.workflow_id, "workflow_id", "workflow")
        _identifier(
            self.expected_execution_id,
            "expected_execution_id",
            "execution",
        )
        if not isinstance(self.status, FeedbackStatus):
            raise TypeError("status must be FeedbackStatus")
        if not isinstance(self.transitions, tuple) or not self.transitions:
            raise ValueError("transitions must not be empty")
        if not all(
            isinstance(item, FeedbackTransition) for item in self.transitions
        ):
            raise TypeError("transitions must contain FeedbackTransition")
        if self.transitions[-1].status is not self.status:
            raise ValueError("Last transition must match current status")
        for value, name, prefix in (
            (self.execution_id, "execution_id", "execution"),
            (self.authorization_id, "authorization_id", "authorization"),
            (self.review_id, "review_id", "review"),
        ):
            if value is not None:
                _identifier(value, name, prefix)
        if self.handover_path is not None:
            _text(self.handover_path, "handover_path")

    def advance(
        self,
        status: FeedbackStatus,
        occurred_at: datetime,
        reference: str,
        **changes: Any
    ) -> "FeedbackLoopRecord":
        if status is self.status:
            return self
        order = tuple(FeedbackStatus)
        if (
            status is not FeedbackStatus.FAILED
            and order.index(status) <= order.index(self.status)
        ):
            raise ValueError("Feedback status cannot move backwards")
        values = self.to_values()
        values.update(changes)
        values["status"] = status
        values["transitions"] = self.transitions + (
            FeedbackTransition(status, occurred_at, reference),
        )
        return FeedbackLoopRecord(**values)

    def to_values(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "architecture_run_id": self.architecture_run_id,
            "workflow_id": self.workflow_id,
            "expected_execution_id": self.expected_execution_id,
            "status": self.status,
            "transitions": self.transitions,
            "execution_id": self.execution_id,
            "authorization_id": self.authorization_id,
            "handover_path": self.handover_path,
            "review_id": self.review_id,
        }

    def to_dict(self) -> Dict[str, Any]:
        result = self.to_values()
        result["status"] = self.status.value
        result["transitions"] = [
            item.to_dict() for item in self.transitions
        ]
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FeedbackLoopRecord":
        return cls(
            schema_version=data["schema_version"],
            architecture_run_id=data["architecture_run_id"],
            workflow_id=data["workflow_id"],
            expected_execution_id=data["expected_execution_id"],
            status=FeedbackStatus(data["status"]),
            transitions=tuple(
                FeedbackTransition(
                    status=FeedbackStatus(item["status"]),
                    occurred_at=datetime.fromisoformat(item["occurred_at"]),
                    reference=item["reference"],
                )
                for item in data["transitions"]
            ),
            execution_id=data["execution_id"],
            authorization_id=data["authorization_id"],
            handover_path=data["handover_path"],
            review_id=data["review_id"],
        )


@dataclass(frozen=True)
class ExecutionAuthorization:
    authorization_id: str
    architecture_run_id: str
    workflow_id: str
    expected_execution_id: str
    decision_artifacts: Tuple[str, ...]
    approval_status: ApprovalStatus
    codex_prompt: str
    prompt_hash: str
    repository: str
    expected_base_commit: str
    allowed_actions: Tuple[str, ...]
    expected_completion_artifacts: Tuple[str, ...]
    authorized_at: datetime
    schema_version: str = "1.0"

    def __post_init__(self) -> None:
        if self.schema_version != "1.0":
            raise ValueError("Unsupported execution authorization schema")
        _identifier(self.authorization_id, "authorization_id", "authorization")
        _identifier(
            self.architecture_run_id,
            "architecture_run_id",
            "architecture-run",
        )
        _identifier(self.workflow_id, "workflow_id", "workflow")
        _identifier(
            self.expected_execution_id,
            "expected_execution_id",
            "execution",
        )
        if not isinstance(self.approval_status, ApprovalStatus):
            raise TypeError("approval_status must be ApprovalStatus")
        for value, name in (
            (self.codex_prompt, "codex_prompt"),
            (self.repository, "repository"),
        ):
            _text(value, name)
        if self.codex_prompt != "prompts/codex-prompt.md":
            raise ValueError("codex_prompt path is not canonical")
        for value, name in (
            (self.prompt_hash, "prompt_hash"),
            (self.expected_base_commit, "expected_base_commit"),
        ):
            _hex(value, name)
        _strings(self.decision_artifacts, "decision_artifacts", required=True)
        _strings(self.allowed_actions, "allowed_actions", required=True)
        _strings(
            self.expected_completion_artifacts,
            "expected_completion_artifacts",
            required=True,
        )
        _aware(self.authorized_at, "authorized_at")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "authorization_id": self.authorization_id,
            "architecture_run_id": self.architecture_run_id,
            "workflow_id": self.workflow_id,
            "expected_execution_id": self.expected_execution_id,
            "decision_artifacts": list(self.decision_artifacts),
            "approval_status": self.approval_status.value,
            "codex_prompt": self.codex_prompt,
            "prompt_hash": self.prompt_hash,
            "repository": self.repository,
            "expected_base_commit": self.expected_base_commit,
            "allowed_actions": list(self.allowed_actions),
            "expected_completion_artifacts": list(
                self.expected_completion_artifacts
            ),
            "authorized_at": self.authorized_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutionAuthorization":
        return cls(
            schema_version=data["schema_version"],
            authorization_id=data["authorization_id"],
            architecture_run_id=data["architecture_run_id"],
            workflow_id=data["workflow_id"],
            expected_execution_id=data["expected_execution_id"],
            decision_artifacts=tuple(data["decision_artifacts"]),
            approval_status=ApprovalStatus(data["approval_status"]),
            codex_prompt=data["codex_prompt"],
            prompt_hash=data["prompt_hash"],
            repository=data["repository"],
            expected_base_commit=data["expected_base_commit"],
            allowed_actions=tuple(data["allowed_actions"]),
            expected_completion_artifacts=tuple(
                data["expected_completion_artifacts"]
            ),
            authorized_at=datetime.fromisoformat(data["authorized_at"]),
        )


@dataclass(frozen=True)
class HandoverDeviation:
    code: str
    message: str

    def __post_init__(self) -> None:
        _text(self.code, "HandoverDeviation code")
        _text(self.message, "HandoverDeviation message")

    def to_dict(self) -> Dict[str, str]:
        return {"code": self.code, "message": self.message}


@dataclass(frozen=True)
class CodexHandoverIntake:
    architecture_run_id: str
    workflow_id: str
    execution_id: str
    authorization_id: str
    decision_ids: Tuple[str, ...]
    attempt_ids: Tuple[str, ...]
    starting_commit: str
    result_commit: str
    handover_path: str
    changed_files: Tuple[str, ...]
    checks: Tuple[str, ...]
    git_status: Tuple[str, ...]
    open_risks: Tuple[str, ...]
    deviations: Tuple[HandoverDeviation, ...]

    def __post_init__(self) -> None:
        _identifier(
            self.architecture_run_id,
            "architecture_run_id",
            "architecture-run",
        )
        _identifier(self.workflow_id, "workflow_id", "workflow")
        _identifier(self.execution_id, "execution_id", "execution")
        _identifier(self.authorization_id, "authorization_id", "authorization")
        for value, name in (
            (self.starting_commit, "starting_commit"),
            (self.result_commit, "result_commit"),
        ):
            _hex(value, name)
        _text(self.handover_path, "handover_path")
        for values, name in (
            (self.decision_ids, "decision_ids"),
            (self.attempt_ids, "attempt_ids"),
            (self.changed_files, "changed_files"),
            (self.checks, "checks"),
            (self.git_status, "git_status"),
            (self.open_risks, "open_risks"),
        ):
            _strings(values, name)
        if not isinstance(self.deviations, tuple) or not all(
            isinstance(item, HandoverDeviation) for item in self.deviations
        ):
            raise TypeError("deviations must contain HandoverDeviation")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": "1.0",
            "architecture_run_id": self.architecture_run_id,
            "workflow_id": self.workflow_id,
            "execution_id": self.execution_id,
            "authorization_id": self.authorization_id,
            "decision_ids": list(self.decision_ids),
            "attempt_ids": list(self.attempt_ids),
            "starting_commit": self.starting_commit,
            "result_commit": self.result_commit,
            "handover_path": self.handover_path,
            "changed_files": list(self.changed_files),
            "checks": list(self.checks),
            "git_status": list(self.git_status),
            "open_risks": list(self.open_risks),
            "deviations": [item.to_dict() for item in self.deviations],
        }


@dataclass(frozen=True)
class ArchitectureImplementationReview:
    review_id: str
    architecture_run_id: str
    workflow_id: str
    execution_id: str
    attempt_ids: Tuple[str, ...]
    recommendation: str
    original_decision_ids: Tuple[str, ...]
    codex_prompt: str
    implementation_result: str
    changed_files: Tuple[str, ...]
    checks: Tuple[str, ...]
    commit: str
    git_status: Tuple[str, ...]
    deviations: Tuple[HandoverDeviation, ...]
    open_risks: Tuple[str, ...]
    conflicts: Tuple[str, ...]
    decision_required: Tuple[str, ...]

    def __post_init__(self) -> None:
        _identifier(self.review_id, "review_id", "review")
        _identifier(
            self.architecture_run_id,
            "architecture_run_id",
            "architecture-run",
        )
        _identifier(self.workflow_id, "workflow_id", "workflow")
        _identifier(self.execution_id, "execution_id", "execution")
        if self.recommendation not in {
            "ADOPT",
            "ADOPT_WITH_CHANGES",
            "REJECT",
            "DEFER",
        }:
            raise ValueError("Review recommendation is invalid")
        for value, name in (
            (self.codex_prompt, "codex_prompt"),
            (self.implementation_result, "implementation_result"),
            (self.commit, "commit"),
        ):
            _text(value, name)
        for values, name in (
            (self.original_decision_ids, "original_decision_ids"),
            (self.attempt_ids, "attempt_ids"),
            (self.changed_files, "changed_files"),
            (self.checks, "checks"),
            (self.git_status, "git_status"),
            (self.open_risks, "open_risks"),
            (self.conflicts, "conflicts"),
            (self.decision_required, "decision_required"),
        ):
            _strings(values, name)
        if not isinstance(self.deviations, tuple):
            raise TypeError("deviations must be a tuple")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": "1.0",
            "review_id": self.review_id,
            "architecture_run_id": self.architecture_run_id,
            "workflow_id": self.workflow_id,
            "execution_id": self.execution_id,
            "attempt_ids": list(self.attempt_ids),
            "recommendation": self.recommendation,
            "original_decision_ids": list(self.original_decision_ids),
            "codex_prompt": self.codex_prompt,
            "implementation_result": self.implementation_result,
            "changed_files": list(self.changed_files),
            "checks": list(self.checks),
            "commit": self.commit,
            "git_status": list(self.git_status),
            "deviations": [item.to_dict() for item in self.deviations],
            "open_risks": list(self.open_risks),
            "conflicts": list(self.conflicts),
            "decision_required": list(self.decision_required),
        }

    def render(self) -> str:
        return "\n".join(
            (
                "# ENTSCHEIDUNGSVORLAGE",
                "",
                "## Empfehlung",
                self.recommendation,
                "",
                "## Kernaussage",
                self.implementation_result,
                "",
                "## Implementierung",
                "- Execution: `{}`".format(self.execution_id),
                "- Attempts: {}".format(
                    ", ".join(self.attempt_ids) or "legacy/none"
                ),
                "- Commit: `{}`".format(self.commit),
                "- Geänderte Dateien: {}".format(len(self.changed_files)),
                "",
                "## Prüfungen",
                _lines(self.checks),
                "",
                "## Abweichungen",
                _lines(tuple(item.message for item in self.deviations)),
                "",
                "## Konflikte",
                _lines(self.conflicts),
                "",
                "## Offene Risiken",
                _lines(self.open_risks),
                "",
                "## Entscheidung erforderlich",
                _lines(self.decision_required),
            )
        )


class ArchitectureFeedbackStore:
    def __init__(self, workflows: ArchitectureWorkflowStore) -> None:
        self.workflows = workflows

    def folder(self, workflow_id: str, create: bool = True) -> Path:
        folder = self.workflows.folder(workflow_id) / "feedback"
        if create:
            folder.mkdir(exist_ok=True)
        if folder.is_symlink():
            raise ValueError("Feedback folder cannot be a symlink")
        return folder

    def authorization_path(self, workflow_id: str) -> Path:
        return self.folder(
            workflow_id,
            create=False,
        ) / "execution-authorization.json"

    def record_path(self, workflow_id: str) -> Path:
        return self.folder(workflow_id, create=False) / "feedback-loop.json"

    def record(self, workflow_id: str) -> Optional[FeedbackLoopRecord]:
        path = self.record_path(workflow_id)
        if not path.is_file():
            return None
        return FeedbackLoopRecord.from_dict(
            json.loads(path.read_text(encoding="utf-8"))
        )

    def write_record(self, record: FeedbackLoopRecord) -> Path:
        self.folder(record.workflow_id)
        path = self.record_path(record.workflow_id)
        previous = self.record(record.workflow_id)
        if previous is not None:
            if previous == record:
                return path
            if record.transitions[:len(previous.transitions)] != (
                previous.transitions
            ):
                raise ValueError("Feedback transitions are append-only")
        self._replace_json(path, record.to_dict())
        return path

    def authorization(
        self,
        workflow_id: str,
    ) -> Optional[ExecutionAuthorization]:
        path = self.authorization_path(workflow_id)
        if not path.is_file():
            return None
        return ExecutionAuthorization.from_dict(
            json.loads(path.read_text(encoding="utf-8"))
        )

    def write_authorization(
        self,
        authorization: ExecutionAuthorization,
    ) -> Path:
        self.folder(authorization.workflow_id)
        path = self.authorization_path(authorization.workflow_id)
        return self._write_once(path, authorization.to_dict())

    def write_intake(self, intake: CodexHandoverIntake) -> Path:
        path = self.folder(intake.workflow_id) / "handover-intake.json"
        return self._write_once(path, intake.to_dict())

    def write_review(
        self,
        review: ArchitectureImplementationReview,
    ) -> Tuple[Path, Path]:
        json_path = self.folder(review.workflow_id) / "integrator-review.json"
        markdown_path = (
            self.folder(review.workflow_id) / "decision-proposal.md"
        )
        self._write_once(json_path, review.to_dict())
        content = review.render() + "\n"
        if markdown_path.exists():
            if markdown_path.read_text(encoding="utf-8") != content:
                raise FileExistsError("A different review already exists")
        else:
            write_text_atomic(markdown_path, content)
        return json_path, markdown_path

    def _write_once(self, path: Path, data: Dict[str, Any]) -> Path:
        if path.exists():
            if json.loads(path.read_text(encoding="utf-8")) != data:
                raise FileExistsError(
                    "A different feedback artifact already exists"
                )
            return path
        write_json(path, data)
        return path

    def _replace_json(self, path: Path, data: Dict[str, Any]) -> None:
        descriptor, temporary_name = tempfile.mkstemp(
            dir=str(path.parent),
            prefix=".feedback-loop-",
            suffix=".tmp",
        )
        temporary = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                json.dump(
                    data,
                    stream,
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                )
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, path)
        except BaseException:
            if temporary.exists():
                temporary.unlink()
            raise


def stable_identifier(prefix: str, *values: str) -> str:
    digest = hashlib.sha256("\0".join(values).encode("utf-8")).hexdigest()
    return "{}-{}".format(prefix, digest[:16])


def _identifier(value: object, name: str, prefix: str) -> None:
    _text(value, name)
    if not str(value).startswith(prefix + "-"):
        raise ValueError("{} is invalid".format(name))


def _text(value: object, name: str) -> None:
    if not isinstance(value, str):
        raise TypeError("{} must be a string".format(name))
    if not value or value != value.strip() or "\x00" in value:
        raise ValueError("{} must be non-empty trimmed text".format(name))


def _hex(value: object, name: str) -> None:
    _text(value, name)
    if not all(char in "0123456789abcdef" for char in str(value).lower()):
        raise ValueError("{} must be hexadecimal".format(name))
    if len(str(value)) < 7:
        raise ValueError("{} is too short".format(name))


def _strings(
    value: object,
    name: str,
    required: bool = False,
) -> None:
    if not isinstance(value, tuple) or not all(
        isinstance(item, str) and item and item == item.strip()
        for item in value
    ):
        raise TypeError("{} must contain strings".format(name))
    if required and not value:
        raise ValueError("{} must not be empty".format(name))


def _aware(value: object, name: str) -> None:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise ValueError("{} must be timezone-aware".format(name))


def _lines(values: Tuple[str, ...]) -> str:
    return "\n".join("- {}".format(item) for item in values) or "- None"
