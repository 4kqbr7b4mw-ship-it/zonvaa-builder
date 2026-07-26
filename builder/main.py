import typer

from builder.runtime import get_runtime
from commands.build import build
from commands.architecture import (
    create_codex_prompt,
    integrate_architecture,
    workflow_app,
)
from commands.doctor import doctor
from commands.handover import handover
from commands.goal import run_goal
from commands.init import init
from commands.preflight import preflight
from commands.role import create_role
from commands.release import release

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
architecture_app.add_typer(workflow_app, name="workflow")

app.add_typer(role_app, name="role")
app.add_typer(goal_app, name="goal")
app.add_typer(architecture_app, name="architecture")


@app.callback()
def main(ctx: typer.Context) -> None:
    """Initialisiert die Builder-Runtime."""
    if ctx.invoked_subcommand not in {"goal", "preflight"}:
        get_runtime()


if __name__ == "__main__":
    app()
