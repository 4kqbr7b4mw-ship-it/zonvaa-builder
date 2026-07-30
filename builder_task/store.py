from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from builder_task.models import ImmutableTask, RepositoryLock, RunReceipt


class BuilderTaskStore:
    def __init__(self, repository: Path) -> None:
        self.repository = repository.resolve()
        self.root = self.repository / "knowledge" / "runtime" / "tasks"
        self.lock_path = self.repository / "knowledge" / "runtime" / "builder-task.lock"

    def task_dir(self, task_id: str) -> Path:
        return self.root / task_id

    def save_task(self, task: ImmutableTask) -> Path:
        path = self.task_dir(task.task_id) / "task.json"
        self._create_immutable(path, task.to_dict())
        return path

    def load_task(self, task_id: str) -> ImmutableTask:
        return ImmutableTask.from_dict(self._read(self.task_dir(task_id) / "task.json"))

    def save_receipt(self, receipt: RunReceipt) -> Path:
        path = self.task_dir(receipt.task_id) / "receipt.json"
        self._create_immutable(path, receipt.to_dict())
        return path

    def load_receipt(self, task_id: str) -> Optional[RunReceipt]:
        path = self.task_dir(task_id) / "receipt.json"
        return RunReceipt.from_dict(self._read(path)) if path.exists() else None

    def write_log(self, task_id: str, name: str, content: str) -> Path:
        path = self.task_dir(task_id) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(content, encoding="utf-8")
        os.replace(str(tmp), str(path))
        return path

    def acquire_lock(self, lock: RepositoryLock) -> None:
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(lock.to_dict(), sort_keys=True, indent=2) + "\n"
        try:
            fd = os.open(str(self.lock_path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            existing = self.read_lock()
            raise RuntimeError("REPOSITORY_LOCKED: {}".format(existing.to_dict()))
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())

    def read_lock(self) -> Optional[RepositoryLock]:
        if not self.lock_path.exists():
            return None
        return RepositoryLock.from_dict(self._read(self.lock_path))

    def release_lock(self, task_id: str, pid: int) -> None:
        lock = self.read_lock()
        if lock is None:
            return
        if lock.task_id != task_id or lock.pid != pid:
            raise RuntimeError("Repository lock ownership changed")
        self.lock_path.unlink()

    @staticmethod
    def _read(path: Path) -> Dict[str, Any]:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("{} must contain an object".format(path))
        return data

    @staticmethod
    def _create_immutable(path: Path, data: Dict[str, Any]) -> None:
        payload = json.dumps(data, sort_keys=True, indent=2) + "\n"
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            if path.read_text(encoding="utf-8") == payload:
                return
            raise RuntimeError("Immutable artifact already exists: {}".format(path))
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
