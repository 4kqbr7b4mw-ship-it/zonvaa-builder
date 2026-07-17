from pathlib import Path

import typer


def create_role(name: str) -> None:
    roles_folder = Path("roles")
    roles_folder.mkdir(parents=True, exist_ok=True)

    filename = roles_folder / f"{name}.md"

    if filename.exists():
        raise typer.BadParameter(
            f"Rolle '{name}' existiert bereits."
        )

    content = f"""# Rolle: {name}

## Version

1.0.0

## Zweck

Beschreibe hier den Zweck der Rolle.

## Verantwortung

- Aufgabe 1
- Aufgabe 2
- Aufgabe 3

## Regeln

- Arbeite präzise.
- Erfinde keine Fakten.
- Dokumentiere Entscheidungen.
- Melde Unsicherheiten klar.

## Eingaben

Beschreibe hier, welche Informationen die Rolle benötigt.

## Ausgaben

Beschreibe hier, welche Ergebnisse die Rolle erzeugen soll.

## Qualitätskriterien

- vollständig
- nachvollziehbar
- testbar
- dokumentiert
"""

    filename.write_text(content, encoding="utf-8")

    print(f"✅ Rolle '{name}' wurde erstellt: {filename}")