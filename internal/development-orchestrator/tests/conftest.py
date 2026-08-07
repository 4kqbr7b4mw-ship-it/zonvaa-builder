from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


TOOL_ROOT = Path(__file__).resolve().parents[1]
if str(TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOL_ROOT))


def git(repository: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=str(repository),
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


@pytest.fixture
def isolated_repository(tmp_path: Path) -> tuple[Path, Path]:
    repository = tmp_path / "repo"
    repository.mkdir()
    git(repository, "init", "-b", "main")
    git(repository, "config", "user.name", "Synthetic Test")
    git(repository, "config", "user.email", "synthetic@example.invalid")
    (repository / "README.md").write_text("# Synthetic repository\n", encoding="utf-8")
    (repository / "docs").mkdir()
    (repository / "docs" / "research.md").write_text(
        "Evidence for a synthetic research case.\n", encoding="utf-8"
    )
    tool_root = repository / "internal" / "development-orchestrator"
    tool_root.mkdir(parents=True)
    (tool_root / "runs").mkdir()
    git(repository, "add", ".")
    git(repository, "commit", "-m", "base")
    return repository, tool_root
