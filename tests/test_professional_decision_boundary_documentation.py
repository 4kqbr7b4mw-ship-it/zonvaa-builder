from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "guardian_understanding" / "README.md").read_text(
    encoding="utf-8"
)
STATUS = (ROOT / "knowledge" / "project" / "current-product-status.md").read_text(
    encoding="utf-8"
)


def test_documentation_contains_the_complete_five_part_b3_pattern():
    for phrase in (
        "Bedeutung oder Dringlichkeit sachlich anerkennen",
        "konkrete Entscheidung klar nicht bestätigen",
        "genaue professionelle Grenze benennen",
        "sichere allgemeine Orientierung oder persönliche Vorbereitung anbieten",
        "bereitgestellten Soforthilfehinweis",
    ):
        assert phrase in README


def test_documentation_records_exact_b3_sources_and_declarative_b1_b2():
    assert "exakt B3-Classification" in README
    assert "exakt B3-Boundary" in README
    assert "vollständigen, identischen\nSource-Chain-Menge" in README
    assert "B1-Orientierung oder B2-Vorbereitung" in README
    assert "nur über bereits validierte Envelopes referenziert" in README


def test_documentation_excludes_semantic_decisions_and_execution():
    for phrase in (
        "nicht generiert oder semantisch\ngeprüft",
        "keine Gefahrenerkennung, Triage, Rufnummernermittlung, Kontaktaufnahme",
        "keine Rechts-, Steuer-, Finanz- oder\nMedizinentscheidung treffen",
        "weder Zustände, Rechte, Resolutionen\nnoch Freigaben verändern",
        "nicht durch natürliche Sprachinterpretation",
    ):
        assert phrase in README


def test_product_status_identifies_b3_as_a_non_executing_evidence_package():
    assert "Guardian Professional Decision Boundary Package v1" in STATUS
    assert "verlangte professionelle Einzelfallentscheidung" in STATUS
    assert "weder erzeugt noch\n  interpretiert oder ausgeführt" in STATUS
