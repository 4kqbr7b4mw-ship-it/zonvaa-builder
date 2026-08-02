import governance


def test_guardian_provider_authorization_public_api_is_complete():
    expected = (
        "AuthorizationDecisionEvidence",
        "AuthorizationDecisionType",
        "AuthorizationExpirationEvidence",
        "AuthorizationRestorationEvidence",
        "AuthorizationRevocationEvidence",
        "AuthorizationSuspensionEvidence",
        "AuthorizationUncertaintyStatus",
        "DecidingActorReference",
        "GuardianProviderAuthorizationPackage",
        "GuardianProviderAuthorizationValidator",
        "ProviderAuthorizationGrant",
        "ProviderAuthorizationPackageCapability",
        "ProviderAuthorizationResolutionSnapshot",
        "ProviderAuthorizationStatus",
        "ProviderAuthorizationValidationError",
        "ProviderIdentity",
        "ProviderIdentityVerificationStatus",
        "ProviderType",
    )
    for name in expected:
        assert name in governance.__all__
        assert getattr(governance, name) is not None
