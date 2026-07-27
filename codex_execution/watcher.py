from datetime import datetime, timezone
from typing import Callable, Tuple

from architecture_integrator import WorkflowStatus
from codex_execution.models import ExecutionStatus
from codex_execution.service import CodexExecutionService


class ArchitectureExecutionWatcher:
    """Performs one restart-safe, idempotent workflow scan."""

    def __init__(
        self,
        service: CodexExecutionService,
        clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
    ) -> None:
        self.service = service
        self.clock = clock

    def run_once(self) -> Tuple[str, ...]:
        results = []
        root = self.service.workflows.root
        if not root.is_dir():
            return ()
        for folder in sorted(root.iterdir(), key=lambda item: item.name):
            if (
                not folder.is_dir()
                or folder.is_symlink()
                or not folder.name.startswith("workflow-")
            ):
                continue
            workflow_id = folder.name
            try:
                if self.service.workflows.status(workflow_id) is not (
                    WorkflowStatus.CODEX_PROMPT_GENERATED
                ):
                    continue
                existing = self.service.status(workflow_id)
                if existing is None:
                    record = self.service.execute(workflow_id)
                elif (
                    existing.status
                    is ExecutionStatus.WAITING_FOR_CAPACITY
                    and existing.retry_count
                    < self.service.policy.max_automatic_retries
                    and existing.completed_at is not None
                    and (
                        self.clock() - existing.completed_at
                    ).total_seconds()
                    >= self.service.policy.retry_delay_seconds
                ):
                    record = self.service.execute(workflow_id, retry=True)
                else:
                    continue
                results.append(
                    "{}:{}".format(workflow_id, record.status.value)
                )
            except (OSError, RuntimeError, TypeError, ValueError) as error:
                results.append(
                    "{}:ERROR:{}".format(
                        workflow_id,
                        type(error).__name__,
                    )
                )
        return tuple(results)
