import json
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from pathlib import Path

import pytest
from typer.testing import CliRunner

import commands.architecture as architecture_commands
from architecture_integrator import (
    ArchitectureContextLoader,
    ArchitectureIntegrator,
    ArchitectureLayer,
    ArchitectureProposal,
    ArchitectureWorkflowOrchestrator,
    ArchitectureWorkflowStore,
    ChiefArchitectDecision,
    DecisionChoice,
    SourceRole,
    WorkflowStatus,
)
from builder.main import app
from builder.runtime import RuntimeManager


@pytest.fixture(scope="module")
def runtime() -> RuntimeManager:
    return RuntimeManager().boot()


def proposal(proposal_id: str, statement: str) -> ArchitectureProposal:
    return ArchitectureProposal(
        proposal_id=proposal_id,
        title="Proposal {}".format(proposal_id),
        source="anonymized architecture source",
        source_role=SourceRole.INTERNAL,
        submitted_at=datetime(2026, 7, 26, 18, 0, tzinfo=timezone.utc),
        content="- {}".format(statement),
        requested_scope="Architecture workflow test",
        related_layers=(ArchitectureLayer.CROSS_LAYER,),
        known_constraints=("Do not weaken binding architecture.",),
        source_references=(
            "knowledge/mdr/"
            "MDR-0001-guardian-conversation-and-continuity.md",
        ),
    )


def decision(proposal_id: str) -> ChiefArchitectDecision:
    return ChiefArchitectDecision(
        decision_id="decision-{}".format(proposal_id),
        proposal_id=proposal_id,
        decision=DecisionChoice.ADOPT,
        accepted_elements=(
            "Accepted content for {}.".format(proposal_id),
        ),
        modified_elements=(),
        rejected_elements=(),
        deferred_elements=(),
        rationale="Explicit Chief Architect test decision.",
        decided_by="Chief Architect",
        decided_at=datetime(2026, 7, 26, 18, 5, tzinfo=timezone.utc),
    )


def orchestrator(
    runtime: RuntimeManager,
    root: Path,
) -> ArchitectureWorkflowOrchestrator:
    return ArchitectureWorkflowOrchestrator(
        ArchitectureIntegrator(ArchitectureContextLoader(runtime)),
        ArchitectureWorkflowStore(root),
    )


def test_complete_workflow_persists_separate_reproducible_stages(
    runtime,
    tmp_path,
):
    flow = orchestrator(runtime, tmp_path / "workflows")
    first = proposal("proposal-a", "First new architecture statement.")
    second = proposal("proposal-b", "Second new architecture statement.")

    workflow = flow.analyze((first, second))

    folder = flow.store.folder(workflow.workflow_id)
    assert flow.store.status(workflow.workflow_id) is (
        WorkflowStatus.WAITING_FOR_DECISION
    )
    assert (folder / "proposals" / "proposal-a.json").is_file()
    assert (folder / "analyses" / "proposal-a.json").is_file()
    assert (
        folder / "decision_proposals" / "proposal-a.md"
    ).is_file()
    assert not (folder / "decisions" / "proposal-a.json").exists()
    assert not flow.store.prompt_path(workflow.workflow_id).exists()

    assert flow.decide(
        workflow.workflow_id,
        decision("proposal-a"),
    ) is WorkflowStatus.WAITING_FOR_DECISION
    assert flow.decide(
        workflow.workflow_id,
        decision("proposal-b"),
    ) is WorkflowStatus.READY_FOR_CODEX

    prompt_path = flow.generate_codex(workflow.workflow_id)

    assert flow.store.status(workflow.workflow_id) is (
        WorkflowStatus.CODEX_PROMPT_GENERATED
    )
    prompt = prompt_path.read_text(encoding="utf-8")
    assert "proposal-a" in prompt
    assert "proposal-b" in prompt
    assert "The workflow made no decision." in prompt
    assert "Do not push." in prompt
    assert prompt.count("## Workflow commit") == 1
    assert prompt.count("## Commit") == 0


def test_multiple_proposals_are_canonicalized_by_stable_id(runtime, tmp_path):
    first = proposal("proposal-a", "First new architecture statement.")
    second = proposal("proposal-b", "Second new architecture statement.")
    left = orchestrator(runtime, tmp_path / "left")
    right = orchestrator(runtime, tmp_path / "right")

    left_workflow = left.analyze((second, first))
    right_workflow = right.analyze((first, second))

    assert left_workflow == right_workflow
    assert left_workflow.proposal_ids == ("proposal-a", "proposal-b")
    assert _tree(left.store.folder(left_workflow.workflow_id)) == _tree(
        right.store.folder(right_workflow.workflow_id)
    )


def test_identical_analysis_resumes_existing_workflow(runtime, tmp_path):
    flow = orchestrator(runtime, tmp_path / "workflows")
    item = proposal("proposal-a", "New architecture statement.")

    first = flow.analyze((item,))
    second = flow.analyze((item,))

    assert first == second
    assert len(tuple(flow.store.root.glob("workflow-*"))) == 1
    with pytest.raises(FrozenInstanceError):
        first.workflow_id = "workflow-0000000000000000"


def test_missing_decision_blocks_codex_prompt(runtime, tmp_path):
    flow = orchestrator(runtime, tmp_path / "workflows")
    workflow = flow.analyze(
        (
            proposal("proposal-a", "First new architecture statement."),
            proposal("proposal-b", "Second new architecture statement."),
        )
    )
    flow.decide(workflow.workflow_id, decision("proposal-a"))

    with pytest.raises(RuntimeError, match="missing.*proposal-b"):
        flow.generate_codex(workflow.workflow_id)

    assert not flow.store.prompt_path(workflow.workflow_id).exists()


def test_decision_for_unrelated_proposal_is_rejected(runtime, tmp_path):
    flow = orchestrator(runtime, tmp_path / "workflows")
    workflow = flow.analyze(
        (proposal("proposal-a", "New architecture statement."),)
    )

    with pytest.raises(ValueError, match="not part"):
        flow.decide(workflow.workflow_id, decision("proposal-other"))


def test_duplicate_proposal_ids_are_rejected_before_persistence(
    runtime,
    tmp_path,
):
    flow = orchestrator(runtime, tmp_path / "workflows")

    with pytest.raises(ValueError, match="unique"):
        flow.analyze(
            (
                proposal("proposal-a", "First statement."),
                proposal("proposal-a", "Second statement."),
            )
        )

    assert not flow.store.root.exists()


def test_workflow_id_rejects_path_traversal(runtime, tmp_path):
    flow = orchestrator(runtime, tmp_path / "workflows")

    with pytest.raises(ValueError, match="workflow_id"):
        flow.store.status("../outside")


def test_cli_workflow_runs_all_gated_stages(
    runtime,
    tmp_path,
    monkeypatch,
):
    flow = orchestrator(runtime, tmp_path / "workflows")
    monkeypatch.setattr(
        architecture_commands,
        "_workflow_orchestrator",
        lambda: flow,
    )
    proposal_path = tmp_path / "proposal.json"
    decision_path = tmp_path / "decision.json"
    proposal_path.write_text(
        json.dumps(
            proposal(
                "proposal-a",
                "New architecture statement.",
            ).to_dict()
        ),
        encoding="utf-8",
    )
    decision_path.write_text(
        json.dumps(decision("proposal-a").to_dict()),
        encoding="utf-8",
    )
    runner = CliRunner()

    analyzed = runner.invoke(
        app,
        [
            "architecture",
            "workflow",
            "analyze",
            "--input",
            str(proposal_path),
        ],
    )
    assert analyzed.exit_code == 0, analyzed.output
    workflow_id = json.loads(analyzed.output)["workflow_id"]

    decided = runner.invoke(
        app,
        [
            "architecture",
            "workflow",
            "decide",
            "--workflow-id",
            workflow_id,
            "--decision",
            str(decision_path),
        ],
    )
    assert decided.exit_code == 0, decided.output
    assert json.loads(decided.output)["status"] == "READY_FOR_CODEX"

    generated = runner.invoke(
        app,
        [
            "architecture",
            "workflow",
            "generate-codex",
            "--workflow-id",
            workflow_id,
        ],
    )
    assert generated.exit_code == 0, generated.output
    assert json.loads(generated.output)["status"] == (
        "CODEX_PROMPT_GENERATED"
    )


def _tree(folder: Path) -> dict:
    return {
        path.relative_to(folder).as_posix(): path.read_bytes()
        for path in sorted(folder.rglob("*"))
        if path.is_file()
    }
