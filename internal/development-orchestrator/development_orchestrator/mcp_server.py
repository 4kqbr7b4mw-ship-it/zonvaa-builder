"""Local STDIO MCP adapter for the existing development orchestrator."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import List, Optional

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from .backends import OpenAIAgentsBackend
from .codex_handoff import CodexHandoffService
from .front_door import ContextCandidate, FrontDoorService
from .model_configuration import V1_LIVE_MODEL_CONFIGURATION
from .schemas import WorkRequest


TOOL_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = TOOL_ROOT.parents[1]


def _load_local_openai_key() -> None:
    if os.environ.get("OPENAI_API_KEY"):
        return
    path = TOOL_ROOT / ".env.local"
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        raise RuntimeError("OPENAI_API_KEY is unavailable") from error
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        name, value = stripped.split("=", 1)
        if name.strip() == "OPENAI_API_KEY" and value.strip():
            os.environ["OPENAI_API_KEY"] = value.strip().strip("'\"")
            return
    raise RuntimeError("OPENAI_API_KEY is unavailable")


def _live_backend() -> OpenAIAgentsBackend:
    _load_local_openai_key()
    return OpenAIAgentsBackend(V1_LIVE_MODEL_CONFIGURATION)


def create_server(
    service: Optional[FrontDoorService] = None,
    handoff_service: Optional[CodexHandoffService] = None,
) -> FastMCP:
    front_door = service or FrontDoorService(
        REPOSITORY_ROOT,
        TOOL_ROOT,
        _live_backend,
    )
    handoff = handoff_service or CodexHandoffService(
        REPOSITORY_ROOT,
        TOOL_ROOT,
        authorized_branch="builder-reset-v2",
    )
    server = FastMCP(
        "zonvaa-development-orchestrator",
        instructions=(
            "Use these tools only for internal ZONVAA research and review. "
            "Never claim commit, push, architecture, governance, or founder authority. "
            "When repository context is proposed, show paths, reasons, and character "
            "counts and call approve_context only after explicit user approval."
        ),
        log_level="ERROR",
    )

    @server.tool(
        description=(
            "Use this when the user wants one Research -> Review orchestrator run. "
            "Repository context candidates are proposed but never transmitted until "
            "approve_context receives explicit approval."
        ),
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=True,
        ),
    )
    async def submit_work(
        goal: str,
        scope: List[str],
        requested_output: str,
        approval_constraints: List[str],
        context_candidates: List[ContextCandidate],
        max_cost: Optional[float] = None,
        max_iterations: int = 2,
    ) -> dict:
        request = WorkRequest(
            goal=goal,
            scope=scope,
            requested_output=requested_output,
            allowed_context=[],
            approval_constraints=approval_constraints,
            max_cost=max_cost,
            max_iterations=max_iterations,
        )
        record = await asyncio.to_thread(
            front_door.submit_work,
            request,
            context_candidates,
        )
        return record.model_dump(mode="json")

    @server.tool(
        description="Use this to inspect a known orchestrator run without starting work.",
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    )
    def get_run_status(run_id: str) -> dict:
        return front_door.get_run_status(run_id).model_dump(mode="json")

    @server.tool(
        description="Use this to retrieve the compact reviewed result of a completed run.",
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    )
    def get_decision_brief(run_id: str) -> dict:
        return front_door.get_decision_brief(run_id).model_dump(mode="json")

    @server.tool(
        description=(
            "Use this only after the user explicitly approves or rejects repository "
            "context for one run. Approved paths must be a subset of that run's proposal."
        ),
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=True,
        ),
    )
    async def approve_context(
        run_id: str,
        approved_context: List[str],
        approved: bool,
    ) -> dict:
        record = await asyncio.to_thread(
            front_door.approve_context,
            run_id,
            approved_context,
            approved,
        )
        return record.model_dump(mode="json")

    @server.tool(
        description="Use this to list runs that require an explicit user decision.",
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    )
    def list_pending_decisions() -> list[dict]:
        return [
            record.model_dump(mode="json")
            for record in front_door.list_pending_decisions()
        ]

    @server.tool(
        description=(
            "Use this only after a human explicitly approves one completed and accepted "
            "orchestrator run for local Codex handoff. Paths are the complete closed write "
            "scope. This never authorizes commit, push, another run, or another task."
        ),
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    async def handoff_reviewed_run(
        run_id: str,
        approved: bool,
        allowed_repository_paths: List[str],
        founder_review_approved: bool = False,
    ) -> dict:
        record = await asyncio.to_thread(
            handoff.handoff_reviewed_run,
            run_id,
            approved,
            allowed_repository_paths,
            founder_review_approved,
        )
        return record.model_dump(mode="json")

    return server


def main() -> None:
    create_server().run(transport="stdio")


if __name__ == "__main__":
    main()
