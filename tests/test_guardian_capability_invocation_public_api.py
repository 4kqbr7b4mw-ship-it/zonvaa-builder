import governance


def test_guardian_capability_invocation_public_api_is_complete():
    expected = (
        "ALLOWED_INVOCATION_OPERATION_MODES",
        "NON_EXECUTING_INVOCATION_CAPABILITIES",
        "REQUIRED_INVOCATION_CHECKS",
        "CapabilityInvocationDecision",
        "CapabilityInvocationEvidence",
        "CapabilityInvocationPackageCapability",
        "CapabilityInvocationReceipt",
        "CapabilityInvocationRequest",
        "CapabilityInvocationResolutionSnapshot",
        "CapabilityInvocationValidationError",
        "GuardianCapabilityInvocationBoundary",
        "GuardianCapabilityInvocationValidator",
        "InvocationCheck",
        "InvocationContextBinding",
        "InvocationContextBindingType",
        "InvocationDataScope",
        "InvocationDecisionReason",
        "InvocationDecisionStatus",
        "InvocationOperationMode",
        "InvocationReceiptValidationStatus",
    )
    for name in expected:
        assert name in governance.__all__
        assert getattr(governance, name) is not None
