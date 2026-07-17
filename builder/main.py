import typer

from agents.document_agent import DocumentAgent
from agents.git_agent import GitAgent

app = typer.Typer()

document_agent = DocumentAgent()
git_agent = GitAgent()


@app.command()
def hello():
    print("🚀 Willkommen beim ZONVAA Builder")


@app.command()
def status():
    print("✅ ZONVAA Builder ist bereit")


@app.command()
def doc(name: str, sync: bool = False):
    document_agent.create(name)

    if sync:
        git_agent.sync(f"Create {name} document")


if __name__ == "__main__":
    app()