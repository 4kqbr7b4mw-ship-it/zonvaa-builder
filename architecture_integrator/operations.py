import json
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from architecture_integrator.feedback import (
    ArchitectureFeedbackStore,
    ArchitectureImplementationReview,
    CodexHandoverIntake,
    ExecutionAuthorization,
    FeedbackLoopRecord,
    FeedbackStatus,
)
from architecture_integrator.workflow import (
    ArchitectureWorkflow,
    ArchitectureWorkflowStore,
    WorkflowStatus,
)
from architecture_integrator.review_decision import (
    ArchitectureImplementationReviewDecision,
    ArchitectureReviewDecisionError,
    ArchitectureReviewDecisionStore,
)
from architecture_integrator.supersession import (
    ArchitectureWorkflowSupersession,
    ArchitectureWorkflowSupersessionStore,
    normalize_topic,
)
from codex_execution.models import ExecutionOrigin, ExecutionRecord, ExecutionStatus
from codex_execution.store import ExecutionStore
from codex_execution.orchestration import (
    CodexExecutionOrchestrationStore,
    CodexExecutionStatus,
)


class ArchitectureNextStep(str, Enum):
    CREATE_ARCHITECTURE_PROPOSAL = "CREATE_ARCHITECTURE_PROPOSAL"
    CHIEF_ARCHITECT_DECISION_REQUIRED = (
        "CHIEF_ARCHITECT_DECISION_REQUIRED"
    )
    GENERATE_CODEX_PROMPT = "GENERATE_CODEX_PROMPT"
    EXECUTION_AUTHORIZED = "EXECUTION_AUTHORIZED"
    EXECUTION_REQUIRED = "EXECUTION_REQUIRED"
    EXECUTION_RUNNING = "EXECUTION_RUNNING"
    EXECUTION_RETRY_REQUIRED = "EXECUTION_RETRY_REQUIRED"
    HANDOVER_REQUIRED = "HANDOVER_REQUIRED"
    HANDOVER_VALIDATION_REQUIRED = "HANDOVER_VALIDATION_REQUIRED"
    INTEGRATOR_REVIEW_REQUIRED = "INTEGRATOR_REVIEW_REQUIRED"
    PUSH_BLOCKED = "PUSH_BLOCKED"
    READY_TO_PUSH = "READY_TO_PUSH"
    COMPLETE = "COMPLETE"
    BLOCKED = "BLOCKED"


class ArchitectureOperationIssueCode(str, Enum):
    WORKFLOW_MISSING = "WORKFLOW_MISSING"
    WORKFLOW_AMBIGUOUS = "WORKFLOW_AMBIGUOUS"
    PROMPT_WITHOUT_PROOF = "PROMPT_WITHOUT_PROOF"
    AUTHORIZATION_WITHOUT_PROMPT = "AUTHORIZATION_WITHOUT_PROMPT"
    EXECUTION_WITHOUT_AUTHORIZATION = "EXECUTION_WITHOUT_AUTHORIZATION"
    SUCCEEDED_EXECUTION_WITHOUT_HANDOVER = (
        "SUCCEEDED_EXECUTION_WITHOUT_HANDOVER"
    )
    HANDOVER_WITHOUT_EXECUTION = "HANDOVER_WITHOUT_EXECUTION"
    INTAKE_WITHOUT_HANDOVER = "INTAKE_WITHOUT_HANDOVER"
    REVIEW_WITHOUT_INTAKE = "REVIEW_WITHOUT_INTAKE"
    DECISION_REQUIRED_WITHOUT_REVIEW = (
        "DECISION_REQUIRED_WITHOUT_REVIEW"
    )
    RESULT_COMMIT_MISMATCH = "RESULT_COMMIT_MISMATCH"
    DUPLICATE_REVIEW = "DUPLICATE_REVIEW"
    DUPLICATE_EXECUTION = "DUPLICATE_EXECUTION"
    INVALID_FEEDBACK_TRANSITION = "INVALID_FEEDBACK_TRANSITION"
    MISSING_ARTIFACT = "MISSING_ARTIFACT"
    UNSAFE_SYMLINK = "UNSAFE_SYMLINK"
    REVIEW_DECISION_WITHOUT_REVIEW = "REVIEW_DECISION_WITHOUT_REVIEW"
    REVIEW_DECISION_MISMATCH = "REVIEW_DECISION_MISMATCH"
    DECISION_STATUS_WITHOUT_ARTIFACT = "DECISION_STATUS_WITHOUT_ARTIFACT"


class ArchitectureQueryFailureCode(str, Enum):
    WORKFLOW_MISSING = "WORKFLOW_MISSING"
    AMBIGUOUS_QUERY = "AMBIGUOUS_QUERY"
    INVALID_QUERY = "INVALID_QUERY"


class ArtifactAvailability(str, Enum):
    PRESENT = "PRESENT"
    MISSING = "MISSING"
    UNSAFE = "UNSAFE"


@dataclass(frozen=True)
class ArchitectureOperationIssue:
    code: ArchitectureOperationIssueCode
    message: str

    def __post_init__(self) -> None:
        if not isinstance(self.code, ArchitectureOperationIssueCode):
            raise TypeError("code must be ArchitectureOperationIssueCode")
        _text(self.message, "message")

    def to_dict(self) -> Dict[str, str]:
        return {"code": self.code.value, "message": self.message}


@dataclass(frozen=True)
class ArchitectureArtifact:
    kind: str
    path: Optional[str]
    availability: ArtifactAvailability

    def __post_init__(self) -> None:
        _text(self.kind, "kind")
        if self.path is not None:
            _text(self.path, "path")
        if not isinstance(self.availability, ArtifactAvailability):
            raise TypeError("availability must be ArtifactAvailability")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "kind": self.kind,
            "path": self.path,
            "availability": self.availability.value,
        }


@dataclass(frozen=True)
class ArchitectureOperationStatus:
    topic: str
    workflow_id: str
    workflow_status: Optional[WorkflowStatus]
    architecture_run_id: Optional[str]
    authorization_id: Optional[str]
    authorized_branch: Optional[str]
    current_branch: Optional[str]
    branch_match: Optional[bool]
    create_commit_authorized: Optional[bool]
    commit_attempted: Optional[bool]
    execution_id: Optional[str]
    execution_origin: Optional[ExecutionOrigin]
    execution_status: Optional[ExecutionStatus]
    orchestration_id: Optional[str]
    orchestration_status: Optional[CodexExecutionStatus]
    orchestration_step: Optional[str]
    orchestration_started_at: Optional[str]
    orchestration_completed_at: Optional[str]
    orchestration_exit_code: Optional[int]
    orchestration_validation: Optional[bool]
    orchestration_blocker: Optional[str]
    attempt_count: int
    result_commit: Optional[str]
    handover_paths: Tuple[str, ...]
    intake_path: Optional[str]
    review_id: Optional[str]
    review_recommendation: Optional[str]
    review_decision_id: Optional[str]
    review_decision: Optional[str]
    review_decision_reason: Optional[str]
    review_decided_at: Optional[str]
    feedback_status: Optional[FeedbackStatus]
    conflicts: Tuple[str, ...]
    deviations: Tuple[str, ...]
    open_risks: Tuple[str, ...]
    missing_artifacts: Tuple[str, ...]
    next_step: ArchitectureNextStep
    push_status: str
    legacy: bool
    executable: bool
    proposal_ids: Tuple[str, ...]
    decision_ids: Tuple[str, ...]
    artifacts: Tuple[ArchitectureArtifact, ...]
    issues: Tuple[ArchitectureOperationIssue, ...]
    superseded: bool
    canonical_workflow_id: Optional[str]
    supersession_id: Optional[str]
    schema_version: str = "1.0"

    def __post_init__(self) -> None:
        if self.schema_version != "1.0":
            raise ValueError("Unsupported operations schema")
        _text(self.topic, "topic")
        _text(self.workflow_id, "workflow_id")
        if self.workflow_status is not None and not isinstance(
            self.workflow_status,
            WorkflowStatus,
        ):
            raise TypeError("workflow_status must be WorkflowStatus or None")
        if self.execution_origin is not None and not isinstance(
            self.execution_origin,
            ExecutionOrigin,
        ):
            raise TypeError("execution_origin must be ExecutionOrigin or None")
        if self.execution_status is not None and not isinstance(
            self.execution_status,
            ExecutionStatus,
        ):
            raise TypeError("execution_status must be ExecutionStatus or None")
        if self.orchestration_status is not None and not isinstance(
            self.orchestration_status,
            CodexExecutionStatus,
        ):
            raise TypeError(
                "orchestration_status must be CodexExecutionStatus or None"
            )
        if self.orchestration_exit_code is not None and (
            isinstance(self.orchestration_exit_code, bool)
            or not isinstance(self.orchestration_exit_code, int)
        ):
            raise TypeError("orchestration_exit_code must be int or None")
        if self.orchestration_validation is not None and not isinstance(
            self.orchestration_validation, bool
        ):
            raise TypeError("orchestration_validation must be bool or None")
        if self.branch_match is not None and not isinstance(
            self.branch_match, bool
        ):
            raise TypeError("branch_match must be bool or None")
        for value, name in (
            (self.create_commit_authorized, "create_commit_authorized"),
            (self.commit_attempted, "commit_attempted"),
        ):
            if value is not None and not isinstance(value, bool):
                raise TypeError("{} must be bool or None".format(name))
        if self.feedback_status is not None and not isinstance(
            self.feedback_status,
            FeedbackStatus,
        ):
            raise TypeError("feedback_status must be FeedbackStatus or None")
        if not isinstance(self.next_step, ArchitectureNextStep):
            raise TypeError("next_step must be ArchitectureNextStep")
        if isinstance(self.attempt_count, bool) or not isinstance(
            self.attempt_count,
            int,
        ) or self.attempt_count < 0:
            raise ValueError("attempt_count must be non-negative")
        for value, name in (
            (self.architecture_run_id, "architecture_run_id"),
            (self.authorization_id, "authorization_id"),
            (self.authorized_branch, "authorized_branch"),
            (self.current_branch, "current_branch"),
            (self.execution_id, "execution_id"),
            (self.orchestration_id, "orchestration_id"),
            (self.orchestration_step, "orchestration_step"),
            (self.orchestration_started_at, "orchestration_started_at"),
            (self.orchestration_completed_at, "orchestration_completed_at"),
            (self.orchestration_blocker, "orchestration_blocker"),
            (self.result_commit, "result_commit"),
            (self.intake_path, "intake_path"),
            (self.review_id, "review_id"),
            (self.review_recommendation, "review_recommendation"),
            (self.review_decision_id, "review_decision_id"),
            (self.review_decision, "review_decision"),
            (self.review_decision_reason, "review_decision_reason"),
            (self.review_decided_at, "review_decided_at"),
            (self.canonical_workflow_id, "canonical_workflow_id"),
            (self.supersession_id, "supersession_id"),
        ):
            if value is not None:
                _text(value, name)
        for values, name in (
            (self.handover_paths, "handover_paths"),
            (self.conflicts, "conflicts"),
            (self.deviations, "deviations"),
            (self.open_risks, "open_risks"),
            (self.missing_artifacts, "missing_artifacts"),
            (self.proposal_ids, "proposal_ids"),
            (self.decision_ids, "decision_ids"),
        ):
            _strings(values, name)
        if not isinstance(self.artifacts, tuple) or not all(
            isinstance(item, ArchitectureArtifact) for item in self.artifacts
        ):
            raise TypeError("artifacts must contain ArchitectureArtifact")
        if not isinstance(self.issues, tuple) or not all(
            isinstance(item, ArchitectureOperationIssue)
            for item in self.issues
        ):
            raise TypeError("issues must contain ArchitectureOperationIssue")
        if not isinstance(self.legacy, bool) or not isinstance(
            self.executable,
            bool,
        ):
            raise TypeError("legacy and executable must be bool")
        if not isinstance(self.superseded, bool):
            raise TypeError("superseded must be bool")
        _text(self.push_status, "push_status")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "topic": self.topic,
            "workflow_id": self.workflow_id,
            "workflow_status": (
                self.workflow_status.value
                if self.workflow_status is not None
                else None
            ),
            "architecture_run_id": self.architecture_run_id,
            "authorization_id": self.authorization_id,
            "authorized_branch": self.authorized_branch,
            "current_branch": self.current_branch,
            "branch_match": self.branch_match,
            "create_commit_authorized": self.create_commit_authorized,
            "commit_attempted": self.commit_attempted,
            "execution_id": self.execution_id,
            "execution_origin": (
                self.execution_origin.value
                if self.execution_origin is not None
                else None
            ),
            "execution_status": (
                self.execution_status.value
                if self.execution_status is not None
                else None
            ),
            "orchestration_id": self.orchestration_id,
            "orchestration_status": (
                self.orchestration_status.value
                if self.orchestration_status is not None else None
            ),
            "orchestration_step": self.orchestration_step,
            "orchestration_started_at": self.orchestration_started_at,
            "orchestration_completed_at": self.orchestration_completed_at,
            "orchestration_exit_code": self.orchestration_exit_code,
            "orchestration_validation": self.orchestration_validation,
            "orchestration_blocker": self.orchestration_blocker,
            "attempt_count": self.attempt_count,
            "result_commit": self.result_commit,
            "handover_paths": list(self.handover_paths),
            "intake_path": self.intake_path,
            "review_id": self.review_id,
            "review_recommendation": self.review_recommendation,
            "review_decision_id": self.review_decision_id,
            "review_decision": self.review_decision,
            "review_decision_reason": self.review_decision_reason,
            "review_decided_at": self.review_decided_at,
            "feedback_status": (
                self.feedback_status.value
                if self.feedback_status is not None
                else None
            ),
            "conflicts": list(self.conflicts),
            "deviations": list(self.deviations),
            "open_risks": list(self.open_risks),
            "missing_artifacts": list(self.missing_artifacts),
            "next_step": self.next_step.value,
            "push_status": self.push_status,
            "legacy": self.legacy,
            "executable": self.executable,
            "proposal_ids": list(self.proposal_ids),
            "decision_ids": list(self.decision_ids),
            "artifacts": [item.to_dict() for item in self.artifacts],
            "issues": [item.to_dict() for item in self.issues],
            "superseded": self.superseded,
            "canonical_workflow_id": self.canonical_workflow_id,
            "supersession_id": self.supersession_id,
        }


@dataclass(frozen=True)
class ArchitectureOperationQuery:
    topic: Optional[str] = None
    workflow_id: Optional[str] = None
    architecture_run_id: Optional[str] = None
    execution_id: Optional[str] = None
    orchestration_id: Optional[str] = None
    authorization_id: Optional[str] = None
    orchestration_status: Optional[str] = None
    review_id: Optional[str] = None
    commit: Optional[str] = None
    handover_path: Optional[str] = None
    proposal_id: Optional[str] = None
    decision_id: Optional[str] = None

    def __post_init__(self) -> None:
        for name, value in self.to_dict().items():
            if value is not None:
                _text(value, name)
        if self.commit is not None and (
            len(self.commit) < 7
            or re.fullmatch(r"[0-9a-fA-F]{7,40}", self.commit) is None
        ):
            raise ValueError("commit must be a 7 to 40 character SHA")
        if self.orchestration_status is not None:
            CodexExecutionStatus(self.orchestration_status)

    def to_dict(self) -> Dict[str, Optional[str]]:
        return {
            "topic": self.topic,
            "workflow_id": self.workflow_id,
            "architecture_run_id": self.architecture_run_id,
            "execution_id": self.execution_id,
            "orchestration_id": self.orchestration_id,
            "authorization_id": self.authorization_id,
            "orchestration_status": self.orchestration_status,
            "review_id": self.review_id,
            "commit": self.commit,
            "handover_path": self.handover_path,
            "proposal_id": self.proposal_id,
            "decision_id": self.decision_id,
        }

    @property
    def empty(self) -> bool:
        return not any(value is not None for value in self.to_dict().values())


@dataclass(frozen=True)
class ArchitectureOperationQueryCandidate:
    topic: str
    workflow_id: str
    architecture_run_id: Optional[str]
    execution_id: Optional[str]
    review_id: Optional[str]
    feedback_status: Optional[str]
    next_step: ArchitectureNextStep
    superseded: bool
    canonical_workflow_id: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "topic": self.topic,
            "workflow_id": self.workflow_id,
            "architecture_run_id": self.architecture_run_id,
            "execution_id": self.execution_id,
            "review_id": self.review_id,
            "feedback_status": self.feedback_status,
            "next_step": self.next_step.value,
            "superseded": self.superseded,
            "canonical_workflow_id": self.canonical_workflow_id,
        }


@dataclass(frozen=True)
class ArchitectureOperationQueryFailure:
    code: ArchitectureQueryFailureCode
    message: str
    candidates: Tuple[str, ...] = ()
    candidate_details: Tuple[ArchitectureOperationQueryCandidate, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code.value,
            "message": self.message,
            "candidates": list(self.candidates),
            "candidate_details": [
                item.to_dict() for item in self.candidate_details
            ],
        }


class ArchitectureOperationQueryError(RuntimeError):
    def __init__(self, failure: ArchitectureOperationQueryFailure) -> None:
        self.failure = failure
        super().__init__(failure.message)


class ArchitectureOperationsAgent:
    """Read-only operational projection over persisted architecture evidence."""

    def __init__(
        self,
        repository: Path,
        workflows: ArchitectureWorkflowStore,
    ) -> None:
        self.repository = repository.resolve()
        self.workflows = workflows
        self.feedback = ArchitectureFeedbackStore(workflows)
        self.executions = ExecutionStore(workflows)
        self.orchestrations = CodexExecutionOrchestrationStore(workflows)
        self.review_decisions = ArchitectureReviewDecisionStore(self.feedback)
        self.supersessions = ArchitectureWorkflowSupersessionStore(workflows)

    def statuses(self) -> Tuple[ArchitectureOperationStatus, ...]:
        workflow_ids = set(self.workflows.workflow_ids())
        workflow_ids.update(
            item.workflow_id for item in self.review_decisions.records()
        )
        return tuple(
            self._status(workflow_id)
            for workflow_id in sorted(workflow_ids)
        )

    def find(
        self,
        query: ArchitectureOperationQuery,
    ) -> Tuple[ArchitectureOperationStatus, ...]:
        if not isinstance(query, ArchitectureOperationQuery):
            raise TypeError("query must be ArchitectureOperationQuery")
        statuses = self.statuses()
        if query.empty:
            return statuses
        matches = self._query_matches(statuses, query)
        if not matches:
            raise ArchitectureOperationQueryError(
                ArchitectureOperationQueryFailure(
                    ArchitectureQueryFailureCode.WORKFLOW_MISSING,
                    "No persisted architecture operation matches the query.",
                )
            )
        if len(matches) > 1:
            raise ArchitectureOperationQueryError(
                ArchitectureOperationQueryFailure(
                    ArchitectureQueryFailureCode.AMBIGUOUS_QUERY,
                    "The architecture query is ambiguous.",
                    tuple(item.workflow_id for item in matches),
                    tuple(self._candidate(item) for item in matches),
                )
            )
        return matches

    def reviews(self) -> Tuple[ArchitectureOperationStatus, ...]:
        return tuple(
            item for item in self.statuses()
            if item.feedback_status
            is FeedbackStatus.CHIEF_ARCHITECT_DECISION_REQUIRED
            and item.review_id is not None
        )

    def _status(self, workflow_id: str) -> ArchitectureOperationStatus:
        decision = self.review_decisions.for_workflow(workflow_id)
        if not (self.workflows.root / workflow_id).is_dir():
            if decision is None:
                raise FileNotFoundError(workflow_id)
            return self._decision_only_status(decision)
        folder = self.workflows.folder(workflow_id)
        issues = []
        artifacts = []
        workflow = self._workflow(workflow_id, issues)
        workflow_status = None
        decisions = ()
        proposal_ids = ()
        if workflow is not None:
            proposal_ids = workflow.proposal_ids
            decisions = self.workflows.decisions_if_present(workflow_id)
            try:
                workflow_status = self.workflows.status(workflow_id)
            except (OSError, TypeError, ValueError) as error:
                issues.append(self._issue(
                    ArchitectureOperationIssueCode.MISSING_ARTIFACT,
                    "Workflow status is unavailable: {}".format(error),
                ))
            self._workflow_artifacts(workflow, artifacts)
        else:
            artifacts.append(self._artifact(
                "workflow",
                folder / "workflow.json",
            ))

        authorization = self._authorization(workflow_id, issues)
        feedback = self._feedback(workflow_id, issues)
        executions = self._executions(workflow_id, issues)
        execution = self._select_execution(executions, feedback)
        orchestrations = self.orchestrations.records(workflow_id)
        orchestration = orchestrations[-1] if orchestrations else None
        if orchestration is not None:
            artifacts.append(self._artifact(
                "codex_execution_orchestration",
                self.orchestrations.path(
                    workflow_id, orchestration.orchestration_id
                ),
            ))
        intake = self._intake(workflow_id, issues)
        review = self._review(workflow_id, issues)
        review_decision = self._review_decision(workflow_id, issues)
        supersession = self.supersessions.for_workflow(workflow_id)
        related_supersessions = self.supersessions.related(workflow_id)
        self._runtime_artifacts(
            workflow_id,
            authorization,
            executions,
            execution,
            feedback,
            intake,
            review,
            review_decision,
            related_supersessions,
            artifacts,
        )
        self._ensure_artifact_kinds(artifacts)
        for artifact in artifacts:
            if artifact.availability is ArtifactAvailability.UNSAFE:
                issues.append(self._issue(
                    ArchitectureOperationIssueCode.UNSAFE_SYMLINK,
                    "Unsafe artifact: {}".format(
                        artifact.path or artifact.kind
                    ),
                ))
        topic = self._topic(workflow, execution, review)
        prompt = folder / "prompts" / "codex-prompt.md"
        proof = folder / "prompts" / "codex-prompt-proof.json"
        legacy = (
            workflow is not None
            and workflow.schema_version == "1.0"
            and prompt.is_file()
            and not proof.exists()
            and authorization is None
            and not executions
        )
        self._inconsistencies(
            workflow,
            prompt,
            proof,
            authorization,
            execution,
            feedback,
            intake,
            review,
            review_decision,
            legacy,
            issues,
        )
        missing = tuple(sorted(
            item.kind for item in artifacts
            if item.availability is ArtifactAvailability.MISSING
        ))
        next_step = self._next_step(
            workflow,
            decisions,
            prompt,
            proof,
            authorization,
            execution,
            feedback,
            intake,
            review,
            review_decision,
            legacy,
            tuple(issues),
        )
        authorization_id = (
            authorization.authorization_id if authorization else None
        )
        if authorization_id is None and execution is not None:
            authorization_id = execution.authorization_reference
        return ArchitectureOperationStatus(
            topic=topic,
            workflow_id=workflow_id,
            workflow_status=workflow_status,
            architecture_run_id=(
                feedback.architecture_run_id
                if feedback is not None
                else (
                    authorization.architecture_run_id
                    if authorization is not None
                    else None
                )
            ),
            authorization_id=authorization_id,
            authorized_branch=(
                authorization.authorized_branch
                if authorization is not None else None
            ),
            current_branch=(
                orchestration.branch if orchestration is not None else None
            ),
            branch_match=(
                orchestration.authorized_branch is not None
                and orchestration.branch == orchestration.authorized_branch
                if orchestration is not None else None
            ),
            create_commit_authorized=(
                authorization.create_commit
                if authorization is not None else None
            ),
            commit_attempted=(
                orchestration.commit_attempted
                if orchestration is not None else None
            ),
            execution_id=execution.execution_id if execution else None,
            execution_origin=execution.origin if execution else None,
            execution_status=execution.status if execution else None,
            orchestration_id=(
                orchestration.orchestration_id if orchestration else None
            ),
            orchestration_status=(
                orchestration.status if orchestration else None
            ),
            orchestration_step=(
                orchestration.current_step.value if orchestration else None
            ),
            orchestration_started_at=(
                orchestration.started_at.isoformat()
                if orchestration else None
            ),
            orchestration_completed_at=(
                orchestration.completed_at.isoformat()
                if orchestration and orchestration.completed_at else None
            ),
            orchestration_exit_code=(
                orchestration.process.exit_code if orchestration else None
            ),
            orchestration_validation=(
                orchestration.validation_summary.passed
                if orchestration and orchestration.validation_summary
                else None
            ),
            orchestration_blocker=(
                orchestration.failure.message
                if orchestration and orchestration.failure else None
            ),
            attempt_count=len(execution.attempts) if execution else 0,
            result_commit=(
                orchestration.result_commit
                if orchestration is not None
                and orchestration.result_commit is not None
                else execution.resulting_commit if execution else None
            ),
            handover_paths=execution.handover_paths if execution else (),
            intake_path=(
                self._relative(
                    self.feedback.runtime_folder(
                        workflow_id,
                        create=False,
                    ) / "handover-intake.json"
                )
                if intake is not None
                else None
            ),
            review_id=review.review_id if review else None,
            review_recommendation=(
                review.recommendation if review else None
            ),
            review_decision_id=(
                review_decision.decision_id if review_decision else None
            ),
            review_decision=(
                review_decision.decision.value if review_decision else None
            ),
            review_decision_reason=(
                review_decision.reason if review_decision else None
            ),
            review_decided_at=(
                review_decision.decided_at.isoformat()
                if review_decision else None
            ),
            feedback_status=feedback.status if feedback else None,
            conflicts=review.conflicts if review else (),
            deviations=(
                tuple(item.message for item in review.deviations)
                if review else ()
            ),
            open_risks=review.open_risks if review else (),
            missing_artifacts=missing,
            next_step=next_step,
            push_status=execution.push_status if execution else "unknown",
            legacy=legacy,
            executable=not legacy and next_step not in {
                ArchitectureNextStep.BLOCKED,
                ArchitectureNextStep.COMPLETE,
                ArchitectureNextStep.CHIEF_ARCHITECT_DECISION_REQUIRED,
            },
            proposal_ids=proposal_ids,
            decision_ids=tuple(item.decision_id for item in decisions) or (
                intake.decision_ids if intake is not None else ()
            ),
            artifacts=tuple(sorted(
                artifacts,
                key=lambda item: (item.kind, item.path or ""),
            )),
            issues=tuple(issues),
            superseded=supersession is not None,
            canonical_workflow_id=(
                supersession.canonical_workflow_id
                if supersession is not None
                else None
            ),
            supersession_id=(
                supersession.supersession_id
                if supersession is not None
                else None
            ),
        )

    def _decision_only_status(
        self,
        decision: ArchitectureImplementationReviewDecision,
    ) -> ArchitectureOperationStatus:
        artifact = self._artifact(
            "chief_architect_review_decision",
            self.review_decisions.path(decision.review_id),
        )
        return ArchitectureOperationStatus(
            topic=decision.review_topic,
            workflow_id=decision.workflow_id,
            workflow_status=None,
            architecture_run_id=decision.architecture_run_id,
            authorization_id=None,
            authorized_branch=None,
            current_branch=None,
            branch_match=None,
            create_commit_authorized=None,
            commit_attempted=None,
            execution_id=decision.execution_id,
            execution_origin=decision.execution_origin,
            execution_status=None,
            orchestration_id=None,
            orchestration_status=None,
            orchestration_step=None,
            orchestration_started_at=None,
            orchestration_completed_at=None,
            orchestration_exit_code=None,
            orchestration_validation=None,
            orchestration_blocker=None,
            attempt_count=0,
            result_commit=decision.reviewed_commit,
            handover_paths=(),
            intake_path=None,
            review_id=decision.review_id,
            review_recommendation=decision.integrator_recommendation,
            review_decision_id=decision.decision_id,
            review_decision=decision.decision.value,
            review_decision_reason=decision.reason,
            review_decided_at=decision.decided_at.isoformat(),
            feedback_status=(
                FeedbackStatus.CHIEF_ARCHITECT_DECISION_RECORDED
            ),
            conflicts=(),
            deviations=(),
            open_risks=(),
            missing_artifacts=(),
            next_step=ArchitectureNextStep.COMPLETE,
            push_status="unknown",
            legacy=False,
            executable=False,
            proposal_ids=(),
            decision_ids=(),
            artifacts=(artifact,),
            issues=(),
            superseded=False,
            canonical_workflow_id=None,
            supersession_id=None,
        )

    def _workflow(
        self,
        workflow_id: str,
        issues: list,
    ) -> Optional[ArchitectureWorkflow]:
        path = self.workflows.folder(workflow_id) / "workflow.json"
        if not path.exists():
            return None
        if path.is_symlink():
            issues.append(self._issue(
                ArchitectureOperationIssueCode.UNSAFE_SYMLINK,
                "Workflow manifest is a symlink.",
            ))
            return None
        try:
            return self.workflows.load(workflow_id)
        except (OSError, TypeError, ValueError) as error:
            issues.append(self._issue(
                ArchitectureOperationIssueCode.MISSING_ARTIFACT,
                "Workflow manifest is invalid: {}".format(error),
            ))
            return None

    def _authorization(
        self,
        workflow_id: str,
        issues: list,
    ) -> Optional[ExecutionAuthorization]:
        try:
            return self.feedback.authorization(workflow_id)
        except (OSError, TypeError, ValueError) as error:
            issues.append(self._issue(
                ArchitectureOperationIssueCode.MISSING_ARTIFACT,
                "Execution authorization is invalid: {}".format(error),
            ))
            return None

    def _feedback(
        self,
        workflow_id: str,
        issues: list,
    ) -> Optional[FeedbackLoopRecord]:
        try:
            return self.feedback.record(workflow_id)
        except (OSError, TypeError, ValueError) as error:
            issues.append(self._issue(
                ArchitectureOperationIssueCode.INVALID_FEEDBACK_TRANSITION,
                "Feedback record is invalid: {}".format(error),
            ))
            return None

    def _executions(
        self,
        workflow_id: str,
        issues: list,
    ) -> Tuple[ExecutionRecord, ...]:
        try:
            records = self.executions.records(workflow_id)
        except (OSError, TypeError, ValueError) as error:
            issues.append(self._issue(
                ArchitectureOperationIssueCode.MISSING_ARTIFACT,
                "Execution records are invalid: {}".format(error),
            ))
            return ()
        if len(records) > 1:
            issues.append(self._issue(
                ArchitectureOperationIssueCode.DUPLICATE_EXECUTION,
                "Multiple execution records belong to this workflow.",
            ))
        return records

    def _intake(
        self,
        workflow_id: str,
        issues: list,
    ) -> Optional[CodexHandoverIntake]:
        try:
            return self.feedback.intake(workflow_id)
        except (OSError, TypeError, ValueError) as error:
            issues.append(self._issue(
                ArchitectureOperationIssueCode.MISSING_ARTIFACT,
                "Handover intake is invalid: {}".format(error),
            ))
            return None

    def _review(
        self,
        workflow_id: str,
        issues: list,
    ) -> Optional[ArchitectureImplementationReview]:
        runtime = self.feedback.runtime_folder(
            workflow_id,
            create=False,
        )
        if runtime.is_dir() and len(tuple(
            runtime.glob("integrator-review*.json")
        )) > 1:
            issues.append(self._issue(
                ArchitectureOperationIssueCode.DUPLICATE_REVIEW,
                "Multiple Integrator review artifacts exist.",
            ))
        try:
            return self.feedback.review(workflow_id)
        except (OSError, TypeError, ValueError) as error:
            issues.append(self._issue(
                ArchitectureOperationIssueCode.MISSING_ARTIFACT,
                "Integrator review is invalid: {}".format(error),
            ))
            return None

    def _review_decision(
        self,
        workflow_id: str,
        issues: list,
    ) -> Optional[ArchitectureImplementationReviewDecision]:
        try:
            return self.review_decisions.load(workflow_id)
        except ArchitectureReviewDecisionError as error:
            issues.append(self._issue(
                ArchitectureOperationIssueCode.MISSING_ARTIFACT,
                "Chief Architect review decision is invalid: {}".format(
                    error
                ),
            ))
            return None

    def _select_execution(
        self,
        executions: Tuple[ExecutionRecord, ...],
        feedback: Optional[FeedbackLoopRecord],
    ) -> Optional[ExecutionRecord]:
        if not executions:
            return None
        if feedback is not None:
            matches = tuple(
                item for item in executions
                if item.execution_id in {
                    feedback.execution_id,
                    feedback.expected_execution_id,
                }
            )
            if len(matches) == 1:
                return matches[0]
        return executions[0] if len(executions) == 1 else None

    def _topic(
        self,
        workflow: Optional[ArchitectureWorkflow],
        execution: Optional[ExecutionRecord],
        review: Optional[ArchitectureImplementationReview],
    ) -> str:
        if workflow is not None and workflow.topic:
            return workflow.topic
        if workflow is not None:
            titles = []
            folder = self.workflows.folder(workflow.workflow_id)
            for relative in workflow.proposal_files:
                data = self._json(folder / relative)
                title = data.get("title") if data else None
                if isinstance(title, str) and title:
                    titles.append(title)
            if titles:
                return " / ".join(titles)
        if execution is not None:
            for relative in execution.handover_paths:
                if not relative.endswith(".json"):
                    continue
                data = self._json(self.repository / relative)
                task = data.get("task") if data else None
                if isinstance(task, str) and task:
                    return task
        if review is not None:
            return "Architecture review {}".format(review.review_id)
        return "Missing topic for {}".format(
            workflow.workflow_id if workflow else "persisted workflow"
        )

    def _workflow_artifacts(
        self,
        workflow: ArchitectureWorkflow,
        artifacts: list,
    ) -> None:
        folder = self.workflows.folder(workflow.workflow_id)
        artifacts.append(self._artifact("workflow", folder / "workflow.json"))
        for relative in workflow.proposal_files:
            artifacts.append(self._artifact("proposal", folder / relative))
        for relative in workflow.analysis_files:
            artifacts.append(self._artifact("analysis", folder / relative))
        for proposal_id in workflow.proposal_ids:
            artifacts.append(self._artifact(
                "decision",
                folder / "decisions" / "{}.json".format(proposal_id),
            ))
        templates = (
            (workflow.decision_template_file,)
            if workflow.decision_template_file
            else workflow.decision_template_files
        )
        for relative in templates:
            artifacts.append(self._artifact(
                "decision_template",
                folder / relative,
            ))
        artifacts.append(self._artifact(
            "codex_prompt",
            folder / "prompts" / "codex-prompt.md",
        ))
        artifacts.append(self._artifact(
            "prompt_proof",
            folder / "prompts" / "codex-prompt-proof.json",
        ))

    def _runtime_artifacts(
        self,
        workflow_id: str,
        authorization: Optional[ExecutionAuthorization],
        executions: Tuple[ExecutionRecord, ...],
        execution: Optional[ExecutionRecord],
        feedback: Optional[FeedbackLoopRecord],
        intake: Optional[CodexHandoverIntake],
        review: Optional[ArchitectureImplementationReview],
        review_decision: Optional[ArchitectureImplementationReviewDecision],
        supersessions: Tuple[ArchitectureWorkflowSupersession, ...],
        artifacts: list,
    ) -> None:
        folder = self.workflows.folder(workflow_id)
        authorization_path = (
            folder / "feedback" / "execution-authorization.json"
        )
        if authorization is not None or authorization_path.exists():
            artifacts.append(self._artifact(
                "execution_authorization",
                authorization_path,
            ))
        for item in executions:
            path = folder / "executions" / "{}.json".format(item.execution_id)
            artifacts.append(self._artifact("execution_record", path))
            artifacts.append(self._artifact("attempt_history", path))
        if execution is not None and execution.authorization_reference:
            external = self._reconstruction_authorization(
                execution.authorization_reference
            )
            if external is not None:
                artifacts.append(self._artifact(
                    "reconstruction_authorization",
                    external,
                ))
        if execution is not None:
            for relative in execution.handover_paths:
                artifacts.append(self._artifact(
                    (
                        "json_handover"
                        if relative.endswith(".json")
                        else "markdown_handover"
                    ),
                    self.repository / relative,
                ))
        runtime = folder / "executions" / "feedback"
        if feedback is not None or runtime.exists():
            artifacts.append(self._artifact(
                "feedback_record",
                runtime / "feedback-loop.json",
            ))
        if intake is not None or (runtime / "handover-intake.json").exists():
            artifacts.append(self._artifact(
                "handover_intake",
                runtime / "handover-intake.json",
            ))
        if review is not None or (runtime / "integrator-review.json").exists():
            artifacts.append(self._artifact(
                "integrator_review",
                runtime / "integrator-review.json",
            ))
            artifacts.append(self._artifact(
                "decision_proposal",
                runtime / "decision-proposal.md",
            ))
        decision_path = (
            self.review_decisions.path(review_decision.review_id)
            if review_decision is not None
            else None
        )
        if review_decision is not None:
            artifacts.append(self._artifact(
                "chief_architect_review_decision",
                decision_path,
            ))
        for supersession in supersessions:
            artifacts.append(self._artifact(
                "workflow_supersession",
                self.supersessions.path(
                    supersession.superseded_workflow_id
                ),
            ))

    def _inconsistencies(
        self,
        workflow: Optional[ArchitectureWorkflow],
        prompt: Path,
        proof: Path,
        authorization: Optional[ExecutionAuthorization],
        execution: Optional[ExecutionRecord],
        feedback: Optional[FeedbackLoopRecord],
        intake: Optional[CodexHandoverIntake],
        review: Optional[ArchitectureImplementationReview],
        review_decision: Optional[ArchitectureImplementationReviewDecision],
        legacy: bool,
        issues: list,
    ) -> None:
        if workflow is None and execution is None and feedback is None:
            issues.append(self._issue(
                ArchitectureOperationIssueCode.WORKFLOW_MISSING,
                "No workflow manifest or reconstructed execution exists.",
            ))
        if prompt.is_file() and not proof.is_file() and not legacy:
            issues.append(self._issue(
                ArchitectureOperationIssueCode.PROMPT_WITHOUT_PROOF,
                "Codex prompt exists without prompt proof.",
            ))
        if authorization is not None and not prompt.is_file():
            issues.append(self._issue(
                ArchitectureOperationIssueCode.AUTHORIZATION_WITHOUT_PROMPT,
                "Execution authorization exists without Codex prompt.",
            ))
        if (
            execution is not None
            and authorization is None
            and execution.origin is ExecutionOrigin.EXECUTION_BRIDGE
        ):
            issues.append(self._issue(
                ArchitectureOperationIssueCode.EXECUTION_WITHOUT_AUTHORIZATION,
                "Bridge execution exists without execution authorization.",
            ))
        if (
            execution is not None
            and execution.status is ExecutionStatus.SUCCEEDED
            and not self._handover_available(execution)
        ):
            issues.append(self._issue(
                ArchitectureOperationIssueCode.SUCCEEDED_EXECUTION_WITHOUT_HANDOVER,
                "Successful execution identifies no handover.",
            ))
        if (
            feedback is not None
            and feedback.handover_path is not None
            and execution is None
        ):
            issues.append(self._issue(
                ArchitectureOperationIssueCode.HANDOVER_WITHOUT_EXECUTION,
                "Feedback references a handover without execution.",
            ))
        if intake is not None and (
            execution is None or intake.handover_path not in execution.handover_paths
        ):
            issues.append(self._issue(
                ArchitectureOperationIssueCode.INTAKE_WITHOUT_HANDOVER,
                "Handover intake has no matching execution handover.",
            ))
        if review is not None and intake is None:
            issues.append(self._issue(
                ArchitectureOperationIssueCode.REVIEW_WITHOUT_INTAKE,
                "Integrator review exists without handover intake.",
            ))
        if review is not None and feedback is None:
            issues.append(self._issue(
                ArchitectureOperationIssueCode.INVALID_FEEDBACK_TRANSITION,
                "Integrator review exists without feedback status.",
            ))
        if (
            feedback is not None
            and feedback.status
            is FeedbackStatus.CHIEF_ARCHITECT_DECISION_REQUIRED
            and review is None
        ):
            issues.append(self._issue(
                ArchitectureOperationIssueCode.DECISION_REQUIRED_WITHOUT_REVIEW,
                "Feedback requires a decision but no review exists.",
            ))
        if (
            execution is not None
            and review is not None
            and execution.resulting_commit != review.commit
        ):
            issues.append(self._issue(
                ArchitectureOperationIssueCode.RESULT_COMMIT_MISMATCH,
                "Execution and review result commits differ.",
            ))
        if review_decision is not None and review is None:
            issues.append(self._issue(
                ArchitectureOperationIssueCode.REVIEW_DECISION_WITHOUT_REVIEW,
                "Chief Architect decision exists without Integrator review.",
            ))
        if review_decision is not None and review is not None and (
            review_decision.review_id != review.review_id
            or review_decision.workflow_id != review.workflow_id
            or review_decision.architecture_run_id
            != review.architecture_run_id
            or review_decision.execution_id != review.execution_id
            or review_decision.reviewed_commit != review.commit
            or review_decision.integrator_recommendation
            != review.recommendation
        ):
            issues.append(self._issue(
                ArchitectureOperationIssueCode.REVIEW_DECISION_MISMATCH,
                "Chief Architect decision references disagree with review.",
            ))
        if (
            feedback is not None
            and feedback.status
            is FeedbackStatus.CHIEF_ARCHITECT_DECISION_RECORDED
            and review_decision is None
        ):
            issues.append(self._issue(
                ArchitectureOperationIssueCode.DECISION_STATUS_WITHOUT_ARTIFACT,
                "Feedback records a decision without decision artifact.",
            ))

    def _next_step(
        self,
        workflow: Optional[ArchitectureWorkflow],
        decisions: tuple,
        prompt: Path,
        proof: Path,
        authorization: Optional[ExecutionAuthorization],
        execution: Optional[ExecutionRecord],
        feedback: Optional[FeedbackLoopRecord],
        intake: Optional[CodexHandoverIntake],
        review: Optional[ArchitectureImplementationReview],
        review_decision: Optional[ArchitectureImplementationReviewDecision],
        legacy: bool,
        issues: Tuple[ArchitectureOperationIssue, ...],
    ) -> ArchitectureNextStep:
        if legacy:
            return ArchitectureNextStep.COMPLETE
        blocking = {
            ArchitectureOperationIssueCode.WORKFLOW_MISSING,
            ArchitectureOperationIssueCode.PROMPT_WITHOUT_PROOF,
            ArchitectureOperationIssueCode.AUTHORIZATION_WITHOUT_PROMPT,
            ArchitectureOperationIssueCode.EXECUTION_WITHOUT_AUTHORIZATION,
            ArchitectureOperationIssueCode.INTAKE_WITHOUT_HANDOVER,
            ArchitectureOperationIssueCode.REVIEW_WITHOUT_INTAKE,
            ArchitectureOperationIssueCode.DECISION_REQUIRED_WITHOUT_REVIEW,
            ArchitectureOperationIssueCode.RESULT_COMMIT_MISMATCH,
            ArchitectureOperationIssueCode.DUPLICATE_EXECUTION,
            ArchitectureOperationIssueCode.DUPLICATE_REVIEW,
            ArchitectureOperationIssueCode.INVALID_FEEDBACK_TRANSITION,
            ArchitectureOperationIssueCode.UNSAFE_SYMLINK,
            ArchitectureOperationIssueCode.REVIEW_DECISION_WITHOUT_REVIEW,
            ArchitectureOperationIssueCode.REVIEW_DECISION_MISMATCH,
            ArchitectureOperationIssueCode.DECISION_STATUS_WITHOUT_ARTIFACT,
        }
        if any(item.code in blocking for item in issues):
            return ArchitectureNextStep.BLOCKED
        if (
            review_decision is not None
            and feedback is not None
            and feedback.status
            is FeedbackStatus.CHIEF_ARCHITECT_DECISION_RECORDED
        ):
            return ArchitectureNextStep.COMPLETE
        if (
            review is not None
            and feedback is not None
            and feedback.status
            is FeedbackStatus.CHIEF_ARCHITECT_DECISION_REQUIRED
        ):
            return ArchitectureNextStep.CHIEF_ARCHITECT_DECISION_REQUIRED
        if workflow is not None and len(decisions) < len(workflow.proposal_ids):
            return ArchitectureNextStep.CHIEF_ARCHITECT_DECISION_REQUIRED
        if workflow is not None and not prompt.is_file():
            return ArchitectureNextStep.GENERATE_CODEX_PROMPT
        if prompt.is_file() and proof.is_file() and authorization is None:
            return ArchitectureNextStep.EXECUTION_AUTHORIZED
        if authorization is not None and execution is None:
            return ArchitectureNextStep.EXECUTION_REQUIRED
        if execution is not None:
            if execution.status in {
                ExecutionStatus.PENDING,
                ExecutionStatus.RUNNING,
                ExecutionStatus.WAITING_FOR_CAPACITY,
            }:
                return ArchitectureNextStep.EXECUTION_RUNNING
            if execution.status in {
                ExecutionStatus.FAILED,
                ExecutionStatus.BLOCKED,
                ExecutionStatus.CANCELLED,
            }:
                return ArchitectureNextStep.EXECUTION_RETRY_REQUIRED
            if execution.status is ExecutionStatus.SUCCEEDED:
                if not self._handover_available(execution):
                    return ArchitectureNextStep.HANDOVER_REQUIRED
                if intake is None:
                    return ArchitectureNextStep.HANDOVER_VALIDATION_REQUIRED
                if review is None:
                    return ArchitectureNextStep.INTEGRATOR_REVIEW_REQUIRED
        if feedback is not None and feedback.status is FeedbackStatus.FAILED:
            return ArchitectureNextStep.BLOCKED
        return ArchitectureNextStep.BLOCKED

    def _matches(
        self,
        item: ArchitectureOperationStatus,
        query: ArchitectureOperationQuery,
    ) -> bool:
        values = query.to_dict()
        for name in (
            "workflow_id",
            "architecture_run_id",
            "execution_id",
            "orchestration_id",
            "authorization_id",
            "review_id",
        ):
            expected = values[name]
            if expected is not None and getattr(item, name) != expected:
                return False
        if values["orchestration_status"] is not None and (
            item.orchestration_status is None
            or item.orchestration_status.value
            != values["orchestration_status"]
        ):
            return False
        if values["commit"] is not None and (
            item.result_commit is None
            or not item.result_commit.startswith(values["commit"].lower())
        ):
            return False
        if values["handover_path"] is not None and (
            values["handover_path"] not in item.handover_paths
        ):
            return False
        if values["proposal_id"] is not None and (
            values["proposal_id"] not in item.proposal_ids
        ):
            return False
        if values["decision_id"] is not None and (
            values["decision_id"] not in item.decision_ids
            and values["decision_id"] != item.review_decision_id
        ):
            return False
        return True

    def _query_matches(
        self,
        statuses: Tuple[ArchitectureOperationStatus, ...],
        query: ArchitectureOperationQuery,
    ) -> Tuple[ArchitectureOperationStatus, ...]:
        matches = tuple(
            item for item in statuses if self._matches(item, query)
        )
        if query.topic is None:
            return matches
        expected = normalize_topic(query.topic)
        exact = tuple(
            item for item in matches
            if normalize_topic(item.topic) == expected
        )
        selected = exact or tuple(
            item for item in matches
            if expected in normalize_topic(item.topic)
        )
        if len(selected) <= 1:
            return selected
        superseded_ids = {
            item.superseded_workflow_id
            for item in self.supersessions.records()
            if item.canonical_workflow_id in {
                candidate.workflow_id for candidate in selected
            }
        }
        return tuple(
            item for item in selected
            if item.workflow_id not in superseded_ids
        )

    def _candidate(
        self,
        item: ArchitectureOperationStatus,
    ) -> ArchitectureOperationQueryCandidate:
        return ArchitectureOperationQueryCandidate(
            topic=item.topic,
            workflow_id=item.workflow_id,
            architecture_run_id=item.architecture_run_id,
            execution_id=item.execution_id,
            review_id=item.review_id,
            feedback_status=(
                item.feedback_status.value
                if item.feedback_status is not None
                else None
            ),
            next_step=item.next_step,
            superseded=item.superseded,
            canonical_workflow_id=item.canonical_workflow_id,
        )

    def _artifact(self, kind: str, path: Path) -> ArchitectureArtifact:
        availability = ArtifactAvailability.MISSING
        if path.is_symlink():
            availability = ArtifactAvailability.UNSAFE
        elif path.is_file():
            try:
                path.resolve().relative_to(self.repository)
                availability = ArtifactAvailability.PRESENT
            except ValueError:
                availability = ArtifactAvailability.UNSAFE
        return ArchitectureArtifact(
            kind=kind,
            path=self._relative(path),
            availability=availability,
        )

    def _ensure_artifact_kinds(self, artifacts: list) -> None:
        required = (
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
            "chief_architect_review_decision",
            "feedback_record",
        )
        present = {item.kind for item in artifacts}
        artifacts.extend(
            ArchitectureArtifact(
                kind=kind,
                path=None,
                availability=ArtifactAvailability.MISSING,
            )
            for kind in required
            if kind not in present
        )

    def _handover_available(self, execution: ExecutionRecord) -> bool:
        if not execution.handover_paths:
            return False
        return all(
            (self.repository / relative).is_file()
            and not (self.repository / relative).is_symlink()
            for relative in execution.handover_paths
        )

    def _reconstruction_authorization(
        self,
        authorization_id: str,
    ) -> Optional[Path]:
        root = self.repository / "knowledge" / "execution_reconstruction"
        if not root.is_dir() or root.is_symlink():
            return None
        matches = []
        for path in sorted(root.glob("*.json")):
            data = self._json(path)
            if data and data.get("authorization_id") == authorization_id:
                matches.append(path)
        return matches[0] if len(matches) == 1 else None

    def _json(self, path: Path) -> Dict[str, Any]:
        if path.is_symlink() or not path.is_file():
            return {}
        try:
            path.resolve().relative_to(self.repository)
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}
        return data if isinstance(data, dict) else {}

    def _relative(self, path: Path) -> str:
        try:
            return str(path.resolve().relative_to(self.repository))
        except ValueError:
            return str(path)

    def _issue(
        self,
        code: ArchitectureOperationIssueCode,
        message: str,
    ) -> ArchitectureOperationIssue:
        return ArchitectureOperationIssue(code, message)


def render_operation(status: ArchitectureOperationStatus) -> str:
    decision_proposal = next(
        (
            item.path for item in status.artifacts
            if item.kind == "decision_proposal"
            and item.availability is ArtifactAvailability.PRESENT
        ),
        None,
    )
    return "\n".join((
        "Thema: {}".format(status.topic),
        "Workflow: {}".format(status.workflow_id),
        "Architecture Run: {}".format(
            status.architecture_run_id or "missing"
        ),
        "Execution: {}".format(status.execution_id or "missing"),
        "Authorized Branch: {}".format(
            status.authorized_branch or "missing"
        ),
        "Current Branch: {}".format(status.current_branch or "missing"),
        "Branch Match: {}".format(
            status.branch_match
            if status.branch_match is not None else "missing"
        ),
        "Create Commit Authorized: {}".format(
            "yes" if status.create_commit_authorized is True
            else "no" if status.create_commit_authorized is False
            else "missing"
        ),
        "Commit Attempted: {}".format(
            "yes" if status.commit_attempted is True
            else "no" if status.commit_attempted is False
            else "missing"
        ),
        "Orchestration: {}".format(status.orchestration_id or "missing"),
        "Orchestration Status: {}".format(
            status.orchestration_status.value
            if status.orchestration_status else "missing"
        ),
        "Orchestration Step: {}".format(
            status.orchestration_step or "missing"
        ),
        "Orchestration Validation: {}".format(
            status.orchestration_validation
            if status.orchestration_validation is not None else "missing"
        ),
        "Orchestration Blocker: {}".format(
            status.orchestration_blocker or "none"
        ),
        "Execution Origin: {}".format(
            status.execution_origin.value
            if status.execution_origin else "missing"
        ),
        "Attempts: {}".format(status.attempt_count),
        "Review: {}".format(status.review_id or "missing"),
        "Commit: {}".format(status.result_commit or "missing"),
        "Status: {}".format(
            status.feedback_status.value
            if status.feedback_status
            else (
                status.workflow_status.value
                if status.workflow_status
                else "missing"
            )
        ),
        "Empfehlung: {}".format(
            status.review_recommendation or "missing"
        ),
        "Chief-Architect-Entscheidung: {}".format(
            status.review_decision or "missing"
        ),
        "Entscheidungs-ID: {}".format(
            status.review_decision_id or "missing"
        ),
        "Entscheidungsbegründung: {}".format(
            status.review_decision_reason or "missing"
        ),
        "Entscheidungszeitpunkt: {}".format(
            status.review_decided_at or "missing"
        ),
        "Konflikte: {}".format(
            "; ".join(status.conflicts) or "none"
        ),
        "Abweichungen: {}".format(
            "; ".join(status.deviations) or "none"
        ),
        "Offene Risiken: {}".format(
            "; ".join(status.open_risks) or "none"
        ),
        "Entscheidungsvorlage: {}".format(
            decision_proposal or "missing"
        ),
        "Nächster Schritt: {}".format(status.next_step.value),
        "Superseded: {}".format(
            "yes" if status.superseded else "no"
        ),
        "Canonical Workflow: {}".format(
            status.canonical_workflow_id or "none"
        ),
        "Supersession-ID: {}".format(
            status.supersession_id or "none"
        ),
        "Legacy: {}".format("yes" if status.legacy else "no"),
        "Blocker: {}".format(
            "; ".join(item.message for item in status.issues) or "none"
        ),
    ))


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


def _strings(values: object, name: str) -> None:
    if not isinstance(values, tuple) or not all(
        isinstance(item, str) and item and item == item.strip()
        for item in values
    ):
        raise TypeError("{} must contain strings".format(name))
