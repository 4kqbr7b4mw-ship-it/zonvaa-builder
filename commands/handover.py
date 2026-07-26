from pathlib import Path

import typer

from builder.handover import HandoverWriter, load_handover_input


def handover(
    input_file: Path = typer.Option(
        ...,
        "--input",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
    ),
) -> None:
    """Create local machine- and human-readable handover files."""
    try:
        record = load_handover_input(input_file)
        json_path, markdown_path = HandoverWriter().write(record)
    except (OSError, TypeError, ValueError) as error:
        typer.echo(
            "Handover failed: {}: {}".format(
                type(error).__name__,
                error,
            ),
            err=True,
        )
        raise typer.Exit(code=1)
    typer.echo("JSON: {}".format(json_path))
    typer.echo("Markdown: {}".format(markdown_path))
