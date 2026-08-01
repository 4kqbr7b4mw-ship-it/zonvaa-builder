from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
README = PROJECT_ROOT / "guardian_understanding" / "README.md"
STATUS = PROJECT_ROOT / "knowledge" / "project" / "current-product-status.md"


def test_documentation_states_allowed_general_b1_orientation_and_case_boundary():
    text = README.read_text(encoding="utf-8")
    assert "Begriffe und allgemeine Abläufe erklären" in text
    assert "keine persönliche Einzelfallentscheidung" in text


def test_documentation_requires_exact_b1_boundary_classification_and_source_chain():
    text = README.read_text(encoding="utf-8")
    assert "wirksame B1-Classification" in text
    assert "B1-Boundary" in text
    assert "mindestens eine vollständig" in text
    assert "Source Chain" in text


def test_documentation_keeps_provider_and_text_validation_declarative():
    text = README.read_text(encoding="utf-8")
    assert "Herkunft und erteilt keine" in text
    assert "Textfelder werden nur strukturell" in text
    assert "keine Antwort-Runtime" in text
    assert "keine Ausführungsmacht" in text


def test_canonical_product_status_contains_controlled_orientation_package():
    text = STATUS.read_text(encoding="utf-8")
    assert "Guardian Controlled Orientation Package v1" in text
    assert "Text, Quellen und fachliche Prüfung werden weder erzeugt" in text
