from pathlib import Path

import typer

from builder.chat_handover import ChatHandover


def handover() -> None:
    """Print the canonical read-only context for a new ZONVAA chat."""
    try:
        text = ChatHandover(Path.cwd()).render()
    except (OSError, TypeError, ValueError) as error:
        typer.echo(
            "Handover failed: {}: {}".format(
                type(error).__name__,
                error,
            ),
            err=True,
        )
        raise typer.Exit(code=1)
    typer.echo(text, nl=False)
