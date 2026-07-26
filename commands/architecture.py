import json
from pathlib import Path
from typing import Optional

import typer

from architecture_integrator import (
    ArchitectureContextLoader,
    ArchitectureIntegrator,
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
