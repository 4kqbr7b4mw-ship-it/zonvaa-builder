from dataclasses import FrozenInstanceError, fields
from pathlib import Path
from typing import Tuple, get_type_hints

import pytest

from builder.runtime import RuntimeManager
from interaction.loader import InteractionLoader
from interaction.models import InteractionContext, InteractionPrinciple


EXPECTED_PRINCIPLES = [
    ("CONVERSATION_ENGINE", "conversation_engine"),
    ("INSTITUTION_BOARD", "institution_board"),
    ("DUAL_SPACE", "dual_space"),
    (
        "CONVERSATION_INSTITUTION_TRANSITION",
        "conversation_institution_transition",
    ),
    ("ARTIFACT_ARCHITECTURE", "artifact_architecture"),
    ("ARTIFACT_ISLAND", "artifact_island"),
    ("AUTHORIZATION_BOUNDARY", "authorization_boundary"),
    ("GUARDIAN_INSTANCE_ISOLATION", "guardian_instance_isolation"),
    ("MULTI_PARTY_GRAPH", "multi_party_graph"),
    ("SHARED_SAFE", "shared_safe"),
    ("NEUTRALITY_GUARANTEE", "neutrality_guarantee"),
    ("INACTIVITY_IS_SUCCESS", "inactivity_is_success"),
    ("OFFBOARDING_NO_LOCK_IN", "offboarding_no_lock_in"),
    ("UNAVAILABILITY_CLAUSE", "unavailability_clause"),
    ("SYSTEM_LIMIT_HANDOVER", "system_limit_handover"),
]


def interaction_document():
    sections = [
        "Conversation Engine",
        "Institution Board",
        "Dual-Space-Interaktion",
        "Conversation → Institution Übergang",
        "Artefakt-Architektur",
        "Artefakt-Insel",
        "Autorisierungs-Graben",
        "Personengebundene Guardian-Instanzen",
        "Multi-Party Graph Engine",
        "Shared Safe",
        "Neutralitäts-Garantie",
        "Inaktivität = Erfolg",
        "Offboarding ohne Lock-in",
        "Unverfügbarkeits-Klausel",
        "Systemgrenzen und Übergabe",
    ]
    return "# Interaction\n\nVersion: 1.0\n\n" + "\n\n".join(
        "## {}\n\nBinding boundary.".format(section)
        for section in sections
    )


def test_interaction_principles_have_stable_complete_values():
    assert [
        (item.name, item.value) for item in InteractionPrinciple
    ] == EXPECTED_PRINCIPLES


def test_interaction_context_is_small_typed_and_immutable():
    context = InteractionLoader().load()

    assert [item.name for item in fields(context)] == [
        "content",
        "source",
        "version",
        "content_hash",
        "principles",
    ]
    assert context.principles == tuple(InteractionPrinciple)
    assert (
        get_type_hints(InteractionContext)["principles"]
        == Tuple[InteractionPrinciple, ...]
    )
    with pytest.raises(FrozenInstanceError):
        context.version = "changed"


def test_canonical_interaction_contract_loads_deterministically():
    first = InteractionLoader().load()
    second = InteractionLoader().load()

    assert first == second
    assert first.source == InteractionLoader.DEFAULT_SOURCE.resolve()
    assert first.version == "1.2"
    assert len(first.content_hash) == 64
    assert (
        "Guardian → Conversation/Interaction → Institution → Runtime"
        in first.content
    )


def test_contract_keeps_board_institution_and_authorization_separate():
    content = InteractionLoader().load().content

    assert "weder der Institution Layer" in content
    assert "Gesprächskontext erzeugt weder einen Workflow-Start" in content
    assert "jeweils eine separate" in content
    assert "nachvollziehbare Autorisierung" in content
    assert "noch eine Vollmacht" in content


def test_contract_preserves_personal_isolation_and_shared_neutrality():
    content = InteractionLoader().load().content

    assert "gehört genau einer Person" in content
    assert "Persönliche Guardian-Kontexte werden weder" in content
    assert "Es entscheidet nicht, welche" in content
    assert "Person recht hat" in content
    assert "keine implementierte Engine" in content


def test_contract_rejects_lock_in_and_claimed_automatic_duties():
    content = InteractionLoader().load().content

    assert "emotionales Re-Engagement" in content
    assert "Offboarding darf weder emotional noch technisch" in content
    assert "keine automatische Handlungs-, Überwachungs- oder" in content
    assert "keine ununterbrochene Verfügbarkeit" in content


def test_contract_marks_concrete_mechanisms_as_open():
    content = InteractionLoader().load().content

    assert "Nicht durch diesen Vertrag festgelegt" in content
    assert "Zeitwerte, Verzögerungen" in content
    assert "biometrische Verfahren" in content
    assert "Zero-Knowledge-Verfahren" in content
    assert "PDF-" in content


def test_contract_points_to_typed_artifact_boundary_without_new_layer():
    content = InteractionLoader().load().content

    assert "`artifact_contract/contract.md`" in content
    assert "keine neue Architekturschicht" in content
    assert "Prinzipien, Rollen, Vetos und Prüfpflichten gehören zu C2" in (
        content
    )
    assert "konkrete Fristen" in content


@pytest.mark.parametrize(
    "missing_heading",
    list(InteractionLoader.REQUIRED_HEADINGS.values()),
)
def test_loader_rejects_missing_principle_sections(
    tmp_path,
    missing_heading,
):
    source = tmp_path / "interaction.md"
    source.write_text(
        interaction_document().replace(
            "## {}\n".format(missing_heading),
            "",
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Prinzipien"):
        InteractionLoader(source).load()


def test_loader_rejects_missing_version_and_near_match_heading(tmp_path):
    source = tmp_path / "interaction.md"
    source.write_text(
        interaction_document().replace("Version: 1.0\n", ""),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Version"):
        InteractionLoader(source).load()

    source.write_text(
        interaction_document().replace(
            "## Conversation Engine",
            "## Conversation Engine extension",
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Conversation Engine"):
        InteractionLoader(source).load()


def test_loader_rejects_missing_or_invalid_source(tmp_path):
    with pytest.raises(FileNotFoundError):
        InteractionLoader(tmp_path / "missing.md").load()

    source = tmp_path / "interaction.md"
    source.write_bytes(b"\xff")
    with pytest.raises(UnicodeError):
        InteractionLoader(source).load()


def test_interaction_context_rejects_invalid_fields():
    valid = {
        "content": "# Interaction",
        "source": Path("interaction.md"),
        "version": "1.0",
        "content_hash": "a" * 64,
        "principles": tuple(InteractionPrinciple),
    }

    for name, value in (
        ("content", ""),
        ("source", "interaction.md"),
        ("version", ""),
        ("content_hash", "not-a-hash"),
        (
            "principles",
            tuple(reversed(tuple(InteractionPrinciple))),
        ),
    ):
        invalid = dict(valid)
        invalid[name] = value
        with pytest.raises((TypeError, ValueError)):
            InteractionContext(**invalid)


def test_runtime_boot_exposes_canonical_interaction_context(monkeypatch):
    monkeypatch.setattr(
        "builder.runtime.ProjectState.collect",
        lambda self: {"verified_facts": {}},
    )

    runtime = RuntimeManager().boot()

    assert runtime.interaction_context == InteractionLoader().load()
