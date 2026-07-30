import json
from pathlib import Path

import typer

from builder_task import (
    BuilderTaskService,
    CommitApproval,
    PushApproval,
    TaskRunError,
)

task_app = typer.Typer(help="Run immutable local development tasks.")


def _service() -> BuilderTaskService:
    return BuilderTaskService(Path.cwd())


def _emit(data: object) -> None:
    typer.echo(json.dumps(data, sort_keys=True, indent=2))


@task_app.command("run")
def run_task(input: Path = typer.Option(..., "--input", exists=True, dir_okay=False)) -> None:
    """Guard and execute one immutable task without staging, commit, or push."""
    service = _service()
    try:
        receipt = service.run(service.load_input(input))
    except TaskRunError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=2)
    _emit(receipt.to_dict())


@task_app.command("status")
def task_status(task_id: str = typer.Option(..., "--task-id")) -> None:
    """Read a task and its single run receipt."""
    _emit(_service().status(task_id))


@task_app.command("commit")
def commit_task(
    task_id: str = typer.Option(..., "--task-id"),
    approval: Path = typer.Option(..., "--approval", exists=True, dir_okay=False),
    message: str = typer.Option(..., "--message"),
) -> None:
    """Create one commit from an explicit, diff-bound human approval."""
    data = json.loads(approval.read_text(encoding="utf-8"))
    try:
        commit = _service().commit(task_id, CommitApproval.from_dict(data), message)
    except TaskRunError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=2)
    _emit({"task_id": task_id, "commit": commit})


@task_app.command("push")
def push_task(
    task_id: str = typer.Option(..., "--task-id"),
    approval: Path = typer.Option(..., "--approval", exists=True, dir_okay=False),
) -> None:
    """Push one exact commit using a separate human approval."""
    data = json.loads(approval.read_text(encoding="utf-8"))
    try:
        commit = _service().push(task_id, PushApproval.from_dict(data))
    except TaskRunError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=2)
    _emit({"task_id": task_id, "pushed_commit": commit})
