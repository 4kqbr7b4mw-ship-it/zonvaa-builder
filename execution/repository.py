import subprocess
from pathlib import Path
from typing import Optional


def confirmed_repository_root(
    _test_repository_root: Optional[Path] = None,
) -> Path:
    """Return a verified Git repository root.

    The private argument exists only for isolated filesystem tests. Production
    callers always use Git's own repository discovery.
    """
    if _test_repository_root is not None:
        root = _test_repository_root.resolve()
    else:
        try:
            completed = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                check=True,
                capture_output=True,
                text=True,
            )
        except (OSError, subprocess.CalledProcessError) as exc:
            raise ValueError("Current directory is not inside a Git repository") from exc
        root = Path(completed.stdout.strip()).resolve()

    _validate_git_marker(root)
    return root


def _validate_git_marker(root: Path) -> None:
    if not root.is_dir():
        raise ValueError("Repository root must be an existing directory")

    marker = root / ".git"
    if marker.is_symlink():
        raise ValueError("Repository .git marker must not be a symlink")
    if marker.is_dir():
        return
    if marker.is_file():
        try:
            marker_value = marker.read_text(encoding="utf-8").strip()
        except (OSError, UnicodeError) as exc:
            raise ValueError("Git worktree marker cannot be read") from exc
        prefix = "gitdir:"
        if not marker_value.startswith(prefix):
            raise ValueError("Git worktree marker is invalid")
        git_dir_value = marker_value[len(prefix) :].strip()
        if not git_dir_value:
            raise ValueError("Git worktree marker is invalid")
        git_dir = Path(git_dir_value)
        if not git_dir.is_absolute():
            git_dir = marker.parent / git_dir
        if git_dir.resolve().is_dir():
            return
    raise ValueError("Repository root has no valid .git marker")
