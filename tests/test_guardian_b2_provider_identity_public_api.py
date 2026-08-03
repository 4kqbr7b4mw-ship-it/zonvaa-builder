import governance


def test_guardian_b2_provider_identity_public_api_is_exposed():
    expected = (
        "B2ProviderIdentity",
        "B2ProviderIdentityId",
        "B2ProviderClass",
        "B2ResponsibilityArea",
        "B2CapabilityDescriptor",
        "B2ProviderProvenance",
        "B2InstitutionalSourceId",
        "B2GovernanceDecisionId",
        "B2RegistrationBasisReference",
        "B2NonPersonalReferenceId",
    )
    for name in expected:
        assert hasattr(governance, name)
        assert name in governance.__all__
