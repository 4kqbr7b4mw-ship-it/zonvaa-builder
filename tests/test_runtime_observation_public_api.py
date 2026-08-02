import governance


def test_runtime_observation_governance_public_api_is_complete():
    expected = (
        "GOVERNANCE_PROFILE_ACTORS",
        "ObservationProfileApprovalStatus",
        "ObservationSnapshotStatus",
        "PROHIBITED_USER_OBSERVATION_CATEGORIES",
        "RUNTIME_EVENT_CATEGORIES",
        "RuntimeObservationCategory",
        "RuntimeObservationEvent",
        "RuntimeObservationGovernance",
        "RuntimeObservationGovernanceValidationError",
        "RuntimeObservationGovernanceValidator",
        "RuntimeObservationProfile",
        "RuntimeObservationScope",
        "RuntimeObservationSnapshot",
        "SYSTEM_OBSERVATION_CATEGORIES",
    )
    for name in expected:
        assert name in governance.__all__
        assert getattr(governance, name) is not None
