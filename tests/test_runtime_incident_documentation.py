from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADR = ROOT / "knowledge" / "adr" / "ADR-0052-runtime-incident-evidence-v1.md"
STATUS = ROOT / "knowledge" / "project" / "current-product-status.md"
PLANS = ROOT / "PLANS.md"


def normalized(path):
    return " ".join(path.read_text(encoding="utf-8").split())


def test_adr_0052_documents_incident_no_incident_and_snapshot_contracts():
    content = normalized(ADR)
    for value in (
        "RuntimeIncidentEvidence",
        "RuntimeNoIncidentEvidence",
        "RuntimeIncidentPackage",
        "RuntimeIncidentSnapshot",
        "Provider-Referenz",
        "Severity",
        "Reviewstatus",
        "Provenienz",
        "weder Qualitätsurteil noch Garantie",
    ):
        assert value in content


def test_adr_0052_documents_e6_and_non_reactive_power_boundary():
    content = normalized(ADR)
    for value in (
        "ADR-0046 E6",
        "keine Runtime-Erweiterung",
        "automatische Incident- oder Gefahrenerkennung",
        "Retry- oder Fallback-Logik",
        "Persistenz",
        "Audit-System",
        "Metriken",
        "Benachrichtigungen",
        "Workflow-, Werkzeug- oder Capability-Aktivierung",
        "keine Reaktion",
    ):
        assert value in content


def test_plan_and_product_status_record_runtime_incident_evidence_v1():
    for content in (normalized(PLANS), normalized(STATUS)):
        assert "Runtime Incident Evidence v1" in content
        assert "keine automatische Incident-Erkennung" in content
        assert "No-Incident" in content
