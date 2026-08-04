import importlib

import governance


PUBLIC = (
    "B2_CAPABILITY_INVOCATION_CONTRACT_VERSION",
    "B2CapabilityInvocationAssertion",
    "B2CapabilityInvocationBinding",
    "B2CapabilityInvocationBindingId",
    "B2CapabilityInvocationDecision",
    "B2CapabilityInvocationDecisionId",
    "B2CapabilityInvocationDecisionResult",
    "B2CapabilityInvocationEvaluator",
    "B2CapabilityInvocationEvidence",
    "B2CapabilityInvocationEvidenceId",
    "B2CapabilityInvocationFoundation",
    "B2CapabilityInvocationFoundationValidator",
    "B2CapabilityInvocationIntent",
    "B2CapabilityInvocationObservationScope",
    "B2CapabilityInvocationReceipt",
    "B2CapabilityInvocationReceiptId",
    "B2CapabilityInvocationRequest",
    "B2CapabilityInvocationRequestId",
    "B2CapabilityInvocationResolutionSnapshot",
    "B2CapabilityInvocationResolutionSnapshotId",
    "B2CapabilityInvocationValidationError",
    "B2CapabilityInvocationValidator",
    "B2CapabilityInvocationViolation",
)


def test_all_ratified_adr_0065_types_are_publicly_importable():
    module = importlib.import_module("governance.b2_capability_invocation")
    for name in PUBLIC:
        assert name in governance.__all__
        assert getattr(governance, name) is getattr(module, name)


def test_internal_helpers_and_b1_types_are_not_exported_as_b2_api():
    for name in (
        "_collect_violations",
        "_reference",
        "B2NegativeCapabilityInvocationEvidence",
        "CapabilityInvocationRequest",
    ):
        assert name not in PUBLIC


def test_existing_b2_public_exports_remain_stable():
    for name in (
        "B2AuthorizationFoundation",
        "B2ProviderIdentity",
        "B2PurposeUODLBindingFoundation",
        "GovernanceDecisionRecord",
    ):
        assert getattr(governance, name) is not None
