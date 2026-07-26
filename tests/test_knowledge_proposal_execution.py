import os
from pathlib import Path

import pytest

from builder.planner import Planner
from execution.engine import ExecutionEngine, ExecutionError
from execution.models import DocumentArtifact
from execution.repository import confirmed_repository_root


def artifact(path, content="content"):
    return DocumentArtifact(
        action="document.create",
        path=path,
        content=content,
    )


def plan_for(*artifacts):
    return Planner().create_plan(
        "Create knowledge proposal",
        document_artifacts=artifacts,
    )


def repository(tmp_path):
    (tmp_path / ".git").mkdir()
    return tmp_path


def test_document_artifact_rejects_unsupported_action():
    with pytest.raises(ValueError, match="document.create"):
        DocumentArtifact(
            action="document.update",
            path="knowledge/project/document.md",
            content="content",
        )


def test_planner_keeps_legacy_plan_without_artifacts():
    assert Planner().create_plan("Legacy goal") == [
        {
            "step": 1,
            "agent": "document",
            "action": "create",
            "target": "Legacy goal",
        },
        {
            "step": 2,
            "agent": "git",
            "action": "sync",
            "message": "Create Legacy goal",
        },
    ]


def test_prepare_with_artifacts_does_not_write(tmp_path):
    cwd_before = set(Path.cwd().rglob("proposal.md"))
    plan = plan_for(artifact("knowledge/project/proposal.md"))

    result = ExecutionEngine().prepare(plan)

    assert not (tmp_path / "knowledge/project/proposal.md").exists()
    assert set(Path.cwd().rglob("proposal.md")) == cwd_before
    assert all(step["execution_status"] == "pending" for step in result)


def test_execute_creates_multiple_documents_and_leaves_git_pending(tmp_path):
    artifacts = (
        artifact("knowledge/project/proposal.md", "product"),
        artifact("knowledge/roadmaps/proposal.md", "roadmap"),
    )

    result = ExecutionEngine().execute(
        plan_for(*artifacts),
        _test_repository_root=repository(tmp_path),
    )

    assert (tmp_path / artifacts[0].path).read_text(encoding="utf-8") == "product"
    assert (tmp_path / artifacts[1].path).read_text(encoding="utf-8") == "roadmap"
    assert [step["execution_status"] for step in result] == [
        "completed",
        "completed",
        "pending",
    ]


@pytest.mark.parametrize(
    "target, expected",
    [
        ("/tmp/outside.md", "Absolute"),
        ("C:\\outside.md", "Absolute"),
        ("knowledge/../outside.md", "traversal"),
        ("docs/outside.md", "knowledge/"),
    ],
)
def test_execute_rejects_unsafe_targets_without_writes(tmp_path, target, expected):
    with pytest.raises(ValueError, match=expected):
        ExecutionEngine().execute(
            plan_for(artifact(target)),
            _test_repository_root=repository(tmp_path),
        )

    assert not (tmp_path / "knowledge").exists()


def test_execute_rejects_existing_file_without_overwrite(tmp_path):
    existing = tmp_path / "knowledge/project/existing.md"
    repository(tmp_path)
    existing.parent.mkdir(parents=True)
    existing.write_text("original", encoding="utf-8")

    with pytest.raises(ValueError, match="already exists"):
        ExecutionEngine().execute(
            plan_for(artifact("knowledge/project/existing.md", "replacement")),
            _test_repository_root=tmp_path,
        )

    assert existing.read_text(encoding="utf-8") == "original"


def test_invalid_group_is_fully_validated_before_first_write(tmp_path):
    plan = plan_for(
        artifact("knowledge/project/valid.md", "valid"),
        artifact("../invalid.md", "invalid"),
    )

    with pytest.raises(ValueError, match="traversal"):
        ExecutionEngine().execute(
            plan,
            _test_repository_root=repository(tmp_path),
        )

    assert not (tmp_path / "knowledge/project/valid.md").exists()


def test_file_and_child_target_conflict_is_rejected_before_writing(tmp_path):
    plan = plan_for(
        artifact("knowledge/project", "file"),
        artifact("knowledge/project/child.md", "child"),
    )

    with pytest.raises(ValueError, match="parent target"):
        ExecutionEngine().execute(
            plan,
            _test_repository_root=repository(tmp_path),
        )

    assert not (tmp_path / "knowledge").exists()


def test_symlink_escape_is_rejected(tmp_path):
    outside = tmp_path / "outside"
    repository(tmp_path)
    outside.mkdir()
    knowledge = tmp_path / "knowledge"
    knowledge.mkdir()
    (knowledge / "linked").symlink_to(outside, target_is_directory=True)

    with pytest.raises(ValueError, match="Symlink"):
        ExecutionEngine().execute(
            plan_for(artifact("knowledge/linked/escape.md")),
            _test_repository_root=tmp_path,
        )

    assert not (outside / "escape.md").exists()


def test_write_failure_rolls_back_created_group(tmp_path, monkeypatch):
    plan = plan_for(
        artifact("knowledge/project/first.md", "first"),
        artifact("knowledge/project/second.md", "second"),
    )
    original_fdopen = os.fdopen
    calls = 0

    def failing_fdopen(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("simulated write failure")
        return original_fdopen(*args, **kwargs)

    monkeypatch.setattr(os, "fdopen", failing_fdopen)

    with pytest.raises(ExecutionError, match="could not be written"):
        ExecutionEngine().execute(
            plan,
            _test_repository_root=repository(tmp_path),
        )

    assert not (tmp_path / "knowledge/project/first.md").exists()
    assert not (tmp_path / "knowledge/project/second.md").exists()


def test_utf8_write_failure_rolls_back_created_group(tmp_path):
    plan = plan_for(
        artifact("knowledge/project/first.md", "first"),
        artifact("knowledge/project/invalid.md", "\ud800"),
    )

    with pytest.raises(ExecutionError, match="could not be written"):
        ExecutionEngine().execute(
            plan,
            _test_repository_root=repository(tmp_path),
        )

    assert not (tmp_path / "knowledge/project/first.md").exists()
    assert not (tmp_path / "knowledge/project/invalid.md").exists()


def test_repository_root_requires_git_marker(tmp_path):
    with pytest.raises(ValueError, match=".git"):
        confirmed_repository_root(tmp_path)


def test_repository_root_accepts_git_directory(tmp_path):
    assert confirmed_repository_root(repository(tmp_path)) == tmp_path


def test_repository_root_accepts_worktree_git_file(tmp_path):
    git_directory = tmp_path / "worktrees/example"
    git_directory.mkdir(parents=True)
    (tmp_path / ".git").write_text(
        "gitdir: worktrees/example\n",
        encoding="utf-8",
    )

    assert confirmed_repository_root(tmp_path) == tmp_path


def test_repository_root_rejects_symlink_git_marker(tmp_path):
    git_directory = tmp_path / "actual-git"
    git_directory.mkdir()
    (tmp_path / ".git").symlink_to(git_directory, target_is_directory=True)

    with pytest.raises(ValueError, match="must not be a symlink"):
        confirmed_repository_root(tmp_path)


def test_execute_rejects_knowledge_itself(tmp_path):
    with pytest.raises(ValueError, match="below knowledge"):
        ExecutionEngine().execute(
            plan_for(artifact("knowledge")),
            _test_repository_root=repository(tmp_path),
        )


def test_symlink_target_is_rejected(tmp_path):
    repository(tmp_path)
    target = tmp_path / "knowledge/project/target.md"
    target.parent.mkdir(parents=True)
    outside = tmp_path / "outside.md"
    outside.write_text("outside", encoding="utf-8")
    target.symlink_to(outside)

    with pytest.raises(ValueError, match="already exists"):
        ExecutionEngine().execute(
            plan_for(artifact("knowledge/project/target.md")),
            _test_repository_root=tmp_path,
        )

    assert outside.read_text(encoding="utf-8") == "outside"


def test_directory_symlink_swap_fails_target_verification(
    tmp_path,
    monkeypatch,
):
    repository(tmp_path)
    project = tmp_path / "knowledge/project"
    project.mkdir(parents=True)
    outside = tmp_path / "outside"
    outside.mkdir()
    original_open = os.open
    swapped = False

    def swapping_open(path, flags, *args, **kwargs):
        nonlocal swapped
        if (
            path == "target.md"
            and kwargs.get("dir_fd") is not None
            and not swapped
        ):
            swapped = True
            project.rename(tmp_path / "detached-project")
            project.symlink_to(outside, target_is_directory=True)
        return original_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(os, "open", swapping_open)

    with pytest.raises(ExecutionError) as captured:
        ExecutionEngine().execute(
            plan_for(artifact("knowledge/project/target.md")),
            _test_repository_root=tmp_path,
        )

    assert not (outside / "target.md").exists()
    assert (tmp_path / "detached-project/target.md").exists()
    assert captured.value.error_type == "TargetVerificationError"
    assert captured.value.completed_steps == []
    assert captured.value.rolled_back_steps == []
    assert captured.value.remaining_resources == [
        "knowledge/project/target.md"
    ]


def test_failure_after_mkdir_reports_unidentified_created_directory(
    tmp_path,
    monkeypatch,
):
    repository(tmp_path)
    existing = tmp_path / "existing.txt"
    existing.write_text("existing", encoding="utf-8")
    original_open = os.open

    def fail_open_after_mkdir(path, flags, *args, **kwargs):
        if (
            path == "knowledge"
            and kwargs.get("dir_fd") is not None
            and (tmp_path / "knowledge").exists()
        ):
            raise OSError(24, "simulated descriptor exhaustion")
        return original_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(os, "open", fail_open_after_mkdir)

    with pytest.raises(ExecutionError) as captured:
        ExecutionEngine().execute(
            plan_for(artifact("knowledge/project/target.md")),
            _test_repository_root=tmp_path,
        )

    error = captured.value
    assert error.error_type == "OSError"
    assert error.completed_steps == []
    assert error.rolled_back_steps == []
    assert error.remaining_resources == ["knowledge"]
    assert "identity could not be captured" in error.rollback_errors[0]
    assert (tmp_path / "knowledge").is_dir()
    assert existing.read_text(encoding="utf-8") == "existing"


def test_rollback_errors_report_remaining_resources(tmp_path, monkeypatch):
    repository(tmp_path)
    plan = plan_for(
        artifact("knowledge/project/first.md", "first"),
        artifact("knowledge/project/invalid.md", "\ud800"),
    )
    original_unlink = os.unlink

    def failing_unlink(path, *args, **kwargs):
        if path == "first.md":
            raise PermissionError("rollback denied")
        return original_unlink(path, *args, **kwargs)

    monkeypatch.setattr(os, "unlink", failing_unlink)

    with pytest.raises(ExecutionError) as captured:
        ExecutionEngine().execute(plan, _test_repository_root=tmp_path)

    error = captured.value
    assert "rollback incomplete" in str(error)
    assert "knowledge/project/first.md" in error.remaining_resources
    assert error.rollback_errors


def test_rollback_preserves_preexisting_resources(tmp_path):
    repository(tmp_path)
    existing = tmp_path / "knowledge/project/existing.md"
    existing.parent.mkdir(parents=True)
    existing.write_text("existing", encoding="utf-8")
    plan = plan_for(
        artifact("knowledge/project/new.md", "new"),
        artifact("knowledge/project/invalid.md", "\ud800"),
    )

    with pytest.raises(ExecutionError):
        ExecutionEngine().execute(plan, _test_repository_root=tmp_path)

    assert existing.read_text(encoding="utf-8") == "existing"
