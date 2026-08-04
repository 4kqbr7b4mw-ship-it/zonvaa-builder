import governance


PUBLIC_NAMES = (
    "GOVERNANCE_DECISION_INCIDENT_CONTRACT_VERSION",
    "GOVERNANCE_DECISION_RECORD_DIRECTORY",
    "GOVERNANCE_INCIDENT_EVIDENCE_DIRECTORY",
    "GovernanceCanonicalArtifactReference",
    "GovernanceCorrectionAction",
    "GovernanceCorrectionStep",
    "GovernanceCorrectionStepState",
    "GovernanceCustodyReferenceValidator",
    "GovernanceDecisionClass",
    "GovernanceDecisionId",
    "GovernanceDecisionRecord",
    "GovernanceDecisionRecordValidator",
    "GovernanceDeviationCode",
    "GovernanceDocumentationState",
    "GovernanceEvidencePrimitiveValidator",
    "GovernanceEvidenceReference",
    "GovernanceEvidenceType",
    "GovernanceEvidenceValidator",
    "GovernanceHistoricalTimeState",
    "GovernanceImpactCode",
    "GovernanceIncidentClass",
    "GovernanceIncidentEvidence",
    "GovernanceIncidentEvidenceValidator",
    "GovernanceIncidentClassificationValidator",
    "GovernanceIncidentId",
    "GovernanceInstitutionalRole",
    "GovernanceKnownTime",
    "GovernanceOpenDecisionQuestion",
    "GovernanceOpenDecisionQuestionValidator",
    "GovernanceOpenQuestionClass",
    "GovernanceProvenance",
    "GovernanceProvenanceArtifactClass",
    "GovernanceProvenanceContext",
    "GovernanceProvenanceId",
    "GovernanceProvenanceValidator",
    "GovernanceRoleDecisionValidator",
    "GovernanceScopeEntry",
    "GovernanceScopeType",
    "GovernanceScopeValidator",
    "GovernanceSectionReference",
    "GovernanceStatementScope",
    "GovernanceStep",
    "GovernanceStepSequenceValidator",
    "GovernanceSubjectReference",
    "GovernanceTimeValidator",
    "MissingGovernanceEvidence",
    "MissingGovernanceEvidenceStatus",
    "MissingGovernanceEvidenceType",
    "MissingGovernanceEvidenceValidator",
)


def test_complete_adr_0064_a1_api_has_stable_exports():
    for name in PUBLIC_NAMES:
        assert name in governance.__all__
        assert getattr(governance, name) is not None


def test_internal_matrices_and_helpers_are_not_public():
    for name in ("_reference", "_aware", "_DECISION_ROLE_MATRIX", "_INCIDENT_DEVIATION_MATRIX"):
        assert name not in governance.__all__


def test_existing_public_exports_remain_available():
    assert governance.B2PurposeScope is not None
    assert governance.B2ProviderIdentity is not None
    assert governance.RuntimeIncidentEvidence is not None
