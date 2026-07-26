from dataclasses import FrozenInstanceError, fields
from pathlib import Path
from typing import Tuple, get_type_hints

import pytest

from builder.runtime import RuntimeManager
from governance.loader import GovernanceLoader
from governance.models import (
    GovernanceBody,
    GovernanceContext,
    NormLevel,
    ProtectionGoal,
    TrustDomain,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONSTITUTION_PATH = PROJECT_ROOT / "constitution" / "constitution.md"


def canonical_constitution():
    return CONSTITUTION_PATH.read_text(encoding="utf-8")


def test_governance_enums_have_stable_complete_values():
    assert [item.value for item in NormLevel] == [
        "c1_constitution",
        "c2_governance_charter",
        "c3_operative_rules",
    ]
    assert [item.value for item in ProtectionGoal] == [
        "no_user_data_sale",
        "no_covert_third_party_training",
        "no_hidden_monetization",
        "no_emotional_dependency_optimization",
        "no_user_sovereignty_bypass",
        "no_portability_or_sunset_abandonment",
        "no_guarantee_weakening",
    ]
    assert [item.value for item in GovernanceBody] == [
        "operational_leadership",
        "trust_council",
        "user_convention",
        "stewardship_structure",
    ]
    assert [item.value for item in TrustDomain] == [
        "data",
        "monetization_and_conflicts",
        "emergency_and_security",
        "guardian_continuity",
        "c1_c2_changes",
    ]


def test_governance_context_is_typed_and_immutable():
    context = GovernanceLoader().load(canonical_constitution())

    assert [item.name for item in fields(context)] == [
        "charter_content",
        "charter_source",
        "charter_version",
        "charter_hash",
        "operative_rules_content",
        "operative_rules_source",
        "operative_rules_version",
        "operative_rules_hash",
        "constitution_hash",
        "norm_levels",
        "protection_goals",
        "bodies",
        "trust_domains",
    ]
    hints = get_type_hints(GovernanceContext)
    assert hints["norm_levels"] == Tuple[NormLevel, ...]
    assert hints["protection_goals"] == Tuple[ProtectionGoal, ...]
    assert hints["bodies"] == Tuple[GovernanceBody, ...]
    assert hints["trust_domains"] == Tuple[TrustDomain, ...]
    with pytest.raises(FrozenInstanceError):
        context.charter_version = "changed"


def test_canonical_governance_contract_loads_deterministically():
    constitution = canonical_constitution()
    first = GovernanceLoader().load(constitution)
    second = GovernanceLoader().load(constitution)

    assert first == second
    assert first.charter_version == "1.0"
    assert first.operative_rules_version == "1.0"
    assert first.norm_levels == tuple(NormLevel)
    assert first.protection_goals == tuple(ProtectionGoal)
    assert first.bodies == tuple(GovernanceBody)
    assert first.trust_domains == tuple(TrustDomain)
    assert all(
        len(value) == 64
        for value in (
            first.constitution_hash,
            first.charter_hash,
            first.operative_rules_hash,
        )
    )


def test_c1_contains_only_protection_contract_not_operational_details():
    content = canonical_constitution()

    assert "Normstufe: C1" in content
    for heading in GovernanceLoader.C1_HEADINGS.values():
        assert "## {}".format(heading) in content
    for operational_detail in (
        "RuntimeManager",
        "python3 -m",
        "pytest",
        "Ratsmitglieder",
        "Amtszeit",
        "Quorum",
    ):
        assert operational_detail not in content


def test_c2_defines_bounded_veto_escalation_and_multikey_change():
    content = GovernanceLoader().load(
        canonical_constitution()
    ).charter_content

    assert "aufschiebendes Veto" in content
    assert "weder absolut noch unbegrenzt unüberstimmbar" in content
    for step in (
        "Prüfung mit dokumentierter Grundlage",
        "begründetem aufschiebendem Veto",
        "Vermittlung",
        "erneuter Prüfung",
        "dokumentierter Eskalation",
    ):
        assert step in content
    assert "Mindestens operative Leitung" in content
    assert "Vertrauensrat und Nutzer-Konvent" in content
    assert "Kein Zentrum kann C1 allein verändern" in content


def test_c2_defines_audit_incident_and_whistleblower_boundaries():
    content = GovernanceLoader().load(
        canonical_constitution()
    ).charter_content

    assert "Unabhängige externe Audits" in content
    assert "rotierende Prüfinstanzen" in content
    assert "erhebliche Verletzungen von" in content
    assert "Bagatell- und Betriebsfälle" in content
    assert "nicht still gelöscht" in content
    assert "geschützter Kanal" in content
    assert "behauptet ohne Umsetzung keine Anonymität" in content


def test_c2_keeps_user_participation_and_legal_form_open():
    content = GovernanceLoader().load(
        canonical_constitution()
    ).charter_content

    assert "Losverfahren" in content
    assert "rotierende Panels" in content
    assert "Direkte offene Onlinewahlen sind nicht" in content
    assert "keine" in content
    assert "Rechtsform als verbindlich" in content
    assert "haftungsfrei oder insolvenzfest behauptet" in content


def test_c3_indexes_existing_rules_without_copying_governance():
    content = GovernanceLoader().load(
        canonical_constitution()
    ).operative_rules_content

    assert "Normstufe: C3" in content
    assert "`AGENTS.md`" in content
    assert "ADRs" in content
    assert "Dieses Register ist ein Normstufen-Index" in content
    assert "führt keine zweite Produkt-, Workflow- oder" in content


@pytest.mark.parametrize(
    "heading",
    list(GovernanceLoader.C1_HEADINGS.values()),
)
def test_loader_rejects_missing_c1_protection_goal(heading):
    constitution = canonical_constitution().replace(
        "## {}\n".format(heading),
        "",
    )

    with pytest.raises(ValueError, match="C1 protection goals"):
        GovernanceLoader().load(constitution)


@pytest.mark.parametrize(
    "heading",
    list(GovernanceLoader.C2_BODY_HEADINGS.values())
    + list(GovernanceLoader.C2_DOMAIN_HEADINGS.values())
    + list(GovernanceLoader.C2_REQUIRED_HEADINGS),
)
def test_loader_rejects_missing_c2_sections(tmp_path, heading):
    source = tmp_path / "charter.md"
    source.write_text(
        GovernanceLoader.DEFAULT_CHARTER.read_text(
            encoding="utf-8"
        ).replace("## {}\n".format(heading), ""),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="C2 governance"):
        GovernanceLoader(charter_source=source).load(
            canonical_constitution()
        )


@pytest.mark.parametrize(
    "heading",
    list(GovernanceLoader.C3_REQUIRED_HEADINGS),
)
def test_loader_rejects_missing_c3_sections(tmp_path, heading):
    source = tmp_path / "operative-rules.md"
    source.write_text(
        GovernanceLoader.DEFAULT_OPERATIVE_RULES.read_text(
            encoding="utf-8"
        ).replace("## {}\n".format(heading), ""),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="C3 operative rules"):
        GovernanceLoader(operative_rules_source=source).load(
            canonical_constitution()
        )


def test_loader_rejects_wrong_norm_level_and_missing_version(tmp_path):
    with pytest.raises(ValueError, match="C1"):
        GovernanceLoader().load(
            canonical_constitution().replace(
                "Normstufe: C1",
                "Normstufe: C2",
            )
        )
    with pytest.raises(ValueError, match="C1 contract has no version"):
        GovernanceLoader().load(
            canonical_constitution().replace("Version: 2.0\n", "")
        )

    charter = tmp_path / "charter.md"
    charter.write_text(
        GovernanceLoader.DEFAULT_CHARTER.read_text(
            encoding="utf-8"
        ).replace("Version: 1.0\n", ""),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="version"):
        GovernanceLoader(charter_source=charter).load(
            canonical_constitution()
        )


def test_loader_rejects_missing_or_invalid_sources(tmp_path):
    with pytest.raises(FileNotFoundError):
        GovernanceLoader(
            charter_source=tmp_path / "missing.md"
        ).load(canonical_constitution())

    source = tmp_path / "charter.md"
    source.write_bytes(b"\xff")
    with pytest.raises(UnicodeError):
        GovernanceLoader(charter_source=source).load(
            canonical_constitution()
        )


def test_governance_context_rejects_invalid_fields():
    valid = {
        "charter_content": "# Charter",
        "charter_source": Path("charter.md"),
        "charter_version": "1.0",
        "charter_hash": "a" * 64,
        "operative_rules_content": "# Rules",
        "operative_rules_source": Path("rules.md"),
        "operative_rules_version": "1.0",
        "operative_rules_hash": "b" * 64,
        "constitution_hash": "c" * 64,
        "norm_levels": tuple(NormLevel),
        "protection_goals": tuple(ProtectionGoal),
        "bodies": tuple(GovernanceBody),
        "trust_domains": tuple(TrustDomain),
    }

    for name, value in (
        ("charter_content", ""),
        ("charter_source", "charter.md"),
        ("charter_version", ""),
        ("charter_hash", "invalid"),
        ("operative_rules_content", ""),
        ("operative_rules_source", "rules.md"),
        ("operative_rules_version", ""),
        ("operative_rules_hash", "invalid"),
        ("constitution_hash", "invalid"),
        ("norm_levels", tuple(reversed(tuple(NormLevel)))),
        (
            "protection_goals",
            tuple(reversed(tuple(ProtectionGoal))),
        ),
        ("bodies", tuple(reversed(tuple(GovernanceBody)))),
        (
            "trust_domains",
            tuple(reversed(tuple(TrustDomain))),
        ),
    ):
        invalid = dict(valid)
        invalid[name] = value
        with pytest.raises((TypeError, ValueError)):
            GovernanceContext(**invalid)


def test_runtime_boot_exposes_canonical_governance_context(monkeypatch):
    monkeypatch.setattr(
        "builder.runtime.ProjectState.collect",
        lambda self: {"verified_facts": {}},
    )

    runtime = RuntimeManager().boot()

    assert runtime.governance_context == GovernanceLoader().load(
        runtime.constitution
    )
