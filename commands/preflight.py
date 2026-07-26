import json

import typer

from builder.preflight import PreflightError, PreflightService
from builder.runtime import get_runtime


def preflight() -> None:
    """Load and validate the mandatory local project context."""
    try:
        context = PreflightService(get_runtime()).build()
    except (OSError, ValueError, RuntimeError, PreflightError) as error:
        typer.echo(
            json.dumps(
                {
                    "status": "failed",
                    "error": {
                        "type": type(error).__name__,
                        "message": str(error),
                    },
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
            err=True,
        )
        raise typer.Exit(code=1)
    typer.echo(
        json.dumps(
            {"status": "ready", "mission_context": context.to_dict()},
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
