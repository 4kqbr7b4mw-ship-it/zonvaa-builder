import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest
from typer.testing import CliRunner

import commands.preflight as preflight_command
from builder.main import app
from builder.preflight import PreflightError, PreflightService
from builder.preflight import WorkflowContext
from governance.loader import GovernanceLoader
from institution.models import InstitutionContext, InstitutionGuarantee
from interaction.models import InteractionContext, InteractionPrinciple


runner = CliRunner()


def runtime_context(tmp_path):
    agents = tmp_path / "AGENTS.md"
    if not agents.exists():
        agents.write_text("1. Run preflight.\n", encoding="utf-8")
    session = tmp_path / "knowledge" / "sessions" / "latest.md"
    session.parent.mkdir(parents=True)
    session.write_text("# Latest", encoding="utf-8")
    constitution = (
        Path(__file__).resolve().parents[1]
        / "constitution"
        / "constitution.md"
    ).read_text(encoding="utf-8")
    return SimpleNamespace(
        project_root=tmp_path,
        institution_context=InstitutionContext(
            content="# Institution",
            source=tmp_path / "institution" / "institution.md",
            version="1.0",
            content_hash="a" * 64,
            guarantees=tuple(InstitutionGuarantee),
        ),
        interaction_context=InteractionContext(
            content="# Interaction",
            source=tmp_path / "interaction" / "interaction.md",
            version="1.0",
            content_hash="b" * 64,
            principles=tuple(InteractionPrinciple),
        ),
        constitution=constitution,
        governance_context=GovernanceLoader().load(constitution),
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

    assert context["schema_version"] == "1.3"
    assert context["governance"]["status"] == "loaded"
    assert context["governance"]["constitution"]["version"] == "2.1"
    assert context["governance"]["charter"]["version"] == "1.1"
    assert (
        context["governance"]["operative_rules"]["version"]
        == "1.1"
    )
    assert context["governance"]["norm_levels"] == [
        "c1_constitution",
        "c2_governance_charter",
        "c3_operative_rules",
    ]
    assert context["institution"] == {
        "status": "loaded",
        "path": "institution/institution.md",
        "version": "1.0",
        "content_hash": "a" * 64,
        "guarantees": [
            guarantee.value for guarantee in InstitutionGuarantee
        ],
    }
    assert context["interaction"] == {
        "status": "loaded",
        "path": "interaction/interaction.md",
        "version": "1.0",
        "content_hash": "b" * 64,
        "principles": [
            principle.value for principle in InteractionPrinciple
        ],
    }
    assert context["constitution"] == {
        "status": "loaded",
        "path": "constitution/constitution.md",
        "version": "2.1",
    }
    assert context["knowledge"]["status"] == "loaded"
    assert context["latest_context"]["kind"] == "sessions"
    assert context["working_rules"] == [
        "Run preflight.",
        "Do not speculate.",
    ]
    assert context["git"]["commit"] == "abc1234"


def test_mission_context_is_deeply_immutable(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    context = PreflightService(runtime_context(tmp_path)).build()

    with pytest.raises(TypeError):
        context.git["commit"] = "changed"
    with pytest.raises(TypeError):
        context.verified_facts["tests"]["verified"] = False


def test_workflow_context_can_only_be_derived_from_mission_context(
    tmp_path,
    monkeypatch,
):
    monkeypatch.chdir(tmp_path)
    mission = PreflightService(runtime_context(tmp_path)).build()

    with pytest.raises(TypeError):
        WorkflowContext(
            schema_version="1.3",
            generated_at=mission.generated_at,
            project_root=mission.project_root,
            git_branch="feature",
            git_commit="abc1234",
        )
    assert mission.for_workflow().git_commit == "abc1234"


def test_preflight_is_deterministic_for_same_runtime_and_clock(
    tmp_path,
    monkeypatch,
):
    monkeypatch.chdir(tmp_path)
    runtime = runtime_context(tmp_path)
    now = datetime(2026, 7, 26, 12, 0, tzinfo=timezone.utc)
    service = PreflightService(runtime, clock=lambda: now)

    assert service.build().to_dict() == service.build().to_dict()


def test_stale_mission_context_is_rejected(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runtime = runtime_context(tmp_path)
    now = datetime(2026, 7, 26, 12, 0, tzinfo=timezone.utc)
    clock = [now]
    service = PreflightService(runtime, clock=lambda: clock[0])
    context = service.build()
    clock[0] = now + timedelta(minutes=6)

    with pytest.raises(PreflightError, match="stale"):
        service.validate(context)


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
        ("institution_context", None, "Institution"),
        ("interaction_context", None, "Interaction"),
        ("governance_context", None, "Governance"),
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


def test_preflight_rejects_governance_for_another_constitution(tmp_path):
    runtime = runtime_context(tmp_path)
    runtime.constitution = runtime.constitution + "\nChanged.\n"

    with pytest.raises(PreflightError, match="does not match"):
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
