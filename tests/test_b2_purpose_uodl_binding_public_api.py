import governance


PUBLIC_NAMES = (
    "B2_PURPOSE_UODL_BINDING_CONTRACT_VERSION",
    "B2BindingEvaluationOutcome",
    "B2BindingObservationScope",
    "B2BindingProvenance",
    "B2CorridorPurposeReference",
    "B2PurposeBinding",
    "B2PurposeBindingEvidence",
    "B2PurposeBindingId",
    "B2PurposeBindingRule",
    "B2PurposeBindingValidator",
    "B2PurposeComparisonRelation",
    "B2PurposeUODLBindingFoundation",
    "B2PurposeUODLBindingFoundationValidator",
    "B2PurposeUODLBindingValidationError",
    "B2UODLLayerRelation",
    "B2UODLMapping",
    "B2UODLMappingEvidence",
    "B2UODLMappingId",
    "B2UODLMappingValidator",
    "B2UODLPairRule",
)


def test_adr_0063_public_api_is_complete_and_stable():
    for name in PUBLIC_NAMES:
        assert name in governance.__all__
        value = getattr(governance, name)
        assert name == "B2_PURPOSE_UODL_BINDING_CONTRACT_VERSION" or (
            value.__module__ == "governance.b2_purpose_uodl_binding"
        )


def test_internal_helpers_are_not_exported():
    assert "_reference" not in governance.__all__
    assert "_invalid" not in governance.__all__
