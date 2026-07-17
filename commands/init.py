from pathlib import Path

import typer


def init(name: str) -> None:
    root = Path(name)

    if root.exists():
        raise typer.BadParameter(
            f"Projektordner '{name}' existiert bereits."
        )

    folders = [
        "docs",
        "knowledge",
        "roles",
        "src",
        "tests",
        "config",
        ".github/workflows",
    ]

    for folder in folders:
        (root / folder).mkdir(parents=True, exist_ok=True)

    (root / "README.md").write_text(
        f"# {name}\n",
        encoding="utf-8",
    )

    (root / ".env.example").write_text(
        "OPENAI_API_KEY=\n",
        encoding="utf-8",
    )

    (root / ".gitignore").write_text(
        ".env\n__pycache__/\n.venv/\n",
        encoding="utf-8",
    )

    print(f"✅ Projekt '{name}' wurde erstellt.")
