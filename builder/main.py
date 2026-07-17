import typer

from constitution.manager import ConstitutionManager
from commands.doctor import doctor
from commands.handover import handover
from commands.init import init
from commands.role import create_role

app = typer.Typer(help="ZONVAA Builder CLI")

role_app = typer.Typer(help="Rollen verwalten")

app.command("handover")(handover)
app.command("doctor")(doctor)
app.command("init")(init)

role_app.command("create")(create_role)

app.add_typer(role_app, name="role")


@app.callback()
def main() -> None:
    """Initialisiert die Builder-Runtime."""

    ConstitutionManager().load()


if __name__ == "__main__":
    app()
