import typer

from builder.runtime import get_runtime
from commands.build import build
from commands.doctor import doctor
from commands.handover import handover
from commands.goal import run_goal
from commands.init import init
from commands.role import create_role
from commands.release import release

app = typer.Typer(help="ZONVAA Builder CLI")

role_app = typer.Typer(help="Rollen verwalten")
goal_app = typer.Typer(help="Ziele ausführen")

app.command("build")(build)
app.command("handover")(handover)
app.command("doctor")(doctor)
app.command("init")(init)
app.command("release")(release)

role_app.command("create")(create_role)
goal_app.command("run")(run_goal)

app.add_typer(role_app, name="role")
app.add_typer(goal_app, name="goal")


@app.callback()
def main(ctx: typer.Context) -> None:
    """Initialisiert die Builder-Runtime."""
    if ctx.invoked_subcommand != "goal":
        get_runtime()


if __name__ == "__main__":
    app()
