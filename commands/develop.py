import json
from pathlib import Path
from typing import List, Optional

import typer

from builder_task.develop import DevelopmentService
from builder_task.models import VetoClassification
from builder_task.service import TaskRunError


develop_app = typer.Typer(
    help="Run one complete development task through Builder Reset v2.",
    invoke_without_command=True,
)


@develop_app.callback()
def develop(
    ctx: typer.Context,
    goal: Optional[str] = typer.Option(None, "--goal"),
    repo: Path = typer.Option(Path("."), "--repo"),
    branch: Optional[str] = typer.Option(None, "--branch"),
    paths: Optional[List[str]] = typer.Option(None, "--paths"),
    veto: Optional[VetoClassification] = typer.Option(None, "--veto"),
    no_commit: bool = typer.Option(False, "--no-commit"),
    no_tests: bool = typer.Option(False, "--no-tests"),
) -> None:
    """Execute a goal or select the separate commit/push commands."""
    if ctx.invoked_subcommand is not None:
        return
    if goal is None:
        raise typer.BadParameter("--goal is required")
    report = DevelopmentService(repo).run(
        goal=goal,
        branch=branch,
        paths=tuple(paths or ()),
        veto=veto,
        no_commit=no_commit,
        no_tests=no_tests,
    )
    typer.echo(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))


@develop_app.command("commit")
def develop_commit(
    repo: Path = typer.Option(Path("."), "--repo"),
    message: Optional[str] = typer.Option(None, "--message"),
    approved_by: str = typer.Option("Human", "--approved-by"),
) -> None:
    """Create one commit after explicit human invocation."""
    try:
        commit = DevelopmentService(repo).commit(message, approved_by)
    except TaskRunError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=2)
    typer.echo(json.dumps({"Commit": commit}, indent=2))


@develop_app.command("push")
def develop_push(
    repo: Path = typer.Option(Path("."), "--repo"),
    remote: str = typer.Option("origin", "--remote"),
    remote_branch: Optional[str] = typer.Option(None, "--remote-branch"),
    approved_by: str = typer.Option("Human", "--approved-by"),
) -> None:
    """Push one exact commit after a separate human invocation."""
    try:
        commit = DevelopmentService(repo).push(
            remote=remote,
            remote_branch=remote_branch,
            approved_by=approved_by,
        )
    except TaskRunError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=2)
    typer.echo(json.dumps({"Gepushter Commit": commit}, indent=2))
