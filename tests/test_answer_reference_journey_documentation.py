from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "guardian_understanding" / "README.md").read_text(
    encoding="utf-8"
)
STATUS = (ROOT / "knowledge" / "project" / "current-product-status.md").read_text(
    encoding="utf-8"
)


def test_documentation_records_supported_complete_and_partial_paths():
    for phrase in (
        "reine B1-Orientierung",
        "B1→B2",
        "direkte B2-Vorbereitung",
        "vollständige B1→B2→B3-Reise",
        "direkte B3-Grenze",
    ):
        assert phrase in README


def test_documentation_records_reference_identity_and_stop_rules():
    for phrase in (
        "eigene exakt\npassende Classification, Boundary, Source Chains und Foundation",
        "terminale\nFoundation bleibt dasselbe Objekt",
        "streng steigenden Schutz",
        "typisierten finalen Stoppgrund",
        "nach ihm\nist kein weiterer Schritt zulässig",
    ):
        assert phrase in README


def test_documentation_records_projection_without_semantic_power():
    for phrase in (
        "validierten Originalobjekte",
        "weder zusammengefasst noch umformuliert",
        "reine Sichtoptionen ohne Handler oder Ausführungsmacht",
        "keine Klassifikation, Antwortgenerierung",
        "keine Änderung eines fachlichen Zustands",
    ):
        assert phrase in README


def test_product_status_contains_the_reference_journey_integration():
    assert "End-to-End Guardian Answer Reference Journey v1" in STATUS
    assert "immutable, deterministisch validierte Referenzreise" in STATUS
    assert "ohne\n  Generierung, Interpretation, Priorisierung" in STATUS
