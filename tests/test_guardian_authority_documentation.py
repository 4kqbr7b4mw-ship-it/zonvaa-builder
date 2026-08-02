from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADR = ROOT / "knowledge" / "adr" / "ADR-0048-guardian-authority-model-v1.md"
STATUS = ROOT / "knowledge" / "project" / "current-product-status.md"


def normalized(path):
    return " ".join(path.read_text(encoding="utf-8").split())


def test_adr_documents_purpose_contract_and_structural_validator():
    content = normalized(ADR)
    assert "Guardian Authority Model v1" in content
    assert "immutable" in content
    assert "AuthorityDefinition" in content
    assert "ActorResponsibilityBoundary" in content
    assert "AuthorityDelegationRule" in content
    assert "ProhibitedAuthorityCombination" in content
    assert "dasselbe unveränderte Modellobjekt" in content


def test_adr_separates_provider_authorization_runtime_llm_and_tools():
    content = normalized(ADR)
    assert "Provider-Autorisierung" in content
    assert "keine Provider-Autorisierung" in content
    assert "keine Runtime" in content
    assert "klassifiziert keine Anfrage" in content
    assert "integriert kein LLM" in content
    assert "aktiviert Werkzeug" in content


def test_adr_documents_no_execution_or_state_power():
    content = normalized(ADR)
    for boundary in (
        "keine Antwortgenerierung",
        "keine Workflow-",
        "keine Zustandsänderung",
        "keine Persistenz",
        "keine UI",
    ):
        assert boundary in content


def test_product_status_records_authority_model_without_provider_power():
    content = normalized(STATUS)
    assert "Guardian Authority Model v1" in content
    assert "autorisiert weder konkrete Provider noch Personen" in content
    assert "keine Runtime" in content
