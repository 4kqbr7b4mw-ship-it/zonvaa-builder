import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest
from typer.testing import CliRunner

import commands.preflight as preflight_command
from artifact_contract.models import (
    ArtifactAuthorization,
    ArtifactContractContext,
    ArtifactState,
    ArtifactTransitionType,
    AuthorizationScope,
    AuthorizationStatus,
    HistoryDataClass,
)
from builder.main import app
from builder.preflight import PreflightError, PreflightService
from builder.preflight import WorkflowContext
from governance.loader import GovernanceLoader
from guardian_runtime import (
    ArtifactAuthorizationEvidence,
    Confidence,
    ExtractionMethod,
    GuardianMemory,
    GuardianRuntimeContractLoader,
    GuardianRuntimeSnapshot,
    KnowledgeItem,
    KnowledgeTransition,
    KnowledgeType,
    Provenance,
    RetentionClass,
    Sensitivity,
    SourceType,
    TransitionResult,
    TransitionType,
    Validity,
    VerificationMethod,
    VerificationStatus,
    Visibility,
)
from institution.models import InstitutionContext, InstitutionGuarantee
from interaction.models import InteractionContext, InteractionPrinciple
from user_owned_data import UserOwnedDataContractLoader


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
        artifact_contract_context=ArtifactContractContext(
            content="# Artifact contract",
            source=tmp_path / "artifact_contract" / "contract.md",
            version="1.0",
            content_hash="c" * 64,
            states=tuple(ArtifactState),
            authorization_scopes=tuple(AuthorizationScope),
            history_data_classes=tuple(HistoryDataClass),
            transition_types=tuple(ArtifactTransitionType),
        ),
        guardian_runtime_contract_context=(
            GuardianRuntimeContractLoader().load()
        ),
        guardian_runtime_snapshot=GuardianRuntimeSnapshot.unbound(
            datetime(2026, 7, 26, 11, 59, tzinfo=timezone.utc)
        ),
        user_owned_data_context=UserOwnedDataContractLoader().load(),
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


def guardian_knowledge(**overrides):
    now = datetime(2026, 7, 26, 12, 0, tzinfo=timezone.utc)
    values = {
        "knowledge_id": "knowledge-1",
        "subject_id": "person-1",
        "owner_id": "person-1",
        "knowledge_type": KnowledgeType.USER_STATEMENT,
        "content_reference": "local-ref:knowledge/knowledge-1",
        "source_references": ("source-1",),
        "provenance": Provenance(
            source_type=SourceType.USER,
            source_id="source-1",
            source_owner="person-1",
            source_timestamp=now - timedelta(hours=2),
            extraction_method=ExtractionMethod.DIRECT_STATEMENT,
            verification_method=VerificationMethod.NONE,
        ),
        "confidence": Confidence.UNKNOWN,
        "validity": Validity.CURRENT,
        "sensitivity": Sensitivity.PERSONAL,
        "visibility": Visibility.OWNER_ONLY,
        "created_at": now,
        "observed_at": now - timedelta(hours=1),
        "valid_from": now - timedelta(hours=1),
        "valid_until": None,
        "supersedes": (),
        "contradicted_by": (),
        "retention_class": RetentionClass.KEEP_UNTIL_REVOKED,
        "verification_status": VerificationStatus.UNVERIFIED,
        "version": 1,
    }
    values.update(overrides)
    return KnowledgeItem(**values)


def guardian_authorization():
    return ArtifactAuthorizationEvidence(
        artifact_id="artifact-guardian-runtime",
        knowledge_ids=("knowledge-1",),
        authorization=ArtifactAuthorization(
            authorization_id="authorization-1",
            subject_id="person-1",
            granted_by="person-1",
            scopes=(
                AuthorizationScope.READ,
                AuthorizationScope.AUTHORIZE_ACTION,
            ),
            purpose="Validate explicitly scoped Guardian knowledge.",
            status=AuthorizationStatus.ACTIVE,
            granted_at=datetime(
                2026,
                7,
                26,
                11,
                0,
                tzinfo=timezone.utc,
            ),
        ),
    )


def test_preflight_builds_compact_context_from_runtime(tmp_path, monkeypatch):
    agents = tmp_path / "AGENTS.md"
    agents.write_text(
        "# Rules\n\n1. Run preflight.\n2. Do not speculate.\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    context = PreflightService(runtime_context(tmp_path)).build().to_dict()

    assert context["schema_version"] == "1.6"
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
    assert context["artifact_contract"] == {
        "status": "loaded",
        "path": "artifact_contract/contract.md",
        "version": "1.0",
        "content_hash": "c" * 64,
        "states": [state.value for state in ArtifactState],
        "authorization_scopes": [
            scope.value for scope in AuthorizationScope
        ],
        "history_data_classes": [
            data_class.value for data_class in HistoryDataClass
        ],
        "transition_types": [
            transition.value for transition in ArtifactTransitionType
        ],
    }
    assert context["guardian_runtime"]["status"] == "unbound"
    assert (
        context["guardian_runtime"]["snapshot_schema_version"]
        == "1.0"
    )
    assert context["guardian_runtime"]["active_guardian_id"] is None
    assert context["guardian_runtime"]["active_subject_id"] is None
    assert context["guardian_runtime"]["provenance_integrity"] is True
    assert context["user_owned_data"]["status"] == "loaded"
    assert context["user_owned_data"]["version"] == "1.0"
    assert context["user_owned_data"]["path"] == (
        "user_owned_data/contract.md"
    )
    assert "locator" not in context["user_owned_data"]
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
            schema_version="1.6",
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
        ("artifact_contract_context", None, "Artifact contract"),
        (
            "guardian_runtime_contract_context",
            None,
            "Guardian Runtime contract",
        ),
        (
            "guardian_runtime_snapshot",
            None,
            "Guardian Runtime snapshot",
        ),
        (
            "user_owned_data_context",
            None,
            "User-Owned Data contract",
        ),
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


def test_preflight_rejects_guardian_runtime_contract_version(tmp_path):
    runtime = runtime_context(tmp_path)
    object.__setattr__(
        runtime.guardian_runtime_contract_context,
        "version",
        "2.0",
    )

    with pytest.raises(PreflightError, match="version"):
        PreflightService(runtime).build()


def test_preflight_rejects_user_owned_data_contract_version(tmp_path):
    runtime = runtime_context(tmp_path)
    object.__setattr__(
        runtime.user_owned_data_context,
        "version",
        "2.0",
    )

    with pytest.raises(PreflightError, match="User-Owned Data.*version"):
        PreflightService(runtime).build()


def test_preflight_rejects_user_owned_data_contract_hash(tmp_path):
    runtime = runtime_context(tmp_path)
    object.__setattr__(
        runtime.user_owned_data_context,
        "content_hash",
        "0" * 64,
    )

    with pytest.raises(PreflightError, match="integrity"):
        PreflightService(runtime).build()


def test_preflight_rejects_guardian_runtime_snapshot_hash(tmp_path):
    runtime = runtime_context(tmp_path)
    object.__setattr__(
        runtime.guardian_runtime_snapshot,
        "runtime_context_hash",
        "0" * 64,
    )

    with pytest.raises(PreflightError, match="hash"):
        PreflightService(runtime).build()


@pytest.mark.parametrize(
    "knowledge",
    (
        guardian_knowledge(
            valid_until=datetime(
                2026,
                7,
                26,
                11,
                59,
                tzinfo=timezone.utc,
            ),
        ),
        guardian_knowledge(
            retention_class=RetentionClass.KEEP_UNTIL_DATE,
            retention_until=datetime(
                2026,
                7,
                26,
                11,
                59,
                tzinfo=timezone.utc,
            ),
        ),
    ),
)
def test_preflight_rejects_stale_validity_or_due_retention(
    tmp_path,
    knowledge,
):
    runtime = runtime_context(tmp_path)
    runtime.guardian_runtime_snapshot = GuardianRuntimeSnapshot.create(
        captured_at=datetime(
            2026,
            7,
            26,
            12,
            0,
            tzinfo=timezone.utc,
        ),
        active_guardian_id="guardian-1",
        active_subject_id="person-1",
        knowledge_snapshot_version=1,
        applicable_memory_scope=(),
        knowledge_items=(knowledge,),
        memory=GuardianMemory(),
        unresolved_conflicts=(),
        active_authorizations=(guardian_authorization(),),
    )
    service = PreflightService(
        runtime,
        clock=lambda: datetime(
            2026,
            7,
            26,
            12,
            0,
            tzinfo=timezone.utc,
        ),
    )

    with pytest.raises(PreflightError, match="stale|retention"):
        service.build()


def test_preflight_rejects_invalid_knowledge_type_transition(tmp_path):
    runtime = runtime_context(tmp_path)
    invalid = object.__new__(KnowledgeTransition)
    for name, value in {
        "transition_id": "transition-invalid",
        "transition_type": TransitionType.VERIFICATION_ADDED,
        "previous_item": None,
        "new_item": None,
        "trigger": "Corrupt transition fixture.",
        "authorization_reference": "authorization-1",
        "occurred_at": datetime(
            2026,
            7,
            26,
            12,
            0,
            tzinfo=timezone.utc,
        ),
        "reason": "Verify preflight rejects invalid transitions.",
        "source_references": (),
        "result": TransitionResult.PLANNED,
    }.items():
        object.__setattr__(invalid, name, value)
    snapshot = runtime.guardian_runtime_snapshot
    object.__setattr__(snapshot, "transitions", (invalid,))
    object.__setattr__(
        snapshot,
        "runtime_context_hash",
        snapshot.calculate_hash(),
    )

    with pytest.raises(PreflightError, match="type transition"):
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
