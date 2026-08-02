from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone

import pytest

from artifact_contract import ArtifactAuthorization, AuthorizationScope, AuthorizationStatus
from governance.authority import AuthorityProvenance, AuthorityReviewStatus
from governance.b2_data_corridor import (
    ALLOWED_B2_DATA_CLASSES,
    ALLOWED_B2_DATA_FLOWS,
    ALLOWED_B2_DATA_SOURCES,
    D1_D6_REFERENCES,
    D3_REFERENCE,
    PROHIBITED_B2_DATA_CLASSES,
    PROHIBITED_B2_DATA_FLOWS,
    PROHIBITED_B2_DATA_SOURCES,
    PROHIBITED_RESIDUAL_IDENTIFIERS,
    REQUIRED_D3_BINDINGS,
    REQUIRED_PROHIBITED_USES,
    B2ConsentBoundary,
    B2ConsentUse,
    B2DataClass,
    B2DataClassification,
    B2DataCorridor,
    B2DataCorridorPackage,
    B2DataCorridorSnapshot,
    B2DataCorridorValidationError,
    B2DataCorridorValidator,
    B2DataSensitivity,
    B2DepersonalizationBoundary,
    B2NegativeCorridorRules,
    B2ProhibitedCombination,
    B2ProhibitedDestination,
    B2ProhibitedPurposeChange,
)
from governance.models import NormLevel
from guardian_runtime import RetentionClass
from user_owned_data import (
    ReferenceAuthorization,
    ReferenceRetention,
    StorageAvailability,
    StorageOperation,
    StorageProvider,
    StorageReference,
    StorageScope,
)


NOW = datetime(2026, 8, 2, 12, 0, tzinfo=timezone.utc)
PURPOSE = "Prepare supplied personal context for B2 review"
PROVENANCE = AuthorityProvenance(
    norm_level=NormLevel.C2_GOVERNANCE_CHARTER,
    source_reference="knowledge/adr/ADR-0059-guardian-b2-data-corridor-consent-boundary-v1.md",
    decision_reference="ADR-0059",
)


def _authorization(identifier="aav-b2-corridor"):
    return ArtifactAuthorization(
        authorization_id=identifier,
        subject_id="person-1",
        granted_by="person-1",
        scopes=(AuthorizationScope.READ,),
        purpose=PURPOSE,
        status=AuthorizationStatus.ACTIVE,
        granted_at=NOW,
        binding_references=("b2-corridor-1", "uodl-b2-input"),
    )


def _storage(authorization):
    return StorageReference(
        reference_id="uodl-b2-input",
        owner="person-1",
        storage_provider=StorageProvider.LOCAL_FOLDER,
        storage_scope=StorageScope.OWNER_PRIVATE,
        locator="vault-ref:b2/input",
        checksum=None,
        version=1,
        created_at=NOW,
        last_verified=None,
        authorization=ReferenceAuthorization(
            reference_id="uodl-b2-input",
            authorization=authorization,
            operations=(StorageOperation.REFERENCE,),
        ),
        capability=None,
        retention=ReferenceRetention(RetentionClass.KEEP_UNTIL_REVOKED),
        availability=StorageAvailability.UNKNOWN,
    )


def valid_package(**changes):
    authorization = _authorization()
    corridor = B2DataCorridor(
        corridor_id="b2-corridor-1",
        version=1,
        purpose=PURPOSE,
        allowed_data_classes=ALLOWED_B2_DATA_CLASSES,
        excluded_data_classes=PROHIBITED_B2_DATA_CLASSES,
        allowed_data_sources=ALLOWED_B2_DATA_SOURCES,
        excluded_data_sources=PROHIBITED_B2_DATA_SOURCES,
        allowed_flow_directions=ALLOWED_B2_DATA_FLOWS,
        excluded_flow_directions=PROHIBITED_B2_DATA_FLOWS,
        d1_d6_references=D1_D6_REFERENCES,
        d3_reference=D3_REFERENCE,
        aav_reference=authorization,
        uodl_reference=_storage(authorization),
        review_status=AuthorityReviewStatus.REVIEWED,
        review_reference="review-adr-0059",
        provenance=PROVENANCE,
    )
    consent = B2ConsentBoundary(
        consent_id="b2-consent-1",
        corridor_reference=corridor.corridor_id,
        purpose_binding=PURPOSE,
        allowed_scope=ALLOWED_B2_DATA_CLASSES,
        d3_binding=REQUIRED_D3_BINDINGS,
        revocation_reference="aav-revocation:b2-corridor-1",
        allowed_use=(B2ConsentUse.STRUCTURE_PERSONAL_PREPARATION,),
        prohibited_use=REQUIRED_PROHIBITED_USES,
        review_status=corridor.review_status,
        review_reference=corridor.review_reference,
        provenance=PROVENANCE,
    )
    classifications = tuple(
        B2DataClassification(
            data_class=data_class,
            sensitivity=(
                B2DataSensitivity.NON_PERSONAL
                if data_class is B2DataClass.GENERAL_NON_PERSONAL_INFORMATION
                else B2DataSensitivity.PERSONAL
            ),
            personal=data_class is not B2DataClass.GENERAL_NON_PERSONAL_INFORMATION,
            depersonalizable=data_class in ALLOWED_B2_DATA_CLASSES,
            never_allowed=data_class in PROHIBITED_B2_DATA_CLASSES,
            allowed_b2_uses=(B2ConsentUse.STRUCTURE_PERSONAL_PREPARATION,)
            if data_class in ALLOWED_B2_DATA_CLASSES
            else (),
            provenance=PROVENANCE,
        )
        for data_class in B2DataClass
    )
    depersonalization = B2DepersonalizationBoundary(
        boundary_id="b2-depersonalization-1",
        d1_d6_references=D1_D6_REFERENCES,
        removed_identifiers=PROHIBITED_RESIDUAL_IDENTIFIERS,
        allowed_residual_data=(B2DataClass.DEPERSONALIZED_CONTEXT,),
        prohibited_residual_identifiers=PROHIBITED_RESIDUAL_IDENTIFIERS,
        review_status=corridor.review_status,
        review_reference=corridor.review_reference,
        provenance=PROVENANCE,
    )
    negative = B2NegativeCorridorRules(
        prohibited_data_classes=PROHIBITED_B2_DATA_CLASSES,
        prohibited_data_sources=PROHIBITED_B2_DATA_SOURCES,
        prohibited_flow_directions=PROHIBITED_B2_DATA_FLOWS,
        prohibited_combinations=tuple(B2ProhibitedCombination),
        prohibited_residual_identifiers=PROHIBITED_RESIDUAL_IDENTIFIERS,
        prohibited_purpose_changes=tuple(B2ProhibitedPurposeChange),
        prohibited_destinations=tuple(B2ProhibitedDestination),
        provenance=PROVENANCE,
    )
    snapshot = B2DataCorridorSnapshot(
        snapshot_id="b2-corridor-snapshot-1",
        corridor=corridor,
        consent_boundary=consent,
        data_classifications=classifications,
        depersonalization_boundary=depersonalization,
        negative_rules=negative,
        review_status=corridor.review_status,
        review_reference=corridor.review_reference,
        provenance=PROVENANCE,
    )
    values = dict(
        package_id="b2-data-corridor-package-1",
        corridor=corridor,
        consent_boundary=consent,
        data_classifications=classifications,
        depersonalization_boundary=depersonalization,
        negative_rules=negative,
        snapshot=snapshot,
    )
    values.update(changes)
    return B2DataCorridorPackage(**values)


def test_valid_corridor_consent_depersonalization_and_snapshot_are_immutable():
    package = valid_package()
    validator = B2DataCorridorValidator()
    assert validator.validate(package) is package
    assert validator.validate(package) is package
    assert package.snapshot.corridor is package.corridor
    with pytest.raises(FrozenInstanceError):
        package.corridor.purpose = "changed"


@pytest.mark.parametrize(
    "change,code",
    (
        (lambda p: replace(p.corridor, d1_d6_references=D1_D6_REFERENCES[:-1]), "D1_D6_BINDING_INCOMPLETE"),
        (lambda p: replace(p.corridor, d3_reference=D1_D6_REFERENCES[0]), "D3_BINDING_REQUIRED"),
        (lambda p: replace(p.corridor, allowed_data_classes=ALLOWED_B2_DATA_CLASSES[:-1]), "ALLOWED_DATA_CLASSES_INVALID"),
        (lambda p: replace(p.corridor, allowed_data_sources=ALLOWED_B2_DATA_SOURCES[:-1]), "ALLOWED_DATA_SOURCES_INVALID"),
        (lambda p: replace(p.corridor, allowed_flow_directions=ALLOWED_B2_DATA_FLOWS[:-1]), "ALLOWED_FLOWS_INVALID"),
    ),
)
def test_missing_rules_and_invalid_positive_corridor_boundaries_are_rejected(change, code):
    package = valid_package()
    changed = change(package)
    with pytest.raises(B2DataCorridorValidationError) as error:
        B2DataCorridorValidator().validate(replace(package, corridor=changed))
    assert error.value.code == code


def test_d3_alone_never_suffices_without_the_same_aav_and_uodl_binding():
    package = valid_package()
    other = _authorization("another-aav")
    corridor = replace(package.corridor, aav_reference=other)
    with pytest.raises(B2DataCorridorValidationError) as error:
        B2DataCorridorValidator().validate(replace(package, corridor=corridor))
    assert error.value.code == "UODL_AAV_IDENTITY_MISMATCH"


@pytest.mark.parametrize(
    "field",
    (
        "prohibited_data_classes",
        "prohibited_data_sources",
        "prohibited_flow_directions",
        "prohibited_combinations",
        "prohibited_residual_identifiers",
        "prohibited_purpose_changes",
        "prohibited_destinations",
    ),
)
def test_each_negative_rule_family_is_mandatory(field):
    package = valid_package()
    rules = package.negative_rules
    changed = replace(rules, **{field: getattr(rules, field)[:-1]})
    with pytest.raises(B2DataCorridorValidationError) as error:
        B2DataCorridorValidator().validate(replace(package, negative_rules=changed))
    assert error.value.code == "NEGATIVE_RULES_INCOMPLETE"


@pytest.mark.parametrize("destination", tuple(B2ProhibitedDestination))
def test_forwarding_to_every_operational_destination_is_explicitly_forbidden(destination):
    package = valid_package()
    retained = tuple(item for item in package.negative_rules.prohibited_destinations if item is not destination)
    rules = replace(package.negative_rules, prohibited_destinations=retained)
    with pytest.raises(B2DataCorridorValidationError, match="negative rules"):
        B2DataCorridorValidator().validate(replace(package, negative_rules=rules))


def test_forbidden_residual_identifier_and_incomplete_classification_are_rejected():
    package = valid_package()
    boundary = replace(
        package.depersonalization_boundary,
        removed_identifiers=PROHIBITED_RESIDUAL_IDENTIFIERS[:-1],
    )
    with pytest.raises(B2DataCorridorValidationError) as error:
        B2DataCorridorValidator().validate(replace(package, depersonalization_boundary=boundary))
    assert error.value.code == "REMOVED_IDENTIFIERS_INCOMPLETE"
    with pytest.raises(B2DataCorridorValidationError) as error:
        B2DataCorridorValidator().validate(replace(package, data_classifications=package.data_classifications[:-1]))
    assert error.value.code == "DATA_CLASSIFICATION_INCOMPLETE"


def test_snapshot_must_reference_the_exact_supplied_contract_objects():
    package = valid_package()
    copied = replace(package.corridor)
    snapshot = replace(package.snapshot, corridor=copied)
    with pytest.raises(B2DataCorridorValidationError) as error:
        B2DataCorridorValidator().validate(replace(package, snapshot=snapshot))
    assert error.value.code == "SNAPSHOT_IDENTITY_MISMATCH"
