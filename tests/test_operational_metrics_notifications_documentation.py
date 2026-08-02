from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADR = ROOT / "knowledge" / "adr" / "ADR-0057-operational-metrics-notifications-v1.md"
PLANS = ROOT / "PLANS.md"
STATUS = ROOT / "knowledge" / "project" / "current-product-status.md"


def normalized(path):
    return " ".join(path.read_text(encoding="utf-8").split())


def test_adr_0057_defines_metrics_after_persistence_and_notifications_after_evidence():
    content = normalized(ADR)
    for value in (
        "Operational Metrics folgen physischer Persistenz, niemals umgekehrt",
        "Operational Notifications folgen einer validierten Metrik",
        "bereits bereitgestellten Wert",
        "erzeugt keine Nachricht und stellt nichts zu",
        "keine automatische Eskalation",
    ):
        assert value in content


def test_adr_0057_contains_absolute_user_and_delivery_boundaries():
    content = normalized(ADR)
    for value in (
        "Nutzerverhalten, Nutzeridentitäten, Nutzersegmente",
        "Gesprächsinhalte, Themen, Lebensbereiche",
        "Häufigkeiten pro Nutzer",
        "keine Nutzeranalyse, Nutzungsstatistik",
        "keine freie Text- oder Nachrichtengenerierung",
        "keine externe Zustellung",
        "keine UI",
    ):
        assert value in content


def test_operational_memory_block_is_complete_without_b2_or_b3_authorization():
    content = normalized(ADR)
    for value in (
        "Operational Memory v1",
        "Physical Operational Persistence v1",
        "Operational Metrics v1",
        "Operational Notifications v1",
        "Operational-Memory-Block` auf Vertragsebene vollständig geschlossen",
        "gibt weder B2 noch B3 frei",
        "lediglich eine gesonderte Architekturentscheidung",
    ):
        assert value in content


def test_project_plan_and_status_include_metrics_and_notifications():
    for content in (normalized(PLANS), normalized(STATUS)):
        assert "Operational Metrics" in content
        assert "Operational Notifications" in content
        assert "B2" in content and "B3" in content
