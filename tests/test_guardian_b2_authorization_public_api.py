import governance


def test_guardian_b2_authorization_public_api_is_exposed():
    expected = (
        "B2Authority",
        "B2AuthorityClass",
        "B2AuthorityId",
        "B2Grant",
        "B2PurposeScope",
        "B2D3Consent",
        "B2T4GrantReceipt",
        "B2AAVBinding",
        "B2UODLBinding",
        "B2AuthorizationEvaluator",
        "B2AuthorizationEvaluationEvidence",
        "B2NegativeGovernanceEvidence",
        "B2AuthorizationDecision",
        "B2AuthorizationReason",
        "B2AuthorizationStructureError",
    )
    for name in expected:
        assert hasattr(governance, name)
        assert name in governance.__all__
