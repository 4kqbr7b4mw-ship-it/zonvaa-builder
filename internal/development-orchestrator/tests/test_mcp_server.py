from __future__ import annotations

import asyncio
from pathlib import Path
import sys

import pytest

pytest.importorskip("mcp")

from development_orchestrator.backends import OfflineContractBackend
from development_orchestrator.front_door import FrontDoorService
from development_orchestrator.mcp_server import create_server
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


EXPECTED_TOOLS = {
    "submit_work",
    "get_run_status",
    "get_decision_brief",
    "approve_context",
    "list_pending_decisions",
}


def server(isolated_repository):
    repository, tool_root = isolated_repository
    service = FrontDoorService(
        repository,
        tool_root,
        lambda: OfflineContractBackend(),
    )
    return create_server(service)


def test_mcp_exposes_only_the_closed_front_door_tool_set(isolated_repository) -> None:
    tools = asyncio.run(server(isolated_repository).list_tools())
    assert {tool.name for tool in tools} == EXPECTED_TOOLS
    assert not EXPECTED_TOOLS.intersection({"commit", "push", "shell", "execute"})


def test_mcp_tool_annotations_match_side_effects(isolated_repository) -> None:
    tools = {
        tool.name: tool for tool in asyncio.run(server(isolated_repository).list_tools())
    }
    assert tools["get_run_status"].annotations.readOnlyHint is True
    assert tools["get_decision_brief"].annotations.readOnlyHint is True
    assert tools["list_pending_decisions"].annotations.readOnlyHint is True
    assert tools["submit_work"].annotations.readOnlyHint is False
    assert tools["approve_context"].annotations.readOnlyHint is False
    assert all(tool.annotations.destructiveHint is False for tool in tools.values())


def test_unknown_tool_is_not_registered(isolated_repository) -> None:
    instance = server(isolated_repository)
    assert instance._tool_manager.get_tool("commit") is None
    assert instance._tool_manager.get_tool("push") is None


def test_server_source_contains_no_secret_literal() -> None:
    source = (
        Path(__file__).resolve().parents[1]
        / "development_orchestrator"
        / "mcp_server.py"
    ).read_text(encoding="utf-8")
    assert "sk-" not in source
    assert "transport=\"stdio\"" in source


def test_real_stdio_protocol_lists_only_the_closed_tool_set() -> None:
    async def list_names() -> set[str]:
        parameters = StdioServerParameters(
            command=sys.executable,
            args=[str(Path(__file__).resolve().parents[1] / "mcp_server.py")],
        )
        async with stdio_client(parameters) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                response = await session.list_tools()
                return {tool.name for tool in response.tools}

    assert asyncio.run(list_names()) == EXPECTED_TOOLS
