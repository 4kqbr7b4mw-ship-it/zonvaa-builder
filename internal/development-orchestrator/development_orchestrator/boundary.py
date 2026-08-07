"""Fail-closed read and write boundaries for the internal workspace."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Iterable, List


class BoundaryViolation(RuntimeError):
    pass


class BoundaryGuard:
    def __init__(self, repository_root: Path, allowed_root: Path) -> None:
        self.repository_root = repository_root.resolve(strict=True)
        self.allowed_root = allowed_root.resolve(strict=True)
        if not self._within(self.allowed_root, self.repository_root):
            raise BoundaryViolation("allowed root must be inside repository")

    @staticmethod
    def _within(candidate: Path, root: Path) -> bool:
        return candidate == root or root in candidate.parents

    def resolve_write_path(self, target: str | Path) -> Path:
        raw = Path(target)
        candidate = raw if raw.is_absolute() else self.allowed_root / raw
        resolved = candidate.resolve(strict=False)
        if not self._within(resolved, self.allowed_root):
            raise BoundaryViolation(
                "write target escapes internal/development-orchestrator"
            )
        self._reject_symlink_components(candidate)
        return resolved

    def resolve_read_path(self, target: str | Path) -> Path:
        raw = Path(target)
        candidate = raw if raw.is_absolute() else self.repository_root / raw
        resolved = candidate.resolve(strict=True)
        if not self._within(resolved, self.repository_root):
            raise BoundaryViolation("read target escapes repository")
        if not resolved.is_file():
            raise BoundaryViolation("read target must be a file")
        return resolved

    def _reject_symlink_components(self, candidate: Path) -> None:
        current = Path(candidate.anchor) if candidate.is_absolute() else Path()
        for part in candidate.parts[1:] if candidate.is_absolute() else candidate.parts:
            current = current / part
            if current.exists() and current.is_symlink():
                raise BoundaryViolation("symlink write targets are forbidden")

    def assert_repository_changes_within_boundary(self) -> List[str]:
        completed = subprocess.run(
            ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
            cwd=str(self.repository_root),
            check=False,
            capture_output=True,
        )
        if completed.returncode != 0:
            raise BoundaryViolation("git status could not verify the write boundary")
        paths = self._parse_porcelain_z(completed.stdout)
        violations = []
        for value in paths:
            resolved = (self.repository_root / value).resolve(strict=False)
            if not self._within(resolved, self.allowed_root):
                violations.append(value)
        if violations:
            raise BoundaryViolation(
                "repository contains out-of-boundary changes: {}".format(
                    ", ".join(sorted(violations))
                )
            )
        return paths

    @staticmethod
    def _parse_porcelain_z(payload: bytes) -> List[str]:
        entries = payload.decode("utf-8", errors="surrogateescape").split("\0")
        paths: List[str] = []
        index = 0
        while index < len(entries) and entries[index]:
            entry = entries[index]
            if len(entry) < 4:
                raise BoundaryViolation("unexpected git status entry")
            status = entry[:2]
            paths.append(entry[3:])
            if "R" in status or "C" in status:
                index += 1
                if index >= len(entries) or not entries[index]:
                    raise BoundaryViolation("incomplete git rename entry")
                paths.append(entries[index])
            index += 1
        return paths


class WorkspaceWriter:
    def __init__(self, guard: BoundaryGuard) -> None:
        self.guard = guard

    def write_text(self, target: str | Path, content: str) -> Path:
        path = self.guard.resolve_write_path(target)
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary = tempfile.mkstemp(
            dir=str(path.parent), prefix=".orchestrator-", suffix=".tmp"
        )
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, path)
        except BaseException:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass
            raise
        return path

    def write_json(self, target: str | Path, value: Any) -> Path:
        return self.write_text(
            target,
            json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        )
