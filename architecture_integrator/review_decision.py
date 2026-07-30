import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from architecture_integrator.feedback import (
    ArchitectureFeedbackStore,
    ArchitectureImplementationReview,
    FeedbackLoopRecord,
    FeedbackStatus,
    stable_identifier,
)
from architecture_integrator.io import write_json
from architecture_integrator.models import DecisionChoice
from architecture_integrator.workflow import ArchitectureWorkflowStore
from codex_execution.models import (
    ExecutionOrigin,
    ExecutionRecord,
    ExecutionStatus,
)
from codex_execution.store import ExecutionStore


class ReviewDecisionErrorCode(str, Enum):
    REVIEW_NOT_FOUND = "REVIEW_NOT_FOUND"
    REVIEW_AMBIGUOUS = "REVIEW_AMBIGUOUS"
    REVIEW_INVALID = "REVIEW_INVALID"
    REVIEW_NOT_DECISION_READY = "REVIEW_NOT_DECISION_READY"
    REVIEW_BLOCKED = "REVIEW_BLOCKED"
    REFERENCE_MISMATCH = "REFERENCE_MISMATCH"
    DECISION_CONFLICT = "DECISION_CONFLICT"
    DECISION_ARTIFACT_INVALID = "DECISION_ARTIFACT_INVALID"
    DECISION_INPUT_INVALID = "DECISION_INPUT_INVALID"


class ArchitectureReviewDecisionError(RuntimeError):
    def __init__(
        self,
        code: ReviewDecisionErrorCode,
        message: str,
    ) -> None:
        self.code = code
        super().__init__(message)

    def to_dict(self) -> Dict[str, str]:
        return {"code": self.code.value, "message": str(self)}


@dataclass(frozen=True)
class ArchitectureReviewDecisionInput:
    decision: DecisionChoice
    reason: str

    def __post_init__(self) -> None:
        if not isinstance(self.decision, DecisionChoice):
            raise TypeError("decision must be DecisionChoice")
        _text(self.reason, "reason")

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> "ArchitectureReviewDecisionInput":
        if not isinstance(data, dict) or set(data) != {"decision", "reason"}:
            raise ArchitectureReviewDecisionError(
                ReviewDecisionErrorCode.DECISION_INPUT_INVALID,
                "Decision input must contain only decision and reason.",
            )
        try:
            decision = DecisionChoice(data["decision"])
            return cls(decision=decision, reason=data["reason"])
        except (TypeError, ValueError, KeyError) as error:
            raise ArchitectureReviewDecisionError(
                ReviewDecisionErrorCode.DECISION_INPUT_INVALID,
                "Decision input is invalid: {}".format(error),
            )


@dataclass(frozen=True)
class ArchitectureImplementationReviewDecision:
    decision_id: str
    review_id: str
    decision: DecisionChoice
    reason: str
    decided_at: datetime
    review_topic: str
    workflow_id: str
    architecture_run_id: str
    execution_id: str
    execution_origin: ExecutionOrigin
    reviewed_commit: str
    integrator_recommendation: str
    schema_version: str = "1.0"

    def __post_init__(self) -> None:
        if self.schema_version != "1.0":
            raise ValueError("Unsupported review decision schema")
        for value, name, prefix in (
            (self.decision_id, "decision_id", "review-decision"),
            (self.review_id, "review_id", "review"),
            (self.workflow_id, "workflow_id", "workflow"),
            (
                self.architecture_run_id,
                "architecture_run_id",
                "architecture-run",
            ),
        ):
            _identifier(value, name, prefix)
        _execution_identifier(self.execution_id)
        if not isinstance(self.decision, DecisionChoice):
            raise TypeError("decision must be DecisionChoice")
        if not isinstance(self.execution_origin, ExecutionOrigin):
            raise TypeError("execution_origin must be ExecutionOrigin")
        for value, name in (
            (self.reason, "reason"),
            (self.review_topic, "review_topic"),
            (self.reviewed_commit, "reviewed_commit"),
            (self.integrator_recommendation, "integrator_recommendation"),
        ):
            _text(value, name)
        if (
            len(self.reviewed_commit) != 40
            or any(character not in "0123456789abcdef" for character in self.reviewed_commit)
        ):
            raise ValueError("reviewed_commit must be a full lowercase SHA")
        if self.integrator_recommendation not in {
            "ADOPT",
            "ADOPT_WITH_CHANGES",
            "REJECT",
            "DEFER",
        }:
            raise ValueError("integrator_recommendation is invalid")
        _aware(self.decided_at, "decided_at")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "decision_id": self.decision_id,
            "review_id": self.review_id,
            "decision": self.decision.value,
            "reason": self.reason,
            "decided_at": self.decided_at.isoformat(),
            "review_topic": self.review_topic,
            "workflow_id": self.workflow_id,
            "architecture_run_id": self.architecture_run_id,
            "execution_id": self.execution_id,
            "execution_origin": self.execution_origin.value,
            "reviewed_commit": self.reviewed_commit,
            "integrator_recommendation": self.integrator_recommendation,
        }

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> "ArchitectureImplementationReviewDecision":
        expected = {
            "schema_version",
            "decision_id",
            "review_id",
            "decision",
            "reason",
            "decided_at",
            "review_topic",
            "workflow_id",
            "architecture_run_id",
            "execution_id",
            "execution_origin",
            "reviewed_commit",
            "integrator_recommendation",
        }
        if not isinstance(data, dict) or set(data) != expected:
            raise ValueError("Review decision fields are invalid")
        return cls(
            schema_version=data["schema_version"],
            decision_id=data["decision_id"],
            review_id=data["review_id"],
            decision=DecisionChoice(data["decision"]),
            reason=data["reason"],
            decided_at=datetime.fromisoformat(data["decided_at"]),
            review_topic=data["review_topic"],
            workflow_id=data["workflow_id"],
            architecture_run_id=data["architecture_run_id"],
            execution_id=data["execution_id"],
            execution_origin=ExecutionOrigin(data["execution_origin"]),
            reviewed_commit=data["reviewed_commit"],
            integrator_recommendation=data["integrator_recommendation"],
        )


class ArchitectureReviewDecisionStore:
    FILE_NAME = "chief-architect-review-decision.json"

    def __init__(
        self,
        feedback: ArchitectureFeedbackStore,
        root: Optional[Path] = None,
    ) -> None:
        self.feedback = feedback
        self.root = (
            root
            if root is not None
            else (
                feedback.workflows.root.parent
                / "architecture_review_decisions"
            )
        )

    def path(self, identifier: str) -> Path:
        review_id = (
            identifier
            if identifier.startswith("review-")
            else self._review_id(identifier)
        )
        _identifier(review_id, "review_id", "review")
        return self.root / "{}.json".format(review_id)

    def legacy_path(self, workflow_id: str) -> Path:
        return (
            self.feedback.runtime_folder(workflow_id, create=False)
            / self.FILE_NAME
        )

    def records(
        self,
    ) -> Tuple[ArchitectureImplementationReviewDecision, ...]:
        if not self.root.exists():
            return ()
        self._ensure_root(create=False)
        records = []
        for path in sorted(self.root.glob("review-*.json")):
            decision = self._load_path(path)
            if decision is None or path != self.path(decision.review_id):
                raise ArchitectureReviewDecisionError(
                    ReviewDecisionErrorCode.DECISION_ARTIFACT_INVALID,
                    "Review decision path is not canonical.",
                )
            records.append(decision)
        return tuple(records)

    def for_workflow(
        self,
        workflow_id: str,
    ) -> Optional[ArchitectureImplementationReviewDecision]:
        matches = tuple(
            item
            for item in self.records()
            if item.workflow_id == workflow_id
        )
        if len(matches) > 1:
            raise ArchitectureReviewDecisionError(
                ReviewDecisionErrorCode.DECISION_CONFLICT,
                "Multiple review decisions reference one workflow.",
            )
        return matches[0] if matches else None

    def load(
        self,
        workflow_id: str,
    ) -> Optional[ArchitectureImplementationReviewDecision]:
        versioned = self.for_workflow(workflow_id)
        if not (
            self.feedback.workflows.root / workflow_id
        ).is_dir():
            return versioned
        legacy = self.legacy_path(workflow_id)
        legacy_decision = self._load_path(legacy)
        review = self.feedback.review(workflow_id)
        if review is None:
            if (
                versioned is not None
                and legacy_decision is not None
                and versioned != legacy_decision
            ):
                raise ArchitectureReviewDecisionError(
                    ReviewDecisionErrorCode.DECISION_CONFLICT,
                    "Canonical and legacy review decisions differ.",
                )
            return versioned or legacy_decision
        canonical = self.path(review.review_id)
        canonical_decision = self._load_path(canonical)
        if canonical_decision is not None and legacy_decision is not None:
            if canonical_decision != legacy_decision:
                raise ArchitectureReviewDecisionError(
                    ReviewDecisionErrorCode.DECISION_CONFLICT,
                    "Canonical and legacy review decisions differ.",
                )
            return canonical_decision
        return canonical_decision or legacy_decision

    def write(
        self,
        decision: ArchitectureImplementationReviewDecision,
    ) -> Path:
        existing = self.load(decision.workflow_id)
        path = self.path(decision.review_id)
        if existing is not None:
            if existing == decision and path.is_file():
                return path
            raise ArchitectureReviewDecisionError(
                ReviewDecisionErrorCode.DECISION_CONFLICT,
                "A different review decision already exists.",
            )
        self._ensure_root(create=True)
        write_json(path, decision.to_dict())
        return path

    def migrate(
        self,
        workflow_id: str,
    ) -> ArchitectureImplementationReviewDecision:
        canonical = self.path(workflow_id)
        legacy = self.legacy_path(workflow_id)
        canonical_decision = self._load_path(canonical)
        legacy_decision = self._load_path(legacy)
        if canonical_decision is None and legacy_decision is None:
            raise ArchitectureReviewDecisionError(
                ReviewDecisionErrorCode.REVIEW_NOT_FOUND,
                "No review decision is available for migration.",
            )
        if canonical_decision is not None:
            if (
                legacy_decision is not None
                and legacy_decision != canonical_decision
            ):
                raise ArchitectureReviewDecisionError(
                    ReviewDecisionErrorCode.DECISION_CONFLICT,
                    "Canonical and legacy review decisions differ.",
                )
            return canonical_decision
        self._ensure_root(create=True)
        write_json(canonical, legacy_decision.to_dict())
        return legacy_decision

    def _ensure_root(self, create: bool) -> None:
        if create:
            self.root.mkdir(parents=True, exist_ok=True)
        if not self.root.is_dir() or self.root.is_symlink():
            raise ArchitectureReviewDecisionError(
                ReviewDecisionErrorCode.DECISION_ARTIFACT_INVALID,
                "Review decision root is unavailable or unsafe.",
            )

    def _review_id(self, workflow_id: str) -> str:
        review = self.feedback.review(workflow_id)
        if review is None:
            raise ArchitectureReviewDecisionError(
                ReviewDecisionErrorCode.REVIEW_NOT_FOUND,
                "Review decision cannot be located without a review.",
            )
        return review.review_id

    def _load_path(
        self,
        path: Path,
    ) -> Optional[ArchitectureImplementationReviewDecision]:
        if not path.exists():
            return None
        if not path.is_file() or path.is_symlink():
            raise ArchitectureReviewDecisionError(
                ReviewDecisionErrorCode.DECISION_ARTIFACT_INVALID,
                "Review decision artifact is unavailable or unsafe.",
            )
        try:
            return ArchitectureImplementationReviewDecision.from_dict(
                json.loads(path.read_text(encoding="utf-8"))
            )
        except (OSError, TypeError, ValueError, KeyError) as error:
            raise ArchitectureReviewDecisionError(
                ReviewDecisionErrorCode.DECISION_ARTIFACT_INVALID,
                "Review decision artifact is invalid: {}".format(error),
            )


class ArchitectureReviewDecisionService:
    def __init__(
        self,
        repository: Path,
        workflows: ArchitectureWorkflowStore,
    ) -> None:
        self.repository = repository.resolve()
        self.workflows = workflows
        self.feedback = ArchitectureFeedbackStore(workflows)
        self.executions = ExecutionStore(workflows)
        self.decisions = ArchitectureReviewDecisionStore(self.feedback)

    def decide(
        self,
        review_id: str,
        request: ArchitectureReviewDecisionInput,
        decided_at: datetime,
    ) -> ArchitectureImplementationReviewDecision:
        _identifier(review_id, "review_id", "review")
        if not isinstance(request, ArchitectureReviewDecisionInput):
            raise TypeError("request must be ArchitectureReviewDecisionInput")
        _aware(decided_at, "decided_at")
        workflow_id, review = self._find_review(review_id)
        existing = self.decisions.load(workflow_id)
        if existing is not None:
            if (
                existing.review_id == review_id
                and existing.decision is request.decision
                and existing.reason == request.reason
            ):
                self._record_status(existing, existing.decided_at)
                return existing
            raise ArchitectureReviewDecisionError(
                ReviewDecisionErrorCode.DECISION_CONFLICT,
                "A different decision or reason already exists.",
            )
        feedback = self.feedback.record(workflow_id)
        if (
            feedback is None
            or feedback.status
            is not FeedbackStatus.CHIEF_ARCHITECT_DECISION_REQUIRED
            or feedback.review_id != review.review_id
        ):
            raise ArchitectureReviewDecisionError(
                ReviewDecisionErrorCode.REVIEW_NOT_DECISION_READY,
                "Review does not require a Chief Architect decision.",
            )
        if review.conflicts or review.deviations:
            raise ArchitectureReviewDecisionError(
                ReviewDecisionErrorCode.REVIEW_BLOCKED,
                "Review contains structured conflicts or deviations.",
            )
        execution = self._execution(review)
        self._validate_references(review, feedback, execution)
        topic = self._topic(review, execution)
        decision = ArchitectureImplementationReviewDecision(
            decision_id=stable_identifier(
                "review-decision",
                review.review_id,
                request.decision.value,
                request.reason,
            ),
            review_id=review.review_id,
            decision=request.decision,
            reason=request.reason,
            decided_at=decided_at,
            review_topic=topic,
            workflow_id=review.workflow_id,
            architecture_run_id=review.architecture_run_id,
            execution_id=review.execution_id,
            execution_origin=execution.origin,
            reviewed_commit=review.commit,
            integrator_recommendation=review.recommendation,
        )
        self.decisions.write(decision)
        self._record_status(decision, decided_at)
        return decision

    def migrate(
        self,
        review_id: str,
    ) -> ArchitectureImplementationReviewDecision:
        _identifier(review_id, "review_id", "review")
        workflow_id, review = self._find_review(review_id)
        existing = self.decisions.load(workflow_id)
        if existing is None or existing.review_id != review.review_id:
            raise ArchitectureReviewDecisionError(
                ReviewDecisionErrorCode.REFERENCE_MISMATCH,
                "Legacy decision does not match the review.",
            )
        decision = self.decisions.migrate(workflow_id)
        return decision

    def _find_review(
        self,
        review_id: str,
    ) -> Tuple[str, ArchitectureImplementationReview]:
        matches = []
        invalid = []
        for workflow_id in self.workflows.workflow_ids():
            try:
                review = self.feedback.review(workflow_id)
            except (OSError, TypeError, ValueError) as error:
                invalid.append("{}: {}".format(workflow_id, error))
                continue
            if review is not None and review.review_id == review_id:
                matches.append((workflow_id, review))
        if len(matches) > 1:
            raise ArchitectureReviewDecisionError(
                ReviewDecisionErrorCode.REVIEW_AMBIGUOUS,
                "Review ID resolves to multiple workflows.",
            )
        if not matches:
            if invalid:
                raise ArchitectureReviewDecisionError(
                    ReviewDecisionErrorCode.REVIEW_INVALID,
                    "Persisted implementation review is invalid: {}".format(
                        "; ".join(invalid)
                    ),
                )
            raise ArchitectureReviewDecisionError(
                ReviewDecisionErrorCode.REVIEW_NOT_FOUND,
                "Review ID was not found.",
            )
        return matches[0]

    def _execution(
        self,
        review: ArchitectureImplementationReview,
    ) -> ExecutionRecord:
        records = tuple(
            item for item in self.executions.records(review.workflow_id)
            if item.execution_id == review.execution_id
        )
        if len(records) != 1:
            raise ArchitectureReviewDecisionError(
                ReviewDecisionErrorCode.REFERENCE_MISMATCH,
                "Review execution is missing or ambiguous.",
            )
        return records[0]

    def _validate_references(
        self,
        review: ArchitectureImplementationReview,
        feedback: FeedbackLoopRecord,
        execution: ExecutionRecord,
    ) -> None:
        if (
            review.workflow_id != feedback.workflow_id
            or review.architecture_run_id != feedback.architecture_run_id
            or review.execution_id != feedback.execution_id
            or review.review_id != feedback.review_id
            or execution.workflow_id != review.workflow_id
            or execution.status is not ExecutionStatus.SUCCEEDED
            or execution.resulting_commit != review.commit
            or tuple(item.attempt_id for item in execution.attempts)
            != review.attempt_ids
        ):
            raise ArchitectureReviewDecisionError(
                ReviewDecisionErrorCode.REFERENCE_MISMATCH,
                "Review, feedback and execution references disagree.",
            )

    def _topic(
        self,
        review: ArchitectureImplementationReview,
        execution: ExecutionRecord,
    ) -> str:
        manifest = self.workflows.manifest_path(review.workflow_id)
        if manifest.is_file() and not manifest.is_symlink():
            return self.workflows.load(review.workflow_id).topic
        topics = []
        for relative in execution.handover_paths:
            if not relative.endswith(".json"):
                continue
            path = self.repository / relative
            if path.is_symlink() or not path.is_file():
                continue
            try:
                path.resolve().relative_to(self.repository)
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if isinstance(data, dict) and isinstance(data.get("task"), str):
                topics.append(data["task"])
        if len(set(topics)) != 1:
            raise ArchitectureReviewDecisionError(
                ReviewDecisionErrorCode.REFERENCE_MISMATCH,
                "Review topic cannot be determined uniquely.",
            )
        return topics[0]

    def _record_status(
        self,
        decision: ArchitectureImplementationReviewDecision,
        decided_at: datetime,
    ) -> None:
        record = self.feedback.record(decision.workflow_id)
        if record is None:
            raise ArchitectureReviewDecisionError(
                ReviewDecisionErrorCode.REFERENCE_MISMATCH,
                "Feedback record is missing.",
            )
        if record.status is FeedbackStatus.CHIEF_ARCHITECT_DECISION_RECORDED:
            if record.transitions[-1].reference != decision.decision_id:
                raise ArchitectureReviewDecisionError(
                    ReviewDecisionErrorCode.DECISION_CONFLICT,
                    "Feedback references a different review decision.",
                )
            return
        advanced = record.advance(
            FeedbackStatus.CHIEF_ARCHITECT_DECISION_RECORDED,
            decided_at,
            decision.decision_id,
        )
        self.feedback.write_record(advanced)


def load_review_decision_input(
    path: Path,
) -> ArchitectureReviewDecisionInput:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise ArchitectureReviewDecisionError(
            ReviewDecisionErrorCode.DECISION_INPUT_INVALID,
            "Decision input cannot be read: {}".format(error),
        )
    return ArchitectureReviewDecisionInput.from_dict(data)


def _text(value: object, name: str) -> None:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or "\x00" in value
        or "\n" in value
        or "\r" in value
    ):
        raise ValueError("{} must be trimmed single-line text".format(name))


def _identifier(value: object, name: str, prefix: str) -> None:
    _text(value, name)
    if not value.startswith(prefix + "-"):
        raise ValueError("{} must start with {}-".format(name, prefix))


def _execution_identifier(value: object) -> None:
    _text(value, "execution_id")
    if not value.startswith(("execution-", "reconstructed-execution-")):
        raise ValueError("execution_id is invalid")


def _aware(value: object, name: str) -> None:
    if not isinstance(value, datetime):
        raise TypeError("{} must be datetime".format(name))
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("{} must be timezone-aware".format(name))
