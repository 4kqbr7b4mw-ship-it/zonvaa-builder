from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADR = ROOT / "knowledge" / "adr" / "ADR-0046-zonvaa-builder-reset-v2.md"


def e7a():
    text = ADR.read_text(encoding="utf-8")
    section = text.split("## E7a – Paket-Granularität", 1)[1]
    return " ".join(section.split())


def test_e7a_is_part_of_the_canonical_builder_reset_adr():
    assert "## E7a – Paket-Granularität" in ADR.read_text(encoding="utf-8")


def test_e7a_requires_coherent_packaging():
    section = e7a()
    assert "fachlich zusammengehörige Teilbausteine" in section
    assert "fachlicher Kohäsion" in section


def test_e7a_requires_separate_component_reporting_and_integration():
    section = e7a()
    assert "getrennten Abschnitten je Teilbaustein" in section
    assert "Integrationsabschnitt" in section


def test_e7a_preserves_the_stop_rule_without_replacement_architecture():
    section = e7a()
    assert "nicht eigenmächtig" in section
    assert "keine Ersatzarchitektur" in section
    assert "kein inkonsistenter Gesamtzustand" in section


def test_e7a_defines_reviewability_limits():
    section = e7a()
    assert "ehrlichen Prüfsitzung" in section
    assert "Macht- oder Risikogrenzen" in section
    assert "klar seziert" in section


def test_e7a_keeps_implementation_commit_and_push_separate():
    section = e7a()
    assert "Implementierung ist keine Commit-Freigabe" in section
    assert "Commit ist keine Push-Freigabe" in section
    assert "Push wird separat freigegeben" in section
