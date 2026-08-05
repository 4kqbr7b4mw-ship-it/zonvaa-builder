from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD = (
    ROOT
    / "governance/decisions/GOV-NO-FABRICATION-REFERENCE-CONSOLIDATION-APPROVAL-V1.md"
)


def content() -> str:
    return RECORD.read_text(encoding="utf-8")


def test_decision_identity_role_and_separate_times_are_explicit():
    text = content()
    normalized = " ".join(text.split())
    for marker in (
        "GOV-NO-FABRICATION-REFERENCE-CONSOLIDATION-APPROVAL-V1",
        "INSTITUTIONAL_IMPLEMENTATION_APPROVAL",
        "INSTITUTION_FOUNDER",
        "05.08.2026",
        "09:42 Uhr",
        "09:44:13 Uhr",
        "Europe/Berlin (CEST, UTC+02:00)",
        "gegenwärtig",
        "Rückwirkende Wirkung ist ausdrücklich ausgeschlossen",
    ):
        assert marker in normalized


def test_granted_scope_is_reference_only_and_closed():
    text = content()
    assert "## 2. Freigegebener Scope (`GRANTED_SCOPE`)" in text
    for marker in (
        "rein dokumentarische Referenzkonsolidierung",
        "Referenz-Mapping bereits bestehender Regelinhaber",
        "bestehenden jeweiligen Geltungsbereiche",
        "bereits vorhandener technischer Durchsetzung",
        "bewusst bestehender technischer Grenzen",
        "als ruhend und nicht materiell geregelt",
        "fokussierte Dokumentationstests",
        "ohne fachliche oder technische Machtwirkung",
    ):
        assert marker in text
    assert "Fehlende Nennung ist Nichtfreigabe" in text


def test_excluded_scope_prevents_new_rule_power_and_runtime():
    text = content()
    assert "## 3. Ausdrücklich ausgeschlossener Scope (`EXCLUDED_SCOPE`)" in text
    for marker in (
        "neue materielle Governance-Regel",
        "Aktivierung von `GOV-NO-FABRICATION-1`",
        "neuer Normtext oder neue Governance-Taxonomie",
        "neue Klassen, Enums, Validatoren, Evaluatoren oder Services",
        "Änderung bestehender ADRs",
        "neue Prioritäts- oder Vorrangregeln",
        "Aktivierung von Accountability & Explanation",
        "Runtime, Runtime Readiness oder Observation",
        "externe Wahrheitsprüfung oder ein Universalvalidator",
        "psychologische oder emotionale Zustandsableitung",
        "personenbezogene Verarbeitung",
        "ADR-0067",
        "Änderung, Anwendung oder Löschung des Recovery-Stash",
        "rückwirkende Legitimierung",
    ):
        assert marker in text


def test_scope_entries_are_machine_readable_and_disjoint():
    lines = content().splitlines()
    scope_lines = [
        line
        for line in lines
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


def test_separate_order_requires_commit_and_push_before_implementation_order():
    text = content()
    assert "separaten\nImplementierungsauftrag" in text
    assert "erst nach eigenem Commit und\nnachweisbarem Push" in text
    assert "keine Stufe impliziert die nächste" in " ".join(text.split())
    assert "keine Referenzkonsolidierung" in text
    assert "keine neue Governance-Regel" in text
