import governance


def test_guardian_authority_public_api_is_complete():
    expected = (
        "ActorResponsibilityBoundary",
        "AuthorityActorClass",
        "AuthorityCapability",
        "AuthorityControlLevel",
        "AuthorityDefinition",
        "AuthorityDelegationRule",
        "AuthorityExercise",
        "AuthorityModelCapability",
        "AuthorityProvenance",
        "AuthorityReviewStatus",
        "AuthorityType",
        "GuardianAuthorityModel",
        "GuardianAuthorityModelValidator",
        "GuardianAuthorityValidationError",
        "ProhibitedAuthorityCombination",
    )

    for name in expected:
        assert name in governance.__all__
        assert getattr(governance, name) is not None
