from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / "governance/b2-purpose-uodl-constitution-proposal.md"
MANIFEST = ROOT / "governance/b2-constitutional-gap-closure-package-manifest.md"


def read(path):
    return path.read_text(encoding="utf-8")


def test_purpose_uodl_proposal_is_non_binding_and_does_not_start_adr_0063():
    text = read(PROPOSAL)
    assert "VORGESCHLAGEN – NICHT RATIFIZIERT" in text
    assert "NICHT IMPLEMENTIERUNGSFREIGEGEBEN – NICHT IMPLEMENTIERT" in text
    assert "Prüffrage Null" in text
    assert "Antwort: **Nein.**" in text
    assert "ADR-0063 wurde nicht begonnen" in text
    assert not list((ROOT / "knowledge/adr").glob("ADR-0063*"))


def test_purpose_proposal_keeps_one_typed_truth_and_forbids_expansion():
    text = " ".join(read(PROPOSAL).split())
    for phrase in (
        "## Teil A – Purpose Binding Constitution",
        "### Varianten",
        "Vorgeschlagen ist Variante 4",
        "B2PurposeScope` aus ADR-0060 bleibt die",
        "einzige kanonische fachliche Purpose-Verfassung",
        "keine zweite Purpose-Liste",
        "gleichen oder engeren Scope",
        "keine Purpose-Eskalation",
        "keine Konvertierungslogik",
    ):
        assert phrase in text


def test_uodl_proposal_requires_explicit_mapping_without_name_equivalence():
    text = read(PROPOSAL)
    for phrase in (
        "## Teil B – UODL Reference Constitution",
        "StorageOperation.REFERENCE",
        "B2UODLOperation.REFERENCE_ONLY",
        "Namensähnlichkeit beweist weder Identität noch Halbordnung",
        "explizites immutable Mapping",
        "keine String-Konvertierung",
        "weder Inhaltszugriff noch Kopie, Schreiben, Speicherung",
    ):
        assert phrase in text


def test_package_a_status_references_are_separate_and_non_binding():
    readiness = read(ROOT / "governance/b2-readiness-statement.md")
    status = read(ROOT / "knowledge/project/current-product-status.md")
    plans = read(ROOT / "PLANS.md")
    for text in (readiness, status, plans):
        assert "B2 Purpose and UODL Constitution Proposal" in text
        assert "nicht ratifiziert" in text.lower()


def test_manifest_assigns_package_a_and_requires_selective_staging():
    text = read(MANIFEST)
    assert "## Paket A – B2 Purpose and UODL Constitution Proposal" in text
    assert "Propose B2 purpose and UODL constitution" in text
    assert "selektives Hunk- beziehungsweise Abschnitts-Staging" in text


def test_no_purpose_uodl_or_b2_execution_module_was_added():
    governance = ROOT / "governance"
    forbidden_patterns = (
        "*purpose*mapping*.py",
        "*uodl*mapping*.py",
        "*b2*capability*invocation*.py",
        "*b2*runtime*.py",
    )
    assert not [
        path
        for pattern in forbidden_patterns
        for path in governance.glob(pattern)
    ]
