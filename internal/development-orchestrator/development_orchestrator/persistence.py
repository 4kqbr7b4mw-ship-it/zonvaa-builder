"""Run artifact persistence confined to the guarded internal workspace."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import BaseModel

from .boundary import WorkspaceWriter


def new_run_id() -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return "run-{}-{}".format(timestamp, uuid4().hex[:12])


class RunWorkspace:
    def __init__(self, writer: WorkspaceWriter, run_id: str) -> None:
        self.writer = writer
        self.run_id = run_id
        self.relative_root = Path("runs") / run_id

    def json(self, name: str, value: Any) -> Path:
        if isinstance(value, BaseModel):
            value = value.model_dump(mode="json")
        return self.writer.write_json(self.relative_root / name, value)

    def markdown(self, name: str, content: str) -> Path:
        return self.writer.write_text(self.relative_root / name, content.rstrip() + "\n")

    def relative(self, name: str) -> str:
        return str(self.relative_root / name)
