import typer

from agents.document_agent import DocumentAgent
from agents.git_agent import GitAgent
from builder.planner import Planner

app = typer.Typer()

planner = Planner()
document_agent = DocumentAgent()
git_agent = GitAgent()


@app.command()
def run(goal: str):

    plan = planner.create_plan(goal)

    for step in plan:

        if step["agent"] == "document":
            document_agent.create(step["target"])

        elif step["agent"] == "git":
            git_agent.sync(step["message"])


if __name__ == "__main__":
    app()