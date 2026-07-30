import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

from builder_task import (
    ApprovalAction,
    BuilderTaskService,
    BuilderTaskStore,
    CommitApproval,
    ImmutableTask,
    PushApproval,
    RepositoryLock,
    TaskRunError,
    VetoClassification,
)
from builder_task.service import CommandResult, LocalCommandRunner


NOW = datetime(2026, 7, 30, 12, 0, tzinfo=timezone.utc)


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=str(repo), text=True, capture_output=True, check=True
    )
    return result.stdout.strip()


def repository(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.name", "Test")
    git(repo, "config", "user.email", "test@example.invalid")
    (repo / "allowed").mkdir()
    (repo / "allowed" / "base.txt").write_text("base\n", encoding="utf-8")
    (repo / ".gitignore").write_text("knowledge/runtime/\n", encoding="utf-8")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "base")
    return repo


class FakeRunner(LocalCommandRunner):
    def __init__(self, write_result: bool = True, exit_code: int = 0) -> None:
        self.starts = 0
        self.write_result = write_result
        self.exit_code = exit_code

    def run(self, arguments, cwd, **kwargs):
        if arguments[:3] == ("python3", "-m", "pytest"):
            return CommandResult(0, "tests passed", "")
        if arguments[:3] == ("python3", "-m", "builder.main"):
            return CommandResult(0, "doctor ok", "")
        return super().run(arguments, cwd, **kwargs)

    def run_tracked(self, arguments, cwd, process_started, **kwargs):
        self.starts += 1
        process_started(4242)
        if self.write_result:
            (cwd / "allowed" / "result.txt").write_text("done\n", encoding="utf-8")
        return CommandResult(self.exit_code, "stdout token=secret", "stderr")


def task(repo: Path, **changes) -> ImmutableTask:
    values = {
        "task_id": "task-example",
        "repository": str(repo),
        "branch": "main",
        "start_head": git(repo, "rev-parse", "HEAD"),
        "goal": "Change an allowed file.",
        "allowed_paths": ("allowed",),
        "non_goals": ("No commit", "No push"),
        "veto_classification": VetoClassification.NO_VETO,
        "commit_permitted": False,
        "push_permitted": False,
    }
    values.update(changes)
    return ImmutableTask(**values)


def test_unknown_veto_blocks_without_start(tmp_path):
    repo = repository(tmp_path)
    runner = FakeRunner()
    service = BuilderTaskService(repo, runner=runner, codex_program="/fake/codex")
    item = task(repo, veto_classification=VetoClassification.HUMAN_CLASSIFICATION_REQUIRED)
    with pytest.raises(TaskRunError, match="VETO_CLASSIFICATION_REQUIRED"):
        service.run(item)
    assert runner.starts == 0


def test_repository_lock_blocks_second_start_and_is_not_removed(tmp_path):
    repo = repository(tmp_path)
    store = BuilderTaskStore(repo)
    lock = RepositoryLock("task-other", 999999, NOW, str(repo))
    store.acquire_lock(lock)
    service = BuilderTaskService(repo, runner=FakeRunner(), codex_program="/fake/codex")
    with pytest.raises(TaskRunError, match="REPOSITORY_LOCKED"):
        service.run(task(repo))
    assert store.read_lock() == lock


def test_run_starts_once_writes_one_receipt_and_never_commits_or_pushes(tmp_path):
    repo = repository(tmp_path)
    runner = FakeRunner()
    service = BuilderTaskService(repo, runner=runner, codex_program="/fake/codex")
    before = git(repo, "rev-parse", "HEAD")
    receipt = service.run(task(repo))
    assert runner.starts == 1
    assert receipt.result.value == "COMPLETED"
    assert receipt.commit_status == "NOT_ATTEMPTED"
    assert receipt.push_status == "NOT_ATTEMPTED"
    assert git(repo, "rev-parse", "HEAD") == before
    assert BuilderTaskStore(repo).load_receipt("task-example") == receipt
    with pytest.raises(TaskRunError, match="TASK_ALREADY_RUN"):
        service.run(task(repo))
    assert runner.starts == 1


def test_unknown_exit_code_remains_unknown_in_receipt(tmp_path):
    repo = repository(tmp_path)
    class MissingRunner(FakeRunner):
        run_tracked = LocalCommandRunner.run_tracked

    receipt = BuilderTaskService(
        repo, runner=MissingRunner(), codex_program="/definitely/missing/codex"
    ).run(task(repo))
    assert receipt.process_started is False
    assert receipt.exit_code is None
    assert receipt.to_dict()["exit_code"] == "unknown"


def test_git_gate_checks_staging_scope_branch_and_head(tmp_path):
    repo = repository(tmp_path)
    service = BuilderTaskService(repo, runner=FakeRunner(), codex_program="/fake/codex")
    item = task(repo)
    (repo / "outside.txt").write_text("bad\n", encoding="utf-8")
    git(repo, "add", "outside.txt")
    gate = service.git_gate(item)
    assert "outside.txt" in gate.staged_paths
    assert "outside.txt" in gate.out_of_scope_paths
    assert "UNEXPECTED_STAGING" in gate.blockers
    assert "OUT_OF_SCOPE_CHANGES" in gate.blockers


def test_diff_change_invalidates_commit_approval(tmp_path):
    repo = repository(tmp_path)
    runner = FakeRunner()
    service = BuilderTaskService(repo, runner=runner, codex_program="/fake/codex")
    item = task(repo, commit_permitted=True)
    receipt = service.run(item)
    approval = CommitApproval(
        item.task_id, item.branch, item.start_head, receipt.git_gate.diff_hash,
        ApprovalAction.COMMIT, NOW, "Human",
    )
    (repo / "allowed" / "result.txt").write_text("changed\n", encoding="utf-8")
    with pytest.raises(TaskRunError, match="COMMIT_APPROVAL_INVALID"):
        service.commit(item.task_id, approval, "Approved")


def test_push_requires_separate_permission_and_approval(tmp_path):
    repo = repository(tmp_path)
    service = BuilderTaskService(repo, runner=FakeRunner(), codex_program="/fake/codex")
    item = task(repo)
    service.store.save_task(item)
    approval = PushApproval(
        item.task_id, "main", item.start_head, "origin", "main",
        ApprovalAction.PUSH, NOW, "Human",
    )
    with pytest.raises(TaskRunError, match="PUSH_NOT_PERMITTED"):
        service.push(item.task_id, approval)


def test_task_and_approval_models_are_frozen(tmp_path):
    repo = repository(tmp_path)
    item = task(repo)
    with pytest.raises(Exception):
        item.goal = "mutated"


def test_task_cli_help_exposes_four_commands():
    import os
    env = dict(os.environ)
    env["PATH"] = "{}:{}".format(Path(sys.executable).parent, env["PATH"])
    result = subprocess.run(
        [sys.executable, "-m", "builder.main", "task", "--help"],
        cwd=str(Path(__file__).parents[1]), text=True, capture_output=True, env=env,
    )
    assert result.returncode == 0
    for command in ("run", "status", "commit", "push"):
        assert command in result.stdout


def test_legacy_execution_owners_are_disabled_before_any_process_start():
    # Import the historical architecture package first to preserve its legacy
    # import order; these objects are deliberately not otherwise initialized.
    import architecture_integrator  # noqa: F401
    from codex_execution.orchestration import (
        CodexExecutionOrchestrator,
        CodexExecutionRequest,
    )
    from codex_execution.runner import SubprocessCommandRunner
    from codex_execution.service import CodexExecutionService

    bridge = object.__new__(CodexExecutionService)
    bridge.runner = SubprocessCommandRunner()
    with pytest.raises(RuntimeError, match="LEGACY_EXECUTION_DISABLED"):
        bridge.execute("workflow-0123456789abcdef")

    orchestrator = object.__new__(CodexExecutionOrchestrator)
    orchestrator.runner = SubprocessCommandRunner()
    with pytest.raises(RuntimeError, match="LEGACY_ORCHESTRATOR_DISABLED"):
        orchestrator.run(CodexExecutionRequest("workflow-0123456789abcdef"))
