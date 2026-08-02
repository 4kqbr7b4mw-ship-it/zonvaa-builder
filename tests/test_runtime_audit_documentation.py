from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADR = ROOT / "knowledge" / "adr" / "ADR-0054-runtime-audit-architecture-v1.md"
PLANS = ROOT / "PLANS.md"
STATUS = ROOT / "knowledge" / "project" / "current-product-status.md"


def normalized(path):
    return " ".join(path.read_text(encoding="utf-8").split())


def test_adr_0054_separates_audit_observation_evidence_and_incident():
    content = normalized(ADR)
    for value in (
        "Audit ist Nachweisprüfung, keine Runtime-Ausführung",
        "von Observation, Runtime Evidence und Incident Evidence getrennt",
        "Fehlende Evidence ist kein No-Incident-Nachweis",
        "Nicht beobachtete Bereiche bleiben ausdrücklich nicht beurteilbar",
        "ausschließlich Systemverhalten, niemals Nutzerverhalten",
    ):
        assert value in content


def test_adr_0054_documents_scope_binding_profiles_and_no_power():
    content = normalized(ADR)
    for value in (
        "No-Incident Evidence ohne diese Observation-Scope-Bindung ist ungültig",
        "versioniert und begründungspflichtig",
        "Runtime-, Modell-, Provider- und Tool-Akteure",
        "keine Persistenz",
        "keine Metriken",
        "Benachrichtigungen",
        "keine Nutzeranalyse",
        "keine automatische Audit-, Incident- oder No-Incident-Erzeugung",
    ):
        assert value in content


def test_adr_0054_and_status_contain_b2_b3_operational_gate():
    for content in (normalized(ADR), normalized(STATUS)):
        assert "B2" in content and "B3" in content
        assert "Operational-Memory-Block" in content
        assert "ratifiziert" in content
        assert "implementiert" in content
        assert "validiert" in content
    assert "Runtime Audit Architecture v1" in normalized(PLANS)
