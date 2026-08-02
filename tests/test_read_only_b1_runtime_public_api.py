import governance


def test_read_only_b1_runtime_public_api_is_complete():
    expected = (
        "B1ReadOnlyProviderAdapter",
        "B1ReadOnlyRuntimeExecutor",
        "B1RuntimeExecutionEnvelope",
        "B1RuntimeExecutionOutcome",
        "B1RuntimeExecutionRequest",
        "B1RuntimeExecutionRequestValidator",
        "B1RuntimeOutputValidator",
        "B1RuntimeResult",
        "B1RuntimeValidationError",
        "ProviderAdapterRequest",
        "ProviderAdapterResult",
        "ProviderOutputKind",
        "ProviderTechnicalStatus",
        "RuntimeBlockReason",
        "RuntimeCheck",
        "RuntimeDataField",
        "RuntimeExecutionEvidence",
        "RuntimeExecutionReceipt",
        "RuntimeExecutionStatus",
        "RuntimeOutputContract",
        "RuntimeProvisionStatus",
        "RuntimeRecordMetadata",
    )
    for name in expected:
        assert name in governance.__all__
        assert getattr(governance, name) is not None
