from __future__ import annotations

from pathlib import Path

import pytest

from development_orchestrator.boundary import (
    BoundaryGuard,
    BoundaryViolation,
    WorkspaceWriter,
)


def test_legitimate_relative_write_is_allowed(isolated_repository) -> None:
    repository, tool_root = isolated_repository
    guard = BoundaryGuard(repository, tool_root)
    assert guard.resolve_write_path("runs/example/result.json") == (
        tool_root / "runs/example/result.json"
    ).resolve()


@pytest.mark.parametrize("target", ["../outside.txt", "../../escape.txt"])
def test_path_traversal_is_blocked(isolated_repository, target: str) -> None:
    repository, tool_root = isolated_repository
    with pytest.raises(BoundaryViolation, match="escapes"):
        BoundaryGuard(repository, tool_root).resolve_write_path(target)


def test_absolute_external_path_is_blocked(isolated_repository, tmp_path: Path) -> None:
    repository, tool_root = isolated_repository
    with pytest.raises(BoundaryViolation, match="escapes"):
        BoundaryGuard(repository, tool_root).resolve_write_path(tmp_path / "outside.txt")


def test_symlink_escape_is_blocked(isolated_repository, tmp_path: Path) -> None:
    repository, tool_root = isolated_repository
    outside = tmp_path / "outside"
    outside.mkdir()
    (tool_root / "linked").symlink_to(outside, target_is_directory=True)
    with pytest.raises(BoundaryViolation, match="escapes|symlink"):
        BoundaryGuard(repository, tool_root).resolve_write_path("linked/result.txt")


def test_writer_writes_only_after_validation(isolated_repository) -> None:
    repository, tool_root = isolated_repository
    writer = WorkspaceWriter(BoundaryGuard(repository, tool_root))
    path = writer.write_text("runs/example/research.md", "synthetic\n")
    assert path.read_text(encoding="utf-8") == "synthetic\n"
    assert not list(path.parent.glob(".orchestrator-*.tmp"))


def test_git_boundary_accepts_only_internal_changes(isolated_repository) -> None:
    repository, tool_root = isolated_repository
    WorkspaceWriter(BoundaryGuard(repository, tool_root)).write_text(
        "runs/example/result.json", "{}\n"
    )
    paths = BoundaryGuard(repository, tool_root).assert_repository_changes_within_boundary()
    assert paths == ["internal/development-orchestrator/runs/example/result.json"]


def test_git_boundary_fails_closed_on_foreign_change(isolated_repository) -> None:
    repository, tool_root = isolated_repository
    (repository / "outside.txt").write_text("violation\n", encoding="utf-8")
    with pytest.raises(BoundaryViolation, match="out-of-boundary"):
        BoundaryGuard(repository, tool_root).assert_repository_changes_within_boundary()


def test_read_path_is_repository_bound(isolated_repository, tmp_path: Path) -> None:
    repository, tool_root = isolated_repository
    guard = BoundaryGuard(repository, tool_root)
    assert guard.resolve_read_path("README.md") == (repository / "README.md").resolve()
    outside = tmp_path / "outside.md"
    outside.write_text("outside\n", encoding="utf-8")
    with pytest.raises(BoundaryViolation):
        guard.resolve_read_path(outside)
