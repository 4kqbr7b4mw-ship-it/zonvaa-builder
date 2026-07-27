from dataclasses import FrozenInstanceError, fields
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Tuple, get_type_hints

import pytest

from artifact_contract import (
    ArtifactAuthorization,
    ArtifactContractContext,
    ArtifactContractLoader,
    ArtifactState,
    ArtifactStateContract,
    ArtifactTransition,
    ArtifactTransitionType,
    AuthorizationScope,
    AuthorizationStatus,
    HistoryDataClass,
)
from builder.runtime import RuntimeManager
from governance import NormLevel


NOW = datetime(2026, 7, 27, 8, 0, tzinfo=timezone.utc)


def authorization(
    authorization_id="authorization-1",
    subject_id="participant-1",
    granted_by="sovereign-1",
    scopes=(AuthorizationScope.AUTHORIZE_ACTION,),
    status=AuthorizationStatus.ACTIVE,
    revoked_at=None,
):
    return ArtifactAuthorization(
        authorization_id=authorization_id,
        subject_id=subject_id,
        granted_by=granted_by,
        scopes=scopes,
        purpose="Coordinate this artifact",
        status=status,
        granted_at=NOW,
        revoked_at=revoked_at,
        binding_references=(),
    )


def transition(
    transition_id="transition-1",
    artifact_id="artifact-1",
    authorized_by="sovereign-1",
    occurred_at=NOW,
    from_state=ArtifactState.DRAFT,
    to_state=ArtifactState.PERSONAL,
    irreversible=False,
    rule_level=NormLevel.C2_GOVERNANCE_CHARTER,
):
    return ArtifactTransition(
        transition_id=transition_id,
        artifact_id=artifact_id,
        transition_type=ArtifactTransitionType.MAKE_PERSONAL,
        from_state=from_state,
        to_state=to_state,
        authorized_by=authorized_by,
        occurred_at=occurred_at,
        irreversible=irreversible,
        rule_level=rule_level,
        reason="Explicitly accepted",
    )


def contract(
    state=ArtifactState.PERSONAL,
    authorizations=(),
    transitions=None,
    participant_ids=("participant-1",),
):
    if transitions is None:
        transitions = (transition(),)
    return ArtifactStateContract(
        contract_version="1.0",
        artifact_id="artifact-1",
        sovereign_id="sovereign-1",
        participant_ids=participant_ids,
        state=state,
        history_data_class=HistoryDataClass.ANONYMIZABLE,
        authorizations=authorizations,
        transitions=transitions,
    )


def test_public_enums_have_stable_complete_values():
    assert [item.value for item in ArtifactState] == [
        "draft",
        "personal",
        "ready_for_authorization",
        "shared",
        "suspended",
        "archived",
        "expired",
    ]
    assert [item.value for item in AuthorizationScope] == [
        "read",
        "contribute",
        "authorize_action",
        "manage_sharing",
    ]
    assert [item.value for item in AuthorizationStatus] == [
        "active",
        "revoked",
        "expired",
    ]
    assert [item.value for item in HistoryDataClass] == [
        "immutable",
        "retention_required",
        "deletable",
        "anonymizable",
    ]
    assert [item.value for item in ArtifactTransitionType] == [
        "make_personal",
        "prepare_authorization",
        "share",
        "suspend",
        "restore",
        "archive",
        "expire",
    ]


def test_models_are_typed_immutable_and_contain_no_document_content():
    item = contract()

    assert [field.name for field in fields(item)] == [
        "contract_version",
        "artifact_id",
        "sovereign_id",
        "participant_ids",
        "state",
        "history_data_class",
        "authorizations",
        "transitions",
    ]
    assert (
        get_type_hints(ArtifactStateContract)["participant_ids"]
        == Tuple[str, ...]
    )
    assert all("content" not in field.name for field in fields(item))
    with pytest.raises(FrozenInstanceError):
        item.state = ArtifactState.SHARED
    with pytest.raises(TypeError, match="scopes"):
        authorization(scopes=("authorize_action",))
    with pytest.raises(TypeError, match="status"):
        authorization(status="active")
    with pytest.raises(TypeError, match="state"):
        ArtifactStateContract(
            contract_version="1.0",
            artifact_id="artifact-1",
            sovereign_id="sovereign-1",
            participant_ids=(),
            state="draft",
            history_data_class=HistoryDataClass.DELETABLE,
        )


def test_valid_contract_keeps_one_sovereign_and_explicit_participants():
    item = contract(authorizations=(authorization(),))

    assert item.sovereign_id == "sovereign-1"
    assert item.participant_ids == ("participant-1",)
    assert item.authorizations[0].subject_id == "participant-1"


def test_authorization_is_granular_purpose_bound_and_revocable():
    revoked = authorization(
        status=AuthorizationStatus.REVOKED,
        revoked_at=NOW + timedelta(minutes=1),
    )

    assert revoked.scopes == (AuthorizationScope.AUTHORIZE_ACTION,)
    assert revoked.purpose == "Coordinate this artifact"
    assert revoked.revoked_at == NOW + timedelta(minutes=1)


@pytest.mark.parametrize(
    "status, revoked_at",
    [
        (AuthorizationStatus.REVOKED, None),
        (AuthorizationStatus.ACTIVE, NOW),
        (AuthorizationStatus.EXPIRED, NOW),
    ],
)
def test_authorization_status_and_revocation_time_stay_consistent(
    status,
    revoked_at,
):
    with pytest.raises(ValueError):
        authorization(status=status, revoked_at=revoked_at)


def test_authorization_rejects_implicit_or_duplicated_access():
    with pytest.raises(ValueError, match="explicit participant"):
        contract(
            authorizations=(
                authorization(subject_id="family-member-not-listed"),
            )
        )
    with pytest.raises(ValueError, match="authorization IDs"):
        contract(
            authorizations=(
                authorization(),
                authorization(subject_id="participant-2"),
            ),
            participant_ids=("participant-1", "participant-2"),
        )
    with pytest.raises(ValueError, match="granted by"):
        contract(
            authorizations=(
                authorization(granted_by="another-person"),
            )
        )


def test_participant_ids_are_unique_and_do_not_duplicate_sovereign():
    with pytest.raises(ValueError, match="participant_ids must be unique"):
        contract(participant_ids=("participant-1", "participant-1"))
    with pytest.raises(ValueError, match="must not be duplicated"):
        contract(participant_ids=("sovereign-1",))


def test_transition_chain_is_auditable_and_prevents_silent_overwrite():
    first = transition()
    second = ArtifactTransition(
        transition_id="transition-2",
        artifact_id="artifact-1",
        transition_type=ArtifactTransitionType.PREPARE_AUTHORIZATION,
        from_state=ArtifactState.PERSONAL,
        to_state=ArtifactState.READY_FOR_AUTHORIZATION,
        authorized_by="participant-1",
        occurred_at=NOW + timedelta(minutes=1),
        irreversible=True,
        rule_level=NormLevel.C3_OPERATIVE_RULES,
        reason="Prepared for a specific authorization",
    )
    item = contract(
        state=ArtifactState.READY_FOR_AUTHORIZATION,
        authorizations=(authorization(),),
        transitions=(first, second),
    )

    assert item.transitions == (first, second)
    assert item.transitions[-1].irreversible is True
    assert item.state is ArtifactState.READY_FOR_AUTHORIZATION


def test_historic_transition_remains_valid_after_later_revocation():
    revoked = authorization(
        status=AuthorizationStatus.REVOKED,
        revoked_at=NOW + timedelta(minutes=2),
    )
    item = contract(
        authorizations=(revoked,),
        transitions=(
            transition(
                authorized_by="participant-1",
                occurred_at=NOW + timedelta(minutes=1),
            ),
        ),
    )

    assert item.transitions[0].authorized_by == "participant-1"


def test_transition_before_grant_or_after_revocation_is_rejected():
    granted_later = authorization()
    with pytest.raises(ValueError, match="explicit authorization"):
        contract(
            authorizations=(granted_later,),
            transitions=(
                transition(
                    authorized_by="participant-1",
                    occurred_at=NOW - timedelta(minutes=1),
                ),
            ),
        )

    revoked = authorization(
        status=AuthorizationStatus.REVOKED,
        revoked_at=NOW + timedelta(minutes=1),
    )
    with pytest.raises(ValueError, match="explicit authorization"):
        contract(
            authorizations=(revoked,),
            transitions=(
                transition(
                    authorized_by="participant-1",
                    occurred_at=NOW + timedelta(minutes=2),
                ),
            ),
        )


def test_transition_rejects_foreign_unordered_or_unauthorized_events():
    with pytest.raises(ValueError, match="another artifact"):
        contract(transitions=(transition(artifact_id="artifact-2"),))
    with pytest.raises(ValueError, match="ordered chain"):
        contract(
            transitions=(
                transition(
                    from_state=ArtifactState.PERSONAL,
                    to_state=ArtifactState.SHARED,
                ),
            )
        )
    with pytest.raises(ValueError, match="explicit authorization"):
        contract(
            transitions=(
                transition(authorized_by="participant-1"),
            )
        )


def test_transition_rejects_duplicate_ids_and_state_without_history():
    first = transition()
    second = ArtifactTransition(
        transition_id=first.transition_id,
        artifact_id="artifact-1",
        transition_type=ArtifactTransitionType.ARCHIVE,
        from_state=ArtifactState.PERSONAL,
        to_state=ArtifactState.ARCHIVED,
        authorized_by="sovereign-1",
        occurred_at=NOW + timedelta(minutes=1),
        irreversible=False,
        rule_level=NormLevel.C3_OPERATIVE_RULES,
        reason="No longer active",
    )
    with pytest.raises(ValueError, match="transition IDs"):
        contract(
            state=ArtifactState.ARCHIVED,
            transitions=(first, second),
        )
    with pytest.raises(ValueError, match="last audited transition"):
        contract(state=ArtifactState.SHARED)


def test_transition_rejects_naive_time_and_c1_operational_rule():
    with pytest.raises(ValueError, match="timezone-aware"):
        transition(occurred_at=datetime(2026, 7, 27, 8, 0))
    with pytest.raises(ValueError, match="C2 or C3"):
        transition(rule_level=NormLevel.C1_CONSTITUTION)


def test_history_class_is_explicit_without_blanket_immutability():
    assert {
        HistoryDataClass.IMMUTABLE,
        HistoryDataClass.RETENTION_REQUIRED,
        HistoryDataClass.DELETABLE,
        HistoryDataClass.ANONYMIZABLE,
    } == set(HistoryDataClass)
    assert (
        contract().history_data_class
        is HistoryDataClass.ANONYMIZABLE
    )


def test_loader_is_deterministic_and_contract_rejects_unconfirmed_claims():
    first = ArtifactContractLoader().load()
    second = ArtifactContractLoader().load()

    assert first == second
    assert first.version == "1.0"
    assert first.states == tuple(ArtifactState)
    assert len(first.content_hash) == 64
    assert "weder\nrechtlich wirksam noch fachlich geprüft" in first.content
    assert "noch eine konkrete\nAufbewahrungs-" in first.content
    assert "Zero-Knowledge-Verfahren" in first.content
    assert "automatische Notfall-" in first.content


@pytest.mark.parametrize(
    "missing_heading",
    ArtifactContractLoader.REQUIRED_HEADINGS,
)
def test_loader_rejects_missing_contract_section(
    tmp_path,
    missing_heading,
):
    canonical = ArtifactContractLoader.DEFAULT_SOURCE.read_text(
        encoding="utf-8"
    )
    source = tmp_path / "contract.md"
    source.write_text(
        canonical.replace(
            "## {}\n".format(missing_heading),
            "",
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="unvollständig"):
        ArtifactContractLoader(source).load()


def test_loader_rejects_missing_invalid_or_unversioned_source(tmp_path):
    with pytest.raises(FileNotFoundError):
        ArtifactContractLoader(tmp_path / "missing.md").load()

    source = tmp_path / "contract.md"
    source.write_bytes(b"\xff")
    with pytest.raises(UnicodeError):
        ArtifactContractLoader(source).load()

    source.write_text("# Contract\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Version"):
        ArtifactContractLoader(source).load()


def test_runtime_boot_exposes_canonical_artifact_contract(monkeypatch):
    monkeypatch.setattr(
        "builder.runtime.ProjectState.collect",
        lambda self: {"verified_facts": {}},
    )

    runtime = RuntimeManager().boot()

    assert runtime.artifact_contract_context == ArtifactContractLoader().load()
