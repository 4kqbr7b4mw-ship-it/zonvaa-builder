from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, Optional, Sequence, Tuple

from builder_task.models import (
    CheckResult,
    CommitApproval,
    ExecutionResult,
    GateStatus,
    GitGateResult,
    GuardResult,
    GuardStatus,
    ImmutableTask,
    PushApproval,
    RepositoryLock,
    RunReceipt,
    RunResult,
    VetoClassification,
)
from builder_task.store import BuilderTaskStore


class CommandResult:
    def __init__(self, exit_code: int, stdout: str, stderr: str) -> None:
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr

    @property
    def output(self) -> str:
        return "\n".join(value for value in (self.stdout.strip(), self.stderr.strip()) if value)


class LocalCommandRunner:
    def run(self, arguments, cwd, **_kwargs):
        result = subprocess.run(
            list(arguments), cwd=str(cwd), capture_output=True, text=True, check=False
        )
        return CommandResult(result.returncode, result.stdout, result.stderr)

    def run_tracked(self, arguments, cwd, process_started, input_text=None, **_kwargs):
        process = subprocess.Popen(
            list(arguments), cwd=str(cwd), stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        process_started(process.pid)
        stdout, stderr = process.communicate(input=input_text)
        return CommandResult(process.returncode, stdout, stderr)


class TaskRunError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__("{}: {}".format(code, message))


class BuilderTaskService:
    """The single process owner for Builder Reset v2 task executions."""

    def __init__(
        self,
        repository: Path,
        runner: Optional[LocalCommandRunner] = None,
        codex_program: Optional[str] = None,
        now: Optional[Callable[[], datetime]] = None,
    ) -> None:
        self.repository = repository.resolve()
        self.store = BuilderTaskStore(self.repository)
        self.runner = runner or LocalCommandRunner()
        self.codex_program = codex_program
        self.now = now or (lambda: datetime.now(timezone.utc))

    def load_input(self, path: Path) -> ImmutableTask:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise TaskRunError("INVALID_TASK", "Task file must contain an object")
        return ImmutableTask.from_dict(data)

    def guard(self, task: ImmutableTask) -> GuardResult:
        blockers = []
        if Path(task.repository).resolve() != self.repository:
            blockers.append("REPOSITORY_MISMATCH")
        branch = self._git("branch", "--show-current").stdout.strip()
        head = self._git("rev-parse", "HEAD").stdout.strip()
        status = self._status_entries()
        if branch != task.branch:
            blockers.append("BRANCH_MISMATCH")
        if head != task.start_head:
            blockers.append("START_HEAD_MISMATCH")
        if status:
            blockers.append("WORKING_TREE_DIRTY")
        if task.veto_classification is VetoClassification.HUMAN_CLASSIFICATION_REQUIRED:
            blockers.append("VETO_CLASSIFICATION_REQUIRED")
        if (
            task.veto_classification is VetoClassification.VETO_REQUIRED
            and (not task.plan_approved_by or not task.plan_approved_at)
        ):
            blockers.append("PLAN_APPROVAL_REQUIRED")
        if self.store.read_lock() is not None:
            blockers.append("REPOSITORY_LOCKED")
        return GuardResult(
            status=GuardStatus.BLOCKED if blockers else GuardStatus.ALLOWED,
            blockers=tuple(blockers),
            branch=branch,
            head=head,
            git_status=status,
        )

    def run(self, task: ImmutableTask) -> RunReceipt:
        if (self.store.task_dir(task.task_id) / "receipt.json").exists():
            raise TaskRunError("TASK_ALREADY_RUN", "A receipt already exists")
        guard = self.guard(task)
        if guard.status is GuardStatus.BLOCKED:
            raise TaskRunError("GUARD_BLOCKED", ", ".join(guard.blockers))
        self.store.save_task(task)
        lock = RepositoryLock(task.task_id, os.getpid(), self.now(), str(self.repository))
        self.store.acquire_lock(lock)
        started = self.now()
        process_started = False
        exit_code = None
        stdout = ""
        stderr = ""
        result = RunResult.INTERRUPTED
        origin_before = self._origin_head()
        try:
            try:
                command = self._codex_command()
                prompt = self._prompt(task)

                def mark_started(_pid: int) -> None:
                    nonlocal process_started
                    process_started = True

                process = self.runner.run_tracked(
                    command,
                    cwd=self.repository,
                    process_started=mark_started,
                    input_text=prompt,
                )
                exit_code, stdout, stderr = process.exit_code, process.stdout, process.stderr
                result = RunResult.COMPLETED if exit_code == 0 else RunResult.FAILED
            except (OSError, TaskRunError) as error:
                stderr = "{}: {}".format(type(error).__name__, error)
                result = RunResult.FAILED
            self.store.write_log(task.task_id, "stdout.log", _redact(stdout))
            self.store.write_log(task.task_id, "stderr.log", _redact(stderr))
            gate = self.git_gate(task, origin_before)
            if not gate.passed:
                result = RunResult.FAILED
            ended = self.now()
            receipt = RunReceipt(
                task_id=task.task_id,
                branch=task.branch,
                start_head=task.start_head,
                started_at=started,
                ended_at=ended,
                process_started=process_started,
                exit_code=exit_code,
                result=result,
                checks=gate.checks,
                commit_status="NOT_ATTEMPTED",
                push_status="NOT_ATTEMPTED",
                git_gate=gate,
            )
            self.store.save_receipt(receipt)
            return receipt
        except KeyboardInterrupt:
            gate = self.git_gate(task, origin_before)
            receipt = RunReceipt(
                task.task_id, task.branch, task.start_head, started, self.now(),
                process_started, None, RunResult.INTERRUPTED, gate.checks,
                "NOT_ATTEMPTED", "NOT_ATTEMPTED", gate,
            )
            self.store.save_receipt(receipt)
            raise
        finally:
            self.store.release_lock(task.task_id, os.getpid())

    def git_gate(self, task: ImmutableTask, origin_before: Optional[str] = None) -> GitGateResult:
        branch = self._git("branch", "--show-current").stdout.strip()
        head = self._git("rev-parse", "HEAD").stdout.strip()
        staged = self._lines(self._git("diff", "--cached", "--name-only").stdout)
        changed = self._changed_paths()
        outside = tuple(path for path in changed if not self._allowed(path, task.allowed_paths))
        checks = (
            self._check(("python3", "-m", "pytest", "-q")),
            self._check(("python3", "-m", "builder.main", "doctor")),
            self._check(("git", "diff", "--check")),
        )
        push_detected = origin_before is not None and self._origin_head() != origin_before
        blockers = []
        if branch != task.branch:
            blockers.append("BRANCH_CHANGED")
        if head != task.start_head:
            blockers.append("HEAD_CHANGED")
        if staged:
            blockers.append("UNEXPECTED_STAGING")
        if outside:
            blockers.append("OUT_OF_SCOPE_CHANGES")
        if push_detected:
            blockers.append("PUSH_DETECTED")
        if not all(check.passed for check in checks):
            blockers.append("QUALITY_CHECK_FAILED")
        return GitGateResult(
            status=GateStatus.BLOCKED if blockers else GateStatus.READY_FOR_HUMAN_REVIEW,
            branch_unchanged=branch == task.branch,
            head_unchanged=head == task.start_head,
            staged_paths=staged,
            changed_paths=changed,
            out_of_scope_paths=outside,
            push_detected=push_detected,
            diff_hash=self.diff_hash(),
            checks=checks,
            blockers=tuple(blockers),
        )

    def status(self, task_id: str) -> Dict[str, object]:
        task = self.store.load_task(task_id)
        receipt = self.store.load_receipt(task_id)
        return {
            "task": task.to_dict(),
            "receipt": receipt.to_dict() if receipt else None,
            "lock": self.store.read_lock().to_dict() if self.store.read_lock() else None,
        }

    def commit(self, task_id: str, approval: CommitApproval, message: str) -> str:
        task = self.store.load_task(task_id)
        receipt = self.store.load_receipt(task_id)
        if not task.commit_permitted or receipt is None or not receipt.git_gate.passed:
            raise TaskRunError("COMMIT_NOT_READY", "Task is not eligible for commit")
        current = self.git_gate(task)
        if (
            approval.task_id != task_id
            or approval.branch != task.branch
            or approval.head != task.start_head
            or approval.diff_hash != current.diff_hash
            or not current.passed
        ):
            raise TaskRunError("COMMIT_APPROVAL_INVALID", "Bound approval no longer matches")
        if not message.strip():
            raise TaskRunError("INVALID_COMMIT_MESSAGE", "Commit message is required")
        self._git("add", "--", *current.changed_paths)
        result = self._git("commit", "-m", message)
        if result.exit_code != 0:
            raise TaskRunError("COMMIT_FAILED", result.stderr)
        return self._git("rev-parse", "HEAD").stdout.strip()

    def push(self, task_id: str, approval: PushApproval) -> str:
        task = self.store.load_task(task_id)
        if not task.push_permitted:
            raise TaskRunError("PUSH_NOT_PERMITTED", "Task does not permit push")
        head = self._git("rev-parse", "HEAD").stdout.strip()
        branch = self._git("branch", "--show-current").stdout.strip()
        if (
            approval.task_id != task_id
            or approval.branch != branch
            or approval.commit != head
        ):
            raise TaskRunError("PUSH_APPROVAL_INVALID", "Bound approval no longer matches")
        result = self._git("push", approval.remote, "{}:{}".format(branch, approval.remote_branch))
        if result.exit_code != 0:
            raise TaskRunError("PUSH_FAILED", result.stderr)
        return head

    def diff_hash(self) -> str:
        digest = hashlib.sha256()
        digest.update(self._git("diff", "--binary", "HEAD").stdout.encode("utf-8"))
        for path in self._lines(self._git("ls-files", "--others", "--exclude-standard").stdout):
            digest.update(path.encode("utf-8"))
            digest.update(b"\0")
            digest.update((self.repository / path).read_bytes())
        return digest.hexdigest()

    def _check(self, command: Tuple[str, ...]) -> CheckResult:
        result = self.runner.run(command, cwd=self.repository)
        summary = _redact(result.output or "exit {}".format(result.exit_code))
        return CheckResult(command, result.exit_code == 0, summary)

    def _git(self, *arguments: str) -> CommandResult:
        return self.runner.run(("git",) + arguments, cwd=self.repository)

    def _codex_command(self) -> Tuple[str, ...]:
        program = self.codex_program or shutil.which("codex")
        if not program:
            raise TaskRunError("CODEX_NOT_FOUND", "Codex CLI is not available")
        return (program, "--ask-for-approval", "never", "exec", "--cd", str(self.repository), "--sandbox", "workspace-write", "-")

    def _prompt(self, task: ImmutableTask) -> str:
        return (
            "Implement this immutable task only.\n\nGoal:\n{}\n\nAllowed paths:\n{}\n\n"
            "Non-goals:\n{}\n\nDo not stage files. Do not commit. Do not push."
        ).format(task.goal, "\n".join(task.allowed_paths), "\n".join(task.non_goals))

    def _origin_head(self) -> Optional[str]:
        result = self._git("rev-parse", "--verify", "origin/{}".format(self._git("branch", "--show-current").stdout.strip()))
        return result.stdout.strip() if result.exit_code == 0 else None

    def _status_entries(self) -> Tuple[str, ...]:
        return self._lines(self._git("status", "--porcelain=v1", "--untracked-files=all").stdout)

    def _changed_paths(self) -> Tuple[str, ...]:
        paths = []
        for entry in self._status_entries():
            path = entry[3:]
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            paths.append(path)
        return tuple(sorted(set(paths)))

    @staticmethod
    def _allowed(path: str, allowed: Sequence[str]) -> bool:
        return any(
            item == "."
            or path == item
            or path.startswith(item.rstrip("/") + "/")
            for item in allowed
        )

    @staticmethod
    def _lines(value: str) -> Tuple[str, ...]:
        return tuple(line for line in value.splitlines() if line)


def _redact(value: str) -> str:
    import re
    return re.sub(
        r"(?i)(authorization|token|api[_-]?key|password|secret)(\\s*[:=]\\s*)\\S+",
        r"\1\2[REDACTED]",
        value,
    )
