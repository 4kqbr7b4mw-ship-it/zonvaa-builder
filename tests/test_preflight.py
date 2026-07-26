import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from typer.testing import CliRunner

import commands.preflight as preflight_command
from builder.main import app
from builder.preflight import PreflightError, PreflightService


runner = CliRunner()


def runtime_context(tmp_path):
    session = tmp_path / "knowledge" / "sessions" / "latest.md"
    session.parent.mkdir(parents=True)
    session.write_text("# Latest", encoding="utf-8")
    return SimpleNamespace(
        constitution="# Constitution\n\nVersion: 1.0\n",
        knowledge={
            "adr": [Path("knowledge/adr/ADR-0001.md")],
            "protocols": [],
            "handovers": [],
            "project": [],
            "sessions": [session],
            "sources": [],
            "verified_facts": {"tests": {"verified": True}},
        },
        verified_facts={"tests": {"verified": True}},
        project_state={
            "python_version": "3.9.6",
            "pytest_version": "8.4.2",
            "git_branch": "feature",
            "git_commit": "abc1234",
            "git_clean": True,
            "verified_facts": {"tests": {"verified": True}},
        },
        latest_context=session,
    )


def test_preflight_builds_compact_context_from_runtime(tmp_path, monkeypatch):
    agents = tmp_path / "AGENTS.md"
    agents.write_text(
        "# Rules\n\n1. Run preflight.\n2. Do not speculate.\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    context = PreflightService(runtime_context(tmp_path)).build().to_dict()

    assert context["constitution"] == {
        "status": "loaded",
        "path": "constitution/constitution.md",
        "version": "1.0",
    }
    assert context["knowledge"]["status"] == "loaded"
    assert context["latest_context"]["kind"] == "sessions"
    assert context["working_rules"] == [
        "Run preflight.",
        "Do not speculate.",
    ]
    assert context["git"]["commit"] == "abc1234"


def test_preflight_marks_absent_session_and_handover_as_missing(
    tmp_path,
    monkeypatch,
):
    runtime = runtime_context(tmp_path)
    runtime.latest_context = None
    monkeypatch.chdir(tmp_path)

    context = PreflightService(runtime).build().to_dict()

    assert context["latest_context"] == {
        "status": "missing",
        "path": None,
        "kind": None,
    }


@pytest.mark.parametrize(
    "attribute, value, message",
    [
        ("constitution", "", "Constitution"),
        ("knowledge", {}, "Knowledge areas"),
        ("project_state", {}, "Project state fields"),
    ],
)
def test_preflight_rejects_structurally_incomplete_context(
    tmp_path,
    attribute,
    value,
    message,
):
    runtime = runtime_context(tmp_path)
    setattr(runtime, attribute, value)

    with pytest.raises(PreflightError, match=message):
        PreflightService(runtime).build()


def test_preflight_cli_returns_machine_readable_success(
    tmp_path,
    monkeypatch,
):
    runtime = runtime_context(tmp_path)
    monkeypatch.setattr(preflight_command, "get_runtime", lambda: runtime)

    result = runner.invoke(app, ["preflight"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "ready"
    assert payload["mission_context"]["git"]["branch"] == "feature"


def test_preflight_cli_fails_without_traceback(monkeypatch):
    runtime = SimpleNamespace(
        constitution="",
        knowledge={},
        project_state={},
    )
    monkeypatch.setattr(preflight_command, "get_runtime", lambda: runtime)

    result = runner.invoke(app, ["preflight"])

    assert result.exit_code == 1
    payload = json.loads(result.output)
    assert payload["status"] == "failed"
    assert payload["error"]["type"] == "PreflightError"
    assert "Traceback" not in result.output
