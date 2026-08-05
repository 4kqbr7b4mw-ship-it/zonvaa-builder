from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "governance/no-fabrication-reference-consolidation.md"


def content() -> str:
    return REFERENCE.read_text(encoding="utf-8")


def test_document_is_reference_not_rule_or_taxonomy():
    text = content()
    for marker in (
        "GOV-NO-FABRICATION-REFERENCE-CONSOLIDATION-V1",
        "kanonische Referenzkonsolidierung",
        "keine Governance-Regel",
        "keine Verfassungsfamilie",
        "keine materielle Norm",
        "keine neue Taxonomie",
        "Navigations- und\nZuständigkeitsübersicht",
    ):
        assert marker in text


def test_four_registered_areas_have_explicit_owners_and_limits():
    text = content()
    for marker in (
        "### 2.1 Erfundene Quellen",
        "### 2.2 Erfundene Gefühle",
        "### 2.3 Erfundene Nachweise",
        "### 2.4 Erfundene Rechenschaft",
        "Primärer materieller Regelinhaber",
        "Unterstützende Regelinhaber",
        "Vorhandene technische Durchsetzung",
        "Bewusste technische Grenze",
        "Nicht zuständig",
    ):
        assert marker in text


def test_existing_rule_owners_remain_local_and_unmodified():
    text = content()
    for marker in (
        "ADR-0047",
        "ADR-0064 und ADR-0064-A1",
        "ADR-0060 und ADR-0062",
        "ADR-0063",
        "ADR-0065",
        "ADR-0066",
        "ausschließlich der referenzierte primäre\nRegelinhaber zuständig",
        "ordnet keine Regel einer anderen unter",
        "bestimmt keinen neuen Vorrang",
    ):
        assert marker in text


def test_accountability_remains_dormant_and_unregulated():
    text = content()
    assert "Primärer materieller Regelinhaber:** gegenwärtig keiner" in text
    for marker in (
        "ruhender Kandidat",
        "nicht aktiviert",
        "nicht materiell\n  geregelt",
        "kein gegenwärtiger Regelinhaber",
        "keine Accountability- oder\n  Explanation-Verträge",
    ):
        assert marker in text


def test_no_material_power_runtime_observation_or_universal_validator():
    text = content()
    for marker in (
        "keine Prioritäts- oder Vorrangregel",
        "keine Runtime, Runtime Readiness",
        "Observation",
        "externe Wahrheitsprüfung",
        "Universalvalidator",
        "keine materielle Norm",
        "keine institutionelle Entscheidung",
        "ADR-0067",
        "Antwort: **Nein.**",
    ):
        assert marker in text


def test_reference_does_not_modify_existing_canonical_artifacts():
    forbidden_paths = (
        "governance/no_fabrication.py",
        "governance/no_fabrication_validator.py",
        "governance/runtime_readiness.py",
    )
    assert all(not (ROOT / path).exists() for path in forbidden_paths)
    assert "class " not in content()
