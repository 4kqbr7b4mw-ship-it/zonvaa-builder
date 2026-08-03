from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def test_product_status_documents_the_implemented_non_executing_identity():
    text = " ".join(read("knowledge/project/current-product-status.md").split())
    for phrase in (
        "Guardian B2 Provider Identity v1 ist implementiert",
        "geschlossenen Provider Classes",
        "keine Autorisierungs-, Invocation- oder Runtime-Wirkung",
        "keine natürliche Person",
        "B2-Runtime und alle späteren B2-Machtstufen bleiben gesperrt",
    ):
        assert phrase in text


def test_plan_documents_the_closed_implementation_scope():
    text = read("PLANS.md")
    for phrase in (
        "B2ProviderIdentity",
        "B2ProviderClass",
        "B2ResponsibilityArea",
        "B2CapabilityDescriptor",
        "B2ProviderProvenance",
        "Keine Provider Authorization, Invocation oder Runtime",
    ):
        assert phrase in text


def test_governance_and_approval_documents_are_not_changed_by_implementation():
    approval = read("governance/institutional-implementation-approval-adr-0061.md")
    adr = read("knowledge/adr/ADR-0061-guardian-b2-provider-identity-v1.md")
    assert "INSTITUTIONELLE IMPLEMENTIERUNGSFREIGABE – GÜLTIG" in approval
    assert "RATIFIZIERT – IMPLEMENTIERUNG BEGRENZT FREIGEGEBEN" in adr
    assert "B2 Provider Authorization" in approval
    assert "B2 Capability Invocation" in approval
    assert "B2 Runtime" in approval
