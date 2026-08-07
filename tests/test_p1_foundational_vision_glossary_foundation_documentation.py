from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "knowledge" / "project"


def _read(name: str) -> str:
    return (PROJECT / name).read_text(encoding="utf-8")


def test_p1_documents_live_in_existing_non_normative_product_location() -> None:
    names = {
        "p1-foundational-documentation-structure-proposal.md",
        "p1-canonical-glossary-governance-proposal.md",
        "p1-canonical-glossary-entry-and-prioritization-proposal.md",
        "p1-international-terminology-practices-assessment.md",
    }
    assert all((PROJECT / name).is_file() for name in names)
    assert not (ROOT / "knowledge" / "adr" / "ADR-0067-foundational-vision.md").exists()
    assert not (ROOT / "governance" / "canonical_glossary.py").exists()


def test_structure_proposal_preserves_architecture_and_runtime_boundaries() -> None:
    text = _read("p1-foundational-documentation-structure-proposal.md")
    normalized = " ".join(text.lower().split())
    for phrase in (
        "keine Vision",
        "kein Glossar",
        "keine Architektur",
        "ADR-0059 bis ADR-0066",
        "knowledge/project/",
        "keine Transition, Runtime Readiness",
        "Ruhende Kandidaten",
    ):
        assert phrase.lower() in normalized


def test_glossary_governance_is_only_a_proposal_without_technical_power() -> None:
    text = _read("p1-canonical-glossary-governance-proposal.md")
    normalized = " ".join(text.split())
    for phrase in (
        "KEINE GOVERNANCE-REGEL",
        "kein ADR",
        "keine Ontologie",
        "Keine Phase löst die nächste automatisch aus",
        "Identifier werden nie recycelt",
        "BCP-47",
        "Kein Registry-Service",
        "keine Observation",
    ):
        assert phrase in normalized


def test_entry_structure_does_not_define_or_canonize_terms() -> None:
    text = _read("p1-canonical-glossary-entry-and-prioritization-proposal.md")
    normalized = " ".join(text.split())
    assert "KEINE BEGRIFFSDEFINITIONEN" in text
    assert "KEINE KANONISIERUNG" in text
    assert "Es ist kein Glossarstatus" in text
    assert "Eine Priorisierung ist keine Freigabe" in normalized
    for adr in range(59, 67):
        assert f"ADR-00{adr}" in text


def test_international_assessment_is_informative_and_does_not_import_models() -> None:
    text = _read("p1-international-terminology-practices-assessment.md")
    for system in (
        "W3C SKOS",
        "IETF/RFC",
        "OMG",
        "ISO 704",
        "Dublin Core",
        "Schema.org",
        "Wikidata/Wikibase",
        "SNOMED CT",
        "ICD-11",
        "HL7 FHIR",
    ):
        assert system in text
    assert "KEINE ÜBERNAHME EINES MODELLS ODER EINER ONTOLOGIE" in text
    assert "Bewusst nicht übernommen" in text


def test_p1_adds_no_productive_or_governance_component() -> None:
    forbidden = (
        ROOT / "governance" / "canonical_glossary.py",
        ROOT / "governance" / "glossary.py",
        ROOT / "knowledge" / "canonical_glossary.py",
        ROOT / "knowledge" / "project" / "canonical_glossary.py",
    )
    assert all(not path.exists() for path in forbidden)
