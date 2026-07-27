from dataclasses import FrozenInstanceError, fields, replace
from datetime import datetime, timedelta, timezone

import pytest

from guardian_succession import (
    AccessType,
    AuditActorType,
    BeneficiaryReference,
    BeneficiaryReferenceType,
    DirectiveStatus,
    EligibilityBlocker,
    EventStatus,
    ReleaseCondition,
    ReleaseDecision,
    ReleaseScope,
    ResourceGrant,
    ResourceType,
    SuccessionAuditEvent,
    SuccessionAuditEventType,
    SuccessionAuditTrail,
    SuccessionDirective,
    SuccessionDirectiveHistory,
    SuccessionEvent,
    SuccessionEventType,
    VerificationStatus,
    evaluate_release_eligibility,
)


NOW = datetime(2026, 7, 27, 14, 0, tzinfo=timezone.utc)


def beneficiary(identifier="beneficiary-1"):
    return BeneficiaryReference(
        beneficiary_id=identifier,
        reference_type=BeneficiaryReferenceType.IDENTITY,
        reference_value="identity-ref:{}".format(identifier),
    )


def grant(
    resource_reference="vault-ref:resource-a",
    beneficiary_id="beneficiary-1",
    grant_id="grant-1",
):
    return ResourceGrant(
        grant_id=grant_id,
        resource_reference=resource_reference,
        resource_type=ResourceType.DOCUMENT,
        access_type=AccessType.VIEW,
        beneficiary_reference_id=beneficiary_id,
    )


def condition():
    return ReleaseCondition(
        condition_id="condition-1",
        required_verification_status=VerificationStatus.VERIFIED,
        verification_reference_ids=("verification-policy:standard",),
    )


def event(**overrides):
    values = {
        "event_id": "event-1",
        "event_type": SuccessionEventType.DEATH,
        "subject_id": "owner-1",
        "status": EventStatus.OPEN,
        "reported_at": NOW,
        "verification_status": VerificationStatus.VERIFIED,
        "evidence_references": ("evidence-ref:verification-1",),
    }
    values.update(overrides)
    return SuccessionEvent(**values)


def directive(**overrides):
    values = {
        "directive_id": "directive-1",
        "owner_id": "owner-1",
        "event_type": SuccessionEventType.DEATH,
        "beneficiary": beneficiary(),
        "resource_grants": (grant(),),
        "release_scope": ReleaseScope.EXPLICIT_RESOURCE_GRANTS,
        "release_conditions": (condition(),),
        "required_verification_status": VerificationStatus.VERIFIED,
        "status": DirectiveStatus.ACTIVE,
        "revision": 1,
        "created_at": NOW - timedelta(days=1),
        "updated_at": NOW - timedelta(days=1),
        "revoked_at": None,
        "previous_revision": None,
        "audit_references": ("audit-ref:directive-created",),
    }
    values.update(overrides)
    return SuccessionDirective(**values)


def audit_event(sequence=1, **overrides):
    values = {
        "audit_event_id": "audit-{}".format(sequence),
        "sequence": sequence,
        "event_type": SuccessionAuditEventType.DIRECTIVE_CREATED,
        "directive_id": "directive-1",
        "occurred_at": NOW + timedelta(minutes=sequence),
        "actor_type": AuditActorType.USER,
        "actor_reference": "identity-ref:owner-1",
        "reason_code": "EXPLICIT_USER_DIRECTIVE",
        "reference_ids": ("directive-ref:directive-1",),
    }
    values.update(overrides)
    return SuccessionAuditEvent(**values)


def blocker(result, expected):
    assert result.decision is ReleaseDecision.NO_RELEASE
    assert result.eligible is False
    assert expected in result.blocking_reasons
    assert result.authorized_actions == ()


def test_stable_enum_values_are_complete():
    assert tuple(item.value for item in SuccessionEventType) == (
        "DEATH",
        "INCAPACITY",
        "POWER_OF_ATTORNEY_EFFECTIVE",
        "BUSINESS_SUCCESSION",
        "FOUNDATION_TRANSFER",
        "CUSTOM",
    )
    assert tuple(item.value for item in VerificationStatus) == (
        "UNKNOWN",
        "PENDING",
        "VERIFIED",
        "REJECTED",
    )
    assert tuple(item.value for item in DirectiveStatus) == (
        "DRAFT",
        "ACTIVE",
        "REVOKED",
        "SUPERSEDED",
        "EXECUTED",
    )
    assert tuple(item.value for item in AccessType) == (
        "VIEW",
        "DOWNLOAD",
        "RECEIVE_COPY",
        "DECRYPT",
        "TRANSFER_CONTROL",
    )
    assert tuple(item.value for item in SuccessionAuditEventType) == (
        "DIRECTIVE_CREATED",
        "DIRECTIVE_UPDATED",
        "DIRECTIVE_REVOKED",
        "VERIFICATION_STARTED",
        "VERIFICATION_STATUS_CHANGED",
        "RELEASE_ELIGIBILITY_EVALUATED",
        "RELEASE_BLOCKED",
        "RELEASE_AUTHORIZED",
        "RELEASE_STARTED",
        "RELEASE_COMPLETED",
        "RELEASE_FAILED",
    )


def test_models_are_immutable_and_keep_explicit_ids():
    stored = directive()

    with pytest.raises(FrozenInstanceError):
        stored.status = DirectiveStatus.REVOKED

    assert stored.directive_id == "directive-1"
    assert stored.beneficiary.beneficiary_id == "beneficiary-1"
    assert stored.resource_grants[0].resource_reference == (
        "vault-ref:resource-a"
    )


@pytest.mark.parametrize(
    "verification_status",
    (
        VerificationStatus.UNKNOWN,
        VerificationStatus.PENDING,
        VerificationStatus.REJECTED,
    ),
)
def test_unverified_event_never_releases(verification_status):
    result = evaluate_release_eligibility(
        directive(),
        event(verification_status=verification_status),
        NOW,
    )

    blocker(result, EligibilityBlocker.VERIFICATION_NOT_MET)


def test_verified_event_without_directive_is_no_release():
    result = evaluate_release_eligibility(None, event(), NOW)

    blocker(result, EligibilityBlocker.DIRECTIVE_MISSING)
    assert result.directive_id is None


def test_verified_death_with_draft_directive_is_blocked():
    result = evaluate_release_eligibility(
        directive(status=DirectiveStatus.DRAFT),
        event(),
        NOW,
    )

    blocker(result, EligibilityBlocker.DIRECTIVE_NOT_ACTIVE)


def test_verified_death_with_revoked_directive_is_blocked():
    result = evaluate_release_eligibility(
        directive(
            status=DirectiveStatus.REVOKED,
            revoked_at=NOW - timedelta(hours=1),
        ),
        event(),
        NOW,
    )

    blocker(result, EligibilityBlocker.DIRECTIVE_REVOKED)


def test_wrong_event_type_is_blocked():
    result = evaluate_release_eligibility(
        directive(event_type=SuccessionEventType.INCAPACITY),
        event(),
        NOW,
    )

    blocker(result, EligibilityBlocker.EVENT_TYPE_MISMATCH)


def test_closed_event_and_wrong_subject_are_blocked():
    result = evaluate_release_eligibility(
        directive(),
        event(status=EventStatus.CLOSED, subject_id="other-owner"),
        NOW,
    )

    blocker(result, EligibilityBlocker.EVENT_NOT_OPEN)
    assert EligibilityBlocker.SUBJECT_MISMATCH in result.blocking_reasons


def test_verified_death_without_resource_is_blocked():
    result = evaluate_release_eligibility(
        directive(resource_grants=()),
        event(),
        NOW,
    )

    blocker(result, EligibilityBlocker.RESOURCE_GRANT_MISSING)


def test_verified_death_without_beneficiary_is_blocked():
    result = evaluate_release_eligibility(
        directive(beneficiary=None),
        event(),
        NOW,
    )

    blocker(result, EligibilityBlocker.BENEFICIARY_MISSING)


def test_active_matching_directive_is_eligible_but_executes_nothing():
    result = evaluate_release_eligibility(directive(), event(), NOW)

    assert result.decision is ReleaseDecision.ELIGIBLE
    assert result.eligible is True
    assert result.blocking_reasons == ()
    assert result.open_conditions == ()
    assert result.authorized_actions == ()
    assert "execution" not in result.to_dict()
    assert "transfer" not in result.to_dict()


def test_resource_a_does_not_release_resource_b():
    result = evaluate_release_eligibility(directive(), event(), NOW)
    serialized = directive().to_dict()

    assert result.eligible is True
    assert [item["resource_reference"] for item in serialized[
        "resource_grants"
    ]] == ["vault-ref:resource-a"]
    assert "vault-ref:resource-b" not in str(serialized)


def test_two_beneficiaries_only_receive_their_explicit_resources():
    first = directive()
    second = directive(
        directive_id="directive-2",
        beneficiary=beneficiary("beneficiary-2"),
        resource_grants=(
            grant(
                resource_reference="vault-ref:resource-b",
                beneficiary_id="beneficiary-2",
                grant_id="grant-2",
            ),
        ),
    )

    assert evaluate_release_eligibility(first, event(), NOW).eligible
    assert evaluate_release_eligibility(second, event(), NOW).eligible
    assert first.resource_grants[0].resource_reference == (
        "vault-ref:resource-a"
    )
    assert second.resource_grants[0].resource_reference == (
        "vault-ref:resource-b"
    )
    assert first.beneficiary != second.beneficiary


def test_grant_for_another_beneficiary_is_blocked():
    result = evaluate_release_eligibility(
        directive(
            resource_grants=(
                grant(beneficiary_id="beneficiary-other"),
            ),
        ),
        event(),
        NOW,
    )

    blocker(result, EligibilityBlocker.GRANT_BENEFICIARY_MISMATCH)


def test_revision_history_preserves_previous_revision():
    original = directive()
    revised = replace(
        original,
        status=DirectiveStatus.ACTIVE,
        revision=2,
        previous_revision=1,
        updated_at=NOW,
        release_scope=ReleaseScope.EXPLICIT_RESOURCE_GRANTS,
        audit_references=(
            "audit-ref:directive-created",
            "audit-ref:directive-updated",
        ),
    )
    history = SuccessionDirectiveHistory((original,)).append(revised)

    assert history.revisions == (original, revised)
    assert history.current.revision == 2
    assert history.revisions[0].audit_references != (
        history.current.audit_references
    )


@pytest.mark.parametrize(
    "terminal_status",
    (DirectiveStatus.REVOKED, DirectiveStatus.EXECUTED),
)
def test_terminal_or_revoked_directive_cannot_be_reactivated(
    terminal_status,
):
    terminal = directive(
        status=terminal_status,
        revoked_at=(NOW if terminal_status is DirectiveStatus.REVOKED else None),
    )
    reactivated = replace(
        terminal,
        status=DirectiveStatus.ACTIVE,
        revision=2,
        previous_revision=1,
        updated_at=NOW + timedelta(minutes=1),
        revoked_at=None,
    )

    with pytest.raises(ValueError, match="cannot be revised"):
        SuccessionDirectiveHistory((terminal, reactivated))


def test_guardian_never_invents_missing_recipient_or_resource():
    incomplete = directive(beneficiary=None, resource_grants=())
    result = evaluate_release_eligibility(incomplete, event(), NOW)

    assert incomplete.beneficiary is None
    assert incomplete.resource_grants == ()
    assert result.blocking_reasons == (
        EligibilityBlocker.BENEFICIARY_MISSING,
        EligibilityBlocker.RESOURCE_GRANT_MISSING,
    )


def test_audit_trail_is_append_only_and_deterministically_ordered():
    first = audit_event(1)
    second = audit_event(
        2,
        event_type=SuccessionAuditEventType.RELEASE_ELIGIBILITY_EVALUATED,
    )
    empty = SuccessionAuditTrail()
    one = empty.append(first)
    two = one.append(second)

    assert empty.events == ()
    assert one.events == (first,)
    assert two.events == (first, second)
    assert [item["sequence"] for item in two.to_dict()["events"]] == [1, 2]


def test_audit_trail_rejects_reordering_and_duplicate_ids():
    with pytest.raises(ValueError, match="contiguous"):
        SuccessionAuditTrail((audit_event(2),))
    with pytest.raises(ValueError, match="unique"):
        SuccessionAuditTrail(
            (
                audit_event(1, audit_event_id="same"),
                audit_event(2, audit_event_id="same"),
            )
        )


def test_audit_event_has_references_but_no_original_evidence_content():
    field_names = tuple(item.name for item in fields(SuccessionAuditEvent))
    payload = audit_event(1).to_dict()

    assert field_names == (
        "audit_event_id",
        "sequence",
        "event_type",
        "directive_id",
        "occurred_at",
        "actor_type",
        "actor_reference",
        "reason_code",
        "reference_ids",
    )
    assert "content" not in payload
    assert "document" not in payload
    assert "evidence" not in payload


def test_event_references_evidence_without_embedding_it():
    field_names = tuple(item.name for item in fields(SuccessionEvent))

    assert field_names == (
        "event_id",
        "event_type",
        "subject_id",
        "status",
        "reported_at",
        "verification_status",
        "evidence_references",
    )
    with pytest.raises(ValueError, match="single line"):
        event(evidence_references=("first line\nsensitive original",))
    with pytest.raises(ValueError, match="not embed"):
        event(evidence_references=("data:text/plain,sensitive",))


def test_identical_eligibility_evaluation_is_deterministic():
    first = evaluate_release_eligibility(directive(), event(), NOW)
    second = evaluate_release_eligibility(directive(), event(), NOW)

    assert first == second
    assert first.to_dict() == second.to_dict()


def test_eligibility_does_not_mutate_inputs():
    source_directive = directive()
    source_event = event()

    evaluate_release_eligibility(source_directive, source_event, NOW)

    assert source_directive == directive()
    assert source_event == event()


def test_strings_are_not_automatically_converted_to_enums():
    with pytest.raises(TypeError, match="SuccessionEventType"):
        event(event_type="DEATH")
    with pytest.raises(TypeError, match="DirectiveStatus"):
        directive(status="ACTIVE")


def test_naive_timestamps_are_rejected():
    naive = datetime(2026, 7, 27, 14, 0)

    with pytest.raises(ValueError, match="timezone-aware"):
        event(reported_at=naive)
    with pytest.raises(ValueError, match="timezone-aware"):
        evaluate_release_eligibility(directive(), event(), naive)


def test_duplicate_resources_and_conditions_are_rejected():
    with pytest.raises(ValueError, match="resource references"):
        directive(
            resource_grants=(
                grant(grant_id="grant-1"),
                grant(grant_id="grant-2"),
            )
        )
    with pytest.raises(ValueError, match="condition IDs"):
        directive(release_conditions=(condition(), condition()))


def test_release_condition_cannot_lower_verified_requirement():
    with pytest.raises(ValueError, match="VERIFIED"):
        ReleaseCondition(
            condition_id="condition-1",
            required_verification_status=VerificationStatus.PENDING,
        )


def test_eligibility_result_cannot_claim_technical_authorization():
    successful = evaluate_release_eligibility(directive(), event(), NOW)

    with pytest.raises(ValueError, match="technical actions"):
        replace(successful, authorized_actions=("transfer-resource",))
