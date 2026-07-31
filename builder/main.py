import typer

from builder.runtime import get_runtime
from commands.build import build
from commands.architecture import (
    architecture_artifacts,
    architecture_next,
    architecture_reviews,
    architecture_status,
    decide_architecture_review,
    migrate_architecture_review_decision,
    supersede_architecture_workflow,
    create_codex_prompt,
    execute_architecture,
    execution_app,
    integrate_architecture,
    run_architecture,
    workflow_app,
    review_app,
)
from commands.doctor import doctor
from commands.handover import handover
from commands.goal import run_goal
from commands.init import init
from commands.preflight import preflight
from commands.role import create_role
from commands.release import release
from commands.task import task_app
from commands.develop import develop_app

app = typer.Typer(help="ZONVAA Builder CLI")

role_app = typer.Typer(help="Rollen verwalten")
goal_app = typer.Typer(help="Ziele ausführen")
architecture_app = typer.Typer(help="Architekturentwürfe integrieren")

app.command("build")(build)
app.command("handover")(handover)
app.command("doctor")(doctor)
app.command("init")(init)
app.command("preflight")(preflight)
app.command("release")(release)

role_app.command("create")(create_role)
goal_app.command("run")(run_goal)
architecture_app.command("integrate")(integrate_architecture)
architecture_app.command("codex-prompt")(create_codex_prompt)
architecture_app.command("run")(run_architecture)
architecture_app.command("execute")(execute_architecture)
architecture_app.command("status")(architecture_status)
architecture_app.command("next")(architecture_next)
architecture_app.command("artifacts")(architecture_artifacts)
architecture_app.command("reviews")(architecture_reviews)
review_app.command("decide")(decide_architecture_review)
review_app.command("migrate")(migrate_architecture_review_decision)
workflow_app.command("supersede")(supersede_architecture_workflow)
architecture_app.add_typer(workflow_app, name="workflow")
architecture_app.add_typer(execution_app, name="execution")
architecture_app.add_typer(review_app, name="review")

app.add_typer(role_app, name="role")
app.add_typer(goal_app, name="goal")
app.add_typer(architecture_app, name="architecture")
app.add_typer(task_app, name="task")
app.add_typer(develop_app, name="develop")


@app.callback()
def main(ctx: typer.Context) -> None:
    """Initialisiert die Builder-Runtime."""
    if ctx.invoked_subcommand not in {
        "goal",
        "handover",
        "preflight",
        "task",
        "develop",
    }:
        get_runtime()


if __name__ == "__main__":
    app()
