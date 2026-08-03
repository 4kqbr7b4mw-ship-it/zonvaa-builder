from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def test_product_status_documents_the_implemented_non_executing_scope():
    text = read("knowledge/project/current-product-status.md")
    for phrase in (
        "eigenständige immutable B2-Typfamilie",
        "zustandslose Evaluation",
        "Negative Governance Evidence",
        "D3 ist notwendig, aber niemals hinreichend",
        "B2-Runtime und alle späteren B2-Machtstufen bleiben gesperrt",
    ):
        assert phrase in text


def test_plan_keeps_provider_runtime_and_personal_processing_outside_scope():
    text = read("PLANS.md")
    for phrase in (
        "Provider, Invocation",
        "Runtime, Persistenz, Sessions, Caches",
        "personenbezogene Verarbeitung",
        "nicht Bestandteil des Pakets",
    ):
        assert phrase in text


def test_ratification_and_approval_documents_remain_canonical_and_bounded():
    adr = read("knowledge/adr/ADR-0060-guardian-b2-authority-authorization-v1.md")
    approval = read("governance/institutional-implementation-approval-adr-0060.md")
    assert "RATIFIZIERT – IMPLEMENTIERUNG BEGRENZT FREIGEGEBEN" in adr
    assert "INSTITUTIONELLE IMPLEMENTIERUNGSFREIGABE – GÜLTIG" in approval
    assert "B2 Capability Invocation und B2 Runtime" in approval
    assert "jede technische Ausführung eines B2 Grants" in approval
