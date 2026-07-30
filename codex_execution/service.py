import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional, Tuple

from architecture_integrator.feedback import (
    ApprovalStatus,
    ExecutionAuthorization,
)
from architecture_integrator.workflow import (
    ArchitectureWorkflowStore,
    WorkflowStatus,
)
from codex_execution.models import (
    AttemptTrigger,
    CheckStatus,
    ExecutionAttempt,
    ExecutionFailure,
    ExecutionFailureKind,
    ExecutionPolicy,
    ExecutionRecord,
    ExecutionStep,
    ExecutionStatus,
    RedactionStatus,
    execution_attempt_id,
)
from codex_execution.errors import (
    ExecutionBridgeError,
    failure_from_exception,
    process_failure,
    redact,
)
from codex_execution.runner import CommandResult, SubprocessCommandRunner
from codex_execution.store import ExecutionStore


class CodexExecutionService:
    """Transports confirmed prompts to Codex without decision authority."""

    DEFAULT_REPOSITORY = Path("/Users/michaelgiese/zonvaa-builder")

    def __init__(
        self,
        workflows: ArchitectureWorkflowStore,
        executions: ExecutionStore,
        repository: Path = DEFAULT_REPOSITORY,
        allowed_repository: Path = DEFAULT_REPOSITORY,
        runner: SubprocessCommandRunner = SubprocessCommandRunner(),
        clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
        codex_resolver: Callable[[], Optional[str]] = (
            lambda: shutil.which("codex")
        ),
        policy: ExecutionPolicy = ExecutionPolicy(),
    ) -> None:
        self.workflows = workflows
        self.executions = executions
        self.repository = repository.resolve()
        self.allowed_repository = allowed_repository.resolve()
        self.runner = runner
        self.clock = clock
        self.codex_resolver = codex_resolver
        self.policy = policy
        if self.repository != self.allowed_repository:
            raise ValueError("Execution repository is not authorized")

    def execution_id(self, workflow_id: str, prompt_hash: str) -> str:
        digest = hashlib.sha256(
            "{}\0{}".format(workflow_id, prompt_hash).encode("utf-8")
        ).hexdigest()
        return "execution-{}".format(digest[:16])

    def status(self, workflow_id: str) -> Optional[ExecutionRecord]:
        proof = self.workflows.prompt_proof(workflow_id)
        execution_id = self.execution_id(
            workflow_id,
            proof["prompt_hash"],
        )
        return self.executions.existing(workflow_id, execution_id)

    def execute(
        self,
        workflow_id: str,
        retry: bool = False,
    ) -> ExecutionRecord:
        if type(self.runner) is SubprocessCommandRunner:
            raise RuntimeError(
                "LEGACY_EXECUTION_DISABLED: use 'builder.main task run'; "
                "the legacy bridge is read-only under Builder Reset v2"
            )
        try:
            return self._execute(workflow_id, retry)
        except ExecutionBridgeError as error:
            failure = error.failure
            if failure.execution_id is not None:
                existing = self.executions.existing(
                    workflow_id,
                    failure.execution_id,
                )
                if existing is not None and existing.status in (
                    ExecutionStatus.PENDING,
                    ExecutionStatus.RUNNING,
                ):
                    return self._finish(
                        existing,
                        ExecutionStatus.FAILED,
                        failure,
                        codex_exit_code=(
                            failure.exit_code
                            if failure.step is ExecutionStep.CODEX_EXECUTION
                            else existing.codex_exit_code
                        ),
                    )
            raise
        except Exception as error:
            kind = (
                ExecutionFailureKind.INPUT_NOT_FOUND
                if (
                    isinstance(error, FileNotFoundError)
                    or "confirmed Codex prompt" in str(error)
                )
                else ExecutionFailureKind.INTERNAL_ERROR
            )
            raise ExecutionBridgeError(
                failure_from_exception(
                    error,
                    step=ExecutionStep.PROMPT_VALIDATION,
                    occurred_at=self.clock(),
                    cwd=self.repository,
                    kind=kind,
                )
            ) from error

    def _execute(
        self,
        workflow_id: str,
        retry: bool = False,
    ) -> ExecutionRecord:
        prompt, prompt_hash = self._approved_prompt(workflow_id)
        execution_id = self.execution_id(workflow_id, prompt_hash)
        authorization = self._feedback_authorization(workflow_id)
        if authorization is not None:
            if (
                authorization.approval_status is not ApprovalStatus.CONFIRMED
                or authorization.workflow_id != workflow_id
                or authorization.expected_execution_id != execution_id
                or authorization.prompt_hash != prompt_hash
                or Path(authorization.repository).resolve()
                != self.repository
            ):
                raise RuntimeError(
                    "Execution authorization does not match the prompt"
                )
        with self.executions.lock(workflow_id):
            existing = self.executions.existing(
                workflow_id,
                execution_id,
            )
            if existing is not None:
                if existing.status is ExecutionStatus.SUCCEEDED:
                    raise RuntimeError(
                        "Workflow prompt was already executed successfully"
                    )
                if not retry:
                    raise RuntimeError(
                        "Existing execution requires explicit retry"
                    )
                if existing.status is ExecutionStatus.RUNNING:
                    raise RuntimeError("Execution is already running")
                if existing.status is ExecutionStatus.CANCELLED:
                    raise RuntimeError("Cancelled execution cannot be retried")
            branch = self._required(
                ExecutionStep.REPOSITORY_INSPECTION,
                "git", "branch", "--show-current",
                execution_id=execution_id,
            )
            if authorization is not None:
                if authorization.authorized_branch is None:
                    raise RuntimeError("AUTHORIZED_BRANCH_MISSING")
                if not branch:
                    raise RuntimeError("DETACHED_HEAD_NOT_ALLOWED")
                if branch != authorization.authorized_branch:
                    raise RuntimeError(
                        "AUTHORIZED_BRANCH_MISMATCH: authorized={} actual={}"
                        .format(authorization.authorized_branch, branch)
                    )
            commit = self._required(
                ExecutionStep.REPOSITORY_INSPECTION,
                "git", "rev-parse", "HEAD",
                execution_id=execution_id,
            )
            git_status = self._lines(
                self._required(
                    ExecutionStep.REPOSITORY_INSPECTION,
                    "git", "status", "--porcelain",
                    execution_id=execution_id,
                )
            )
            root = Path(
                self._required(
                    ExecutionStep.REPOSITORY_INSPECTION,
                    "git", "rev-parse", "--show-toplevel",
                    execution_id=execution_id,
                )
            ).resolve()
            if root != self.repository:
                raise RuntimeError("Git repository root changed")
            if (
                authorization is not None
                and commit != authorization.expected_base_commit
            ):
                raise RuntimeError(
                    "Repository HEAD differs from authorized base commit"
                )
            if existing is None and git_status:
                if (
                    authorization is None
                    or not self._authorized_workflow_changes(
                        workflow_id,
                        git_status,
                    )
                ):
                    raise RuntimeError(
                        "New execution requires a clean working tree"
                    )
            if existing is not None:
                if branch != existing.starting_branch:
                    raise RuntimeError(
                        "Retry branch differs from the recorded branch"
                    )
                if commit != existing.starting_commit:
                    raise RuntimeError(
                        "Retry commit differs from the recorded start commit"
                    )
                branch = existing.starting_branch
                commit = existing.starting_commit
                starting_status = existing.starting_git_status
                retry_count = existing.retry_count + 1
                started_at = existing.started_at
            else:
                starting_status = git_status
                retry_count = 0
                started_at = self.clock()

            attempt_number = len(existing.attempts) + 1 if existing else 1
            attempt_started_at = self.clock()
            attempt = ExecutionAttempt(
                attempt_id=self.attempt_id(execution_id, attempt_number),
                execution_id=execution_id,
                attempt_number=attempt_number,
                started_at=attempt_started_at,
                completed_at=None,
                status=ExecutionStatus.PENDING,
                trigger=(
                    AttemptTrigger.RETRY if retry else AttemptTrigger.INITIAL
                ),
                step=ExecutionStep.REPOSITORY_INSPECTION,
                program=None,
                arguments=(),
                working_directory=str(self.repository),
                exit_code=None,
                stdout="",
                stderr="",
                failure_kind=None,
                exception_type=None,
                exception_message=None,
                technical_cause=None,
                verification_status=CheckStatus.NOT_RUN,
                verification_result=None,
                redaction_status=RedactionStatus.PENDING,
                authorization_reference=self._authorization_reference(
                    workflow_id,
                    prompt_hash,
                ),
            )

            record = ExecutionRecord(
                execution_id=execution_id,
                workflow_id=workflow_id,
                prompt_path="prompts/codex-prompt.md",
                prompt_hash=prompt_hash,
                repository_path=str(self.repository),
                starting_branch=branch,
                starting_commit=commit,
                starting_git_status=starting_status,
                status=ExecutionStatus.PENDING,
                started_at=started_at,
                completed_at=None,
                codex_exit_code=None,
                test_status=CheckStatus.NOT_RUN,
                test_result=None,
                doctor_status=CheckStatus.NOT_RUN,
                doctor_result=None,
                diff_check_status=CheckStatus.NOT_RUN,
                resulting_commit=None,
                handover_paths=(),
                failure=None,
                attempts=(existing.attempts if existing else ()) + (attempt,),
                retry_count=retry_count,
            )
            self.executions.write(record)

            try:
                codex = self.codex_resolver()
            except Exception as error:
                raise ExecutionBridgeError(
                    failure_from_exception(
                        error,
                        step=ExecutionStep.CODEX_RESOLUTION,
                        occurred_at=self.clock(),
                        cwd=self.repository,
                        execution_id=execution_id,
                    )
                ) from error
            if codex is None:
                return self._finish(
                    record,
                    ExecutionStatus.BLOCKED,
                    ExecutionFailure(
                        kind=ExecutionFailureKind.EXECUTABLE_NOT_FOUND,
                        step=ExecutionStep.CODEX_RESOLUTION,
                        program="codex",
                        arguments=(),
                        working_directory=str(self.repository),
                        exit_code=None,
                        stdout="",
                        stderr="",
                        exception_type="ExecutableNotFoundError",
                        exception_message="Codex CLI executable was not found.",
                        technical_cause=(
                            "The executable resolver returned no program path."
                        ),
                        occurred_at=self.clock(),
                        execution_id=execution_id,
                    ),
                )
            auth = self._run(
                (codex, "login", "status"),
                ExecutionStep.AUTHENTICATION_CHECK,
                execution_id,
            )
            if auth.exit_code != 0:
                return self._finish(
                    record,
                    ExecutionStatus.BLOCKED,
                    self._process_failure(
                        ExecutionStep.AUTHENTICATION_CHECK,
                        (codex, "login", "status"),
                        auth,
                        execution_id,
                    ),
                )

            codex_arguments = (
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
            running_attempt = record.attempts[-1].transition(
                status=ExecutionStatus.RUNNING,
                step=ExecutionStep.CODEX_EXECUTION,
                program=codex,
                arguments=codex_arguments[1:],
            )
            running = record.evolve(
                status=ExecutionStatus.RUNNING,
                attempts=record.attempts[:-1] + (running_attempt,),
            )
            self.executions.write(running)
            codex_result = self._run(
                codex_arguments,
                ExecutionStep.CODEX_EXECUTION,
                execution_id,
                input_text=prompt,
                sensitive_values=(prompt,),
            )
            if codex_result.exit_code != 0:
                status = (
                    ExecutionStatus.WAITING_FOR_CAPACITY
                    if self._capacity_failure(codex_result)
                    else ExecutionStatus.FAILED
                )
                return self._finish(
                    running,
                    status,
                    self._process_failure(
                        ExecutionStep.CODEX_EXECUTION,
                        codex_arguments,
                        codex_result,
                        execution_id,
                        sensitive_values=(prompt,),
                    ),
                    codex_exit_code=codex_result.exit_code,
                )

            test_arguments = (sys.executable, "-m", "pytest", "-q")
            test = self._run(
                test_arguments,
                ExecutionStep.TEST_EXECUTION,
                execution_id,
            )
            if test.exit_code != 0:
                return self._finish(
                    running,
                    ExecutionStatus.FAILED,
                    self._process_failure(
                        ExecutionStep.TEST_EXECUTION,
                        test_arguments,
                        test,
                        execution_id,
                    ),
                    codex_exit_code=0,
                    test_status=CheckStatus.FAILED,
                    test_result=self._summary(test, "Tests failed."),
                )
            doctor_arguments = (
                sys.executable, "-m", "builder.main", "doctor"
            )
            doctor = self._run(
                doctor_arguments,
                ExecutionStep.DOCTOR_EXECUTION,
                execution_id,
            )
            if doctor.exit_code != 0:
                return self._finish(
                    running,
                    ExecutionStatus.FAILED,
                    self._process_failure(
                        ExecutionStep.DOCTOR_EXECUTION,
                        doctor_arguments,
                        doctor,
                        execution_id,
                    ),
                    codex_exit_code=0,
                    test_status=CheckStatus.PASSED,
                    test_result=self._summary(test, "Tests passed."),
                    doctor_status=CheckStatus.FAILED,
                    doctor_result=self._summary(doctor, "Doctor failed."),
                )
            diff_worktree_arguments = ("git", "diff", "--check")
            diff_worktree = self._run(
                diff_worktree_arguments,
                ExecutionStep.DIFF_CHECK,
                execution_id,
            )
            result_commit = self._required(
                ExecutionStep.RESULT_VERIFICATION,
                "git", "rev-parse", "HEAD",
                execution_id=execution_id,
            )
            diff_commit_arguments = (
                    "git",
                    "diff",
                    "--check",
                    "{}..{}".format(commit, result_commit),
            )
            diff_commit = self._run(
                diff_commit_arguments,
                ExecutionStep.DIFF_CHECK,
                execution_id,
            )
            if diff_worktree.exit_code != 0 or diff_commit.exit_code != 0:
                return self._finish(
                    running,
                    ExecutionStatus.FAILED,
                    self._process_failure(
                        ExecutionStep.DIFF_CHECK,
                        (
                            diff_worktree_arguments
                            if diff_worktree.exit_code != 0
                            else diff_commit_arguments
                        ),
                        (
                            diff_worktree
                            if diff_worktree.exit_code != 0
                            else diff_commit
                        ),
                        execution_id,
                    ),
                    codex_exit_code=0,
                    test_status=CheckStatus.PASSED,
                    test_result=self._summary(test, "Tests passed."),
                    doctor_status=CheckStatus.PASSED,
                    doctor_result=self._summary(doctor, "Doctor passed."),
                    diff_check_status=CheckStatus.FAILED,
                )
            if result_commit == commit:
                return self._finish(
                    running,
                    ExecutionStatus.FAILED,
                    self._internal_failure(
                        ExecutionStep.RESULT_VERIFICATION,
                        "ResultCommitMissingError",
                        "Codex produced no result commit.",
                        execution_id,
                        program=codex,
                        arguments=codex_arguments[1:],
                        exit_code=codex_result.exit_code,
                        stdout=codex_result.stdout,
                        stderr=codex_result.stderr,
                        sensitive_values=(prompt,),
                    ),
                    codex_exit_code=0,
                    test_status=CheckStatus.PASSED,
                    test_result=self._summary(test, "Tests passed."),
                    doctor_status=CheckStatus.PASSED,
                    doctor_result=self._summary(doctor, "Doctor passed."),
                    diff_check_status=CheckStatus.PASSED,
                )
            handovers = self._handover_paths(commit, result_commit)
            if not self._complete_handover(handovers):
                return self._finish(
                    running,
                    ExecutionStatus.FAILED,
                    self._internal_failure(
                        ExecutionStep.RESULT_VERIFICATION,
                        "HandoverMissingError",
                        "Result commit has no complete JSON and Markdown handover.",
                        execution_id,
                        program=codex,
                        arguments=codex_arguments[1:],
                        exit_code=codex_result.exit_code,
                        stdout=codex_result.stdout,
                        stderr=codex_result.stderr,
                        sensitive_values=(prompt,),
                    ),
                    codex_exit_code=0,
                    test_status=CheckStatus.PASSED,
                    test_result=self._summary(test, "Tests passed."),
                    doctor_status=CheckStatus.PASSED,
                    doctor_result=self._summary(doctor, "Doctor passed."),
                    diff_check_status=CheckStatus.PASSED,
                )
            final_status = self._lines(
                self._required(
                    ExecutionStep.RESULT_VERIFICATION,
                    "git", "status", "--porcelain",
                    execution_id=execution_id,
                )
            )
            if final_status:
                return self._finish(
                    running,
                    ExecutionStatus.FAILED,
                    self._internal_failure(
                        ExecutionStep.RESULT_VERIFICATION,
                        "WorkingTreeDirtyError",
                        "Working tree is not clean after the result commit.",
                        execution_id,
                        program=codex,
                        arguments=codex_arguments[1:],
                        exit_code=codex_result.exit_code,
                        stdout=codex_result.stdout,
                        stderr=codex_result.stderr,
                        sensitive_values=(prompt,),
                    ),
                    codex_exit_code=0,
                    test_status=CheckStatus.PASSED,
                    test_result=self._summary(test, "Tests passed."),
                    doctor_status=CheckStatus.PASSED,
                    doctor_result=self._summary(doctor, "Doctor passed."),
                    diff_check_status=CheckStatus.PASSED,
                )
            completed_at = self.clock()
            succeeded_attempt = running.attempts[-1].transition(
                status=ExecutionStatus.SUCCEEDED,
                completed_at=completed_at,
                step=ExecutionStep.RESULT_VERIFICATION,
                program=codex,
                arguments=codex_arguments[1:],
                exit_code=0,
                stdout=redact(codex_result.stdout, (prompt,)),
                stderr=redact(codex_result.stderr, (prompt,)),
                failure_kind=None,
                exception_type=None,
                exception_message=None,
                technical_cause=None,
                verification_status=CheckStatus.PASSED,
                verification_result="All result verification checks passed.",
                redaction_status=RedactionStatus.APPLIED,
            )
            succeeded = running.evolve(
                status=ExecutionStatus.SUCCEEDED,
                completed_at=completed_at,
                codex_exit_code=0,
                test_status=CheckStatus.PASSED,
                test_result=self._summary(test, "Tests passed."),
                doctor_status=CheckStatus.PASSED,
                doctor_result=self._summary(doctor, "Doctor passed."),
                diff_check_status=CheckStatus.PASSED,
                resulting_commit=result_commit,
                handover_paths=handovers,
                attempts=running.attempts[:-1] + (succeeded_attempt,),
            )
            self.executions.write(succeeded)
            return succeeded

    def cancel(self, workflow_id: str) -> ExecutionRecord:
        record = self.status(workflow_id)
        if record is None:
            raise RuntimeError("No execution exists")
        if record.status is ExecutionStatus.RUNNING:
            raise RuntimeError(
                "A running process must be stopped before cancellation"
            )
        if record.status is ExecutionStatus.SUCCEEDED:
            raise RuntimeError("Successful execution cannot be cancelled")
        cancelled = record.evolve(
            status=ExecutionStatus.CANCELLED,
            completed_at=self.clock(),
            failure=None,
        )
        self.executions.write(cancelled)
        return cancelled

    def _approved_prompt(self, workflow_id: str) -> Tuple[str, str]:
        if self.workflows.status(workflow_id) is not (
            WorkflowStatus.CODEX_PROMPT_GENERATED
        ):
            raise RuntimeError("Workflow has no confirmed Codex prompt")
        self.workflows.decisions(workflow_id)
        path = self.workflows.prompt_path(workflow_id)
        if path.is_symlink():
            raise ValueError("Codex prompt cannot be a symlink")
        resolved = path.resolve()
        resolved.relative_to(self.repository)
        expected = (
            self.workflows.folder(workflow_id)
            / "prompts"
            / "codex-prompt.md"
        ).resolve()
        if resolved != expected:
            raise ValueError("Codex prompt path is not canonical")
        proof = self.workflows.prompt_proof(workflow_id)
        content = path.read_text(encoding="utf-8")
        calculated = hashlib.sha256(content.encode("utf-8")).hexdigest()
        if calculated != proof["prompt_hash"]:
            raise ValueError("Codex prompt hash changed")
        return content, calculated

    def _run(
        self,
        arguments: Tuple[str, ...],
        step: ExecutionStep,
        execution_id: Optional[str],
        input_text: Optional[str] = None,
        sensitive_values: Tuple[str, ...] = (),
    ) -> CommandResult:
        try:
            return self.runner.run(
                arguments,
                cwd=self.repository,
                input_text=input_text,
                step=step,
                execution_id=execution_id,
                sensitive_values=sensitive_values,
            )
        except ExecutionBridgeError:
            raise
        except Exception as error:
            raise ExecutionBridgeError(
                failure_from_exception(
                    error,
                    step=step,
                    occurred_at=self.clock(),
                    cwd=self.repository,
                    execution_id=execution_id,
                    arguments=arguments,
                    sensitive_values=sensitive_values,
                )
            ) from error

    def _required(
        self,
        step: ExecutionStep,
        *arguments: str,
        execution_id: Optional[str] = None
    ) -> str:
        result = self._run(tuple(arguments), step, execution_id)
        if result.exit_code != 0:
            raise ExecutionBridgeError(
                self._process_failure(
                    step, tuple(arguments), result, execution_id
                )
            )
        return result.stdout.strip()

    def _finish(
        self,
        record: ExecutionRecord,
        status: ExecutionStatus,
        failure: ExecutionFailure,
        **changes: object
    ) -> ExecutionRecord:
        completed_at = self.clock()
        current_attempt = record.attempts[-1]
        completed_attempt = current_attempt.transition(
            status=status,
            completed_at=completed_at,
            step=failure.step,
            program=failure.program,
            arguments=failure.arguments,
            exit_code=failure.exit_code,
            stdout=failure.stdout,
            stderr=failure.stderr,
            failure_kind=failure.kind,
            exception_type=failure.exception_type,
            exception_message=failure.exception_message,
            technical_cause=failure.technical_cause,
            verification_status=CheckStatus.FAILED,
            verification_result=failure.exception_message,
            redaction_status=RedactionStatus.APPLIED,
        )
        completed = record.evolve(
            status=status,
            completed_at=completed_at,
            failure=failure,
            attempts=record.attempts[:-1] + (completed_attempt,),
            **changes
        )
        self.executions.write(completed)
        return completed

    def _handover_paths(
        self,
        starting_commit: str,
        resulting_commit: str,
    ) -> Tuple[str, ...]:
        output = self._required(
            ExecutionStep.RESULT_VERIFICATION,
            "git",
            "diff-tree",
            "--no-commit-id",
            "--name-only",
            "-r",
            "{}..{}".format(starting_commit, resulting_commit),
        )
        return tuple(
            line
            for line in self._lines(output)
            if line.startswith("knowledge/handovers/")
            and (line.endswith(".json") or line.endswith(".md"))
        )

    def _complete_handover(self, paths: Tuple[str, ...]) -> bool:
        json_stems = {
            Path(path).with_suffix("").as_posix()
            for path in paths
            if path.endswith(".json")
        }
        markdown_stems = {
            Path(path).with_suffix("").as_posix()
            for path in paths
            if path.endswith(".md")
        }
        return bool(json_stems & markdown_stems)

    def _capacity_failure(self, result: CommandResult) -> bool:
        output = result.output.lower()
        return any(
            phrase in output
            for phrase in (
                "usage limit",
                "rate limit",
                "capacity",
                "quota",
                "try again later",
            )
        )

    def _summary(self, result: CommandResult, fallback: str) -> str:
        lines = self._lines(result.output)
        value = lines[-1] if lines else fallback
        return value[:1000]

    def _process_failure(
        self,
        step: ExecutionStep,
        arguments: Tuple[str, ...],
        result: CommandResult,
        execution_id: Optional[str],
        sensitive_values: Tuple[str, ...] = (),
    ) -> ExecutionFailure:
        return process_failure(
            step=step,
            occurred_at=self.clock(),
            cwd=self.repository,
            arguments=arguments,
            exit_code=result.exit_code,
            stdout=result.stdout,
            stderr=result.stderr,
            execution_id=execution_id,
            sensitive_values=sensitive_values,
        )

    def _internal_failure(
        self,
        step: ExecutionStep,
        exception_type: str,
        message: str,
        execution_id: Optional[str],
        program: Optional[str] = None,
        arguments: Tuple[str, ...] = (),
        exit_code: Optional[int] = None,
        stdout: str = "",
        stderr: str = "",
        sensitive_values: Tuple[str, ...] = (),
    ) -> ExecutionFailure:
        return ExecutionFailure(
            kind=ExecutionFailureKind.INTERNAL_ERROR,
            step=step,
            program=program,
            arguments=arguments,
            working_directory=str(self.repository),
            exit_code=exit_code,
            stdout=redact(stdout, sensitive_values),
            stderr=redact(stderr, sensitive_values),
            exception_type=exception_type,
            exception_message=message,
            technical_cause=message,
            occurred_at=self.clock(),
            execution_id=execution_id,
        )

    def _lines(self, value: str) -> Tuple[str, ...]:
        return tuple(line for line in value.splitlines() if line.strip())

    def attempt_id(self, execution_id: str, attempt_number: int) -> str:
        return execution_attempt_id(execution_id, attempt_number)

    def _authorization_reference(
        self,
        workflow_id: str,
        prompt_hash: str,
    ) -> str:
        return "{}:prompts/codex-prompt.md#sha256={}".format(
            workflow_id,
            prompt_hash,
        )

    def _feedback_authorization(
        self,
        workflow_id: str,
    ) -> Optional[ExecutionAuthorization]:
        path = (
            self.workflows.folder(workflow_id)
            / "feedback"
            / "execution-authorization.json"
        )
        if not path.exists():
            return None
        if path.is_symlink() or not path.is_file():
            raise ValueError("Execution authorization is unsafe")
        return ExecutionAuthorization.from_dict(
            json.loads(path.read_text(encoding="utf-8"))
        )

    def _authorized_workflow_changes(
        self,
        workflow_id: str,
        git_status: Tuple[str, ...],
    ) -> bool:
        prefix = "knowledge/architecture_workflows/{}/".format(workflow_id)
        paths = []
        for line in git_status:
            if len(line) < 4:
                return False
            path = line[3:]
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            paths.append(path)
        return bool(paths) and all(path.startswith(prefix) for path in paths)
