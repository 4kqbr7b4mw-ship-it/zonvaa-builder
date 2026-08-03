from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADR = ROOT / "knowledge/adr/ADR-0063-b2-purpose-uodl-binding-constitution-v1.md"


def read(path):
    return path.read_text(encoding="utf-8")


def test_adr_0063_is_ratified_and_approved_but_not_implemented():
    text = read(ADR)
    assert "ADR-0063 – B2 Purpose and UODL Binding Constitution v1" in text
    assert "RATIFIZIERT – IMPLEMENTIERUNG BEGRENZT FREIGEGEBEN – IMPLEMENTIERT UND VALIDIERT" in text
    assert "GOV-RATIFICATION-ADR-0063-V1" in text
    assert "GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0063-V1" in text
    assert "governance/b2_purpose_uodl_binding.py" in text
    assert "keinen Migrationspfad" in text


def test_adr_0063_implementation_approval_is_current_scoped_and_non_executing():
    text = read(ROOT / "governance/institutional-implementation-approval-adr-0063.md")
    assert "INSTITUTIONELLE IMPLEMENTIERUNGSFREIGABE – GÜLTIG" in text
    assert "03.08.2026, 20:00:35 Uhr" in text
    assert "03.08.2026, 20:00:39 Uhr" in text
    assert "Keine frühere Gutachterbewertung" in text
    assert "nicht rückwirkend" in text
    assert "## Freigegeben" in text
    assert "## Ausdrücklich nicht freigegeben" in text
    assert "ADR-0064 bleibt fachlich unabhängig, ratifiziert, aber nicht" in text
    assert "kein Implementierungsauftrag" in text
    assert "nach nachweisbarem Push" in text


def test_adr_0063_ratification_record_separates_scope_and_times():
    text = read(ROOT / "governance/ratification-adr-0063.md")
    assert "RATIFIZIERUNG DOKUMENTIERT – KEINE IMPLEMENTIERUNGSFREIGABE" in text
    assert "03.08.2026, 19:26:49 Uhr" in text
    assert "03.08.2026, 19:27:02 Uhr" in text
    assert "Beschlusszeitpunkt" in text
    assert "Repository-Dokumentation" in text
    assert "## Freigegeben" in text
    assert "## Ausdrücklich nicht freigegeben" in text
    assert "Implementierung" in text
    assert "Commit" in text
    assert "Push" in text


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
