from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / "governance/governance-decision-incident-evidence-proposal.md"
MANIFEST = ROOT / "governance/b2-constitutional-gap-closure-package-manifest.md"


def read(path):
    return path.read_text(encoding="utf-8")


def test_governance_evidence_proposal_is_non_binding_and_unimplemented():
    text = read(PROPOSAL)
    assert "VORGESCHLAGEN – NICHT RATIFIZIERT" in text
    assert "NICHT IMPLEMENTIERUNGSFREIGEGEBEN – NICHT IMPLEMENTIERT" in text
    assert "Prüffrage Null" in text
    assert "Antwort: **Nein.**" in text
    assert "formalen Vorschlag ADR-0064" in text


def test_adr_0059_evidence_status_is_exact_and_unknowns_stay_unknown():
    text = " ".join(read(PROPOSAL).split())
    for phrase in (
        "Klassifikation: **3. nur indirekte Governance-Evidenz vorhanden.**",
        "kein eigenständiges `ratification-adr-0059`-Dokument",
        "Datum, Uhrzeit, Zeitzone und Entscheidungsrolle",
        "**UNBEKANNT**",
        "nicht rückdatiert",
        "nicht in einen früheren oder getrennten",
        "Ratifikationsbeschluss umgedeutet",
    ):
        assert phrase in text


def test_governance_incident_evidence_has_no_person_or_power_effect():
    text = read(PROPOSAL)
    for phrase in (
        "keine natürliche Person als Schuldige",
        "keine Profile",
        "Sanktionen",
        "Sperren",
        "Autorisierung",
        "Runtime-Wirkung",
        "automatische Governance-Entscheidung",
        "Provenienz ersetzt keine fehlende Evidenz",
        "legitimiert nichts rückwirkend",
    ):
        assert phrase in text


def test_decision_and_documentation_times_are_separate():
    text = read(PROPOSAL)
    assert "externen Beschlusszeitpunkt und Zeitpunkt der" in text
    assert "Repository-Dokumentation getrennt" in text
    assert "Erfassungszeitpunkt darf ihn nicht ersetzen" in text


def test_package_b_status_references_are_separate_and_non_binding():
    readiness = read(ROOT / "governance/b2-readiness-statement.md")
    status = read(ROOT / "knowledge/project/current-product-status.md")
    plans = read(ROOT / "PLANS.md")
    for text in (readiness, status, plans):
        assert "ADR-0064" in text
        assert "nicht ratifiziert" in text.lower()


def test_manifest_assigns_package_b_and_excludes_current_adr_0059_decision():
    text = " ".join(read(MANIFEST).split())
    assert "## Paket B – Governance Decision and Incident Evidence Constitution" in text
    assert "Document governance decision incident architecture" in text
    assert "drittes, ausschließlich menschlich initiiertes Governance-Paket" in text
    assert "weder gefasst noch dokumentiert" in text


def test_no_governance_incident_implementation_module_was_added():
    assert not list((ROOT / "governance").glob("*governance*incident*.py"))
