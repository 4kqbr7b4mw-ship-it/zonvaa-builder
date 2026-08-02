from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADR = ROOT / "knowledge" / "adr" / "ADR-0049-guardian-provider-authorization-v1.md"
STATUS = ROOT / "knowledge" / "project" / "current-product-status.md"


def normalized(path):
    return " ".join(path.read_text(encoding="utf-8").split())


def test_adr_documents_identity_grant_decision_and_lifecycle_evidence():
    content = normalized(ADR)
    for value in (
        "ProviderIdentity",
        "ProviderAuthorizationGrant",
        "AuthorizationDecisionEvidence",
        "Widerruf, Aussetzung, Ablauf und Wiederherstellung",
        "ProviderAuthorizationResolutionSnapshot",
    ):
        assert value in content


def test_adr_reuses_adr_0048_without_second_authority_hierarchy():
    content = normalized(ADR)
    assert "ausschließlich aus ADR-0048 wiederverwendet" in content
    assert "keine zweite Authority-, Capability- oder Kontrollhierarchie" in content
    assert "AuthorityDelegationRule" in content
    assert "ActorResponsibilityBoundary" in content


def test_adr_forbids_runtime_iam_selection_trust_and_automatic_status():
    content = normalized(ADR)
    for value in (
        "keine Runtime",
        "keine allgemeine IAM-, RBAC-",
        "wählt keinen Provider",
        "bewertet, priorisiert oder wählt keinen Provider",
        "keine zeitabhängige Statusberechnung",
        "keine automatische Autorisierung",
        "keine Persistenz",
    ):
        assert value in content


def test_product_status_records_non_executing_provider_authorization_package():
    content = normalized(STATUS)
    assert "Guardian Provider Authorization Package v1" in content
    assert "wählt keinen Provider" in content
    assert "aktiviert keine Capability" in content
    assert "keine Runtime" in content
