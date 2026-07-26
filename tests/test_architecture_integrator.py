import hashlib
import json
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from pathlib import Path

import pytest
from typer.testing import CliRunner

from architecture_integrator import (
    ArchitectureContextLoader,
    ArchitectureIntegrator,
    ArchitectureLayer,
    ArchitectureProposal,
    ChiefArchitectDecision,
    CodexPromptBuilder,
    DecisionChoice,
    NormLevel,
    SourceRole,
    SourceStatus,
)
from architecture_integrator.io import (
    load_analysis,
    load_decision,
    load_proposal,
)
from builder.main import app
from builder.runtime import RuntimeManager


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def runtime() -> RuntimeManager:
    return RuntimeManager().boot()


def proposal(content: str) -> ArchitectureProposal:
    return ArchitectureProposal(
        proposal_id="proposal-001",
        title="Portable Guardian extension",
        source="anonymized external draft",
        source_role=SourceRole.OTHER,
        submitted_at=datetime(2026, 7, 26, tzinfo=timezone.utc),
        content=content,
        requested_scope="Guardian and governance architecture",
        related_layers=(
            ArchitectureLayer.GUARDIAN,
            ArchitectureLayer.GOVERNANCE,
        ),
        known_constraints=("Do not weaken C1 or MDR-0001.",),
        source_references=(
            "knowledge/mdr/"
            "MDR-0001-guardian-conversation-and-continuity.md",
        ),
    )


def integrator(runtime: RuntimeManager) -> ArchitectureIntegrator:
    return ArchitectureIntegrator(ArchitectureContextLoader(runtime))


def decision() -> ChiefArchitectDecision:
    return ChiefArchitectDecision(
        decision_id="decision-001",
        proposal_id="proposal-001",
        decision=DecisionChoice.ADOPT_WITH_CHANGES,
        accepted_elements=("Add a documented export guarantee.",),
        modified_elements=("Keep explicit user authorization.",),
        rejected_elements=("Do not bypass user sovereignty.",),
        deferred_elements=("Defer concrete storage technology.",),
        rationale="The accepted scope preserves existing protection goals.",
        decided_by="Chief Architect",
        decided_at=datetime(2026, 7, 26, tzinfo=timezone.utc),
    )


def test_context_loader_loads_complete_architecture_in_priority_order(runtime):
    sources = ArchitectureContextLoader(runtime).load(
        (ArchitectureLayer.CROSS_LAYER,)
    )
    levels = [source.norm_level for source in sources]

    assert levels == sorted(levels, key=lambda level: level.priority)
    assert levels[0] is NormLevel.C1_CONSTITUTION
    assert NormLevel.MDR in levels
    assert NormLevel.C2_GOVERNANCE in levels
    assert NormLevel.SPECIFICATION in levels
    assert NormLevel.ADR in levels
    assert NormLevel.C3_OPERATIVE in levels
    assert NormLevel.HISTORICAL in levels
    assert levels[-1] is NormLevel.HANDOVER
    assert (
        NormLevel.EXTERNAL.priority
        > NormLevel.HISTORICAL.priority
    )
    assert all(len(source.content_hash) == 64 for source in sources)


def test_mdr_0001_is_prioritized_as_binding_detail_source(runtime):
    analysis = integrator(runtime).analyze(
        proposal("# 1. Guardian und Conversation Engine")
    )

    mdr = next(
        source
        for source in analysis.loaded_context_sources
        if source.source_id.startswith("MDR-0001")
    )
    assert mdr.norm_level is NormLevel.MDR
    assert mdr.status is SourceStatus.BINDING
    assert analysis.duplicate_elements == (
        "1. Guardian und Conversation Engine",
    )
    assert (
        "knowledge/mdr/MDR-0001-guardian-conversation-and-continuity.md"
        in analysis.affected_documents
    )


def test_integrator_detects_normative_conflict_without_resolving_it(runtime):
    analysis = integrator(runtime).analyze(
        proposal("- Umgehung der Nutzerhoheit")
    )

    assert len(analysis.conflicting_elements) == 1
    conflict = analysis.conflicting_elements[0]
    assert conflict.existing_source == "constitution/constitution.md"
    assert conflict.norm_level is NormLevel.C1_CONSTITUTION
    assert conflict.requires_chief_architect_decision is True
    assert "Do not integrate automatically" in conflict.suggested_resolution
    assert analysis.decision_required


def test_integrator_detects_addition(runtime):
    statement = "A review ledger records architecture consultation dates."
    analysis = integrator(runtime).analyze(proposal("- " + statement))

    assert analysis.additive_elements == (statement,)
    assert analysis.conflicting_elements == ()


def test_integrator_detects_exact_redundancy(runtime):
    analysis = integrator(runtime).analyze(
        proposal("- Keine Umgehung der Nutzerhoheit")
    )

    assert analysis.duplicate_elements == (
        "Keine Umgehung der Nutzerhoheit",
    )
    assert analysis.conflicting_elements == ()


def test_historical_adrs_are_not_current_applicable_norms(runtime):
    analysis = integrator(runtime).analyze(proposal("- New neutral statement."))
    historical = {
        source.source_id
        for source in analysis.loaded_context_sources
        if source.norm_level is NormLevel.HISTORICAL
    }

    assert {
        "ADR-0023-guardian-conversation-principles",
        "ADR-0024-guardian-first-workflow-second",
        "ADR-0026-conversation-interaction-architecture",
    } <= historical
    assert historical.isdisjoint(analysis.applicable_norms)


def test_analysis_is_deterministic(runtime):
    first = integrator(runtime).analyze(proposal("- New neutral statement."))
    second = integrator(runtime).analyze(proposal("- New neutral statement."))

    assert first.to_dict() == second.to_dict()


def test_analysis_does_not_modify_architecture_sources(runtime):
    paths = (
        ROOT / "constitution" / "constitution.md",
        ROOT / "knowledge" / "mdr"
        / "MDR-0001-guardian-conversation-and-continuity.md",
        ROOT / "governance" / "charter.md",
        ROOT / "institution" / "institution.md",
        ROOT / "interaction" / "interaction.md",
    )
    before = {
        path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths
    }

    integrator(runtime).analyze(proposal("- New neutral statement."))

    assert {
        path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths
    } == before


def test_models_are_immutable_and_keep_strict_enums():
    item = proposal("- New neutral statement.")

    with pytest.raises(FrozenInstanceError):
        item.title = "changed"
    with pytest.raises(TypeError, match="source_role"):
        ArchitectureProposal(
            proposal_id=item.proposal_id,
            title=item.title,
            source=item.source,
            source_role="GEMINI",
            submitted_at=item.submitted_at,
            content=item.content,
            requested_scope=item.requested_scope,
            related_layers=item.related_layers,
            known_constraints=item.known_constraints,
            source_references=item.source_references,
        )
    with pytest.raises(TypeError, match="related_layers"):
        ArchitectureProposal(
            proposal_id=item.proposal_id,
            title=item.title,
            source=item.source,
            source_role=item.source_role,
            submitted_at=item.submitted_at,
            content=item.content,
            requested_scope=item.requested_scope,
            related_layers=("GUARDIAN",),
            known_constraints=item.known_constraints,
            source_references=item.source_references,
        )


def test_json_loader_rejects_unknown_role_layer_and_status(tmp_path):
    data = proposal("- New neutral statement.").to_dict()
    path = tmp_path / "proposal.json"

    data["source_role"] = "UNAPPROVED"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="source_role"):
        load_proposal(path)

    data["source_role"] = "OTHER"
    data["related_layers"] = ["UNKNOWN"]
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="related_layers"):
        load_proposal(path)

    decision_data = {
        "decision_id": "decision-001",
        "proposal_id": "proposal-001",
        "decision": "APPROVE",
        "accepted_elements": [],
        "modified_elements": [],
        "rejected_elements": [],
        "deferred_elements": [],
        "rationale": "Explicit test decision.",
        "decided_by": "Chief Architect",
        "decided_at": "2026-07-26T17:00:00+00:00",
    }
    decision_path = tmp_path / "decision.json"
    decision_path.write_text(json.dumps(decision_data), encoding="utf-8")
    with pytest.raises(ValueError, match="decision"):
        load_decision(decision_path)


def test_context_loader_rejects_missing_required_sources():
    empty_runtime = RuntimeManager()

    with pytest.raises(RuntimeError, match="incomplete"):
        ArchitectureContextLoader(empty_runtime).load(
            (ArchitectureLayer.CROSS_LAYER,)
        )


def test_unavailable_proposal_reference_is_marked_open(runtime):
    item = proposal("- New neutral statement.")
    item = ArchitectureProposal(
        proposal_id=item.proposal_id,
        title=item.title,
        source=item.source,
        source_role=item.source_role,
        submitted_at=item.submitted_at,
        content=item.content,
        requested_scope=item.requested_scope,
        related_layers=item.related_layers,
        known_constraints=item.known_constraints,
        source_references=("knowledge/mdr/MDR-9999-missing.md",),
    )

    analysis = integrator(runtime).analyze(item)

    assert analysis.unresolved_questions[0] == (
        "Source reference was not loaded: "
        "knowledge/mdr/MDR-9999-missing.md"
    )


def test_prompt_requires_confirmed_chief_architect_decision(runtime):
    analysis = integrator(runtime).analyze(proposal("- New neutral statement."))

    with pytest.raises(TypeError, match="confirmed"):
        CodexPromptBuilder().build(analysis, None)


def test_codex_prompt_is_complete_and_chat_independent(runtime):
    analysis = integrator(runtime).analyze(
        proposal("- Add a documented export guarantee.")
    )

    prompt = CodexPromptBuilder().build(analysis, decision())

    assert "Complete submitted architecture content" in prompt
    assert "Add a documented export guarantee." in prompt
    assert "Binding accepted content" in prompt
    assert "Binding modifications" in prompt
    assert "Explicitly rejected content" in prompt
    assert "Deferred content" in prompt
    assert "C1-CONSTITUTION" in prompt
    assert "MDR-0001" in prompt
    assert "python3 -m builder.main doctor" in prompt
    assert "git diff --check" in prompt
    assert "Create JSON and Markdown handover files" in prompt
    assert "Do not push" in prompt
    assert "previous chat" not in prompt.casefold()
    assert "siehe " not in prompt.casefold()


def test_decision_template_has_exact_compact_structure(runtime):
    analysis = integrator(runtime).analyze(proposal("- New neutral statement."))
    rendered = integrator(runtime).render_decision_template(analysis)

    assert tuple(
        line for line in rendered.splitlines() if line.startswith("#")
    ) == (
        "# ENTSCHEIDUNGSVORLAGE",
        "## Empfehlung",
        "## Kernaussage",
        "## Übernehmen",
        "## Ändern",
        "## Ablehnen",
        "## Konflikte",
        "## Betroffene Architektur",
        "## Entscheidung erforderlich",
    )


def test_cli_outputs_human_and_machine_readable_analysis(runtime, tmp_path):
    input_path = tmp_path / "proposal.json"
    output_path = tmp_path / "analysis.json"
    input_path.write_text(
        json.dumps(proposal("- New neutral statement.").to_dict()),
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "architecture",
            "integrate",
            "--input",
            str(input_path),
            "--output",
            str(output_path),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "# ENTSCHEIDUNGSVORLAGE" in result.output
    assert "# MACHINE-READABLE ANALYSIS" in result.output
    assert json.loads(output_path.read_text(encoding="utf-8"))[
        "proposal"
    ]["proposal_id"] == "proposal-001"


def test_documented_examples_are_schema_valid_and_build_prompt():
    examples = ROOT / "examples" / "architecture_integrator"
    analysis = load_analysis(examples / "analysis.json")
    example_decision = load_decision(examples / "decision.json")

    prompt = CodexPromptBuilder().build(analysis, example_decision)

    assert analysis.proposal == load_proposal(examples / "proposal.json")
    assert "Chief Architect decision" in prompt
