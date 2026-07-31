import subprocess
from pathlib import Path

import pytest

from builder_task.develop import DevelopmentService
from builder_task.service import (
    BuilderTaskService,
    CommandResult,
    LocalCommandRunner,
)


def git(repo: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=str(repo),
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.strip()


def repository(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.name", "Test")
    git(repo, "config", "user.email", "test@example.invalid")
    (repo / ".gitignore").write_text("knowledge/runtime/\n", encoding="utf-8")
    (repo / "source.txt").write_text("base\n", encoding="utf-8")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "base")
    return repo


class DevelopRunner(LocalCommandRunner):
    def __init__(
        self,
        failing_check=(),
        codex_answer="done",
        change_files=True,
    ) -> None:
        self.failing_check = tuple(failing_check)
        self.codex_answer = codex_answer
        self.change_files = change_files
        self.starts = 0
        self.pushes = 0

    def run(self, arguments, cwd, **kwargs):
        command = tuple(arguments)
        if command[:3] == ("python3", "-m", "pytest"):
            return self._check(command)
        if command[:3] == ("python3", "-m", "builder.main"):
            return self._check(command)
        if command == ("git", "diff", "--check") and self.failing_check == command:
            return CommandResult(1, "", "diff failed")
        if command[:2] == ("git", "push"):
            self.pushes += 1
            return CommandResult(0, "pushed", "")
        return super().run(arguments, cwd, **kwargs)

    def run_tracked(self, arguments, cwd, process_started, **kwargs):
        self.starts += 1
        process_started(1234)
        if self.change_files:
            (cwd / "source.txt").write_text("changed\n", encoding="utf-8")
        return CommandResult(0, self.codex_answer, "")

    def _check(self, command):
        if self.failing_check and command[: len(self.failing_check)] == self.failing_check:
            return CommandResult(1, "", "check failed")
        return CommandResult(0, "ok", "")


def service(repo: Path, runner: DevelopRunner) -> DevelopmentService:
    return DevelopmentService(
        repo,
        core_factory=lambda path: BuilderTaskService(
            path, runner=runner, codex_program="/fake/codex"
        ),
    )


def test_successful_one_command_run_uses_single_core_execution(tmp_path):
    repo = repository(tmp_path)
    runner = DevelopRunner()
    report = service(repo, runner).run("Improve the documentation")
    assert runner.starts == 1
    assert report.changed_files == ("source.txt",)
    assert report.tests == "Erfolgreich"
    assert report.doctor == "Erfolgreich"
    assert report.diff_status == "Erfolgreich"
    assert report.blockers == ()
    assert report.commit_ready is True
    assert git(repo, "rev-parse", "HEAD") == git(repo, "rev-list", "--max-parents=0", "HEAD")


def test_read_only_analysis_includes_complete_codex_answer(tmp_path):
    repo = repository(tmp_path)
    answer = "Analyseergebnis:\n- Befund A\n- Befund B\n\nKeine Änderungen vorgenommen."
    report = service(
        repo,
        DevelopRunner(codex_answer=answer, change_files=False),
    ).run("Analyze the source without changes")

    assert report.codex_answer == answer
    assert report.to_dict()["Codex-Antwort"] == answer


def test_zero_changed_files_require_no_commit(tmp_path):
    repo = repository(tmp_path)
    report = service(repo, DevelopRunner(change_files=False)).run(
        "Analyze the source without changes"
    )

    assert report.changed_files == ()
    assert report.commit_ready is False
    assert report.to_dict()["Commit bereit"] == "Kein Commit erforderlich"


def test_veto_path_stops_before_execution(tmp_path):
    repo = repository(tmp_path)
    runner = DevelopRunner()
    report = service(repo, runner).run("Change governance authorization")
    assert runner.starts == 0
    assert report.blockers == ("PLAN_APPROVAL_REQUIRED",)
    assert report.commit_ready is False


def test_guard_blocker_is_reported_without_internal_state(tmp_path):
    repo = repository(tmp_path)
    (repo / "unrelated.txt").write_text("dirty\n", encoding="utf-8")
    runner = DevelopRunner()
    report = service(repo, runner).run("Update source")
    assert runner.starts == 0
    assert report.blockers == ("GUARD_BLOCKED",)


@pytest.mark.parametrize(
    ("failure", "field"),
    [
        (("python3", "-m", "pytest"), "tests"),
        (("python3", "-m", "builder.main"), "doctor"),
        (("git", "diff", "--check"), "diff_status"),
    ],
)
def test_quality_failure_blocks_commit_readiness(tmp_path, failure, field):
    repo = repository(tmp_path)
    report = service(repo, DevelopRunner(failure)).run("Update source")
    assert getattr(report, field) == "Fehlgeschlagen"
    assert "QUALITY_CHECK_FAILED" in report.blockers
    assert report.commit_ready is False


def test_develop_commit_uses_bound_approval_after_successful_run(tmp_path):
    repo = repository(tmp_path)
    runner = DevelopRunner()
    facade = service(repo, runner)
    assert facade.run("Update source").commit_ready is True
    commit = facade.commit("Update source")
    assert commit == git(repo, "rev-parse", "HEAD")
    assert git(repo, "status", "--short") == ""


def test_develop_push_requires_prior_matching_task_and_separate_call(tmp_path):
    repo = repository(tmp_path)
    runner = DevelopRunner()
    facade = service(repo, runner)
    assert facade.run("Update source").commit_ready is True
    commit = facade.commit("Update source")
    pushed = facade.push(remote="origin", remote_branch="main")
    assert pushed == commit
    assert runner.pushes == 1
