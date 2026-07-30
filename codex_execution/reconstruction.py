import hashlib
import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from architecture_integrator.feedback import (
    ApprovalStatus,
    ArchitectureFeedbackStore,
    ExecutionAuthorization,
    FeedbackLoopRecord,
    FeedbackStatus,
    FeedbackTransition,
)
from architecture_integrator.feedback import stable_identifier
from architecture_integrator.feedback_loop import ArchitectureFeedbackLoop
from architecture_integrator.integrator import ArchitectureIntegrator
from architecture_integrator.workflow import ArchitectureWorkflowStore
from codex_execution.models import (
    CheckStatus,
    ExecutionOrigin,
    ExecutionRecord,
    ExecutionStatus,
)
from codex_execution.errors import redact
from codex_execution.store import ExecutionStore


class ReconstructionAuthorizationStatus(str, Enum):
    CONFIRMED = "CONFIRMED"


class ReconstructionFailureKind(str, Enum):
    AUTHORIZATION_MISSING = "AUTHORIZATION_MISSING"
    AUTHORIZATION_MISMATCH = "AUTHORIZATION_MISMATCH"
    HANDOVER_MISSING = "HANDOVER_MISSING"
    HANDOVER_INVALID = "HANDOVER_INVALID"
    BASE_COMMIT_MISMATCH = "BASE_COMMIT_MISMATCH"
    RESULT_COMMIT_MISSING = "RESULT_COMMIT_MISSING"
    RESULT_COMMIT_MISMATCH = "RESULT_COMMIT_MISMATCH"
    CHECKS_MISSING = "CHECKS_MISSING"
    CHECK_FAILED = "CHECK_FAILED"
    GIT_HISTORY_CONFLICT = "GIT_HISTORY_CONFLICT"
    EXECUTION_ALREADY_EXISTS = "EXECUTION_ALREADY_EXISTS"
    EXECUTION_CONFLICT = "EXECUTION_CONFLICT"
    RECONSTRUCTION_NOT_ALLOWED = "RECONSTRUCTION_NOT_ALLOWED"


class ReconstructionSource(str, Enum):
    CHIEF_ARCHITECT_AUTHORIZATION = "CHIEF_ARCHITECT_AUTHORIZATION"


def _text(value: object, name: str) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or "\n" in value
        or "\r" in value
    ):
        raise ValueError("{} must be trimmed single-line text".format(name))
    return value


def _aware(value: object, name: str) -> datetime:
    if not isinstance(value, datetime):
        raise TypeError("{} must be datetime".format(name))
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("{} must be timezone-aware".format(name))
    return value


def _commit(value: object, name: str) -> str:
    text = _text(value, name)
    if re.fullmatch(r"[0-9a-f]{40}", text) is None:
        raise ValueError("{} must be a full commit SHA".format(name))
    return text


@dataclass(frozen=True)
class ExecutionReconstructionAuthorization:
    authorization_id: str
    decision_reference: str
    repository: str
    expected_start_commit: str
    expected_result_commit: str
    expected_handover_paths: Tuple[str, str]
    allowed_actions: Tuple[str, ...]
    authorized_at: datetime
    status: ReconstructionAuthorizationStatus
    prompt_hash: Optional[str] = None
    schema_version: str = "1.0"

    def __post_init__(self) -> None:
        if self.schema_version != "1.0":
            raise ValueError("Unsupported reconstruction authorization")
        _text(self.authorization_id, "authorization_id")
        if not self.authorization_id.startswith(
            "reconstruction-authorization-"
        ):
            raise ValueError("authorization_id is invalid")
        _text(self.decision_reference, "decision_reference")
        _text(self.repository, "repository")
        _commit(self.expected_start_commit, "expected_start_commit")
        _commit(self.expected_result_commit, "expected_result_commit")
        if (
            not isinstance(self.expected_handover_paths, tuple)
            or len(self.expected_handover_paths) != 2
            or not all(isinstance(item, str) for item in self.expected_handover_paths)
        ):
            raise TypeError("expected_handover_paths must contain two paths")
        if not any(path.endswith(".json") for path in self.expected_handover_paths):
            raise ValueError("JSON handover path is required")
        if not any(path.endswith(".md") for path in self.expected_handover_paths):
            raise ValueError("Markdown handover path is required")
        if not isinstance(self.allowed_actions, tuple):
            raise TypeError("allowed_actions must be a tuple")
        if (
            not self.allowed_actions
            or len(set(self.allowed_actions)) != len(self.allowed_actions)
            or not all(
                isinstance(item, str) and item == item.strip() and item
                for item in self.allowed_actions
            )
        ):
            raise ValueError("allowed_actions must be unique action names")
        if "reconstruct_execution" not in self.allowed_actions:
            raise ValueError("reconstruction is not authorized")
        _aware(self.authorized_at, "authorized_at")
        if not isinstance(self.status, ReconstructionAuthorizationStatus):
            raise TypeError("status must be ReconstructionAuthorizationStatus")
        if self.prompt_hash is not None and re.fullmatch(
            r"[0-9a-f]{64}", self.prompt_hash
        ) is None:
            raise ValueError("prompt_hash must be SHA-256")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "authorization_id": self.authorization_id,
            "decision_reference": self.decision_reference,
            "repository": self.repository,
            "expected_start_commit": self.expected_start_commit,
            "expected_result_commit": self.expected_result_commit,
            "expected_handover_paths": list(self.expected_handover_paths),
            "allowed_actions": list(self.allowed_actions),
            "authorized_at": self.authorized_at.isoformat(),
            "status": self.status.value,
            "prompt_hash": self.prompt_hash,
        }

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> "ExecutionReconstructionAuthorization":
        return cls(
            authorization_id=data["authorization_id"],
            decision_reference=data["decision_reference"],
            repository=data["repository"],
            expected_start_commit=data["expected_start_commit"],
            expected_result_commit=data["expected_result_commit"],
            expected_handover_paths=tuple(data["expected_handover_paths"]),
            allowed_actions=tuple(data["allowed_actions"]),
            authorized_at=datetime.fromisoformat(data["authorized_at"]),
            status=ReconstructionAuthorizationStatus(data["status"]),
            prompt_hash=data.get("prompt_hash"),
            schema_version=data["schema_version"],
        )


@dataclass(frozen=True)
class ExecutionReconstructionRequest:
    authorization: ExecutionReconstructionAuthorization
    reconstructed_at: datetime
    source: ReconstructionSource

    def __post_init__(self) -> None:
        if not isinstance(
            self.authorization,
            ExecutionReconstructionAuthorization,
        ):
            raise TypeError("authorization is required")
        _aware(self.reconstructed_at, "reconstructed_at")
        if not isinstance(self.source, ReconstructionSource):
            raise TypeError("source must be ReconstructionSource")


@dataclass(frozen=True)
class ExecutionReconstructionFailure:
    kind: ReconstructionFailureKind
    message: str

    def __post_init__(self) -> None:
        if not isinstance(self.kind, ReconstructionFailureKind):
            raise TypeError("kind must be ReconstructionFailureKind")
        _text(self.message, "message")

    def to_dict(self) -> Dict[str, str]:
        return {"kind": self.kind.value, "message": self.message}


class ExecutionReconstructionError(RuntimeError):
    def __init__(self, failure: ExecutionReconstructionFailure) -> None:
        self.failure = failure
        super().__init__(failure.message)


@dataclass(frozen=True)
class ExecutionReconstructionResult:
    reconstruction_id: str
    architecture_run_id: str
    workflow_id: str
    execution: ExecutionRecord
    feedback: FeedbackLoopRecord

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reconstruction_id": self.reconstruction_id,
            "architecture_run_id": self.architecture_run_id,
            "workflow_id": self.workflow_id,
            "execution": self.execution.to_dict(),
            "feedback": self.feedback.to_dict(),
        }


class ExecutionReconstructionService:
    def __init__(
        self,
        repository: Path,
        workflows: ArchitectureWorkflowStore,
        integrator: ArchitectureIntegrator,
    ) -> None:
        self.repository = repository.resolve()
        self.workflows = workflows
        self.integrator = integrator

    def reconstruct(
        self,
        request: ExecutionReconstructionRequest,
    ) -> ExecutionReconstructionResult:
        if not isinstance(request, ExecutionReconstructionRequest):
            self._fail(
                ReconstructionFailureKind.AUTHORIZATION_MISSING,
                "A typed reconstruction authorization is required.",
            )
        authorization = request.authorization
        if Path(authorization.repository).resolve() != self.repository:
            self._fail(
                ReconstructionFailureKind.AUTHORIZATION_MISMATCH,
                "Authorized repository does not match.",
            )
        start = authorization.expected_start_commit
        result = authorization.expected_result_commit
        self._require_commit(result, ReconstructionFailureKind.RESULT_COMMIT_MISSING)
        self._require_commit(start, ReconstructionFailureKind.BASE_COMMIT_MISMATCH)
        parent = self._git(("rev-parse", "{}^".format(result)))
        if parent != start:
            self._fail(
                ReconstructionFailureKind.GIT_HISTORY_CONFLICT,
                "Result commit parent does not match authorized start commit.",
            )
        paths = authorization.expected_handover_paths
        json_path = next(path for path in paths if path.endswith(".json"))
        markdown_path = next(path for path in paths if path.endswith(".md"))
        handover = self._load_handover(json_path)
        self._safe_file(markdown_path, ReconstructionFailureKind.HANDOVER_MISSING)
        required_handover_fields = {
            "starting_commit",
            "ending_commit",
            "changed_files",
            "checks",
            "git_status",
            "open_risks",
            "push_status",
        }
        if not required_handover_fields.issubset(handover):
            self._fail(
                ReconstructionFailureKind.HANDOVER_INVALID,
                "Handover is missing required machine-readable fields.",
            )
        if handover.get("starting_commit") != start:
            self._fail(
                ReconstructionFailureKind.BASE_COMMIT_MISMATCH,
                "Handover start commit does not match authorization.",
            )
        ending = handover.get("ending_commit")
        if (
            ending != result
            and not (
                handover.get("schema_version") == "1.0"
                and ending is None
            )
        ):
            self._fail(
                ReconstructionFailureKind.RESULT_COMMIT_MISMATCH,
                "Handover result commit contradicts authorization.",
            )
        changed = set(self._git(("diff-tree", "--no-commit-id", "--name-only", "-r", result)).splitlines())
        if json_path not in changed or markdown_path not in changed:
            self._fail(
                ReconstructionFailureKind.RESULT_COMMIT_MISMATCH,
                "Authorized handovers are not part of the result commit.",
            )
        checks = handover.get("checks")
        if not isinstance(checks, list) or not checks:
            self._fail(
                ReconstructionFailureKind.CHECKS_MISSING,
                "Machine-readable handover checks are missing.",
            )
        required = {
            "tests": any("pytest" in str(item.get("command", "")).lower() for item in checks if isinstance(item, dict)),
            "doctor": any("builder.main doctor" in str(item.get("command", "")).lower() for item in checks if isinstance(item, dict)),
            "diff": any("git diff --check" in str(item.get("command", "")).lower() for item in checks if isinstance(item, dict)),
        }
        if not all(required.values()):
            self._fail(
                ReconstructionFailureKind.CHECKS_MISSING,
                "Tests, Doctor and git diff --check must be reported.",
            )
        if any(
            not isinstance(item, dict) or item.get("status") != "passed"
            for item in checks
        ):
            self._fail(
                ReconstructionFailureKind.CHECK_FAILED,
                "A handover check did not pass.",
            )
        digest_values = (
            authorization.authorization_id,
            start,
            result,
            json_path,
            authorization.prompt_hash or "missing",
        )
        digest = hashlib.sha256("\0".join(digest_values).encode("utf-8")).hexdigest()
        reconstruction_id = "reconstruction-{}".format(digest[:16])
        execution_id = "reconstructed-execution-{}".format(digest[:16])
        workflow_id = stable_identifier("workflow", "reconstruction", reconstruction_id)
        architecture_run_id = stable_identifier(
            "architecture-run", "reconstruction", reconstruction_id
        )
        feedback_authorization_id = stable_identifier(
            "authorization",
            authorization.authorization_id,
            execution_id,
        )
        folder = self.workflows.root / workflow_id
        folder.mkdir(parents=True, exist_ok=True)
        store = ExecutionStore(self.workflows)
        record = ExecutionRecord(
            execution_id=execution_id,
            workflow_id=workflow_id,
            prompt_path=authorization.decision_reference,
            prompt_hash=authorization.prompt_hash,
            repository_path=str(self.repository),
            starting_branch=None,
            starting_commit=start,
            starting_git_status=None,
            status=ExecutionStatus.SUCCEEDED,
            started_at=None,
            completed_at=None,
            codex_exit_code=None,
            test_status=CheckStatus.PASSED,
            test_result=self._check_result(checks, "pytest"),
            doctor_status=CheckStatus.PASSED,
            doctor_result=self._check_result(checks, "builder.main doctor"),
            diff_check_status=CheckStatus.PASSED,
            resulting_commit=result,
            handover_paths=paths,
            failure=None,
            attempts=(),
            retry_count=0,
            origin=ExecutionOrigin.RECONSTRUCTED,
            reconstructed_at=request.reconstructed_at,
            authorization_reference=authorization.authorization_id,
            reconstruction_source=request.source.value,
        )
        existing = store.existing(workflow_id, execution_id)
        if existing is not None and existing != record:
            self._fail(
                ReconstructionFailureKind.EXECUTION_CONFLICT,
                "A different reconstructed execution already exists.",
            )
        if existing is None:
            store.write(record)
        feedback_store = ArchitectureFeedbackStore(self.workflows)
        feedback = feedback_store.record(workflow_id)
        if feedback is not None and (
            feedback.architecture_run_id != architecture_run_id
            or feedback.expected_execution_id != execution_id
        ):
            self._fail(
                ReconstructionFailureKind.EXECUTION_CONFLICT,
                "Reconstruction feedback context conflicts with evidence.",
            )
        if feedback is None:
            feedback = FeedbackLoopRecord(
                architecture_run_id=architecture_run_id,
                workflow_id=workflow_id,
                expected_execution_id=execution_id,
                status=FeedbackStatus.DECISION_CONFIRMED,
                transitions=(
                    FeedbackTransition(
                        FeedbackStatus.DECISION_CONFIRMED,
                        authorization.authorized_at,
                        authorization.decision_reference,
                    ),
                ),
            )
            feedback_store.write_record(feedback)
            feedback = feedback.advance(
                FeedbackStatus.EXECUTION_AUTHORIZED,
                authorization.authorized_at,
                authorization.authorization_id,
                authorization_id=feedback_authorization_id,
            )
            feedback_store.write_record(feedback)
        loop = ArchitectureFeedbackLoop(
            workflows=self.workflows,
            execution=None,
            integrator=self.integrator,
            repository=self.repository,
            store=feedback_store,
        )
        adapted = ExecutionAuthorization(
            schema_version="1.0",
            authorization_id=feedback_authorization_id,
            architecture_run_id=architecture_run_id,
            workflow_id=workflow_id,
            expected_execution_id=execution_id,
            decision_artifacts=(authorization.decision_reference,),
            approval_status=ApprovalStatus.CONFIRMED,
            codex_prompt="prompts/codex-prompt.md",
            prompt_hash=authorization.prompt_hash or hashlib.sha256(
                authorization.decision_reference.encode("utf-8")
            ).hexdigest(),
            repository=str(self.repository),
            expected_base_commit=start,
            allowed_actions=("create_commit", "create_handover"),
            expected_completion_artifacts=("result_commit", "json_handover", "markdown_handover"),
            authorized_at=authorization.authorized_at,
        )
        feedback = loop.review_completed_execution(
            feedback,
            adapted,
            record,
            (authorization.decision_reference,),
            request.reconstructed_at,
        )
        return ExecutionReconstructionResult(
            reconstruction_id,
            architecture_run_id,
            workflow_id,
            record,
            feedback,
        )

    def _safe_file(self, relative: str, kind: ReconstructionFailureKind) -> Path:
        candidate = self.repository / relative
        if Path(relative).is_absolute():
            self._fail(kind, "Artifact path must be repository-relative.")
        if candidate.is_symlink() or not candidate.is_file():
            self._fail(kind, "Artifact is missing or unsafe.")
        try:
            candidate.resolve().relative_to(self.repository)
        except ValueError:
            self._fail(kind, "Artifact is outside the repository.")
        return candidate

    def _load_handover(self, relative: str) -> Dict[str, Any]:
        path = self._safe_file(relative, ReconstructionFailureKind.HANDOVER_MISSING)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            self._fail(
                ReconstructionFailureKind.HANDOVER_INVALID,
                "Handover JSON is invalid.",
            )
        if not isinstance(data, dict):
            self._fail(
                ReconstructionFailureKind.HANDOVER_INVALID,
                "Handover JSON must be an object.",
            )
        return data

    def _require_commit(self, commit: str, kind: ReconstructionFailureKind) -> None:
        result = subprocess.run(
            ("git", "cat-file", "-e", "{}^{{commit}}".format(commit)),
            cwd=str(self.repository),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            self._fail(kind, "Required commit is unavailable.")

    def _git(self, arguments: Tuple[str, ...]) -> str:
        result = subprocess.run(
            ("git",) + arguments,
            cwd=str(self.repository),
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            self._fail(
                ReconstructionFailureKind.GIT_HISTORY_CONFLICT,
                "Git history cannot verify the reconstruction.",
            )
        return result.stdout.strip()

    def _check_result(self, checks: list, marker: str) -> str:
        for item in checks:
            if marker in str(item.get("command", "")).lower():
                return redact(item.get("result", "passed"))
        return "passed"

    def _fail(self, kind: ReconstructionFailureKind, message: str) -> None:
        raise ExecutionReconstructionError(
            ExecutionReconstructionFailure(kind, message)
        )
