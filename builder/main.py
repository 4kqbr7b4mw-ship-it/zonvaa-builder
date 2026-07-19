import typer

from builder.runtime import get_runtime
from commands.build import build
from commands.doctor import doctor
from commands.handover import handover
from commands.init import init
from commands.role import create_role
from commands.release import release

app = typer.Typer(help="ZONVAA Builder CLI")

role_app = typer.Typer(help="Rollen verwalten")

app.command("build")(build)
app.command("handover")(handover)
app.command("doctor")(doctor)
app.command("init")(init)
app.command("release")(release)

role_app.command("create")(create_role)

app.add_typer(role_app, name="role")


@app.callback()
def main() -> None:
    """Initialisiert die Builder-Runtime."""
    get_runtime()


if __name__ == "__main__":
    app()
