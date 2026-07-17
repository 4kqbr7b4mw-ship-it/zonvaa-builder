from datetime import datetime
from pathlib import Path

import typer

from agents.role_agent import RoleAgent
from agents.tasks import build_handover_task
from brain.context_analyzer import ContextAnalyzer
from brain.context_collector import ContextCollector


role_agent = RoleAgent()
context_collector = ContextCollector()
context_analyzer = ContextAnalyzer()


def handover(title: str = typer.Argument(...)) -> None:
    project_context = context_collector.collect()
    analyzed_context = context_analyzer.analyze(project_context)

    task = build_handover_task(
        title=title,
        project_context=analyzed_context,
    )

    content = role_agent.run("handover", task)

    folder = Path("knowledge/sessions")
    folder.mkdir(parents=True, exist_ok=True)

    safe_title = "".join(
        character if character.isalnum() or character in "-_" else "-"
        for character in title.strip()
    ).strip("-")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = folder / f"{timestamp}_{safe_title}.md"

    filename.write_text(content, encoding="utf-8")

    typer.echo(f"✅ Übergabe erstellt: {filename}")


if __name__ == "__main__":
    typer.run(handover)
