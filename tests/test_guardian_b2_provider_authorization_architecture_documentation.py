from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADR = ROOT / "knowledge/adr/ADR-0062-guardian-b2-provider-authorization-v1.md"


def read(path):
    return path.read_text(encoding="utf-8")


def normalized():
    return " ".join(read(ADR).split())


def test_adr_0062_is_ratified_with_separate_limited_implementation_approval():
    text = read(ADR)
    assert "ADR-0062 – Guardian B2 Provider Authorization v1" in text
    assert "RATIFIZIERT – IMPLEMENTIERUNG BEGRENZT FREIGEGEBEN" in text
    assert "GOV-RATIFICATION-ADR-0062-V1" in text
    assert "GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0062-V1" in text
    assert "weiterhin nicht implementiert" in text
    assert not (ROOT / "knowledge/adr/ADR-0063-guardian-b2-provider-authorization-v1.md").exists()


def test_provider_authorization_only_applies_adr_0060():
    text = normalized()
    for phrase in (
        "Provider Authorization ist Anwendung von ADR-0060 und keine neue Autorisierungsverfassung",
        "genau eine Referenz auf eine unveränderte `B2ProviderIdentity`",
        "keine Authority, keinen Grant, keine Einwilligung",
        "B1-Identitäten, natürliche Personen",
    ):
        assert phrase in text


def test_d3_and_t4_are_distinct_conjunctive_evidence():
    text = normalized()
    for phrase in (
        "D3 ist notwendig, aber niemals hinreichend",
        "T4 ist die unveränderliche Erteilungsquittung",
        "T4 beweist die historische Grant-Erteilung",
        "Eine aktuelle D3-Einwilligung ersetzt T4 nicht",
        "Eine T4-Quittung ersetzt weder aktuelle D3-Wirksamkeit",
    ):
        assert phrase in text


def test_every_touched_uodl_hook_is_named_and_narrowed():
    text = read(ADR)
    section = text.split("## 5. Einzeln berührte UODL-Hooks", 1)[1].split("## 6.", 1)[0]
    for phrase in (
        "UODL Reference Identity",
        "Grant Binding",
        "AAV Binding",
        "Reference Operation",
        "Temporal Effectiveness",
        "User Ownership / Reference before Copy",
        "`REFERENCE_ONLY`",
        "weder `READ`",
        "StorageReference`-Locator",
    ):
        assert phrase in section


def test_negative_governance_evidence_has_no_decision_or_blocking_power():
    text = normalized()
    for phrase in (
        "ausschließlich als deklarierter Beobachtungsumfang",
        "kein Entscheidungsinput für Grant-Wirksamkeit",
        "keine Provider Authorization automatisch verweigern oder blockieren",
        "keine Sperrliste, Sanktion, Risikobewertung oder Profilbildung",
        "verändert das Ergebnis aber nicht",
    ):
        assert phrase in text


def test_effectiveness_is_point_in_time_stateless_and_has_no_status_fields():
    text = normalized()
    for phrase in (
        "explizit übergebenen timezone-aware Auswertungszeitpunkt",
        "liest keinen aktuellen Zustand selbst",
        "kein Repository oder Service",
        "keine globale Uhr oder Systemzeit",
        "Wirksamkeit ist kein gespeicherter Zustand",
        "`active`, `valid`, `revoked`, `expired`, `authorized`, `blocked`",
    ):
        assert phrase in text


def test_provenance_is_reconstructable_non_personal_and_not_self_confirming():
    text = normalized()
    for phrase in (
        "eigene immutable, vollständig rekonstruierbare",
        "institutionelle Source ID",
        "ADR-0060-Evaluation-Evidence-ID",
        "kein Ausstellerbeweis, keine Selbstbestätigung",
        "Provider Identity darf ihre eigene Autorisierung",
    ):
        assert phrase in text


def test_no_invocation_runtime_operations_or_operational_layers_are_authorized():
    text = read(ADR)
    for phrase in (
        "B2 Capability Invocation",
        "B2 Runtime und jede technische Ausführung",
        "personenbezogene Verarbeitung oder Speicherung",
        "Observation und Runtime Audit",
        "Operational Memory, Metrics und Notifications",
        "UI, Workflow- oder Werkzeugaktivierung",
    ):
        assert phrase in text


def test_zero_question_is_unambiguously_no():
    text = normalized()
    assert "Kann durch die dokumentierte Architektur eine Provider Authorization bereits" in text
    assert "Antwort: Nein." in text


def test_ratification_is_external_scope_limited_and_not_an_implementation_approval():
    ratification = read(ROOT / "governance/ratification-adr-0062.md")
    text = " ".join(ratification.split())
    for phrase in (
        "GOV-RATIFICATION-ADR-0062-V1",
        "RATIFIZIERUNG DOKUMENTIERT",
        "03.08.2026, 13:29:18 Uhr Europe/Berlin (CEST)",
        "Zeitpunkt der Auftragsübergabe",
        "nicht der Zeitpunkt der Repository-Dokumentation",
        "Institutionsgründer in konstituierender Funktion",
        "## Freigegeben",
        "keine neue Autorisierungssemantik",
        "## Ausdrücklich nicht freigegeben",
        "keine institutionelle Implementierungsfreigabe",
        "ADR-0058, ADR-0059, ADR-0060 und ADR-0061",
        "nächste eigenständige menschliche Beschluss",
    ):
        assert phrase in text


def test_implementation_approval_is_closed_non_executing_and_requires_push_gate():
    approval = read(
        ROOT / "governance/institutional-implementation-approval-adr-0062.md"
    )
    text = " ".join(approval.split())
    for phrase in (
        "GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0062-V1",
        "INSTITUTIONELLE IMPLEMENTIERUNGSFREIGABE – GÜLTIG",
        "03.08.2026, 15:15 Uhr Europe/Berlin (CEST, UTC+02:00)",
        "Repository-Dokumentationszeitpunkt: 03.08.2026, 15:17:10 Uhr",
        "Beschlusszeitpunkt und Repository-Dokumentationszeitpunkt sind ausdrücklich getrennt",
        "## Freigegeben",
        "D3 als aktuell wirksame, notwendige, aber niemals hinreichende",
        "T4 ausschließlich als historische Quittierung",
        "UODL Reference Identity",
        "User Ownership / Reference before Copy",
        "## Ausdrücklich nicht freigegeben",
        "Statusfelder wie `valid`, `active`, `revoked`, `expired`, `authorized`, `denied` oder `blocked`",
        "Implementierung von ADR-0062 in diesem Dokumentationsauftrag",
        "weiterhin nicht implementiert",
        "Freigabedokument nachweisbar auf `origin/builder-reset-v2` gepusht",
        "Prozessvorfall – Implementierungsbeginn vor kanonischem Freigabe-Push",
        "Prüffrage Null",
    ):
        assert phrase in text
