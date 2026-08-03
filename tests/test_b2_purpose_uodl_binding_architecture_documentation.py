from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADR = ROOT / "knowledge/adr/ADR-0063-b2-purpose-uodl-binding-constitution-v1.md"


def read(path):
    return path.read_text(encoding="utf-8")


def test_adr_0063_is_formal_but_unratified_and_unimplemented():
    text = read(ADR)
    assert "ADR-0063 – B2 Purpose and UODL Binding Constitution v1" in text
    assert "VORGESCHLAGEN – NICHT RATIFIZIERT" in text
    assert "NICHT IMPLEMENTIERUNGSFREIGEGEBEN – NICHT IMPLEMENTIERT" in text


def test_adr_0063_has_one_purpose_constitution_and_fail_closed_order():
    text = " ".join(read(ADR).split())
    for phrase in (
        "genau eine fachlich autoritative Purpose-Verfassung",
        "B2PurposeScope` aus ADR-0060",
        "keine zweite Purpose-Liste",
        "identischen oder nachweisbar engeren",
        "nicht vergleichbare Scopes führen fail closed",
        "Evidence, Provenienz oder Validatorannahmen ersetzen keine fehlende Purpose-Bindung",
    ):
        assert phrase in text


def test_adr_0063_defines_typed_purpose_evidence_without_power():
    text = read(ADR)
    for phrase in (
        "Bindungs-ID",
        "Corridor-Referenz",
        "Ausgangs-Purpose-Referenz",
        "Vergleichsrelation",
        "explizit bereitgestellten timezone-aware Erstellungszeitpunkt",
        "keine Autorisierung",
        "Statusfelder wie `valid`, `active`, `approved` oder",
    ):
        assert phrase in text


def test_adr_0063_keeps_uodl_types_separate_and_maps_one_pair():
    text = " ".join(read(ADR).split())
    for phrase in (
        "bleiben unterschiedliche geschlossene Typen",
        "StorageOperation.REFERENCE",
        "B2UODLOperation.REFERENCE_ONLY",
        "Kein anderes Paar ist zulässig",
        "keine String-Konvertierung",
        "keine String-Konvertierung, Alias- oder Namensähnlichkeitslogik",
    ):
        assert phrase in text


def test_adr_0063_forbids_automatic_migration_and_execution():
    text = read(ADR)
    assert "dürfen nicht automatisch migriert" in text
    assert "keine Textinterpretation oder Ähnlichkeitszuordnung" in text
    assert "Capability Invocation" in text
    assert "Runtime" in text
    assert "Antwort: **Nein.**" in text


def test_no_purpose_or_uodl_mapping_implementation_exists():
    governance = ROOT / "governance"
    assert not list(governance.glob("*purpose*mapping*.py"))
    assert not list(governance.glob("*uodl*mapping*.py"))
