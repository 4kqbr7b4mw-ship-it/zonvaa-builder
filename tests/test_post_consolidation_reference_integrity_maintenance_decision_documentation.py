from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD = (
    ROOT
    / "governance/decisions/GOV-POST-CONSOLIDATION-REFERENCE-INTEGRITY-MAINTENANCE-APPROVAL-V1.md"
)


def content() -> str:
    return RECORD.read_text(encoding="utf-8")


def test_decision_identity_role_and_separate_times_are_explicit():
    text = " ".join(content().split())
    for marker in (
        "GOV-POST-CONSOLIDATION-REFERENCE-INTEGRITY-MAINTENANCE-APPROVAL-V1",
        "INSTITUTIONAL_IMPLEMENTATION_APPROVAL",
        "INSTITUTION_FOUNDER",
        "05.08.2026",
        "15:28 Uhr",
        "15:31:58 Uhr",
        "Europe/Berlin (CEST, UTC+02:00)",
        "gegenwärtig",
        "Rückwirkende Wirkung ist ausdrücklich ausgeschlossen",
    ):
        assert marker in text


def test_all_review_findings_are_the_only_approved_maintenance_subjects():
    text = content()
    for finding in ("G-01", "G-02", "G-03", "D-01", "D-02", "D-03"):
        assert finding in text
    for marker in (
        "eindeutige Trennung des offenen Kandidaten",
        "tatsächlich realisierten Repository-Artefakten",
        "historischen ADR-0066-Gate-Zustands",
        "falschen ADR-0059-Dateipfads",
        "Inventars ruhender Kandidaten",
        "fokussierte Dokumentationstests",
        "ohne fachliche oder technische Machtwirkung",
    ):
        assert marker in text
    assert "Fehlende Nennung ist Nichtfreigabe" in text


def test_excluded_scope_preserves_history_and_blocks_power_expansion():
    text = content()
    for marker in (
        "Durchführung der eigentlichen Referenzintegritätskorrekturen",
        "neue Architektur, Governance-Regel, materielle Norm oder Taxonomie",
        "rückwirkende Umbenennung vorhandener Dokument-IDs",
        "rückwirkende Änderung des ursprünglichen Beschlusses",
        "Ersetzung oder Löschung historischer Scope-Referenzen",
        "rückwirkende Legitimierung historischer Prozesszustände",
        "Änderung bestehender Vertragssemantik oder produktiver Module",
        "neue Prioritäts- oder Vorrangregeln",
        "Aktivierung als geltende Regel",
        "Runtime, Runtime Readiness oder Observation",
        "personenbezogene Verarbeitung",
        "ADR-0067",
        "Erstellung historischer Commit- oder Push-Decision-Records",
        "Änderung, Anwendung oder Löschung des Recovery-Stash",
    ):
        assert marker in text


def test_scope_entries_are_machine_readable_and_disjoint():
    scope_lines = [
        line
        for line in content().splitlines()
        if line.startswith("- `GRANTED_SCOPE`")
        or line.startswith("- `EXCLUDED_SCOPE`")
    ]
    assert scope_lines
    assert all(
        "kanonische Artefaktreferenz" in line and "Abschnitt `" in line
        for line in scope_lines
    )
    granted = {
        tuple(line.split(" — ")[1:]) for line in scope_lines if "GRANTED" in line
    }
    excluded = {
        tuple(line.split(" — ")[1:]) for line in scope_lines if "EXCLUDED" in line
    }
    assert granted.isdisjoint(excluded)


def test_record_does_not_preempt_maintenance_or_change_existing_decisions():
    text = " ".join(content().split())
    assert "Dieser Beschluss führt die Maintenance nicht aus" in text
    assert "Der ursprüngliche Inhalt bestehender Decisions" in text
    assert "bleibt unverändert erhalten" in text
    assert "erst nach eigenem Commit und nachweisbarem Push" in text
    assert "separaten Implementierungsauftrag" in text
    assert "keine Stufe impliziert die nächste" in text


def test_existing_decisions_and_maintenance_targets_remain_unchanged_by_record():
    expected = {
        "GOV-B2-NORMATIVE-STATUS-CONSOLIDATION-APPROVAL-V1.md",
        "GOV-NO-FABRICATION-REFERENCE-CONSOLIDATION-APPROVAL-V1.md",
        "GOV-POST-CONSOLIDATION-REFERENCE-INTEGRITY-MAINTENANCE-APPROVAL-V1.md",
        "README.md",
    }
    assert {path.name for path in (ROOT / "governance/decisions").iterdir()} == expected
    for path in (
        ROOT / "governance/b2-constitution-v1.0-completion-report.md",
        ROOT / "governance/no-fabrication-reference-consolidation.md",
        ROOT / "governance/institutional-approval-process.md",
    ):
        assert path.is_file()
