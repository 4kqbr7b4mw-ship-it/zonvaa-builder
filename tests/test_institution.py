from dataclasses import FrozenInstanceError, fields
from pathlib import Path

import pytest

import builder.runtime as runtime_module
from builder.runtime import RuntimeManager
from institution.loader import InstitutionLoader
from institution.models import InstitutionContext, InstitutionGuarantee


CORE_RULE = "Keine Funktion darf Vertrauen verbrauchen."


def institution_document():
    return """# Institution

Version: 1.0

## Governance

Rules remain accountable.

## Nutzerhoheit

The user retains agency.

## Guardian Continuity

The Guardian remains continuous.

## Transparenz

The system remains explainable.

## Verantwortung

Responsibility remains attributable.

## Schutz

People and knowledge remain protected.

## Würde

Human dignity remains inviolable.

## Vertrauensmodell

Trust must not be consumed.
"""


def test_institution_guarantees_have_stable_complete_values():
    assert [(item.name, item.value) for item in InstitutionGuarantee] == [
        ("GOVERNANCE", "governance"),
        ("USER_SOVEREIGNTY", "user_sovereignty"),
        ("GUARDIAN_CONTINUITY", "guardian_continuity"),
        ("TRANSPARENCY", "transparency"),
        ("RESPONSIBILITY", "responsibility"),
        ("PROTECTION", "protection"),
        ("DIGNITY", "dignity"),
        ("TRUST_MODEL", "trust_model"),
    ]


def test_institution_context_is_small_typed_and_immutable():
    context = InstitutionLoader().load()

    assert [item.name for item in fields(context)] == [
        "content",
        "source",
        "version",
        "content_hash",
        "guarantees",
    ]
    assert context.guarantees == tuple(InstitutionGuarantee)
    with pytest.raises(FrozenInstanceError):
        context.version = "changed"


def test_canonical_institution_charter_loads_deterministically():
    first = InstitutionLoader().load()
    second = InstitutionLoader().load()

    assert first == second
    assert first.source == InstitutionLoader.DEFAULT_SOURCE.resolve()
    assert first.version == "1.2"
    assert CORE_RULE in first.content


@pytest.mark.parametrize(
    "missing_heading",
    [
        "Governance",
        "Nutzerhoheit",
        "Guardian Continuity",
        "Transparenz",
        "Verantwortung",
        "Schutz",
        "Würde",
        "Vertrauensmodell",
    ],
)
def test_loader_rejects_missing_guarantee_sections(
    tmp_path,
    missing_heading,
):
    source = tmp_path / "institution.md"
    content = institution_document().replace(
        "## {0}\n".format(missing_heading),
        "",
    )
    source.write_text(content, encoding="utf-8")

    with pytest.raises(ValueError, match="Garantien"):
        InstitutionLoader(source).load()


def test_loader_rejects_missing_version(tmp_path):
    source = tmp_path / "institution.md"
    source.write_text(
        institution_document().replace("Version: 1.0\n", ""),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Version"):
        InstitutionLoader(source).load()


def test_loader_rejects_heading_that_only_starts_like_guarantee(tmp_path):
    source = tmp_path / "institution.md"
    source.write_text(
        institution_document().replace(
            "## Governance",
            "## Governance extension",
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Governance"):
        InstitutionLoader(source).load()


def test_loader_rejects_missing_or_invalid_source(tmp_path):
    with pytest.raises(FileNotFoundError):
        InstitutionLoader(tmp_path / "missing.md").load()

    source = tmp_path / "institution.md"
    source.write_bytes(b"\xff")
    with pytest.raises(UnicodeError):
        InstitutionLoader(source).load()


def test_institution_context_rejects_invalid_fields():
    valid = {
        "content": "# Institution",
        "source": Path("institution.md"),
        "version": "1.0",
        "content_hash": "a" * 64,
        "guarantees": tuple(InstitutionGuarantee),
    }

    for name, value in (
        ("content", ""),
        ("source", "institution.md"),
        ("version", ""),
        ("content_hash", "not-a-hash"),
        ("guarantees", tuple(reversed(tuple(InstitutionGuarantee)))),
    ):
        invalid = dict(valid)
        invalid[name] = value
        with pytest.raises((TypeError, ValueError)):
            InstitutionContext(**invalid)


def test_runtime_boot_exposes_canonical_institution_context(monkeypatch):
    monkeypatch.setattr(
        "builder.runtime.ProjectState.collect",
        lambda self: {"verified_facts": {}},
    )
    runtime = RuntimeManager().boot()

    assert runtime.institution_context == InstitutionLoader().load()


def test_runtime_loads_identity_institution_interaction_and_governance(
    monkeypatch,
):
    calls = []
    identity_loader = runtime_module.IdentityLoader
    institution_loader = runtime_module.InstitutionLoader
    interaction_loader = runtime_module.InteractionLoader
    constitution_manager = runtime_module.ConstitutionManager
    governance_loader = runtime_module.GovernanceLoader

    class RecordingIdentityLoader:
        def load(self):
            calls.append("identity")
            return identity_loader().load()

    class RecordingInstitutionLoader:
        def load(self):
            calls.append("institution")
            return institution_loader().load()

    class RecordingInteractionLoader:
        def load(self):
            calls.append("interaction")
            return interaction_loader().load()

    class RecordingConstitutionManager:
        def load(self):
            calls.append("constitution")
            return constitution_manager().load()

    class RecordingGovernanceLoader:
        def load(self, constitution):
            calls.append("governance")
            return governance_loader().load(constitution)

    monkeypatch.setattr(
        runtime_module,
        "IdentityLoader",
        RecordingIdentityLoader,
    )
    monkeypatch.setattr(
        runtime_module,
        "InstitutionLoader",
        RecordingInstitutionLoader,
    )
    monkeypatch.setattr(
        runtime_module,
        "InteractionLoader",
        RecordingInteractionLoader,
    )
    monkeypatch.setattr(
        runtime_module,
        "ConstitutionManager",
        RecordingConstitutionManager,
    )
    monkeypatch.setattr(
        runtime_module,
        "GovernanceLoader",
        RecordingGovernanceLoader,
    )
    monkeypatch.setattr(
        runtime_module.ProjectState,
        "collect",
        lambda self: {"verified_facts": {}},
    )

    RuntimeManager().boot()

    assert calls[:5] == [
        "identity",
        "institution",
        "interaction",
        "constitution",
        "governance",
    ]
