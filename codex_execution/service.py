import hashlib
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional, Tuple

from architecture_integrator import ArchitectureWorkflowStore, WorkflowStatus
from codex_execution.models import (
    CheckStatus,
    ExecutionPolicy,
    ExecutionRecord,
    ExecutionStatus,
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
        prompt, prompt_hash = self._approved_prompt(workflow_id)
        execution_id = self.execution_id(workflow_id, prompt_hash)
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
            branch = self._required("git", "branch", "--show-current")
            commit = self._required("git", "rev-parse", "HEAD")
            git_status = self._lines(
                self._required("git", "status", "--porcelain")
            )
            root = Path(
                self._required("git", "rev-parse", "--show-toplevel")
            ).resolve()
            if root != self.repository:
                raise RuntimeError("Git repository root changed")
            if existing is None and git_status:
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
                failure_reason=None,
                retry_count=retry_count,
            )
            self.executions.write(record)

            codex = self.codex_resolver()
            if codex is None:
                return self._finish(
                    record,
                    ExecutionStatus.BLOCKED,
                    "Codex CLI is not installed.",
                )
            auth = self.runner.run(
                (codex, "login", "status"),
                cwd=self.repository,
            )
            if auth.exit_code != 0:
                return self._finish(
                    record,
                    ExecutionStatus.BLOCKED,
                    "Codex authentication is unavailable.",
                )

            running = record.evolve(status=ExecutionStatus.RUNNING)
            self.executions.write(running)
            codex_result = self.runner.run(
                (
                    codex,
                    "exec",
                    "--cd",
                    str(self.repository),
                    "--sandbox",
                    "workspace-write",
                    "--ask-for-approval",
                    "never",
                    "-",
                ),
                cwd=self.repository,
                input_text=prompt,
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
                    self._summary(codex_result, "Codex execution failed."),
                    codex_exit_code=codex_result.exit_code,
                )

            test = self.runner.run(
                (sys.executable, "-m", "pytest", "-q"),
                cwd=self.repository,
            )
            if test.exit_code != 0:
                return self._finish(
                    running,
                    ExecutionStatus.FAILED,
                    "Full tests failed; no result is approved.",
                    codex_exit_code=0,
                    test_status=CheckStatus.FAILED,
                    test_result=self._summary(test, "Tests failed."),
                )
            doctor = self.runner.run(
                (sys.executable, "-m", "builder.main", "doctor"),
                cwd=self.repository,
            )
            if doctor.exit_code != 0:
                return self._finish(
                    running,
                    ExecutionStatus.FAILED,
                    "Doctor failed; no result is approved.",
                    codex_exit_code=0,
                    test_status=CheckStatus.PASSED,
                    test_result=self._summary(test, "Tests passed."),
                    doctor_status=CheckStatus.FAILED,
                    doctor_result=self._summary(doctor, "Doctor failed."),
                )
            diff_worktree = self.runner.run(
                ("git", "diff", "--check"),
                cwd=self.repository,
            )
            result_commit = self._required("git", "rev-parse", "HEAD")
            diff_commit = self.runner.run(
                (
                    "git",
                    "diff",
                    "--check",
                    "{}..{}".format(commit, result_commit),
                ),
                cwd=self.repository,
            )
            if diff_worktree.exit_code != 0 or diff_commit.exit_code != 0:
                return self._finish(
                    running,
                    ExecutionStatus.FAILED,
                    "git diff --check failed; no result is approved.",
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
                    "Codex produced no result commit.",
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
                    "Result commit has no complete JSON and Markdown handover.",
                    codex_exit_code=0,
                    test_status=CheckStatus.PASSED,
                    test_result=self._summary(test, "Tests passed."),
                    doctor_status=CheckStatus.PASSED,
                    doctor_result=self._summary(doctor, "Doctor passed."),
                    diff_check_status=CheckStatus.PASSED,
                )
            final_status = self._lines(
                self._required("git", "status", "--porcelain")
            )
            if final_status:
                return self._finish(
                    running,
                    ExecutionStatus.FAILED,
                    "Working tree is not clean after the result commit.",
                    codex_exit_code=0,
                    test_status=CheckStatus.PASSED,
                    test_result=self._summary(test, "Tests passed."),
                    doctor_status=CheckStatus.PASSED,
                    doctor_result=self._summary(doctor, "Doctor passed."),
                    diff_check_status=CheckStatus.PASSED,
                )
            succeeded = running.evolve(
                status=ExecutionStatus.SUCCEEDED,
                completed_at=self.clock(),
                codex_exit_code=0,
                test_status=CheckStatus.PASSED,
                test_result=self._summary(test, "Tests passed."),
                doctor_status=CheckStatus.PASSED,
                doctor_result=self._summary(doctor, "Doctor passed."),
                diff_check_status=CheckStatus.PASSED,
                resulting_commit=result_commit,
                handover_paths=handovers,
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
            failure_reason="Cancelled by explicit user request.",
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

    def _required(self, *arguments: str) -> str:
        result = self.runner.run(arguments, cwd=self.repository)
        if result.exit_code != 0:
            raise RuntimeError(
                self._summary(result, "{} failed.".format(arguments[0]))
            )
        return result.stdout.strip()

    def _finish(
        self,
        record: ExecutionRecord,
        status: ExecutionStatus,
        reason: str,
        **changes: object
    ) -> ExecutionRecord:
        completed = record.evolve(
            status=status,
            completed_at=self.clock(),
            failure_reason=reason,
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

    def _lines(self, value: str) -> Tuple[str, ...]:
        return tuple(line for line in value.splitlines() if line.strip())
