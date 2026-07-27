from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone

import pytest

from artifact_contract import (
    ArtifactAuthorization,
    AuthorizationScope,
    AuthorizationStatus,
)
from guardian_runtime import (
    ArtifactAuthorizationEvidence,
    Confidence,
    ExtractionMethod,
    GuardianMemory,
    GuardianRuntimeSnapshot,
    GuardianRuntimeContractLoader,
    GuardianRuntimeTransitionPlanner,
    KnowledgeConflict,
    KnowledgeItem,
    KnowledgeTransition,
    KnowledgeTransitionRequest,
    KnowledgeType,
    MemoryScope,
    Provenance,
    RetentionClass,
    Sensitivity,
    SourceType,
    TransitionType,
    Validity,
    VerificationMethod,
    VerificationStatus,
    Visibility,
    replace_item,
)
from knowledge.manager import KnowledgeManager


NOW = datetime(2026, 7, 27, 8, 0, tzinfo=timezone.utc)


def provenance(
    *,
    source_type=SourceType.USER,
    verification_method=VerificationMethod.NONE,
):
    return Provenance(
        source_type=source_type,
        source_id="source-1",
        source_owner="person-1",
        source_timestamp=NOW - timedelta(hours=2),
        extraction_method=ExtractionMethod.DIRECT_STATEMENT,
        verification_method=verification_method,
    )


def item(**overrides):
    values = {
        "knowledge_id": "knowledge-1",
        "subject_id": "person-1",
        "owner_id": "person-1",
        "knowledge_type": KnowledgeType.USER_STATEMENT,
        "content_reference": "local-ref:knowledge/knowledge-1",
        "source_references": ("source-1",),
        "provenance": provenance(),
        "confidence": Confidence.UNKNOWN,
        "validity": Validity.CURRENT,
        "sensitivity": Sensitivity.PERSONAL,
        "visibility": Visibility.OWNER_ONLY,
        "created_at": NOW,
        "observed_at": NOW - timedelta(hours=1),
        "valid_from": NOW - timedelta(hours=1),
        "valid_until": None,
        "supersedes": (),
        "contradicted_by": (),
        "retention_class": RetentionClass.KEEP_UNTIL_REVOKED,
        "verification_status": VerificationStatus.UNVERIFIED,
        "version": 1,
    }
    values.update(overrides)
    return KnowledgeItem(**values)


def authorization(
    authorization_id="authorization-owner-1",
    knowledge_ids=("knowledge-1", "knowledge-2"),
    scopes=(
        AuthorizationScope.READ,
        AuthorizationScope.AUTHORIZE_ACTION,
    ),
):
    return ArtifactAuthorizationEvidence(
        artifact_id="artifact-guardian-runtime",
        knowledge_ids=knowledge_ids,
        authorization=ArtifactAuthorization(
            authorization_id=authorization_id,
            subject_id="person-1",
            granted_by="person-1",
            scopes=scopes,
            purpose="Manage explicitly scoped Guardian knowledge.",
            status=AuthorizationStatus.ACTIVE,
            granted_at=NOW - timedelta(days=1),
        ),
    )


def snapshot(
    *,
    items=(),
    conflicts=(),
    memory=GuardianMemory(),
    authorizations=(authorization(),),
    version=1,
):
    return GuardianRuntimeSnapshot.create(
        captured_at=NOW,
        active_guardian_id="guardian-1",
        active_subject_id="person-1",
        knowledge_snapshot_version=version,
        applicable_memory_scope=tuple(MemoryScope),
        knowledge_items=items,
        memory=memory,
        unresolved_conflicts=conflicts,
        active_authorizations=authorizations,
    )


def request(transition_type, candidate, **overrides):
    values = {
        "transition_type": transition_type,
        "knowledge_id": (
            candidate.knowledge_id
            if candidate is not None
            else "knowledge-1"
        ),
        "candidate_item": candidate,
        "trigger": "explicit user-controlled test input",
        "authorization_reference": "authorization-owner-1",
        "requested_at": NOW + timedelta(minutes=1),
        "reason": "Test the explicit state transition.",
        "source_references": ("source-1",),
        "expected_snapshot_version": 1,
    }
    values.update(overrides)
    return KnowledgeTransitionRequest(**values)


def test_stable_knowledge_type_values_have_no_additional_members():
    assert tuple(item.value for item in KnowledgeType) == (
        "VERIFIED_FACT",
        "USER_STATEMENT",
        "EXTERNAL_STATEMENT",
        "OBSERVATION",
        "HYPOTHESIS",
        "INTERPRETATION",
        "PREFERENCE",
        "DECISION",
        "COMMITMENT",
        "MEMORY",
        "PROCEDURAL_KNOWLEDGE",
        "UNKNOWN",
    )


def test_status_confidence_validity_and_transition_values_are_stable():
    assert tuple(item.value for item in VerificationStatus) == (
        "UNVERIFIED",
        "USER_CONFIRMED",
        "SOURCE_CONFIRMED",
        "SYSTEM_VALIDATED",
        "DISPUTED",
        "SUPERSEDED",
        "INVALIDATED",
    )
    assert tuple(item.value for item in Confidence) == (
        "UNKNOWN",
        "LOW",
        "MEDIUM",
        "HIGH",
        "CONFIRMED",
    )
    assert tuple(item.value for item in Validity) == (
        "CURRENT",
        "TEMPORARY",
        "EXPIRED",
        "SUPERSEDED",
        "DISPUTED",
        "UNKNOWN",
    )
    assert tuple(item.value for item in TransitionType) == (
        "statement_recorded",
        "source_attached",
        "verification_added",
        "hypothesis_created",
        "hypothesis_confirmed",
        "hypothesis_rejected",
        "interpretation_added",
        "contradiction_detected",
        "knowledge_superseded",
        "retention_changed",
        "knowledge_archived",
        "knowledge_anonymized",
        "knowledge_deleted",
    )


def test_user_statement_does_not_become_verified_fact_by_confirmation():
    statement = item()
    confirmed = replace_item(
        statement,
        verification_status=VerificationStatus.USER_CONFIRMED,
        confidence=Confidence.HIGH,
        provenance=provenance(
            verification_method=VerificationMethod.USER_CONFIRMATION
        ),
        version=2,
    )

    transition = KnowledgeTransition(
        transition_id="transition-1",
        transition_type=TransitionType.VERIFICATION_ADDED,
        previous_item=statement,
        new_item=confirmed,
        trigger="User confirmation.",
        authorization_reference="authorization-owner-1",
        occurred_at=NOW + timedelta(minutes=1),
        reason="Record confirmation without changing knowledge type.",
        source_references=("source-1",),
    )

    assert transition.new_item.knowledge_type is KnowledgeType.USER_STATEMENT


def test_verified_fact_requires_traceable_verification():
    with pytest.raises(ValueError, match="confirmed verification"):
        item(knowledge_type=KnowledgeType.VERIFIED_FACT)

    fact = item(
        knowledge_type=KnowledgeType.VERIFIED_FACT,
        confidence=Confidence.CONFIRMED,
        verification_status=VerificationStatus.SOURCE_CONFIRMED,
        provenance=provenance(
            source_type=SourceType.DOCUMENT_REFERENCE,
            verification_method=VerificationMethod.SOURCE_COMPARISON,
        ),
    )

    assert fact.knowledge_type is KnowledgeType.VERIFIED_FACT


def test_hypothesis_requires_sources_and_remains_uncertain():
    with pytest.raises(ValueError, match="source references"):
        item(
            knowledge_type=KnowledgeType.HYPOTHESIS,
            source_references=(),
            confidence=Confidence.LOW,
        )
    with pytest.raises(ValueError, match="explicitly uncertain"):
        item(
            knowledge_type=KnowledgeType.HYPOTHESIS,
            confidence=Confidence.CONFIRMED,
        )


def test_verification_transition_is_deterministic_and_auditable():
    before = item()
    after = replace_item(
        before,
        verification_status=VerificationStatus.USER_CONFIRMED,
        confidence=Confidence.HIGH,
        provenance=provenance(
            verification_method=VerificationMethod.USER_CONFIRMATION
        ),
        version=2,
    )
    current = snapshot(items=(before,))
    transition_request = request(
        TransitionType.VERIFICATION_ADDED,
        after,
    )
    planner = GuardianRuntimeTransitionPlanner()

    first = planner.plan(current, transition_request)
    second = planner.plan(current, transition_request)

    assert first.to_dict() == second.to_dict()
    assert first.transition.previous_item is before
    assert first.transition.new_item is after
    assert first.resulting_snapshot.knowledge_snapshot_version == 2
    assert current.knowledge_items == (before,)


def test_conflict_preserves_both_sources_and_requires_clarification():
    left = item(
        validity=Validity.DISPUTED,
        verification_status=VerificationStatus.DISPUTED,
        contradicted_by=("knowledge-2",),
    )
    right = item(
        knowledge_id="knowledge-2",
        knowledge_type=KnowledgeType.EXTERNAL_STATEMENT,
        content_reference="local-ref:knowledge/knowledge-2",
        source_references=("source-2",),
        provenance=Provenance(
            source_type=SourceType.EXTERNAL_PERSON,
            source_id="source-2",
            source_owner="external-person",
            source_timestamp=NOW - timedelta(hours=3),
            extraction_method=ExtractionMethod.DIRECT_STATEMENT,
            verification_method=VerificationMethod.NONE,
        ),
        validity=Validity.DISPUTED,
        verification_status=VerificationStatus.DISPUTED,
    )
    conflict = KnowledgeConflict(
        conflict_id="conflict-1",
        knowledge_ids=("knowledge-1", "knowledge-2"),
        detected_at=NOW,
        reason="The two retained statements explicitly conflict.",
    )

    state = snapshot(items=(left, right), conflicts=(conflict,))

    assert len(state.knowledge_items) == 2
    assert state.unresolved_conflicts[0].requires_clarification is True
    assert {
        source
        for knowledge in state.knowledge_items
        for source in knowledge.source_references
    } == {"source-1", "source-2"}


def test_event_observation_storage_and_validity_time_are_separate():
    timed = item(
        created_at=NOW,
        observed_at=NOW - timedelta(days=2),
        event_at=NOW - timedelta(days=3),
        valid_from=NOW - timedelta(days=5),
        valid_until=NOW + timedelta(days=5),
        validity=Validity.TEMPORARY,
    )

    assert timed.observed_at != timed.created_at
    assert timed.event_at != timed.observed_at
    assert timed.valid_from != timed.observed_at
    with pytest.raises(ValueError, match="observed_at"):
        item(observed_at=NOW + timedelta(seconds=1))
    with pytest.raises(ValueError, match="valid_until"):
        item(
            valid_from=NOW,
            valid_until=NOW - timedelta(seconds=1),
        )


def test_provenance_is_required_except_for_explicit_unknown():
    with pytest.raises(ValueError, match="requires provenance"):
        item(provenance=None)

    unknown = item(
        knowledge_type=KnowledgeType.UNKNOWN,
        provenance=None,
        source_references=(),
    )

    assert unknown.provenance is None


@pytest.mark.parametrize(
    "content_reference",
    (
        "Complete document text without a reference scheme",
        "data:text/plain;base64,SGVsbG8=",
        "base64:SGVsbG8=",
        "local-ref:first line\nsecond line",
    ),
)
def test_content_reference_cannot_embed_original_document_content(
    content_reference,
):
    with pytest.raises(ValueError, match="reference|single line"):
        item(content_reference=content_reference)


def test_person_bound_snapshot_rejects_foreign_knowledge():
    foreign = item(owner_id="person-2", subject_id="person-2")

    with pytest.raises(ValueError, match="person-bound"):
        snapshot(items=(foreign,))


def test_shared_visibility_requires_explicit_active_authorization():
    shared = item(
        visibility=Visibility.SHARED_SAFE,
        authorization_references=("authorization-share-1",),
    )

    with pytest.raises(ValueError, match="active authorization"):
        snapshot(items=(shared,))

    state = snapshot(
        items=(shared,),
        authorizations=(
            authorization(),
            authorization(
                authorization_id="authorization-share-1",
            ),
        ),
    )
    assert state.knowledge_items == (shared,)


def test_authorization_evidence_rejects_revoked_or_insufficient_scope():
    revoked = ArtifactAuthorization(
        authorization_id="authorization-revoked",
        subject_id="person-1",
        granted_by="person-1",
        scopes=(
            AuthorizationScope.READ,
            AuthorizationScope.AUTHORIZE_ACTION,
        ),
        purpose="Previously permitted Guardian knowledge access.",
        status=AuthorizationStatus.REVOKED,
        granted_at=NOW - timedelta(days=2),
        revoked_at=NOW - timedelta(days=1),
    )
    with pytest.raises(ValueError, match="active"):
        ArtifactAuthorizationEvidence(
            artifact_id="artifact-guardian-runtime",
            knowledge_ids=("knowledge-1",),
            authorization=revoked,
        )

    with pytest.raises(ValueError, match="authorize_action"):
        authorization(scopes=(AuthorizationScope.READ,))


def test_shared_visibility_cannot_exceed_authorized_knowledge_scope():
    shared = item(
        visibility=Visibility.SHARED_SAFE,
        authorization_references=("authorization-share-1",),
    )
    unrelated = authorization(
        authorization_id="authorization-share-1",
        knowledge_ids=("knowledge-2",),
    )

    with pytest.raises(ValueError, match="exceeds authorization scope"):
        snapshot(items=(shared,), authorizations=(unrelated,))


def test_all_retention_and_memory_scope_values_are_stable():
    assert tuple(item.value for item in RetentionClass) == (
        "KEEP_UNTIL_REVOKED",
        "KEEP_FOR_ACTIVE_CONTEXT",
        "KEEP_UNTIL_DATE",
        "ARCHIVE",
        "ANONYMIZE",
        "DELETE",
        "LEGAL_HOLD",
        "UNKNOWN",
    )
    assert tuple(item.value for item in MemoryScope) == (
        "EPISODIC",
        "SEMANTIC",
        "USER_PREFERENCE",
        "CONFIRMED_DECISION",
        "OPEN_COMMITMENT",
        "RELATIONSHIP_AND_TRUST",
        "HISTORICAL",
    )


def test_retention_dates_and_holds_require_explicit_basis():
    with pytest.raises(ValueError, match="retention_until"):
        item(retention_class=RetentionClass.KEEP_UNTIL_DATE)
    with pytest.raises(ValueError, match="binding references"):
        item(retention_class=RetentionClass.LEGAL_HOLD)

    held = item(
        retention_class=RetentionClass.LEGAL_HOLD,
        retention_basis_references=("binding-1",),
    )
    state = snapshot(items=(held,))

    assert state.retention_constraints[0].knowledge_id == "knowledge-1"


def test_deletion_is_blocked_until_derived_knowledge_is_reevaluated():
    source = item(retention_class=RetentionClass.DELETE)
    derived = item(
        knowledge_id="knowledge-2",
        knowledge_type=KnowledgeType.INTERPRETATION,
        content_reference="local-ref:knowledge/knowledge-2",
        source_references=("knowledge-1",),
        provenance=Provenance(
            source_type=SourceType.DERIVED,
            source_id="knowledge-1",
            source_owner="person-1",
            source_timestamp=NOW,
            extraction_method=(
                ExtractionMethod.DETERMINISTIC_TRANSFORMATION
            ),
            verification_method=VerificationMethod.NONE,
        ),
    )
    current = snapshot(items=(source, derived))

    with pytest.raises(ValueError, match="reevaluation"):
        GuardianRuntimeTransitionPlanner().plan(
            current,
            request(
                TransitionType.KNOWLEDGE_DELETED,
                None,
            ),
        )


def test_models_are_immutable_and_memory_references_are_unique():
    record = item()
    with pytest.raises(FrozenInstanceError):
        record.version = 2
    with pytest.raises(ValueError, match="only one memory scope"):
        GuardianMemory(
            episodic_ids=("knowledge-1",),
            historical_ids=("knowledge-1",),
        )


def test_transition_rejects_unrelated_silent_mutation():
    before = item()
    after = replace_item(
        before,
        content_reference="local-ref:changed-content",
        verification_status=VerificationStatus.USER_CONFIRMED,
        confidence=Confidence.HIGH,
        provenance=provenance(
            verification_method=VerificationMethod.USER_CONFIRMATION
        ),
        version=2,
    )

    with pytest.raises(ValueError, match="unrelated mutations"):
        KnowledgeTransition(
            transition_id="transition-1",
            transition_type=TransitionType.VERIFICATION_ADDED,
            previous_item=before,
            new_item=after,
            trigger="User confirmation.",
            authorization_reference="authorization-owner-1",
            occurred_at=NOW,
            reason="Invalid combined mutation.",
            source_references=("source-1",),
        )


def test_transition_rejects_implicit_knowledge_type_conversion():
    before = item()
    fact = item(
        knowledge_type=KnowledgeType.VERIFIED_FACT,
        confidence=Confidence.CONFIRMED,
        verification_status=VerificationStatus.SOURCE_CONFIRMED,
        provenance=provenance(
            source_type=SourceType.DOCUMENT_REFERENCE,
            verification_method=VerificationMethod.SOURCE_COMPARISON,
        ),
        version=2,
    )

    with pytest.raises(ValueError, match="cannot be converted"):
        KnowledgeTransition(
            transition_id="transition-1",
            transition_type=TransitionType.VERIFICATION_ADDED,
            previous_item=before,
            new_item=fact,
            trigger="Source confirmation.",
            authorization_reference="authorization-owner-1",
            occurred_at=NOW,
            reason="Invalid implicit fact conversion.",
            source_references=("source-1",),
        )


def test_planner_rejects_missing_authorization_and_stale_snapshot():
    current = snapshot(items=(item(),))
    candidate = replace_item(
        item(),
        verification_status=VerificationStatus.USER_CONFIRMED,
        confidence=Confidence.HIGH,
        provenance=provenance(
            verification_method=VerificationMethod.USER_CONFIRMATION
        ),
        version=2,
    )
    planner = GuardianRuntimeTransitionPlanner()

    with pytest.raises(ValueError, match="active authorization"):
        planner.plan(
            current,
            request(
                TransitionType.VERIFICATION_ADDED,
                candidate,
                authorization_reference="authorization-missing",
            ),
        )
    with pytest.raises(ValueError, match="precede"):
        planner.plan(
            current,
            request(
                TransitionType.VERIFICATION_ADDED,
                candidate,
                requested_at=NOW - timedelta(seconds=1),
            ),
        )
    with pytest.raises(ValueError, match="snapshot version"):
        planner.plan(
            current,
            request(
                TransitionType.VERIFICATION_ADDED,
                candidate,
                expected_snapshot_version=2,
            ),
        )


def test_unbound_runtime_contains_no_person_or_memory_data():
    state = GuardianRuntimeSnapshot.unbound(NOW)

    assert state.active_guardian_id is None
    assert state.active_subject_id is None
    assert state.knowledge_items == ()
    assert state.memory == GuardianMemory()
    assert state.runtime_context_hash == state.calculate_hash()


def test_knowledge_manager_remains_the_guardian_knowledge_interface():
    manager = KnowledgeManager()
    record = item()

    assert manager.validate_guardian_knowledge(record) is record
    assert manager.unbound_guardian_runtime(NOW) == (
        GuardianRuntimeSnapshot.unbound(NOW)
    )
    with pytest.raises(TypeError, match="KnowledgeItem"):
        manager.validate_guardian_knowledge("not knowledge")


def test_contract_loader_is_versioned_complete_and_deterministic():
    first = GuardianRuntimeContractLoader().load()
    second = GuardianRuntimeContractLoader().load()

    assert first == second
    assert first.version == "1.0"
    assert len(first.content_hash) == 64
    assert first.knowledge_types == tuple(KnowledgeType)
    assert first.retention_classes == tuple(RetentionClass)
    assert first.transition_types == tuple(TransitionType)


def test_contract_loader_rejects_incomplete_contract(tmp_path):
    source = tmp_path / "guardian-runtime.md"
    source.write_text(
        "# Guardian Runtime\n\nVersion: 1.0\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="incomplete"):
        GuardianRuntimeContractLoader(source).load()
