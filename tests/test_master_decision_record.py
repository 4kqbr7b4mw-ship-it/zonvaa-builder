from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MDR = (
    ROOT
    / "knowledge"
    / "mdr"
    / "MDR-0001-guardian-conversation-and-continuity.md"
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_mdr_is_the_single_binding_guardian_architecture_source() -> None:
    content = read(MDR)

    assert "## Status\n\nBeschlossen" in content
    assert "ausschließlich MDR-0001 die verbindliche Detailquelle" in content
    assert "Bei Abweichung\ngilt MDR-0001" in content
    assert "keine verabschiedete Regel ausgelassen" in content
    assert "keine unaufgelösten normativen Widersprüche" in content


def test_mdr_preserves_conversation_and_interaction_decisions() -> None:
    content = read(MDR)
    required_terms = (
        "Conversation Engine",
        "Institution Board",
        "Dual-Space",
        "Artefakt-Insel",
        "Autorisierungs",
        "Personengebundene Guardian-Instanzen",
        "Multi-Party Graph Engine",
        "Shared Safe",
        "Neutralität",
        "Nicht-Nutzung",
        "Offboarding",
        "moralische Letztentscheidungen",
        "Notfälle",
        "Guardian → Conversation/Interaction → Institution → Runtime",
    )

    for term in required_terms:
        assert term in content


def test_mdr_preserves_guardian_continuity_decisions() -> None:
    content = read(MDR)
    required_terms = (
        "Unternehmensunabhängigkeit",
        "nutzerkontrollierte Originale",
        "offenen, dokumentierten Formaten",
        "proprietäre ZONVAA-Laufzeit",
        "Sprachmodell",
        "Sunset",
        "Insolvenz",
        "technischem Lock-in",
        "Digitales Vermächtnis",
        "widerruf",
        "rollenbasiert",
        "Interessenkonflikt",
        "wenn ZONVAA morgen nicht mehr existiert",
    )

    for term in required_terms:
        assert term.casefold() in content.casefold()


def test_mdr_records_tensions_and_deferred_implementation_details() -> None:
    content = read(MDR)

    for heading in (
        "## 16. Konsolidierte Spannungen und ihre Auflösung",
        "## 17. Bewusst offene Implementierungsfragen",
        "## 19. Herkunfts- und Vollständigkeitsmatrix",
    ):
        assert heading in content

    for detail in (
        "feste Antwortverzögerungen",
        "feste Zeichenzahlen",
        "feste Anzahl von Gesprächsrunden",
        "starre Wort-, Verb- oder Promptfilter",
        "Drei-Sekunden",
        "konkrete Farben",
        "biometrische",
        "Zero-Knowledge",
        "PDF/A",
        "Haftungs-",
    ):
        assert detail.casefold() in content.casefold()


def test_replaced_adrs_point_to_mdr() -> None:
    for number, name in (
        ("0023", "guardian-conversation-principles"),
        ("0024", "guardian-first-workflow-second"),
        ("0026", "conversation-interaction-architecture"),
    ):
        content = read(ROOT / "knowledge" / "adr" / f"ADR-{number}-{name}.md")
        assert "Ersetzt durch MDR-0001" in content
        assert str(MDR.relative_to(ROOT)) in content


def test_active_architecture_layers_reference_mdr_without_being_replaced() -> None:
    mdr_path = str(MDR.relative_to(ROOT))
    for relative_path in (
        "constitution/constitution.md",
        "institution/institution.md",
        "governance/charter.md",
        "interaction/interaction.md",
        "knowledge/adr/ADR-0025-institution-layer.md",
        "knowledge/adr/ADR-0027-governance-architecture.md",
    ):
        assert mdr_path in read(ROOT / relative_path)

    interaction = read(ROOT / "interaction" / "interaction.md")
    assert "Status: abgeleiteter technischer Nachweis" in interaction
    assert "keine eigenständige normative Quelle" in interaction
