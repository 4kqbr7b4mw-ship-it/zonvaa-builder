from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_adr_0059_documents_the_constitutional_corridor_boundaries():
    text = (ROOT / "knowledge/adr/ADR-0059-guardian-b2-data-corridor-consent-boundary-v1.md").read_text()
    for phrase in (
        "Datenfluss ist die erste B2-Machtgrenze",
        "vor jeder Authority",
        "D1–D6",
        "notwendige, aber niemals hinreichende Voraussetzung",
        "AAV",
        "UODL",
        "GOV-SYSTEM-BEHAVIOR-ONLY-1",
        "blind gegenüber B2-Inhalten",
        "Keine Runtime",
    ):
        assert phrase in text


def test_project_documents_keep_all_later_b2_packages_blocked():
    for relative in (
        "PLANS.md",
        "knowledge/project/current-product-status.md",
        "governance/b2-readiness-statement.md",
    ):
        text = (ROOT / relative).read_text()
        assert "ADR-0059" in text
        assert "B2-Runtime" in text
        assert "GESPERRT" in text
