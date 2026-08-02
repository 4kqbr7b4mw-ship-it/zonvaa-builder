from dataclasses import FrozenInstanceError, replace

import pytest

from governance.authority import (
    ActorResponsibilityBoundary,
    AuthorityActorClass,
    AuthorityCapability,
    AuthorityControlLevel,
    AuthorityDefinition,
    AuthorityDelegationRule,
    AuthorityExercise,
    AuthorityModelCapability,
    AuthorityProvenance,
    AuthorityReviewStatus,
    AuthorityType,
    GuardianAuthorityModel,
    GuardianAuthorityModelValidator,
    GuardianAuthorityValidationError,
    ProhibitedAuthorityCombination,
)
from governance.models import NormLevel


def provenance(source="knowledge/adr/ADR-0048-guardian-authority-model-v1.md"):
    return AuthorityProvenance(
        norm_level=NormLevel.C2_GOVERNANCE_CHARTER,
        source_reference=source,
        decision_reference="ADR-0048",
    )


def authority(
    identifier,
    authority_type,
    capability,
    exercise,
    *,
    revocable,
    controls=(AuthorityControlLevel.EXPLICIT_HUMAN_CONTROL,),
    joint=(),
    source=None,
):
    return AuthorityDefinition(
        authority_id=identifier,
        authority_type=authority_type,
        responsibility="Verantwortung {}".format(identifier),
        capabilities=(capability,),
        exercise=exercise,
        revocable=revocable,
        required_control_levels=controls,
        joint_actor_classes=joint,
        provenance=source or provenance(),
    )


def boundary(identifier, actor_class, allowed, all_authorities, source=None):
    return ActorResponsibilityBoundary(
        boundary_id=identifier,
        actor_class=actor_class,
        responsibilities=("Begrenzte Verantwortung",),
        allowed_authority_references=tuple(allowed),
        prohibited_authority_references=tuple(
            item for item in all_authorities if item not in allowed
        ),
        provenance=source or provenance(),
    )


def valid_model():
    sovereign = authority(
        "authority-sovereign",
        AuthorityType.SOVEREIGN_DECISION,
        AuthorityCapability.DEFINE_PERSONAL_INTENT,
        AuthorityExercise.NON_DELEGABLE,
        revocable=False,
    )
    operational = authority(
        "authority-operational",
        AuthorityType.OPERATIONAL_IMPLEMENTATION,
        AuthorityCapability.IMPLEMENT_APPROVED_CHANGE,
        AuthorityExercise.DELEGABLE,
        revocable=True,
        controls=(
            AuthorityControlLevel.EXPLICIT_HUMAN_CONTROL,
            AuthorityControlLevel.STRUCTURAL_VALIDATION,
        ),
    )
    joint = authority(
        "authority-constitutional-change",
        AuthorityType.GOVERNANCE_OVERSIGHT,
        AuthorityCapability.APPROVE_CONSTITUTION_CHANGE,
        AuthorityExercise.JOINT_EXERCISE,
        revocable=False,
        controls=(AuthorityControlLevel.MULTI_PARTY_CONTROL,),
        joint=(
            AuthorityActorClass.OPERATIONAL_LEADERSHIP,
            AuthorityActorClass.TRUST_COUNCIL,
            AuthorityActorClass.USER_CONVENTION,
        ),
    )
    authority_ids = tuple(item.authority_id for item in (sovereign, operational, joint))
    boundaries = (
        boundary(
            "boundary-sovereign",
            AuthorityActorClass.HUMAN_SOVEREIGN,
            (sovereign.authority_id,),
            authority_ids,
        ),
        boundary(
            "boundary-operational",
            AuthorityActorClass.OPERATIONAL_LEADERSHIP,
            (operational.authority_id, joint.authority_id),
            authority_ids,
        ),
        boundary(
            "boundary-core",
            AuthorityActorClass.DETERMINISTIC_CORE,
            (operational.authority_id,),
            authority_ids,
        ),
        boundary(
            "boundary-trust",
            AuthorityActorClass.TRUST_COUNCIL,
            (joint.authority_id,),
            authority_ids,
        ),
        boundary(
            "boundary-users",
            AuthorityActorClass.USER_CONVENTION,
            (joint.authority_id,),
            authority_ids,
        ),
    )
    return GuardianAuthorityModel(
        authority_model_id="guardian-authority-model-v1",
        version="1.0",
        authorities=(sovereign, operational, joint),
        actor_boundaries=boundaries,
        delegation_rules=(
            AuthorityDelegationRule(
                delegation_rule_id="delegation-operational-core",
                authority_reference=operational.authority_id,
                delegating_actor_class=AuthorityActorClass.OPERATIONAL_LEADERSHIP,
                receiving_actor_classes=(AuthorityActorClass.DETERMINISTIC_CORE,),
                requires_explicit_human_confirmation=True,
                revocable=True,
                provenance=provenance(),
            ),
        ),
        prohibited_combinations=(
            ProhibitedAuthorityCombination(
                combination_id="combination-sovereign-operational",
                first_authority_reference=sovereign.authority_id,
                second_authority_reference=operational.authority_id,
                reason="Sovereign intent and implementation remain separated.",
                provenance=provenance(),
            ),
        ),
        provenance=provenance(),
        review_status=AuthorityReviewStatus.REVIEWED,
        review_reference="review-authority-v1",
    )


def test_valid_authority_model_is_immutable_deterministic_and_returned_unchanged():
    model = valid_model()
    validator = GuardianAuthorityModelValidator()

    assert validator.validate(model) is model
    assert validator.validate(model) is model
    with pytest.raises(FrozenInstanceError):
        model.version = "changed"


def test_all_contracts_are_immutable():
    model = valid_model()
    for value in (
        model.provenance,
        model.authorities[0],
        model.actor_boundaries[0],
        model.delegation_rules[0],
        model.prohibited_combinations[0],
    ):
        with pytest.raises(FrozenInstanceError):
            value.provenance = provenance()


def test_duplicate_identities_and_unknown_authority_references_are_rejected():
    model = valid_model()
    duplicate = replace(
        model.actor_boundaries[0],
        boundary_id=model.authorities[0].authority_id,
    )
    with pytest.raises(GuardianAuthorityValidationError) as duplicate_error:
        GuardianAuthorityModelValidator().validate(
            replace(model, actor_boundaries=(duplicate,) + model.actor_boundaries[1:])
        )
    assert duplicate_error.value.code == "DUPLICATE_IDENTITY"

    unknown = replace(
        model.actor_boundaries[0],
        prohibited_authority_references=("authority-unknown",),
    )
    with pytest.raises(GuardianAuthorityValidationError) as reference_error:
        GuardianAuthorityModelValidator().validate(
            replace(model, actor_boundaries=(unknown,) + model.actor_boundaries[1:])
        )
    assert reference_error.value.code == "UNKNOWN_AUTHORITY_REFERENCE"


def test_contradictory_and_incomplete_responsibility_boundaries_are_rejected():
    model = valid_model()
    original = model.actor_boundaries[0]
    contradictory = replace(
        original,
        prohibited_authority_references=(
            original.allowed_authority_references[0],
        ) + original.prohibited_authority_references,
    )
    with pytest.raises(GuardianAuthorityValidationError) as conflict:
        GuardianAuthorityModelValidator().validate(
            replace(model, actor_boundaries=(contradictory,) + model.actor_boundaries[1:])
        )
    assert conflict.value.code == "CONTRADICTORY_BOUNDARY"

    incomplete = replace(original, prohibited_authority_references=())
    with pytest.raises(GuardianAuthorityValidationError) as missing:
        GuardianAuthorityModelValidator().validate(
            replace(model, actor_boundaries=(incomplete,) + model.actor_boundaries[1:])
        )
    assert missing.value.code == "INCOMPLETE_RESPONSIBILITY_BOUNDARY"


def test_non_delegable_and_joint_authorities_cannot_be_delegated():
    model = valid_model()
    for authority_id in (
        "authority-sovereign",
        "authority-constitutional-change",
    ):
        invalid_rule = replace(
            model.delegation_rules[0],
            delegation_rule_id="rule-{}".format(authority_id),
            authority_reference=authority_id,
        )
        with pytest.raises(GuardianAuthorityValidationError) as error:
            GuardianAuthorityModelValidator().validate(
                replace(
                    model,
                    delegation_rules=model.delegation_rules + (invalid_rule,),
                )
            )
        assert error.value.code == "NON_DELEGABLE_AUTHORITY_DELEGATED"


def test_delegation_must_remain_inside_both_responsibility_boundaries():
    model = valid_model()
    guardian_ids = tuple(item.authority_id for item in model.authorities)
    guardian_boundary = boundary(
        "boundary-guardian",
        AuthorityActorClass.GUARDIAN,
        (),
        guardian_ids,
    )
    invalid_rule = replace(
        model.delegation_rules[0],
        receiving_actor_classes=(AuthorityActorClass.GUARDIAN,),
    )
    with pytest.raises(GuardianAuthorityValidationError) as error:
        GuardianAuthorityModelValidator().validate(
            replace(
                model,
                actor_boundaries=model.actor_boundaries + (guardian_boundary,),
                delegation_rules=(invalid_rule,),
            )
        )
    assert error.value.code == "RESPONSIBILITY_BOUNDARY_EXCEEDED"


def test_delegation_revocability_must_match_the_authority_definition():
    model = valid_model()
    invalid_rule = replace(model.delegation_rules[0], revocable=False)
    with pytest.raises(GuardianAuthorityValidationError) as error:
        GuardianAuthorityModelValidator().validate(
            replace(model, delegation_rules=(invalid_rule,))
        )
    assert error.value.code == "REVOCABILITY_MISMATCH"


def test_joint_authority_requires_all_joint_boundaries_and_multi_party_control():
    model = valid_model()
    joint = model.authorities[2]
    without_control = replace(
        joint,
        required_control_levels=(AuthorityControlLevel.INDEPENDENT_REVIEW,),
    )
    with pytest.raises(GuardianAuthorityValidationError) as control:
        GuardianAuthorityModelValidator().validate(
            replace(model, authorities=model.authorities[:2] + (without_control,))
        )
    assert control.value.code == "MULTI_PARTY_CONTROL_REQUIRED"

    missing_users = tuple(
        item
        for item in model.actor_boundaries
        if item.actor_class is not AuthorityActorClass.USER_CONVENTION
    )
    with pytest.raises(GuardianAuthorityValidationError) as boundary_error:
        GuardianAuthorityModelValidator().validate(
            replace(model, actor_boundaries=missing_users)
        )
    assert boundary_error.value.code == "ACTOR_BOUNDARY_REQUIRED"


def test_prohibited_authority_combination_cannot_fit_one_actor_boundary():
    model = valid_model()
    original = model.actor_boundaries[0]
    invalid = replace(
        original,
        allowed_authority_references=(
            "authority-sovereign",
            "authority-operational",
        ),
        prohibited_authority_references=("authority-constitutional-change",),
    )
    with pytest.raises(GuardianAuthorityValidationError) as error:
        GuardianAuthorityModelValidator().validate(
            replace(model, actor_boundaries=(invalid,) + model.actor_boundaries[1:])
        )
    assert error.value.code == "PROHIBITED_AUTHORITY_COMBINATION"


def test_provenance_and_review_status_are_structurally_consistent():
    model = valid_model()
    changed = replace(model.authorities[0], provenance=provenance("other.md"))
    with pytest.raises(GuardianAuthorityValidationError) as provenance_error:
        GuardianAuthorityModelValidator().validate(
            replace(model, authorities=(changed,) + model.authorities[1:])
        )
    assert provenance_error.value.code == "PROVENANCE_MISMATCH"

    with pytest.raises(GuardianAuthorityValidationError) as review_error:
        GuardianAuthorityModelValidator().validate(
            replace(model, review_reference=None)
        )
    assert review_error.value.code == "REVIEW_REFERENCE_REQUIRED"


@pytest.mark.parametrize(
    "capability",
    tuple(
        item
        for item in AuthorityModelCapability
        if item is not AuthorityModelCapability.DESCRIBE_AUTHORITY_MODEL
    ),
)
def test_authority_model_rejects_every_executing_capability(capability):
    model = valid_model()
    with pytest.raises(GuardianAuthorityValidationError) as error:
        GuardianAuthorityModelValidator().validate(
            replace(model, capabilities=(capability,))
        )
    assert error.value.code == "EXECUTING_CAPABILITY_FORBIDDEN"


def test_contract_does_not_authorize_providers_or_offer_runtime_methods():
    model = valid_model()
    for forbidden in (
        "authorize_provider",
        "activate",
        "execute",
        "classify",
        "generate",
        "research",
        "persist",
    ):
        assert not hasattr(model, forbidden)
