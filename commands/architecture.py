import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import typer

from architecture_integrator import (
    ArchitectureContextLoader,
    ArchitectureFeedbackLoop,
    ArchitectureFeedbackStore,
    ArchitectureIntegrator,
    ArchitectureWorkflowOrchestrator,
    ArchitectureWorkflowStore,
    ArchitectureOperationQuery,
    ArchitectureOperationQueryError,
    ArchitectureOperationsAgent,
    ArchitectureQueryFailureCode,
    ArchitectureReviewDecisionError,
    ArchitectureReviewDecisionService,
    ArchitectureWorkflowSupersessionError,
    ArchitectureWorkflowSupersessionStore,
    CodexPromptBuilder,
    render_operation,
    load_review_decision_input,
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
    ArchitectureExecutionPreparationService,
    CodexExecutionOrchestrator,
    CodexExecutionRequest,
    CodexExecutionStatus,
    CodexExecutionService,
    ExecutionBridgeError,
    ExecutionStore,
)
from codex_execution.reconstruction import (
    ExecutionReconstructionAuthorization,
    ExecutionReconstructionError,
    ExecutionReconstructionRequest,
    ExecutionReconstructionService,
    ReconstructionSource,
)


workflow_app = typer.Typer(
    help="Persistente Architekturentscheidungs-Workflows verwalten"
)
execution_app = typer.Typer(
    help="Lokale Codex-Ausführungen sicher verwalten"
)
review_app = typer.Typer(
    help="Chief-Architect-Entscheidungen zu Implementierungsreviews"
)


def migrate_architecture_review_decision(
    review_id: str = typer.Option(..., "--review-id"),
) -> None:
    """Migrate one legacy review decision to its versioned canonical path."""
    try:
        decision = ArchitectureReviewDecisionService(
            repository=Path.cwd(),
            workflows=ArchitectureWorkflowStore(),
        ).migrate(review_id)
    except (
        ArchitectureReviewDecisionError,
        OSError,
        TypeError,
        ValueError,
    ) as error:
        payload = (
            error.to_dict()
            if isinstance(error, ArchitectureReviewDecisionError)
            else {
                "code": "REVIEW_DECISION_MIGRATION_FAILED",
                "message": "{}: {}".format(type(error).__name__, error),
            }
        )
        typer.echo(json.dumps(
            {"error": payload},
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ))
        raise typer.Exit(code=1)
    typer.echo(json.dumps(
        decision.to_dict(),
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ))


def supersede_architecture_workflow(
    superseded_workflow_id: str = typer.Option(
        ...,
        "--superseded-workflow-id",
    ),
    canonical_workflow_id: str = typer.Option(
        ...,
        "--canonical-workflow-id",
    ),
    reason: str = typer.Option(..., "--reason"),
) -> None:
    """Persist one explicit immutable workflow supersession."""
    try:
        record = ArchitectureWorkflowSupersessionStore(
            ArchitectureWorkflowStore()
        ).record(
            superseded_workflow_id=superseded_workflow_id,
            canonical_workflow_id=canonical_workflow_id,
            reason=reason,
            recorded_at=datetime.now().astimezone(),
        )
    except (
        ArchitectureWorkflowSupersessionError,
        OSError,
        TypeError,
        ValueError,
    ) as error:
        typer.echo(json.dumps(
            {
                "error": {
                    "code": "WORKFLOW_SUPERSESSION_FAILED",
                    "message": "{}: {}".format(
                        type(error).__name__,
                        error,
                    ),
                }
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ))
        raise typer.Exit(code=1)
    typer.echo(json.dumps(
        record.to_dict(),
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ))


def decide_architecture_review(
    review_id: str = typer.Option(..., "--review-id"),
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
    """Persist one explicit Chief Architect implementation-review decision."""
    try:
        request = load_review_decision_input(decision_file)
        decision = ArchitectureReviewDecisionService(
            repository=Path.cwd(),
            workflows=ArchitectureWorkflowStore(),
        ).decide(
            review_id=review_id,
            request=request,
            decided_at=datetime.now().astimezone(),
        )
    except (
        ArchitectureReviewDecisionError,
        OSError,
        TypeError,
        ValueError,
    ) as error:
        payload = (
            error.to_dict()
            if isinstance(error, ArchitectureReviewDecisionError)
            else {
                "code": "REVIEW_DECISION_FAILED",
                "message": "{}: {}".format(type(error).__name__, error),
            }
        )
        typer.echo(json.dumps(
            {"error": payload},
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ))
        raise typer.Exit(code=1)
    typer.echo(json.dumps(
        decision.to_dict(),
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ))


def architecture_status(
    topic: Optional[str] = typer.Option(None, "--topic"),
    workflow_id: Optional[str] = typer.Option(None, "--workflow-id"),
    architecture_run_id: Optional[str] = typer.Option(
        None,
        "--architecture-run-id",
    ),
    execution_id: Optional[str] = typer.Option(None, "--execution-id"),
    review_id: Optional[str] = typer.Option(None, "--review-id"),
    commit: Optional[str] = typer.Option(None, "--commit"),
    handover_path: Optional[str] = typer.Option(None, "--handover-path"),
    proposal_id: Optional[str] = typer.Option(None, "--proposal-id"),
    decision_id: Optional[str] = typer.Option(None, "--decision-id"),
    orchestration_id: Optional[str] = typer.Option(
        None, "--orchestration-id"
    ),
    authorization_id: Optional[str] = typer.Option(
        None, "--authorization-id"
    ),
    orchestration_status: Optional[str] = typer.Option(
        None, "--orchestration-status"
    ),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Show deterministic read-only architecture operation status."""
    _show_operations(
        _operation_query(
            topic,
            workflow_id,
            architecture_run_id,
            execution_id,
            review_id,
            commit,
            handover_path,
            proposal_id,
            decision_id,
            orchestration_id,
            authorization_id,
            orchestration_status,
        ),
        json_output,
    )


def architecture_next(
    topic: Optional[str] = typer.Option(None, "--topic"),
    workflow_id: Optional[str] = typer.Option(None, "--workflow-id"),
    architecture_run_id: Optional[str] = typer.Option(
        None,
        "--architecture-run-id",
    ),
    execution_id: Optional[str] = typer.Option(None, "--execution-id"),
    review_id: Optional[str] = typer.Option(None, "--review-id"),
    commit: Optional[str] = typer.Option(None, "--commit"),
    handover_path: Optional[str] = typer.Option(None, "--handover-path"),
    proposal_id: Optional[str] = typer.Option(None, "--proposal-id"),
    decision_id: Optional[str] = typer.Option(None, "--decision-id"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Show exactly one next permissible architecture step."""
    query = _operation_query(
        topic,
        workflow_id,
        architecture_run_id,
        execution_id,
        review_id,
        commit,
        handover_path,
        proposal_id,
        decision_id,
    )
    try:
        matches = _operations_agent().find(query)
        if len(matches) != 1:
            raise ArchitectureOperationQueryError(
                _ambiguous_failure(matches)
            )
    except (OSError, TypeError, ValueError, ArchitectureOperationQueryError) as error:
        _operations_error(error, json_output)
    status = matches[0]
    if json_output:
        typer.echo(json.dumps(
            {
                "schema_version": "1.0",
                "workflow_id": status.workflow_id,
                "next_step": status.next_step.value,
                "issues": [item.to_dict() for item in status.issues],
            },
            indent=2,
            sort_keys=True,
        ))
    else:
        typer.echo(status.next_step.value)


def architecture_artifacts(
    topic: Optional[str] = typer.Option(None, "--topic"),
    workflow_id: Optional[str] = typer.Option(None, "--workflow-id"),
    architecture_run_id: Optional[str] = typer.Option(
        None,
        "--architecture-run-id",
    ),
    execution_id: Optional[str] = typer.Option(None, "--execution-id"),
    review_id: Optional[str] = typer.Option(None, "--review-id"),
    commit: Optional[str] = typer.Option(None, "--commit"),
    handover_path: Optional[str] = typer.Option(None, "--handover-path"),
    proposal_id: Optional[str] = typer.Option(None, "--proposal-id"),
    decision_id: Optional[str] = typer.Option(None, "--decision-id"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """List persisted artifacts and explicitly missing expectations."""
    query = _operation_query(
        topic,
        workflow_id,
        architecture_run_id,
        execution_id,
        review_id,
        commit,
        handover_path,
        proposal_id,
        decision_id,
    )
    try:
        matches = _operations_agent().find(query)
        if len(matches) != 1:
            raise ArchitectureOperationQueryError(
                _ambiguous_failure(matches)
            )
    except (OSError, TypeError, ValueError, ArchitectureOperationQueryError) as error:
        _operations_error(error, json_output)
    status = matches[0]
    if json_output:
        typer.echo(json.dumps(
            {
                "schema_version": "1.0",
                "workflow_id": status.workflow_id,
                "artifacts": [
                    item.to_dict() for item in status.artifacts
                ],
            },
            indent=2,
            sort_keys=True,
        ))
    else:
        typer.echo("\n".join(
            "{}: {} [{}]".format(
                item.kind,
                item.path or "missing",
                item.availability.value,
            )
            for item in status.artifacts
        ))


def architecture_reviews(
    topic: Optional[str] = typer.Option(None, "--topic"),
    workflow_id: Optional[str] = typer.Option(None, "--workflow-id"),
    architecture_run_id: Optional[str] = typer.Option(
        None,
        "--architecture-run-id",
    ),
    execution_id: Optional[str] = typer.Option(None, "--execution-id"),
    review_id: Optional[str] = typer.Option(None, "--review-id"),
    commit: Optional[str] = typer.Option(None, "--commit"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """List reviews awaiting an explicit Chief Architect decision."""
    query = _operation_query(
        topic,
        workflow_id,
        architecture_run_id,
        execution_id,
        review_id,
        commit,
        None,
        None,
        None,
    )
    try:
        agent = _operations_agent()
        reviews = agent.reviews()
        if not query.empty:
            selected = agent.find(query)
            selected_ids = {item.workflow_id for item in selected}
            reviews = tuple(
                item for item in reviews
                if item.workflow_id in selected_ids
            )
    except (OSError, TypeError, ValueError, ArchitectureOperationQueryError) as error:
        _operations_error(error, json_output)
    if json_output:
        typer.echo(json.dumps(
            {
                "schema_version": "1.0",
                "reviews": [item.to_dict() for item in reviews],
            },
            indent=2,
            sort_keys=True,
        ))
    else:
        typer.echo(
            "\n\n---\n\n".join(render_operation(item) for item in reviews)
            or "Keine entscheidungsreifen Reviews."
        )


def _operation_query(
    topic: Optional[str],
    workflow_id: Optional[str],
    architecture_run_id: Optional[str],
    execution_id: Optional[str],
    review_id: Optional[str],
    commit: Optional[str],
    handover_path: Optional[str],
    proposal_id: Optional[str],
    decision_id: Optional[str],
    orchestration_id: Optional[str] = None,
    authorization_id: Optional[str] = None,
    orchestration_status: Optional[str] = None,
) -> ArchitectureOperationQuery:
    return ArchitectureOperationQuery(
        topic=topic,
        workflow_id=workflow_id,
        architecture_run_id=architecture_run_id,
        execution_id=execution_id,
        review_id=review_id,
        commit=commit,
        handover_path=handover_path,
        proposal_id=proposal_id,
        decision_id=decision_id,
        orchestration_id=orchestration_id,
        authorization_id=authorization_id,
        orchestration_status=orchestration_status,
    )


def _operations_agent() -> ArchitectureOperationsAgent:
    return ArchitectureOperationsAgent(
        repository=Path.cwd(),
        workflows=ArchitectureWorkflowStore(),
    )


def _show_operations(
    query: ArchitectureOperationQuery,
    json_output: bool,
) -> None:
    try:
        statuses = _operations_agent().find(query)
    except (OSError, TypeError, ValueError, ArchitectureOperationQueryError) as error:
        _operations_error(error, json_output)
    if json_output:
        typer.echo(json.dumps(
            {
                "schema_version": "1.0",
                "operations": [item.to_dict() for item in statuses],
            },
            indent=2,
            sort_keys=True,
        ))
    else:
        typer.echo("\n\n---\n\n".join(
            render_operation(item) for item in statuses
        ))


def _ambiguous_failure(matches):
    from architecture_integrator.operations import (
        ArchitectureOperationQueryFailure,
    )
    return ArchitectureOperationQueryFailure(
        ArchitectureQueryFailureCode.AMBIGUOUS_QUERY,
        "The architecture query is ambiguous.",
        tuple(item.workflow_id for item in matches),
    )


def _operations_error(error: BaseException, json_output: bool) -> None:
    if isinstance(error, ArchitectureOperationQueryError):
        payload = error.failure.to_dict()
    else:
        payload = {
            "code": ArchitectureQueryFailureCode.INVALID_QUERY.value,
            "message": "{}: {}".format(type(error).__name__, error),
            "candidates": [],
        }
    if json_output:
        typer.echo(json.dumps({"error": payload}, indent=2, sort_keys=True))
    else:
        typer.echo(
            "{}: {}".format(payload["code"], payload["message"]),
            err=True,
        )
    raise typer.Exit(code=1)


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
    create_commit: bool = typer.Option(
        False,
        "--create-commit/--no-create-commit",
        help="Explicitly authorize one validated commit; default: disabled.",
    ),
) -> None:
    """Generate a Codex order only after every required decision."""
    try:
        orchestrator = _workflow_orchestrator()
        path = orchestrator.generate_codex(
            workflow_id,
            create_commit=create_commit,
        )
        status = orchestrator.store.status(workflow_id)
        authorization = _feedback_loop(
            workflows=orchestrator.store,
            integrator=orchestrator.integrator,
        ).authorize(workflow_id, create_commit=create_commit)
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        _workflow_error("Codex prompt generation", error)
    typer.echo(
        json.dumps(
            {
                "workflow_id": workflow_id,
                "status": status.value,
                "codex_prompt": str(path),
                "authorization": authorization.to_dict(),
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
    create_commit: bool = typer.Option(
        False,
        "--create-commit/--no-create-commit",
        help="Explicitly authorize one validated commit; default: disabled.",
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
            create_commit=create_commit,
        )
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        _workflow_error("run", error)
    if result.status.value == "WAITING_FOR_DECISION":
        typer.echo(result.decision_template)
        return
    feedback = _feedback_loop(
        workflows=orchestrator.store,
        integrator=orchestrator.integrator,
    ).advance(
        result.workflow.workflow_id,
        create_commit=create_commit,
    )
    typer.echo(
        json.dumps(
            {
                "workflow_id": result.workflow.workflow_id,
                "status": result.status.value,
                "codex_prompt": str(result.codex_prompt),
                "feedback": feedback.to_dict(),
            },
            indent=2,
            sort_keys=True,
        )
    )
    if feedback.status.value == "FAILED":
        raise typer.Exit(code=1)


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
    workflow_id: Optional[str] = typer.Option(None, "--workflow-id"),
    orchestration_id: Optional[str] = typer.Option(
        None, "--orchestration-id"
    ),
) -> None:
    """Show one orchestration or legacy Bridge execution record."""
    try:
        if orchestration_id is not None:
            records = tuple(
                item for item in _orchestration_service().store.records()
                if item.orchestration_id == orchestration_id
            )
            if len(records) != 1:
                raise RuntimeError("No unique orchestration exists")
            typer.echo(json.dumps(
                records[0].to_dict(), indent=2, sort_keys=True
            ))
            return
        if workflow_id is None:
            raise ValueError(
                "--orchestration-id or --workflow-id is required"
            )
        record = _execution_service().status(workflow_id)
        if record is None:
            raise RuntimeError("No execution exists")
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        _workflow_error("execution status", error)
    typer.echo(
        json.dumps(record.to_dict(), indent=2, sort_keys=True)
    )


def run_execution_orchestration(
    workflow_id: str = typer.Option(..., "--workflow-id"),
) -> None:
    """Run one explicitly authorized workflow through controlled Codex."""
    try:
        result = _orchestration_service().run(
            CodexExecutionRequest(workflow_id)
        )
    except (
        ExecutionBridgeError,
        OSError,
        RuntimeError,
        TypeError,
        ValueError,
    ) as error:
        _workflow_error("execution orchestration", error)
    typer.echo(json.dumps(
        result.orchestration.to_dict(), indent=2, sort_keys=True
    ))
    if result.orchestration.status.value not in {
        "COMMIT_READY",
        "COMPLETED",
    }:
        raise typer.Exit(code=1)


def prepare_execution_orchestration(
    workflow_id: str = typer.Option(..., "--workflow-id"),
) -> None:
    """Capture the immutable authorized workflow preparation baseline."""
    try:
        baseline = _preparation_service().prepare(workflow_id)
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        _workflow_error("execution preparation", error)
    typer.echo(json.dumps(
        baseline.to_dict(), indent=2, sort_keys=True
    ))


def execution_preparation_status(
    workflow_id: str = typer.Option(..., "--workflow-id"),
) -> None:
    """Show a preparation baseline without creating or changing it."""
    try:
        service = _preparation_service()
        baseline = service.store.read(workflow_id)
        if baseline is None:
            raise RuntimeError("No preparation baseline exists")
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        _workflow_error("execution preparation status", error)
    typer.echo(json.dumps(
        baseline.to_dict(), indent=2, sort_keys=True
    ))


def list_execution_orchestrations(
    workflow_id: Optional[str] = typer.Option(None, "--workflow-id"),
    architecture_run_id: Optional[str] = typer.Option(
        None, "--architecture-run-id"
    ),
    execution_id: Optional[str] = typer.Option(None, "--execution-id"),
    authorization_id: Optional[str] = typer.Option(
        None, "--authorization-id"
    ),
    status: Optional[str] = typer.Option(None, "--status"),
) -> None:
    """List persisted orchestration runs without starting a process."""
    try:
        records = _orchestration_service().store.records(workflow_id)
        filters = (
            ("architecture_run_id", architecture_run_id),
            ("execution_id", execution_id),
            ("authorization_id", authorization_id),
        )
        for field_name, value in filters:
            if value is not None:
                records = tuple(
                    item for item in records
                    if getattr(item, field_name) == value
                )
        if status is not None:
            expected_status = CodexExecutionStatus(status)
            records = tuple(
                item for item in records if item.status is expected_status
            )
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        _workflow_error("execution orchestration list", error)
    typer.echo(json.dumps(
        {"orchestrations": [item.to_dict() for item in records]},
        indent=2,
        sort_keys=True,
    ))


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
        service = _execution_service()
        feedback = _feedback_loop(
            workflows=service.workflows,
            execution=service,
        )
        results = ArchitectureExecutionWatcher(
            service,
            completion_callback=feedback.advance,
        ).run_once()
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        _workflow_error("execution watcher", error)
    typer.echo(
        json.dumps({"results": list(results)}, indent=2, sort_keys=True)
    )


def reconstruct_execution(
    authorization_file: Path = typer.Option(
        ...,
        "--authorization",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
    ),
    reconstructed_at: str = typer.Option(..., "--reconstructed-at"),
) -> None:
    """Reconstruct and review one explicitly authorized direct execution."""
    try:
        authorization = ExecutionReconstructionAuthorization.from_dict(
            json.loads(authorization_file.read_text(encoding="utf-8"))
        )
        workflows = ArchitectureWorkflowStore()
        service = ExecutionReconstructionService(
            repository=Path.cwd(),
            workflows=workflows,
            integrator=ArchitectureIntegrator(
                ArchitectureContextLoader(get_runtime())
            ),
        )
        result = service.reconstruct(
            ExecutionReconstructionRequest(
                authorization=authorization,
                reconstructed_at=datetime.fromisoformat(reconstructed_at),
                source=ReconstructionSource.CHIEF_ARCHITECT_AUTHORIZATION,
            )
        )
    except ExecutionReconstructionError as error:
        typer.echo(
            json.dumps(
                {"error": error.failure.to_dict()},
                indent=2,
                sort_keys=True,
            ),
            err=True,
        )
        raise typer.Exit(code=1)
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        _workflow_error("execution reconstruction", error)
    typer.echo(json.dumps(result.to_dict(), indent=2, sort_keys=True))


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


def _orchestration_service() -> CodexExecutionOrchestrator:
    return CodexExecutionOrchestrator(
        workflows=ArchitectureWorkflowStore(),
        repository=Path.cwd(),
    )


def _preparation_service() -> ArchitectureExecutionPreparationService:
    return ArchitectureExecutionPreparationService(
        workflows=ArchitectureWorkflowStore(),
        repository=Path.cwd(),
    )


def feedback_status(
    workflow_id: str = typer.Option(..., "--workflow-id"),
) -> None:
    """Show the machine-readable Architecture-to-Codex pipeline status."""
    try:
        workflows = ArchitectureWorkflowStore()
        record = ArchitectureFeedbackStore(workflows).record(workflow_id)
        if record is None:
            raise RuntimeError("No feedback loop exists")
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        _workflow_error("feedback status", error)
    typer.echo(json.dumps(record.to_dict(), indent=2, sort_keys=True))


def _feedback_loop(
    workflows: Optional[ArchitectureWorkflowStore] = None,
    execution: Optional[CodexExecutionService] = None,
    integrator: Optional[ArchitectureIntegrator] = None,
) -> ArchitectureFeedbackLoop:
    workflow_store = workflows or ArchitectureWorkflowStore()
    architecture_integrator = integrator or ArchitectureIntegrator(
        ArchitectureContextLoader(get_runtime())
    )
    execution_service = execution or CodexExecutionService(
        workflows=workflow_store,
        executions=ExecutionStore(workflow_store),
    )
    return ArchitectureFeedbackLoop(
        workflows=workflow_store,
        execution=execution_service,
        integrator=architecture_integrator,
        repository=execution_service.repository,
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
workflow_app.command("feedback-status")(feedback_status)
execution_app.command("status")(execution_status)
execution_app.command("run")(run_execution_orchestration)
execution_app.command("prepare")(prepare_execution_orchestration)
execution_app.command("preparation-status")(execution_preparation_status)
execution_app.command("list")(list_execution_orchestrations)
execution_app.command("retry")(retry_execution)
execution_app.command("cancel")(cancel_execution)
execution_app.command("watch-once")(watch_executions_once)
execution_app.command("reconstruct")(reconstruct_execution)
