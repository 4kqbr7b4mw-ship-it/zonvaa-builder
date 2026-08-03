from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADR = ROOT / "knowledge/adr/ADR-0061-guardian-b2-provider-identity-v1.md"


def read(path):
    return path.read_text(encoding="utf-8")


def normalized():
    return " ".join(read(ADR).split())


def normalized_text(path):
    return " ".join(read(path).split())


def test_adr_0061_is_ratified_with_separate_limited_implementation_approval():
    text = read(ADR)
    assert ADR.exists()
    assert "ADR-0061 – Guardian B2 Provider Identity v1" in text
    assert "RATIFIZIERT – IMPLEMENTIERUNG BEGRENZT FREIGEGEBEN" in text
    assert "GOV-RATIFICATION-ADR-0061-V1" in text
    assert "GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0061-V1" in text
    assert not (ROOT / "knowledge/adr/ADR-0062-guardian-b2-provider-identity-v1.md").exists()


def test_ratification_is_external_scope_limited_and_not_an_implementation_approval():
    ratification = read(ROOT / "governance/ratification-adr-0061.md")
    normalized_ratification = " ".join(ratification.split())
    for phrase in (
        "GOV-RATIFICATION-ADR-0061-V1",
        "RATIFIZIERUNG DOKUMENTIERT",
        "03.08.2026, 10:43 Uhr Europe/Berlin",
        "Zeitpunkt der Auftragsübergabe",
        "nicht der Zeitpunkt der Repository-Dokumentation",
        "Institutionsgründer in konstituierender Funktion",
        "## Freigegeben",
        "## Ausdrücklich nicht freigegeben",
        "keine institutionelle Implementierungsfreigabe",
        "ADR-0058, ADR-0059 und ADR-0060",
        "nächste eigenständige menschliche Beschluss",
    ):
        assert phrase in normalized_ratification


def test_implementation_approval_is_scope_limited_non_executing_and_non_personal():
    approval = normalized_text(
        ROOT / "governance/institutional-implementation-approval-adr-0061.md"
    )
    for phrase in (
        "GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0061-V1",
        "INSTITUTIONELLE IMPLEMENTIERUNGSFREIGABE – GÜLTIG",
        "03.08.2026, 11:28:19 Uhr Europe/Berlin (CEST)",
        "GOV-RATIFICATION-ADR-0061-V1",
        "Ratifizierung und institutionelle Implementierungsfreigabe sind zwei getrennte",
        "## Freigegeben",
        "eigenständige B2 Provider Identity",
        "geschlossenen B2 Provider Classes",
        "## Ausdrücklich nicht freigegeben",
        "B2 Provider Authorization",
        "B2 Capability Invocation",
        "B2 Runtime",
        "personenbezogene Verarbeitung",
        "Key Custody",
        "Provider Identity besitzt keinerlei Autorisierungswirkung",
        "niemals natürliche Personen",
        "strukturell nicht modellierbar",
        "kein Codex-Implementierungsauftrag",
    ):
        assert phrase in approval


def test_provider_classes_are_closed_complete_and_non_personal():
    text = read(ADR)
    expected = (
        "INSTITUTIONAL_SERVICE_UNIT",
        "PROFESSIONAL_ROLE_UNIT",
        "MODEL_SERVICE_UNIT",
        "RESEARCH_SERVICE_UNIT",
        "TECHNICAL_TOOL_SERVICE_UNIT",
    )
    for value in expected:
        assert value in text
    class_section = text.split("## 4. Geschlossene Provider Classes v1", 1)[1].split("## 5.", 1)[0]
    for forbidden in ("exemplarisch", "insbesondere", "nicht abschließend"):
        assert forbidden not in class_section.lower()
    assert "niemals eine konkrete natürliche Person" in class_section
    normalized_class_section = " ".join(class_section.split())
    for phrase in (
        "institutionelle fachliche Modellierungs- oder Unterstützungseinheit",
        "weder ein ML-Modell noch ein Datenmodell, einen Modellprozess, Tool-Aufruf",
        "keinerlei technische Modell- oder Ausführungssemantik",
        "kein Tool-Aufruf, keine Invocation und keine Runtime-Identität",
        "keinerlei Ausführungsmacht",
    ):
        assert phrase in normalized_class_section


def test_responsibilities_and_capabilities_are_closed_codes_without_free_semantics():
    text = read(ADR)
    for value in (
        "GENERAL_ORIENTATION_SUPPORT",
        "PERSONAL_PREPARATION_SUPPORT",
        "PROFESSIONAL_REVIEW_PREPARATION_SUPPORT",
        "SOURCE_REFERENCE_SUPPORT",
        "GENERAL_ORIENTATION_SERVICE_DESCRIPTOR",
        "PERSONAL_PREPARATION_SERVICE_DESCRIPTOR",
        "PROFESSIONAL_REVIEW_PREPARATION_DESCRIPTOR",
        "SOURCE_REFERENCE_SERVICE_DESCRIPTOR",
    ):
        assert value in text
    assert "Freitext" in text
    assert "kein Token, Grant, Permission" in normalized()


def test_provenance_is_non_personal_explicit_and_has_no_hidden_clock():
    text = normalized()
    for phrase in (
        "typisierte institutionelle Source ID",
        "Governance-Decision-ID",
        "Vertrags- oder Registrierungsgrundlage",
        "explizit übergebenen timezone-aware Erstellungszeitpunkt",
        "keinen Aussteller als natürliche Person",
        "kein Konstruktor oder Validator darf `now()`",
    ):
        assert phrase in text


def test_no_new_schema_versioning_is_invented():
    text = read(ADR)
    section = " ".join(
        text.split("## 8. Versionierung", 1)[1].split("## 9.", 1)[0].split()
    )
    assert "keine kanonische `schema_version`" in section
    assert "führt deshalb kein `schema_version`" in section
    assert "optionale Vorgängerreferenz" in section


def test_b1_and_b2_identity_semantics_remain_structurally_separate():
    text = normalized()
    for phrase in (
        "eigenständige Typfamilie",
        "weder konvertiert, erweitert, vererbt noch als Union-Alternative",
        "keinen B1→B2-Upgradepfad",
        "keine gemeinsame Identitäts-, Vertrauens- oder Autorisierungssemantik",
    ):
        assert phrase in text


def test_negative_rules_and_blocked_layers_are_complete():
    text = read(ADR)
    for phrase in (
        "Negative Provider Identity Rules",
        "B2 Provider Authorization",
        "B2 Capability Invocation",
        "B2 Runtime",
        "personenbezogene Akteursbindung",
        "Key Custody",
        "Inhaltszugriff",
        "Sessions, Caches und Tokens",
        "Operational Memory, Metrics und Notifications",
        "externe oder produktive Integrationen",
    ):
        assert phrase in text


def test_reference_scenarios_use_only_synthetic_typed_values():
    text = read(ADR)
    section = text.split("## 11. Referenzszenarien", 1)[1].split("## 12.", 1)[0]
    assert "b2-provider-identity:institutional-unit-01" in section
    assert "b2-provider-identity:professional-role-unit-01" in section
    assert "keine Namen, Kontakte oder fachlichen Freitexte" in section


def test_adr_and_approval_documents_remain_non_executing_documents():
    text = normalized()
    for phrase in (
        "keine institutionelle Implementierungsfreigabe",
        "implementiert keine Klasse, Enum, Value Object, API, Runtime",
        "ändert weder ADR-0060 noch bestehende Implementierungsfreigaben",
        "Antwort: Nein",
    ):
        assert phrase in text
