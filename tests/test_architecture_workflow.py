import hashlib
import json
from types import SimpleNamespace
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


class FakeFeedbackLoop:
    def authorize(self, workflow_id, create_commit=False):
        return SimpleNamespace(
            to_dict=lambda: {
                "workflow_id": workflow_id,
                "approval_status": "CONFIRMED",
                "create_commit": create_commit,
            }
        )

    def advance(self, workflow_id, create_commit=False):
        return SimpleNamespace(
            status=SimpleNamespace(
                value="CHIEF_ARCHITECT_DECISION_REQUIRED"
            ),
            to_dict=lambda: {
                "workflow_id": workflow_id,
                "status": "CHIEF_ARCHITECT_DECISION_REQUIRED",
                "create_commit": create_commit,
            }
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
        folder / "decision_proposals" / "decision-proposal.md"
    ).is_file()
    assert workflow.schema_version == "2.0"
    assert workflow.topic == "Proposal proposal-a / Proposal proposal-b"
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
    monkeypatch.setattr(
        architecture_commands,
        "_feedback_loop",
        lambda **kwargs: FakeFeedbackLoop(),
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
    assert json.loads(generated.output)["authorization"][
        "create_commit"
    ] is False


def test_architecture_run_emits_only_compact_decision_template(
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
    proposal_path.write_text(
        json.dumps(
            proposal(
                "proposal-a",
                "New architecture statement.",
            ).to_dict()
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "architecture",
            "run",
            "--topic",
            "Architecture Workflow v2",
            "--proposal",
            str(proposal_path),
        ],
    )

    assert result.exit_code == 0, result.output
    assert result.output.startswith("# ENTSCHEIDUNGSVORLAGE\n")
    assert tuple(
        line for line in result.output.splitlines() if line.startswith("## ")
    ) == (
        "## Empfehlung",
        "## Übernehmen",
        "## Ändern",
        "## Ablehnen",
        "## Offene Entscheidungen",
    )
    assert "MACHINE-READABLE" not in result.output
    assert "Kernaussage" not in result.output
    assert "Betroffene Architektur" not in result.output
    workflow = next(
        path for path in flow.store.root.iterdir() if path.is_dir()
    )
    assert flow.store.status(workflow.name) is (
        WorkflowStatus.WAITING_FOR_DECISION
    )


def test_architecture_run_records_decisions_and_generates_prompt_automatically(
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
    monkeypatch.setattr(
        architecture_commands,
        "_feedback_loop",
        lambda **kwargs: FakeFeedbackLoop(),
    )
    first = proposal("proposal-a", "First architecture statement.")
    second = proposal("proposal-b", "Second architecture statement.")
    workflow = flow.run(
        proposals=(first, second),
        topic="Architecture Workflow v2",
    ).workflow
    first_decision = tmp_path / "decision-a.json"
    second_decision = tmp_path / "decision-b.json"
    first_decision.write_text(
        json.dumps(decision("proposal-a").to_dict()),
        encoding="utf-8",
    )
    second_decision.write_text(
        json.dumps(decision("proposal-b").to_dict()),
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "architecture",
            "run",
            "--workflow-id",
            workflow.workflow_id,
            "--decision",
            str(first_decision),
            "--decision",
            str(second_decision),
            "--create-commit",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload == {
        "codex_prompt": str(
            flow.store.prompt_path(workflow.workflow_id)
        ),
        "status": "CODEX_PROMPT_GENERATED",
        "workflow_id": workflow.workflow_id,
        "feedback": {
            "status": "CHIEF_ARCHITECT_DECISION_REQUIRED",
            "workflow_id": workflow.workflow_id,
            "create_commit": True,
        },
    }
    assert flow.store.status(workflow.workflow_id) is (
        WorkflowStatus.CODEX_PROMPT_GENERATED
    )
    assert len(flow.store.decisions(workflow.workflow_id)) == 2
    assert flow.store.prompt_path(workflow.workflow_id).is_file()
    proof = flow.store.prompt_proof(workflow.workflow_id)
    assert proof["workflow_id"] == workflow.workflow_id
    assert proof["decision_ids"] == [
        "decision-proposal-a",
        "decision-proposal-b",
    ]
    assert proof["prompt_hash"] == hashlib.sha256(
        flow.store.prompt_path(workflow.workflow_id).read_bytes()
    ).hexdigest()


def test_architecture_run_waits_when_only_some_decisions_exist(
    runtime,
    tmp_path,
):
    flow = orchestrator(runtime, tmp_path / "workflows")
    waiting = flow.run(
        proposals=(
            proposal("proposal-a", "First architecture statement."),
            proposal("proposal-b", "Second architecture statement."),
        ),
        topic="Architecture Workflow v2",
        decisions=(decision("proposal-a"),),
    )

    assert waiting.status is WorkflowStatus.WAITING_FOR_DECISION
    assert waiting.decision_template.startswith("# ENTSCHEIDUNGSVORLAGE")
    assert waiting.codex_prompt is None
    assert not flow.store.prompt_path(
        waiting.workflow.workflow_id
    ).exists()


def test_architecture_run_rejects_missing_input(runtime, tmp_path):
    flow = orchestrator(runtime, tmp_path / "workflows")

    with pytest.raises(ValueError, match="Proposals or"):
        flow.run()


def test_workflow_v2_topic_changes_deterministic_identity(runtime, tmp_path):
    first = orchestrator(runtime, tmp_path / "first").analyze(
        (proposal("proposal-a", "Architecture statement."),),
        topic="First topic",
    )
    second = orchestrator(runtime, tmp_path / "second").analyze(
        (proposal("proposal-a", "Architecture statement."),),
        topic="Second topic",
    )

    assert first.workflow_id != second.workflow_id


def test_architecture_run_result_is_immutable(runtime, tmp_path):
    flow = orchestrator(runtime, tmp_path / "workflows")
    result = flow.run(
        proposals=(
            proposal("proposal-a", "Architecture statement."),
        ),
        topic="Architecture Workflow v2",
    )

    with pytest.raises(FrozenInstanceError):
        result.status = WorkflowStatus.READY_FOR_CODEX


def test_store_reads_existing_workflow_schema_1(runtime, tmp_path):
    root = tmp_path / "workflows"
    folder = root / "workflow-0123456789abcdef"
    for name in (
        "proposals",
        "analyses",
        "decision_proposals",
        "decisions",
        "prompts",
    ):
        (folder / name).mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": "1.0",
        "workflow_id": folder.name,
        "created_at": "2026-07-26T18:00:00+00:00",
        "proposal_ids": ["proposal-a"],
        "proposal_files": ["proposals/proposal-a.json"],
        "analysis_files": ["analyses/proposal-a.json"],
        "decision_template_files": [
            "decision_proposals/proposal-a.md"
        ],
    }
    (folder / "workflow.json").write_text(
        json.dumps(manifest),
        encoding="utf-8",
    )
    (folder / "decision_proposals" / "proposal-a.md").write_text(
        "# ENTSCHEIDUNGSVORLAGE\n",
        encoding="utf-8",
    )
    store = ArchitectureWorkflowStore(root)

    workflow = store.load(folder.name)

    assert workflow.schema_version == "1.0"
    assert workflow.topic == ""
    assert store.status(folder.name) is WorkflowStatus.WAITING_FOR_DECISION
    assert store.decision_template(folder.name) == (
        "# ENTSCHEIDUNGSVORLAGE"
    )


def _tree(folder: Path) -> dict:
    return {
        path.relative_to(folder).as_posix(): path.read_bytes()
        for path in sorted(folder.rglob("*"))
        if path.is_file()
    }
