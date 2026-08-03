import governance


def test_guardian_b2_provider_authorization_public_api_is_exposed():
    expected = (
        "B2ProviderAuthorization",
        "B2ProviderAuthorizationId",
        "B2ProviderAuthorizationProvenance",
        "B2ProviderAuthorizationEvaluator",
        "B2ProviderAuthorizationValidator",
        "B2ProviderAuthorizationEvaluationEvidence",
        "B2ProviderAuthorizationNegativeGovernanceEvidence",
        "B2ProviderAuthorizationReason",
        "B2ProviderAuthorizationValidationError",
        "B2AuthorizationFoundation",
        "B2AuthorizationFoundationValidator",
    )
    for name in expected:
        assert hasattr(governance, name)
        assert name in governance.__all__


def test_public_api_exposes_no_runtime_invocation_or_execution_adapter():
    forbidden = (
        "B2ProviderAuthorizationRuntime",
        "B2ProviderAuthorizationInvoker",
        "B2ProviderAuthorizationAdapter",
        "B2ProviderAuthorizationSession",
        "B2ProviderAuthorizationToken",
    )
    for name in forbidden:
        assert not hasattr(governance, name)
        assert name not in governance.__all__
