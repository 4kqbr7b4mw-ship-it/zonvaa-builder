import json
from pathlib import Path
from typing import List, Optional

import typer

from architecture_integrator import (
    ArchitectureContextLoader,
    ArchitectureIntegrator,
    ArchitectureWorkflowOrchestrator,
    ArchitectureWorkflowStore,
    CodexPromptBuilder,
)
from architecture_integrator.io import (
    load_analysis,
    load_decision,
    load_proposal,
    write_json,
    write_text_atomic,
)
from builder.runtime import get_runtime
from codex_execution import (
    ArchitectureExecutionWatcher,
    CodexExecutionService,
    ExecutionBridgeError,
    ExecutionStore,
)


workflow_app = typer.Typer(
    help="Persistente Architekturentscheidungs-Workflows verwalten"
)
execution_app = typer.Typer(
    help="Lokale Codex-Ausführungen sicher verwalten"
)


def integrate_architecture(
    input_file: Path = typer.Option(
        ...,
        "--input",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
        help="Optional path for the machine-readable analysis JSON.",
    ),
) -> None:
    """Compare an external architecture proposal without approving it."""
    try:
        proposal = load_proposal(input_file)
        integrator = ArchitectureIntegrator(
            ArchitectureContextLoader(get_runtime())
        )
        analysis = integrator.analyze(proposal)
        payload = analysis.to_dict()
        if output is not None:
            write_json(output, payload)
        typer.echo(integrator.render_decision_template(analysis))
        typer.echo("\n# MACHINE-READABLE ANALYSIS")
        typer.echo(
            json.dumps(
                payload,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
        )
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        typer.echo(
            "Architecture integration failed: {}: {}".format(
                type(error).__name__,
                error,
            ),
            err=True,
        )
        raise typer.Exit(code=1)


def create_codex_prompt(
    analysis_file: Path = typer.Option(
        ...,
        "--analysis",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
    ),
    decision_file: Path = typer.Option(
        ...,
        "--decision",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
    ),
    output: Path = typer.Option(
        ...,
        "--output",
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
    ),
) -> None:
    """Create a Codex order from a confirmed Chief Architect decision."""
    try:
        analysis = load_analysis(analysis_file)
        decision = load_decision(decision_file)
        prompt = CodexPromptBuilder().build(analysis, decision)
        write_text_atomic(output, prompt + "\n")
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        typer.echo(
            "Codex prompt creation failed: {}: {}".format(
                type(error).__name__,
                error,
            ),
            err=True,
        )
        raise typer.Exit(code=1)
    typer.echo("Codex prompt: {}".format(output))


def analyze_workflow(
    input_files: List[Path] = typer.Option(
        ...,
        "--input",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help="One or more architecture proposal JSON files.",
    ),
) -> None:
    """Analyze and persist one or more proposals without deciding."""
    try:
        orchestrator = _workflow_orchestrator()
        workflow = orchestrator.analyze(
            tuple(load_proposal(path) for path in input_files)
        )
        status = orchestrator.store.status(workflow.workflow_id)
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        _workflow_error("analysis", error)
    typer.echo(
        json.dumps(
            {
                "workflow_id": workflow.workflow_id,
                "status": status.value,
                "path": str(
                    orchestrator.store.root / workflow.workflow_id
                ),
                "proposal_ids": list(workflow.proposal_ids),
            },
            indent=2,
            sort_keys=True,
        )
    )


def decide_workflow(
    workflow_id: str = typer.Option(..., "--workflow-id"),
    decision_file: Path = typer.Option(
        ...,
        "--decision",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
    ),
) -> None:
    """Persist one explicit Chief Architect decision."""
    try:
        orchestrator = _workflow_orchestrator()
        decision = load_decision(decision_file)
        status = orchestrator.decide(workflow_id, decision)
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        _workflow_error("decision", error)
    typer.echo(
        json.dumps(
            {
                "workflow_id": workflow_id,
                "proposal_id": decision.proposal_id,
                "status": status.value,
            },
            indent=2,
            sort_keys=True,
        )
    )


def generate_workflow_codex(
    workflow_id: str = typer.Option(..., "--workflow-id"),
) -> None:
    """Generate a Codex order only after every required decision."""
    try:
        orchestrator = _workflow_orchestrator()
        path = orchestrator.generate_codex(workflow_id)
        status = orchestrator.store.status(workflow_id)
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        _workflow_error("Codex prompt generation", error)
    typer.echo(
        json.dumps(
            {
                "workflow_id": workflow_id,
                "status": status.value,
                "codex_prompt": str(path),
            },
            indent=2,
            sort_keys=True,
        )
    )


def run_architecture(
    proposal_files: List[Path] = typer.Option(
        [],
        "--proposal",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help="One or more new architecture proposal JSON files.",
    ),
    topic: Optional[str] = typer.Option(
        None,
        "--topic",
        help="Topic for a newly created architecture workflow.",
    ),
    workflow_id: Optional[str] = typer.Option(
        None,
        "--workflow-id",
        help="Existing waiting workflow to continue.",
    ),
    decision_files: List[Path] = typer.Option(
        [],
        "--decision",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help="Confirmed Chief Architect decision JSON files.",
    ),
) -> None:
    """Run the next valid architecture stage through one entry point."""
    try:
        orchestrator = _workflow_orchestrator()
        result = orchestrator.run(
            proposals=tuple(
                load_proposal(path) for path in proposal_files
            ),
            topic=topic,
            workflow_id=workflow_id,
            decisions=tuple(
                load_decision(path) for path in decision_files
            ),
        )
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        _workflow_error("run", error)
    if result.status.value == "WAITING_FOR_DECISION":
        typer.echo(result.decision_template)
        return
    typer.echo(
        json.dumps(
            {
                "workflow_id": result.workflow.workflow_id,
                "status": result.status.value,
                "codex_prompt": str(result.codex_prompt),
            },
            indent=2,
            sort_keys=True,
        )
    )


def execute_architecture(
    workflow_id: str = typer.Option(..., "--workflow-id"),
) -> None:
    """Execute one confirmed workflow prompt through local Codex CLI."""
    try:
        record = _execution_service().execute(workflow_id)
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        _workflow_error("execution", error)
    typer.echo(
        json.dumps(record.to_dict(), indent=2, sort_keys=True)
    )
    if record.status.value != "SUCCEEDED":
        raise typer.Exit(code=1)


def execution_status(
    workflow_id: str = typer.Option(..., "--workflow-id"),
) -> None:
    """Show the local execution record for one workflow."""
    try:
        record = _execution_service().status(workflow_id)
        if record is None:
            raise RuntimeError("No execution exists")
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        _workflow_error("execution status", error)
    typer.echo(
        json.dumps(record.to_dict(), indent=2, sort_keys=True)
    )


def retry_execution(
    workflow_id: str = typer.Option(..., "--workflow-id"),
) -> None:
    """Explicitly retry a failed, blocked or capacity-limited execution."""
    try:
        record = _execution_service().execute(workflow_id, retry=True)
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        _workflow_error("execution retry", error)
    typer.echo(
        json.dumps(record.to_dict(), indent=2, sort_keys=True)
    )
    if record.status.value != "SUCCEEDED":
        raise typer.Exit(code=1)


def cancel_execution(
    workflow_id: str = typer.Option(..., "--workflow-id"),
) -> None:
    """Cancel a non-running local execution by explicit request."""
    try:
        record = _execution_service().cancel(workflow_id)
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        _workflow_error("execution cancellation", error)
    typer.echo(
        json.dumps(record.to_dict(), indent=2, sort_keys=True)
    )


def watch_executions_once() -> None:
    """Run one idempotent watcher scan for launchd."""
    try:
        results = ArchitectureExecutionWatcher(
            _execution_service()
        ).run_once()
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        _workflow_error("execution watcher", error)
    typer.echo(
        json.dumps({"results": list(results)}, indent=2, sort_keys=True)
    )


def _workflow_orchestrator() -> ArchitectureWorkflowOrchestrator:
    integrator = ArchitectureIntegrator(
        ArchitectureContextLoader(get_runtime())
    )
    return ArchitectureWorkflowOrchestrator(
        integrator,
        ArchitectureWorkflowStore(),
    )


def _execution_service() -> CodexExecutionService:
    workflows = ArchitectureWorkflowStore()
    return CodexExecutionService(
        workflows=workflows,
        executions=ExecutionStore(workflows),
    )


def _workflow_error(stage: str, error: BaseException) -> None:
    if isinstance(error, ExecutionBridgeError):
        typer.echo(
            json.dumps(
                {"error": error.failure.to_dict()},
                indent=2,
                sort_keys=True,
            ),
            err=True,
        )
        raise typer.Exit(code=1)
    typer.echo(
        "Architecture workflow {} failed: {}: {}".format(
            stage,
            type(error).__name__,
            error,
        ),
        err=True,
    )
    raise typer.Exit(code=1)


workflow_app.command("analyze")(analyze_workflow)
workflow_app.command("decide")(decide_workflow)
workflow_app.command("generate-codex")(generate_workflow_codex)
execution_app.command("status")(execution_status)
execution_app.command("retry")(retry_execution)
execution_app.command("cancel")(cancel_execution)
execution_app.command("watch-once")(watch_executions_once)
