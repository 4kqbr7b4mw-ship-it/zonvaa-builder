import json
import os
import tempfile
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterator, Optional

from architecture_integrator import ArchitectureWorkflowStore
from codex_execution.models import (
    CheckStatus,
    ExecutionFailure,
    ExecutionFailureKind,
    ExecutionRecord,
    ExecutionStep,
    ExecutionStatus,
)


class ExecutionStore:
    """Stores local execution state under the owning workflow."""

    def __init__(self, workflows: ArchitectureWorkflowStore) -> None:
        if not isinstance(workflows, ArchitectureWorkflowStore):
            raise TypeError("workflows must be ArchitectureWorkflowStore")
        self.workflows = workflows

    def folder(self, workflow_id: str) -> Path:
        folder = self.workflows.folder(workflow_id) / "executions"
        folder.mkdir(mode=0o700, exist_ok=True)
        if folder.is_symlink():
            raise ValueError("Execution folder cannot be a symlink")
        folder.resolve().relative_to(self.workflows.folder(workflow_id).resolve())
        return folder

    def path(self, workflow_id: str, execution_id: str) -> Path:
        if not execution_id.startswith("execution-"):
            raise ValueError("execution_id is invalid")
        return self.folder(workflow_id) / "{}.json".format(execution_id)

    def write(self, record: ExecutionRecord) -> None:
        path = self.path(record.workflow_id, record.execution_id)
        self._replace(
            path,
            json.dumps(
                record.to_dict(),
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
        self._replace(
            path.with_suffix(".md"),
            self._markdown(record),
        )

    def load(
        self,
        workflow_id: str,
        execution_id: str,
    ) -> ExecutionRecord:
        data = json.loads(
            self.path(workflow_id, execution_id).read_text(encoding="utf-8")
        )
        failure_data = data.get("failure")
        failure = (
            ExecutionFailure.from_dict(failure_data)
            if failure_data is not None
            else None
        )
        if failure is None and data.get("failure_reason"):
            failure = ExecutionFailure(
                kind=ExecutionFailureKind.INTERNAL_ERROR,
                step=ExecutionStep.RESULT_VERIFICATION,
                program=None,
                arguments=(),
                working_directory=data["repository_path"],
                exit_code=data["codex_exit_code"],
                stdout="",
                stderr="",
                exception_type="LegacyExecutionError",
                exception_message=data["failure_reason"],
                technical_cause=data["failure_reason"],
                occurred_at=datetime.fromisoformat(
                    data["completed_at"] or data["started_at"]
                ),
                execution_id=data["execution_id"],
            )
        return ExecutionRecord(
            execution_id=data["execution_id"],
            workflow_id=data["workflow_id"],
            prompt_path=data["prompt_path"],
            prompt_hash=data["prompt_hash"],
            repository_path=data["repository_path"],
            starting_branch=data["starting_branch"],
            starting_commit=data["starting_commit"],
            starting_git_status=tuple(data["starting_git_status"]),
            status=ExecutionStatus(data["status"]),
            started_at=datetime.fromisoformat(data["started_at"]),
            completed_at=(
                datetime.fromisoformat(data["completed_at"])
                if data["completed_at"] is not None
                else None
            ),
            codex_exit_code=data["codex_exit_code"],
            test_status=CheckStatus(data["test_status"]),
            test_result=data["test_result"],
            doctor_status=CheckStatus(data["doctor_status"]),
            doctor_result=data["doctor_result"],
            diff_check_status=CheckStatus(data["diff_check_status"]),
            resulting_commit=data["resulting_commit"],
            handover_paths=tuple(data["handover_paths"]),
            failure=failure,
            retry_count=data["retry_count"],
            push_status=data["push_status"],
            schema_version="1.1",
        )

    def existing(
        self,
        workflow_id: str,
        execution_id: str,
    ) -> Optional[ExecutionRecord]:
        if not self.path(workflow_id, execution_id).is_file():
            return None
        return self.load(workflow_id, execution_id)

    @contextmanager
    def lock(self, workflow_id: str) -> Iterator[None]:
        path = self.folder(workflow_id) / ".lock"
        try:
            descriptor = os.open(
                str(path),
                os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                0o600,
            )
        except FileExistsError as exc:
            raise RuntimeError(
                "Another execution is already running"
            ) from exc
        try:
            os.write(descriptor, str(os.getpid()).encode("ascii"))
            os.close(descriptor)
            yield
        finally:
            try:
                os.close(descriptor)
            except OSError:
                pass
            try:
                path.unlink()
            except FileNotFoundError:
                pass

    def _replace(self, path: Path, content: str) -> None:
        descriptor, temporary_name = tempfile.mkstemp(
            dir=str(path.parent),
            prefix=".execution-",
            suffix=".tmp",
        )
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_name, path)
        except BaseException:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass
            raise

    def _markdown(self, record: ExecutionRecord) -> str:
        duration = (
            (record.completed_at - record.started_at).total_seconds()
            if record.completed_at is not None
            else None
        )
        lines = [
            "# Codex Execution {}".format(record.execution_id),
            "",
            "- Workflow: `{}`".format(record.workflow_id),
            "- Auftrag: `{}` (`{}`)".format(
                record.prompt_path,
                record.prompt_hash,
            ),
            "- Status: `{}`".format(record.status.value),
            "- Start commit: `{}`".format(record.starting_commit),
            "- Result commit: `{}`".format(
                record.resulting_commit or "missing"
            ),
            "- Tests: `{}` — {}".format(
                record.test_status.value,
                record.test_result or "not run",
            ),
            "- Doctor: `{}` — {}".format(
                record.doctor_status.value,
                record.doctor_result or "not run",
            ),
            "- Handover: {}".format(
                ", ".join(record.handover_paths) or "missing"
            ),
            "- Git status at start: {}".format(
                ", ".join(record.starting_git_status) or "clean"
            ),
            "- Duration seconds: {}".format(
                duration if duration is not None else "running"
            ),
            "- Failure or blocker: {}".format(
                (
                    "{} / {} / {}".format(
                        record.failure.kind.value,
                        record.failure.step.value,
                        record.failure.exception_message,
                    )
                    if record.failure
                    else "none"
                )
            ),
            "- Push status: `not_pushed`",
            "",
        ]
        return "\n".join(lines)
