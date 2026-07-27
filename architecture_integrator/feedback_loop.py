import json
import subprocess
from pathlib import Path
from typing import Optional, Tuple

from architecture_integrator.feedback import (
    ApprovalStatus,
    ArchitectureFeedbackStore,
    ArchitectureImplementationReview,
    CodexHandoverIntake,
    ExecutionAuthorization,
    FeedbackLoopRecord,
    FeedbackStatus,
    FeedbackTransition,
    HandoverDeviation,
    stable_identifier,
)
from architecture_integrator.integrator import ArchitectureIntegrator
from architecture_integrator.workflow import (
    ArchitectureWorkflowStore,
    WorkflowStatus,
)
from codex_execution.models import CheckStatus, ExecutionRecord, ExecutionStatus
from codex_execution.errors import redact
from codex_execution.service import CodexExecutionService


class ArchitectureFeedbackLoop:
    """Closes transport gaps without granting architecture authority."""

    ALLOWED_ACTIONS = (
        "modify_authorized_repository",
        "run_tests",
        "run_doctor",
        "run_diff_check",
        "create_commit",
        "create_handover",
    )
    EXPECTED_ARTIFACTS = (
        "result_commit",
        "json_handover",
        "markdown_handover",
        "test_result",
        "doctor_result",
        "git_status",
    )

    def __init__(
        self,
        workflows: ArchitectureWorkflowStore,
        execution: CodexExecutionService,
        integrator: ArchitectureIntegrator,
        repository: Path,
        store: Optional[ArchitectureFeedbackStore] = None,
    ) -> None:
        self.workflows = workflows
        self.execution = execution
        self.integrator = integrator
        self.repository = repository.resolve()
        self.store = store or ArchitectureFeedbackStore(workflows)

    def authorize(
        self,
        workflow_id: str,
        expected_base_commit: Optional[str] = None,
    ) -> ExecutionAuthorization:
        if self.workflows.status(workflow_id) is not (
            WorkflowStatus.CODEX_PROMPT_GENERATED
        ):
            raise RuntimeError(
                "Confirmed decisions and Codex prompt are required"
            )
        existing = self.store.authorization(workflow_id)
        if existing is not None:
            return existing
        decisions = self.workflows.decisions(workflow_id)
        proof = self.workflows.prompt_proof(workflow_id)
        base_commit = expected_base_commit or self._git_head()
        execution_id = self.execution.execution_id(
            workflow_id,
            proof["prompt_hash"],
        )
        decision_ids = tuple(item.decision_id for item in decisions)
        run_id = stable_identifier(
            "architecture-run",
            workflow_id,
            proof["prompt_hash"],
            *decision_ids
        )
        authorization = ExecutionAuthorization(
            authorization_id=stable_identifier(
                "authorization",
                run_id,
                execution_id,
                base_commit,
            ),
            architecture_run_id=run_id,
            workflow_id=workflow_id,
            expected_execution_id=execution_id,
            decision_artifacts=tuple(
                "decisions/{}.json".format(item.proposal_id)
                for item in decisions
            ),
            approval_status=ApprovalStatus.CONFIRMED,
            codex_prompt="prompts/codex-prompt.md",
            prompt_hash=proof["prompt_hash"],
            repository=str(self.repository),
            expected_base_commit=base_commit,
            allowed_actions=self.ALLOWED_ACTIONS,
            expected_completion_artifacts=self.EXPECTED_ARTIFACTS,
            authorized_at=max(item.decided_at for item in decisions),
        )
        self.store.write_authorization(authorization)
        if self.store.record(workflow_id) is None:
            initial = FeedbackLoopRecord(
                architecture_run_id=run_id,
                workflow_id=workflow_id,
                expected_execution_id=execution_id,
                status=FeedbackStatus.DECISION_CONFIRMED,
                transitions=(
                    FeedbackTransition(
                        FeedbackStatus.DECISION_CONFIRMED,
                        authorization.authorized_at,
                        ",".join(decision_ids),
                    ),
                ),
            )
            self.store.write_record(initial)
            self._advance_record(
                initial,
                FeedbackStatus.EXECUTION_AUTHORIZED,
                authorization.authorized_at,
                authorization.authorization_id,
                authorization_id=authorization.authorization_id,
            )
        return authorization

    def advance(self, workflow_id: str) -> FeedbackLoopRecord:
        authorization = self.authorize(workflow_id)
        record = self.store.record(workflow_id)
        if record is None:
            raise RuntimeError("Feedback record was not created")
        if record.status in {
            FeedbackStatus.CHIEF_ARCHITECT_DECISION_REQUIRED,
            FeedbackStatus.FAILED,
        }:
            return record
        execution = self.execution.status(workflow_id)
        if execution is None:
            record = self._advance_record(
                record,
                FeedbackStatus.EXECUTION_RUNNING,
                authorization.authorized_at,
                authorization.expected_execution_id,
                execution_id=authorization.expected_execution_id,
            )
            try:
                execution = self.execution.execute(workflow_id)
            except Exception as error:
                self._advance_record(
                    record,
                    FeedbackStatus.FAILED,
                    authorization.authorized_at,
                    "{}: {}".format(type(error).__name__, error),
                )
                raise
        if execution.status is not ExecutionStatus.SUCCEEDED:
            return self._advance_record(
                record,
                FeedbackStatus.FAILED,
                execution.completed_at or execution.started_at,
                execution.failure.exception_type
                if execution.failure
                else execution.status.value,
                execution_id=execution.execution_id,
            )
        record = self._advance_record(
            record,
            FeedbackStatus.EXECUTION_COMPLETED,
            execution.completed_at or execution.started_at,
            execution.execution_id,
            execution_id=execution.execution_id,
        )
        handover_path = self._handover_json(execution)
        record = self._advance_record(
            record,
            FeedbackStatus.HANDOVER_DISCOVERED,
            execution.completed_at or execution.started_at,
            handover_path,
            handover_path=handover_path,
        )
        intake = self.validate_handover(authorization, execution, handover_path)
        self.store.write_intake(intake)
        if intake.deviations:
            return self._advance_record(
                record,
                FeedbackStatus.FAILED,
                execution.completed_at or execution.started_at,
                ",".join(item.code for item in intake.deviations),
            )
        record = self._advance_record(
            record,
            FeedbackStatus.HANDOVER_VALIDATED,
            execution.completed_at or execution.started_at,
            handover_path,
        )
        review = self.integrator.review_handover(intake)
        self.store.write_review(review)
        record = self._advance_record(
            record,
            FeedbackStatus.INTEGRATOR_REVIEW_READY,
            execution.completed_at or execution.started_at,
            review.review_id,
            review_id=review.review_id,
        )
        return self._advance_record(
            record,
            FeedbackStatus.CHIEF_ARCHITECT_DECISION_REQUIRED,
            execution.completed_at or execution.started_at,
            review.review_id,
        )

    def validate_handover(
        self,
        authorization: ExecutionAuthorization,
        execution: ExecutionRecord,
        handover_path: str,
    ) -> CodexHandoverIntake:
        deviations = []
        if execution.execution_id != authorization.expected_execution_id:
            deviations.append(self._deviation(
                "EXECUTION_ID_MISMATCH",
                "Execution ID does not match the authorization.",
            ))
        if execution.starting_commit != authorization.expected_base_commit:
            deviations.append(self._deviation(
                "BASE_COMMIT_MISMATCH",
                "Execution base commit does not match the authorization.",
            ))
        if execution.resulting_commit is None:
            deviations.append(self._deviation(
                "RESULT_COMMIT_MISSING",
                "Execution has no result commit.",
            ))
        path = (self.repository / handover_path).resolve()
        try:
            path.relative_to(self.repository)
        except ValueError:
            deviations.append(self._deviation(
                "HANDOVER_OUTSIDE_REPOSITORY",
                "Handover path leaves the repository.",
            ))
        data = {}
        if path.is_symlink() or not path.is_file():
            deviations.append(self._deviation(
                "HANDOVER_UNAVAILABLE",
                "Handover is missing or unsafe.",
            ))
        else:
            try:
                loaded = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    data = loaded
                else:
                    raise ValueError("not an object")
            except (OSError, ValueError) as error:
                deviations.append(self._deviation(
                    "HANDOVER_INVALID",
                    "Handover JSON is invalid: {}".format(error),
                ))
        required = {
            "starting_commit",
            "ending_commit",
            "changed_files",
            "checks",
            "git_status",
            "open_risks",
            "push_status",
        }
        for field in sorted(required - set(data)):
            deviations.append(self._deviation(
                "MISSING_{}".format(field.upper()),
                "Handover field {} is missing.".format(field),
            ))
        if data.get("starting_commit") != execution.starting_commit:
            deviations.append(self._deviation(
                "HANDOVER_BASE_MISMATCH",
                "Handover starting commit does not match the execution.",
            ))
        if data.get("ending_commit") != execution.resulting_commit:
            deviations.append(self._deviation(
                "HANDOVER_RESULT_MISMATCH",
                "Handover ending commit does not match the execution.",
            ))
        checks = data.get("checks", [])
        if not isinstance(checks, list):
            checks = []
        check_lines = tuple(
            redact("{}: {} ({})".format(
                item.get("command", "unknown"),
                item.get("status", "unknown"),
                item.get("result", "missing"),
            ))
            for item in checks
            if isinstance(item, dict)
        )
        for label, status in (
            ("tests", execution.test_status),
            ("doctor", execution.doctor_status),
            ("diff", execution.diff_check_status),
        ):
            if status is not CheckStatus.PASSED:
                deviations.append(self._deviation(
                    "{}_NOT_PASSED".format(label.upper()),
                    "{} was not reported as passed.".format(label),
                ))
        if not check_lines:
            deviations.append(self._deviation(
                "CHECKS_MISSING",
                "Handover contains no machine-readable checks.",
            ))
        if any(
            item.get("status") != "passed"
            for item in checks
            if isinstance(item, dict)
        ):
            deviations.append(self._deviation(
                "HANDOVER_CHECK_FAILED",
                "Handover reports a check that did not pass.",
            ))
        lowered_commands = tuple(
            str(item.get("command", "")).lower()
            for item in checks
            if isinstance(item, dict)
        )
        for code, label, markers in (
            ("TEST_REPORT_MISSING", "Tests", ("pytest",)),
            (
                "DOCTOR_REPORT_MISSING",
                "Doctor",
                ("builder.main doctor",),
            ),
            (
                "DIFF_REPORT_MISSING",
                "Git diff check",
                ("git diff --check",),
            ),
        ):
            if not any(
                all(marker in command for marker in markers)
                for command in lowered_commands
            ):
                deviations.append(self._deviation(
                    code,
                    "{} is not reported in the handover.".format(label),
                ))
        if not data.get("git_status"):
            deviations.append(self._deviation(
                "GIT_STATUS_MISSING",
                "Handover contains no Git status.",
            ))
        if (
            "push" not in authorization.allowed_actions
            and data.get("push_status") != "not_pushed"
        ):
            deviations.append(self._deviation(
                "UNAUTHORIZED_PUSH_STATUS",
                "Handover does not confirm that no push occurred.",
            ))
        decisions = self.workflows.decisions(authorization.workflow_id)
        return CodexHandoverIntake(
            architecture_run_id=authorization.architecture_run_id,
            workflow_id=authorization.workflow_id,
            execution_id=execution.execution_id,
            authorization_id=authorization.authorization_id,
            decision_ids=tuple(item.decision_id for item in decisions),
            attempt_ids=tuple(
                item.attempt_id for item in execution.attempts
            ),
            starting_commit=execution.starting_commit,
            result_commit=execution.resulting_commit or (
                authorization.expected_base_commit
            ),
            handover_path=handover_path,
            changed_files=self._string_values(
                data.get("changed_files", [])
            ),
            checks=check_lines,
            git_status=self._string_values(data.get("git_status", [])),
            open_risks=self._string_values(data.get("open_risks", [])),
            deviations=tuple(deviations),
        )

    def _handover_json(self, execution: ExecutionRecord) -> str:
        candidates = tuple(
            item for item in execution.handover_paths
            if item.endswith(".json")
        )
        if len(candidates) != 1:
            raise ValueError(
                "Execution must identify exactly one JSON handover"
            )
        return candidates[0]

    def _advance_record(
        self,
        record: FeedbackLoopRecord,
        status: FeedbackStatus,
        occurred_at,
        reference: str,
        **changes
    ) -> FeedbackLoopRecord:
        updated = record.advance(status, occurred_at, reference, **changes)
        self.store.write_record(updated)
        return updated

    def _git_head(self) -> str:
        result = subprocess.run(
            ("git", "rev-parse", "HEAD"),
            cwd=str(self.repository),
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError("Cannot determine repository HEAD")
        return result.stdout.strip()

    def _deviation(self, code: str, message: str) -> HandoverDeviation:
        return HandoverDeviation(code=code, message=message)

    def _string_values(self, value: object) -> Tuple[str, ...]:
        if not isinstance(value, list):
            return ()
        return tuple(
            redact(item)
            for item in value
            if isinstance(item, str) and item
        )
