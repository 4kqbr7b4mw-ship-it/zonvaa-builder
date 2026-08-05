from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD = (
    ROOT
    / "governance/decisions/GOV-B2-NORMATIVE-STATUS-CONSOLIDATION-APPROVAL-V1.md"
)


def content() -> str:
    return RECORD.read_text(encoding="utf-8")


def test_decision_identity_class_role_and_times_are_explicit():
    text = content()
    normalized = " ".join(text.split())
    for marker in (
        "GOV-B2-NORMATIVE-STATUS-CONSOLIDATION-APPROVAL-V1",
        "INSTITUTIONAL_IMPLEMENTATION_APPROVAL",
        "INSTITUTION_FOUNDER",
        "04.08.2026",
        "23:35 Uhr",
        "23:36:50 Uhr",
        "Europe/Berlin (CEST, UTC+02:00)",
        "gegenwärtig",
        "Rückwirkende Wirkung ist ausdrücklich ausgeschlossen",
    ):
        assert marker in normalized


def test_granted_and_excluded_scopes_are_separate_and_closed():
    text = content()
    assert "## 2. Freigegebener Scope (`GRANTED_SCOPE`)" in text
    assert "## 3. Ausdrücklich ausgeschlossener Scope (`EXCLUDED_SCOPE`)" in text
    for marker in (
        "Korrektur objektiv überholter oder widersprüchlicher Statusangaben",
        "historischem Entscheidungsstand",
        "aktuellem normativem Status",
        "Implementierungs-, Validierungs- und Repository-Evidenz",
        "Erhaltung sämtlicher historischer Entscheidungen",
        "fokussierte Dokumentationstests",
        "eigentliche ADR-Konsolidierung in diesem Auftrag",
        "Änderungen produktiver B2-Module",
        "Änderung oder Entfernung des freien Corridor-Purpose-Feldes",
        "Umbenennung von `B2CapabilityInvocationObservationScope`",
    ):
        assert marker in text
    assert "Fehlende Nennung ist Nichtfreigabe" in text
    scope_lines = [
        line for line in text.splitlines() if line.startswith("- `GRANTED_SCOPE`") or line.startswith("- `EXCLUDED_SCOPE`")
    ]
    assert scope_lines
    assert all("kanonische Artefaktreferenz" in line and "Abschnitt `" in line for line in scope_lines)


def test_record_has_no_retroactive_or_technical_effect():
    text = content()
    for marker in (
        "keine fachliche oder technische Machtwirkung",
        "Runtime, Runtime Readiness",
        "Provider-, Tool-, API-, MCP- oder Agent-Aufrufe",
        "Observation oder personenbezogene Verarbeitung",
        "legitimiert, heilt, überschreibt oder deutet keine historische Vorstufe",
        "keine Konsolidierung, kein Commit, kein Push",
    ):
        assert marker in text


def test_separate_order_requires_commit_and_push_first():
    text = content()
    assert "separaten Implementierungsauftrag" in text
    assert "erst nach eigenem Commit und nachweisbarem Push" in text
    assert "keine Stufe impliziert die\nnächste" in text
