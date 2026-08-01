from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
README = PROJECT_ROOT / "guardian_understanding" / "README.md"
STATUS = PROJECT_ROOT / "knowledge" / "project" / "current-product-status.md"


def test_documentation_describes_allowed_personal_preparation_and_case_boundary():
    text = README.read_text(encoding="utf-8")
    assert "bereitgestellte persönliche Angaben" in text
    assert "bekannte Tatsachen, offene Fragen" in text
    assert "keine konkrete Rechtsgestaltung empfehlen" in text
    assert "professionelle Einzelfallentscheidung" in text


def test_documentation_requires_b2_boundary_classification_and_complete_sources():
    text = README.read_text(encoding="utf-8")
    assert "B2-Classification" in text
    assert "B2-Boundary" in text
    assert "vollständig identische Source-Chain-Menge" in text


def test_documentation_keeps_b1_provider_review_and_text_handling_declarative():
    text = README.read_text(encoding="utf-8")
    assert "optional rein deklarativ referenziert" in text
    assert "Textfelder werden ausschließlich strukturell" in text
    assert "Provider-Herkunft" in text
    assert "keine Recherche, Runtime" in text


def test_product_status_contains_personal_preparation_package():
    text = STATUS.read_text(encoding="utf-8")
    assert "Guardian Personal Preparation Package v1" in text
    assert "exakt B2/B2" in text
    assert "nicht erzeugt, interpretiert, priorisiert oder entschieden" in text
