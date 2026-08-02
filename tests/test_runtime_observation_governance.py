from dataclasses import FrozenInstanceError, replace

import pytest

from governance.authority import (
    AuthorityActorClass,
    AuthorityProvenance,
    AuthorityReviewStatus,
)
from governance.models import NormLevel
from governance.runtime_observation import (
    GOVERNANCE_PROFILE_ACTORS,
    PROHIBITED_USER_OBSERVATION_CATEGORIES,
    SYSTEM_OBSERVATION_CATEGORIES,
    ObservationProfileApprovalStatus,
    ObservationSnapshotStatus,
    RuntimeObservationCategory,
    RuntimeObservationEvent,
    RuntimeObservationGovernance,
    RuntimeObservationGovernanceValidationError,
    RuntimeObservationGovernanceValidator,
    RuntimeObservationProfile,
    RuntimeObservationScope,
)


def provenance():
    return AuthorityProvenance(
        norm_level=NormLevel.C2_GOVERNANCE_CHARTER,
        source_reference=(
            "knowledge/adr/ADR-0053-runtime-observation-governance-v1.md"
        ),
        decision_reference="ADR-0053",
    )


def profile(version=1, previous_reference=None, **changes):
    values = dict(
        profile_id="runtime-observation-profile-v{}".format(version),
        version=version,
        name="Read-only B1 Runtime Observation",
        purpose="Governance of explicitly permitted system event observation.",
        observation_scope_reference="runtime-observation-scope-v{}".format(version),
        explicitly_unobserved_areas=PROHIBITED_USER_OBSERVATION_CATEGORIES,
        allowed_categories=SYSTEM_OBSERVATION_CATEGORIES,
        prohibited_categories=PROHIBITED_USER_OBSERVATION_CATEGORIES,
        responsibility_reference="authority:governance-oversight",
        approval_status=ObservationProfileApprovalStatus.APPROVED,
        approval_reference="approval:runtime-observation-v{}".format(version),
        review_status=AuthorityReviewStatus.REVIEWED,
        review_reference="review:runtime-observation-v{}".format(version),
        change_actor_class=AuthorityActorClass.TRUST_COUNCIL,
        change_authority_reference="authority:observation-profile-governance",
        previous_profile_reference=previous_reference,
        provenance=provenance(),
    )
    values.update(changes)
    return RuntimeObservationProfile(**values)


def scope(version=1, **changes):
    observed = (
        RuntimeObservationEvent.EXECUTION_REQUEST_VALIDATED,
        RuntimeObservationEvent.PROVIDER_INVOCATION_STARTED,
        RuntimeObservationEvent.PROVIDER_INVOCATION_COMPLETED,
        RuntimeObservationEvent.PROVIDER_TECHNICAL_ERROR,
        RuntimeObservationEvent.PROVIDER_TIMEOUT,
        RuntimeObservationEvent.OUTPUT_BOUNDARY_ACCEPTED,
        RuntimeObservationEvent.OUTPUT_BOUNDARY_REJECTED,
        RuntimeObservationEvent.EXECUTION_BLOCKED,
        RuntimeObservationEvent.CONTROLLED_DEGRADATION,
        RuntimeObservationEvent.RUNTIME_RESULT_RECORDED,
    )
    unobserved = tuple(item for item in RuntimeObservationEvent if item not in observed)
    values = dict(
        scope_id="runtime-observation-scope-v{}".format(version),
        version=version,
        observed_runtime_events=observed,
        explicitly_unobserved_runtime_events=unobserved,
        justification=(
            "Only technical runtime lifecycle and boundary outcomes are in scope."
        ),
        provenance=provenance(),
    )
    values.update(changes)
    return RuntimeObservationScope(**values)


def governance(version=1, previous=None, **changes):
    previous_reference = previous.profile_id if previous is not None else None
    values = dict(
        governance_id="runtime-observation-governance-v{}".format(version),
        profile=profile(version, previous_reference),
        scope=scope(version),
        previous_profile=previous,
    )
    values.update(changes)
    return RuntimeObservationGovernance(**values)


def test_valid_observation_profile_is_immutable_and_returned_unchanged():
    value = governance()
    validator = RuntimeObservationGovernanceValidator()
    assert validator.validate(value) is value
    assert validator.validate(value) is value
    with pytest.raises(FrozenInstanceError):
        value.profile.version = 2


def test_profile_versioning_is_explicit_consecutive_and_declarative():
    previous = profile()
    current = governance(version=2, previous=previous)
    assert RuntimeObservationGovernanceValidator().validate(current) is current

    wrong_sequence = replace(
        current,
        profile=replace(current.profile, version=3),
        scope=replace(current.scope, version=3),
    )
    with pytest.raises(RuntimeObservationGovernanceValidationError) as error:
        RuntimeObservationGovernanceValidator().validate(wrong_sequence)
    assert error.value.code == "PROFILE_VERSION_SEQUENCE_INVALID"

    without_previous = replace(current, previous_profile=None)
    with pytest.raises(RuntimeObservationGovernanceValidationError) as error:
        RuntimeObservationGovernanceValidator().validate(without_previous)
    assert error.value.code == "PREVIOUS_PROFILE_REQUIRED"


def test_observed_and_unobserved_runtime_scope_must_not_overlap():
    value = governance()
    overlap = replace(
        value.scope,
        explicitly_unobserved_runtime_events=(
            RuntimeObservationEvent.EXECUTION_REQUEST_VALIDATED,
        )
        + value.scope.explicitly_unobserved_runtime_events,
    )
    with pytest.raises(RuntimeObservationGovernanceValidationError) as error:
        RuntimeObservationGovernanceValidator().validate(
            replace(value, scope=overlap)
        )
    assert error.value.code == "CONTRADICTORY_OBSERVATION_SCOPE"


def test_user_observation_is_always_rejected():
    value = governance()
    changed = replace(
        value.profile,
        allowed_categories=value.profile.allowed_categories
        + (RuntimeObservationCategory.USER_BEHAVIOR,),
    )
    with pytest.raises(RuntimeObservationGovernanceValidationError) as error:
        RuntimeObservationGovernanceValidator().validate(
            replace(value, profile=changed)
        )
    assert error.value.code == "USER_OBSERVATION_PROHIBITED"


def test_profile_building_and_usage_statistics_are_always_rejected():
    value = governance()
    for prohibited in (
        RuntimeObservationCategory.USER_PROFILE,
        RuntimeObservationCategory.USER_INTERACTION_PATTERN,
        RuntimeObservationCategory.USAGE_STATISTICS,
    ):
        changed = replace(
            value.profile,
            allowed_categories=value.profile.allowed_categories + (prohibited,),
        )
        with pytest.raises(RuntimeObservationGovernanceValidationError) as error:
            RuntimeObservationGovernanceValidator().validate(
                replace(value, profile=changed)
            )
        assert error.value.code == "USER_OBSERVATION_PROHIBITED"


@pytest.mark.parametrize(
    "actor_class",
    (
        AuthorityActorClass.DETERMINISTIC_CORE,
        AuthorityActorClass.MODEL_LAYER,
        AuthorityActorClass.GUARDIAN,
    ),
)
def test_runtime_or_non_governance_actor_cannot_change_profile(actor_class):
    value = governance()
    changed = replace(value.profile, change_actor_class=actor_class)
    with pytest.raises(RuntimeObservationGovernanceValidationError) as error:
        RuntimeObservationGovernanceValidator().validate(
            replace(value, profile=changed)
        )
    assert error.value.code == "RUNTIME_PROFILE_CHANGE_PROHIBITED"


@pytest.mark.parametrize("actor_class", GOVERNANCE_PROFILE_ACTORS)
def test_each_governance_profile_actor_is_structurally_allowed(actor_class):
    value = governance()
    changed = replace(value.profile, change_actor_class=actor_class)
    assert RuntimeObservationGovernanceValidator().validate(
        replace(value, profile=changed)
    )


def test_scope_is_a_complete_partition_of_runtime_events():
    value = governance()
    all_events = set(value.scope.observed_runtime_events) | set(
        value.scope.explicitly_unobserved_runtime_events
    )
    assert all_events == set(RuntimeObservationEvent)

    incomplete = replace(
        value.scope,
        explicitly_unobserved_runtime_events=(),
    )
    with pytest.raises(RuntimeObservationGovernanceValidationError) as error:
        RuntimeObservationGovernanceValidator().validate(
            replace(value, scope=incomplete)
        )
    assert error.value.code == "INCOMPLETE_OBSERVATION_SCOPE"


def test_profile_scope_reference_version_and_provenance_must_match():
    value = governance()
    cases = (
        (replace(value.profile, observation_scope_reference="scope:other"), value.scope),
        (value.profile, replace(value.scope, version=2)),
        (
            value.profile,
            replace(
                value.scope,
                provenance=replace(
                    provenance(),
                    decision_reference="ADR:other",
                ),
            ),
        ),
    )
    expected = (
        "SCOPE_REFERENCE_MISMATCH",
        "SCOPE_VERSION_MISMATCH",
        "PROVENANCE_INCONSISTENT",
    )
    for (changed_profile, changed_scope), code in zip(cases, expected):
        with pytest.raises(RuntimeObservationGovernanceValidationError) as error:
            RuntimeObservationGovernanceValidator().validate(
                replace(value, profile=changed_profile, scope=changed_scope)
            )
        assert error.value.code == code


def test_global_observation_identities_are_unique():
    value = governance()
    changed = replace(value.scope, scope_id=value.governance_id)
    with pytest.raises(RuntimeObservationGovernanceValidationError) as error:
        RuntimeObservationGovernanceValidator().validate(
            replace(value, scope=changed)
        )
    assert error.value.code == "DUPLICATE_IDENTITY"


def test_snapshot_is_read_only_and_preserves_profile_and_scope_identity():
    value = governance()
    snapshot = RuntimeObservationGovernanceValidator().create_snapshot(
        value,
        snapshot_id="runtime-observation-snapshot-v1",
        review_status=AuthorityReviewStatus.REVIEWED,
        review_reference="review:runtime-observation-snapshot",
        provenance=provenance(),
    )
    assert snapshot.profile is value.profile
    assert snapshot.scope is value.scope
    assert snapshot.version == 1
    assert snapshot.status is ObservationSnapshotStatus.GOVERNANCE_PROFILE_VALIDATED
    with pytest.raises(FrozenInstanceError):
        snapshot.version = 2


def test_deterministic_repetition_produces_equal_snapshots():
    value = governance()
    validator = RuntimeObservationGovernanceValidator()
    arguments = dict(
        snapshot_id="runtime-observation-snapshot-v1",
        review_status=AuthorityReviewStatus.REVIEWED,
        review_reference="review:runtime-observation-snapshot",
        provenance=provenance(),
    )
    first = validator.create_snapshot(value, **arguments)
    second = validator.create_snapshot(value, **arguments)
    assert first == second
    assert first.profile is value.profile
    assert first.scope is value.scope


def test_governance_contract_has_no_observer_analysis_or_execution_api():
    validator = RuntimeObservationGovernanceValidator()
    for name in (
        "observe",
        "collect",
        "analyze",
        "profile_user",
        "record_metric",
        "persist",
        "notify",
        "activate_workflow",
        "activate_tool",
    ):
        assert not hasattr(validator, name)
