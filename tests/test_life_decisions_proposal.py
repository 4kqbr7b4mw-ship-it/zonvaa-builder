import json
from pathlib import Path


PROPOSAL = Path("knowledge/proposals/life-decisions.json")


def test_life_decisions_proposal_contains_expected_artifacts():
    proposal = json.loads(PROPOSAL.read_text(encoding="utf-8"))

    assert proposal["why_assessment"]["status"] == "aligned"
    assert [artifact["path"] for artifact in proposal["artifacts"]] == [
        "knowledge/project/life-decisions.md",
        "knowledge/adr/ADR-0018-life-decisions.md",
        "knowledge/roadmaps/life-decisions-roadmap.md",
    ]
    assert all(
        artifact["action"] == "document.create"
        for artifact in proposal["artifacts"]
    )


def test_life_decisions_documents_preserve_scope_and_data_principles():
    proposal = json.loads(PROPOSAL.read_text(encoding="utf-8"))
    product, adr, roadmap = [
        artifact["content"] for artifact in proposal["artifacts"]
    ]

    for subject in (
        "Testament und Nachlass",
        "Vorsorgevollmacht",
        "Patientenverfügung",
        "digitale Konten und digitaler Nachlass",
        "persönliche Wünsche und Familienwissen",
    ):
        assert subject in product

    assert "ersetzt keine Rechtsanwälte" in product
    assert "Nutzer bestimmen" in product
    assert "Originale, extrahierte Fakten" in product
    assert "stillschweigende Wiederverwendung" in product
    assert "# ADR-0018 – Life Decisions" in adr
    assert "nicht zum zentralen Besitzer" in adr

    for phase in range(1, 11):
        assert "## {}.".format(phase) in roadmap
    assert roadmap.count("**Ziel:**") == 10
    assert roadmap.count("**Konkrete Ergebnisse:**") == 10
    assert roadmap.count("**Abnahmekriterien:**") == 10
    assert roadmap.count("**Wesentliche Risiken:**") == 10
    assert roadmap.count("**Ausgeschlossen:**") == 10
