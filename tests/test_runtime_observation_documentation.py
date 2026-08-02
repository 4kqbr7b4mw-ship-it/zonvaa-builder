from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADR = ROOT / "knowledge" / "adr" / "ADR-0053-runtime-observation-governance-v1.md"
PLANS = ROOT / "PLANS.md"
STATUS = ROOT / "knowledge" / "project" / "current-product-status.md"


def normalized(path):
    return " ".join(path.read_text(encoding="utf-8").split())


def test_adr_0053_defines_observation_as_governance_only():
    content = normalized(ADR)
    for value in (
        "Runtime Observation Governance v1",
        "ausschließlich beschreibende Governance-Schicht",
        "versioniert",
        "begründungspflichtig",
        "Observation Profiles dürfen nicht einseitig durch die Runtime geändert",
        "beobachtet selbst nichts",
    ):
        assert value in content


def test_adr_0053_separates_observation_evidence_incident_and_users():
    content = normalized(ADR)
    for value in (
        "Trennung von Observation, Evidence und Incident",
        "Observation erzeugt weder Evidence noch Incident",
        "ausschließlich Systemverhalten",
        "niemals Nutzerverhalten",
        "keine Profilbildung",
        "Verhaltensanalyse",
        "Nutzungsstatistik",
        "Telemetrie",
    ):
        assert value in content


def test_adr_0053_documents_complete_non_goals():
    content = normalized(ADR)
    for value in (
        "keine Runtime-Erweiterung",
        "Incident-Erkennung",
        "Evidence-Erzeugung",
        "Audit-Infrastruktur",
        "Persistenz",
        "Metriken",
        "Benachrichtigungen",
        "Workflow-, Werkzeug- oder Capability-Aktivierung",
        "Zustandsänderung",
        "UI",
    ):
        assert value in content


def test_plan_and_status_record_runtime_observation_governance_v1():
    for content in (normalized(PLANS), normalized(STATUS)):
        assert "Runtime Observation Governance v1" in content
        assert "keine Nutzerbeobachtung" in content
        assert "keine Observation Runtime" in content
