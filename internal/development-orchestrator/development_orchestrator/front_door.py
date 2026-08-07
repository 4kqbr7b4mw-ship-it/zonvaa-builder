"""Thin tool-facing control plane over the existing orchestrator."""

from __future__ import annotations

from enum import Enum
import os
from pathlib import Path
import re
from typing import Callable, Dict, List, Optional

from pydantic import Field

from .backends import AgentBackend
from .boundary import BoundaryGuard, WorkspaceWriter
from .context_loader import ProjectContextLoader
from .orchestrator import DevelopmentOrchestrator
from .persistence import new_run_id
from .policies import requested_forbidden_git_action
from .schemas import DecisionBrief, FrozenModel, WorkRequest


class FrontDoorError(RuntimeError):
    pass


_SENSITIVE_VALUE = re.compile(
    r"(?i)(bearer\s+)[^\s,;]+|\bsk-[A-Za-z0-9_-]+|"
    r"((?:api[-_ ]?key|token|secret|password)\s*[=:]\s*)[^\s,;]+"
)


def _safe_error_message(error: Exception) -> str:
    """Return bounded local diagnostics without persisting known secrets."""
    message = " ".join(str(error).split())
    for name, value in os.environ.items():
        secret_name = any(
            marker in name.upper()
            for marker in ("KEY", "TOKEN", "SECRET", "PASSWORD")
        )
        if value and secret_name:
            message = message.replace(value, "[REDACTED]")
    message = _SENSITIVE_VALUE.sub(
        lambda match: "{}[REDACTED]".format(match.group(1) or match.group(2) or ""),
        message,
    )
    return message[:1000] or "No exception message was provided."


class FrontDoorStatus(str, Enum):
    AWAITING_CONTEXT_APPROVAL = "AWAITING_CONTEXT_APPROVAL"
    CONTEXT_REJECTED = "CONTEXT_REJECTED"
    REJECTED_POLICY = "REJECTED_POLICY"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    ESCALATED = "ESCALATED"
    FAILED = "FAILED"


class ContextCandidate(FrozenModel):
    path: str = Field(min_length=1)
    reason: str = Field(min_length=1)


class ContextProposal(FrozenModel):
    path: str
    reason: str
    characters: int = Field(ge=0)
    truncated: bool


class FrontDoorRecord(FrozenModel):
    run_id: str
    status: FrontDoorStatus
    request: WorkRequest
    context_proposal: List[ContextProposal] = Field(default_factory=list)
    approved_context: List[str] = Field(default_factory=list)
    active_agent: Optional[str] = None
    review_cycle: int = Field(default=0, ge=0)
    open_decision: Optional[str] = None
    decision_brief_available: bool = False


class FrontDoorService:
    """Persist requests and delegate all agent work to DevelopmentOrchestrator."""

    def __init__(
        self,
        repository_root: Path,
        tool_root: Path,
        backend_factory: Callable[[], AgentBackend],
    ) -> None:
        self.repository_root = repository_root.resolve(strict=True)
        self.tool_root = tool_root.resolve(strict=True)
        self.backend_factory = backend_factory
        self.guard = BoundaryGuard(self.repository_root, self.tool_root)
        self.writer = WorkspaceWriter(self.guard)
        self.loader = ProjectContextLoader(self.guard)

    def submit_work(
        self,
        request: WorkRequest,
        context_candidates: List[ContextCandidate],
    ) -> FrontDoorRecord:
        if request.allowed_context:
            raise FrontDoorError(
                "allowed_context is controlled by explicit context candidates"
            )
        paths = [candidate.path for candidate in context_candidates]
        if len(paths) != len(set(paths)):
            raise FrontDoorError("context candidate paths must be unique")

        run_id = new_run_id()
        inputs = [request.goal, *request.scope, *request.approval_constraints]
        if requested_forbidden_git_action(inputs):
            record = FrontDoorRecord(
                run_id=run_id,
                status=FrontDoorStatus.REJECTED_POLICY,
                request=request,
                open_decision="Commit and push are outside the front-door tool scope.",
            )
            self._write_record(record)
            return record

        if context_candidates:
            preview_request = request.model_copy(update={"allowed_context": paths})
            bundle = self.loader.load(preview_request.goal, paths)
            reasons: Dict[str, str] = {
                candidate.path: candidate.reason for candidate in context_candidates
            }
            proposal = [
                ContextProposal(
                    path=document.path,
                    reason=reasons[document.path],
                    characters=len(document.content),
                    truncated=document.truncated,
                )
                for document in bundle.documents
            ]
            record = FrontDoorRecord(
                run_id=run_id,
                status=FrontDoorStatus.AWAITING_CONTEXT_APPROVAL,
                request=request,
                context_proposal=proposal,
                open_decision="Approve the exact repository context for external transfer.",
            )
            self._write_record(record)
            return record

        record = FrontDoorRecord(
            run_id=run_id,
            status=FrontDoorStatus.RUNNING,
            request=request,
            active_agent="research_agent",
        )
        self._write_record(record)
        return self._execute(record, request)

    def approve_context(
        self,
        run_id: str,
        approved_context: List[str],
        approved: bool,
    ) -> FrontDoorRecord:
        record = self._read_record(run_id)
        if record.status is not FrontDoorStatus.AWAITING_CONTEXT_APPROVAL:
            raise FrontDoorError("run is not awaiting context approval")
        if not approved:
            rejected = record.model_copy(
                update={
                    "status": FrontDoorStatus.CONTEXT_REJECTED,
                    "open_decision": None,
                }
            )
            self._write_record(rejected)
            return rejected

        proposed = {item.path for item in record.context_proposal}
        selected = list(dict.fromkeys(approved_context))
        if not selected:
            raise FrontDoorError("at least one proposed context path must be approved")
        unproposed = set(selected) - proposed
        if unproposed:
            raise FrontDoorError(
                "approved context contains unproposed paths: {}".format(
                    ", ".join(sorted(unproposed))
                )
            )
        request = record.request.model_copy(update={"allowed_context": selected})
        running = record.model_copy(
            update={
                "status": FrontDoorStatus.RUNNING,
                "request": request,
                "approved_context": selected,
                "active_agent": "research_agent",
                "open_decision": None,
            }
        )
        self._write_record(running)
        return self._execute(running, request)

    def get_run_status(self, run_id: str) -> FrontDoorRecord:
        return self._read_record(run_id)

    def get_decision_brief(self, run_id: str) -> DecisionBrief:
        record = self._read_record(run_id)
        if not record.decision_brief_available:
            raise FrontDoorError("decision brief is not available")
        path = self._run_path(run_id, "result.json")
        return DecisionBrief.model_validate_json(path.read_text(encoding="utf-8"))

    def list_pending_decisions(self) -> List[FrontDoorRecord]:
        records: List[FrontDoorRecord] = []
        runs = self.guard.resolve_write_path("runs")
        if not runs.exists():
            return records
        for state in sorted(runs.glob("run-*/front-door.json")):
            try:
                record = FrontDoorRecord.model_validate_json(
                    state.read_text(encoding="utf-8")
                )
            except (OSError, ValueError):
                continue
            if record.open_decision:
                records.append(record)
        return records

    def _execute(
        self,
        running: FrontDoorRecord,
        request: WorkRequest,
    ) -> FrontDoorRecord:
        try:
            brief = DevelopmentOrchestrator(
                self.repository_root,
                self.tool_root,
                self.backend_factory(),
            ).run(request, run_id=running.run_id)
        except Exception as error:
            self.writer.write_json(
                Path("runs") / running.run_id / "front-door-error.json",
                {
                    "error_type": type(error).__name__,
                    "message": _safe_error_message(error),
                },
            )
            failed = running.model_copy(
                update={
                    "status": FrontDoorStatus.FAILED,
                    "active_agent": None,
                    "open_decision": "Run failed; inspect local run evidence.",
                }
            )
            self._write_record(failed)
            return failed
        final_status = {
            "COMPLETED": FrontDoorStatus.COMPLETED,
            "FAILED": FrontDoorStatus.FAILED,
        }.get(brief.status.value, FrontDoorStatus.ESCALATED)
        completed = running.model_copy(
            update={
                "status": final_status,
                "active_agent": None,
                "review_cycle": self._review_cycles(running.run_id),
                "open_decision": (
                    "Founder review is required."
                    if brief.founder_decision_required
                    else None
                ),
                "decision_brief_available": True,
            }
        )
        self._write_record(completed)
        return completed

    def _review_cycles(self, run_id: str) -> int:
        path = self._run_path(run_id, "review.md")
        try:
            return path.read_text(encoding="utf-8").count("## Cycle ")
        except OSError:
            return 0

    def _write_record(self, record: FrontDoorRecord) -> None:
        self.writer.write_json(
            Path("runs") / record.run_id / "front-door.json",
            record.model_dump(mode="json"),
        )

    def _read_record(self, run_id: str) -> FrontDoorRecord:
        self._validate_run_id(run_id)
        path = self._run_path(run_id, "front-door.json")
        try:
            return FrontDoorRecord.model_validate_json(path.read_text(encoding="utf-8"))
        except FileNotFoundError as error:
            raise FrontDoorError("unknown run ID") from error
        except (OSError, ValueError) as error:
            raise FrontDoorError("run state is unreadable") from error

    def _run_path(self, run_id: str, name: str) -> Path:
        self._validate_run_id(run_id)
        return self.guard.resolve_write_path(Path("runs") / run_id / name)

    @staticmethod
    def _validate_run_id(run_id: str) -> None:
        if not run_id.startswith("run-") or any(
            character not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
            for character in run_id
        ):
            raise FrontDoorError("invalid run ID")
