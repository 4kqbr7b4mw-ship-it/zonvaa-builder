from pathlib import Path


class DocumentAgent:

    def create(self, name: str):

        folders = {
            "vision": "foundation",
            "mission": "foundation",
            "manifest": "foundation",
            "values": "foundation",
        }

        folder = folders.get(name.lower(), "documents")

        Path(folder).mkdir(parents=True, exist_ok=True)

        filename = f"{folder}/{name}.md"

        content = f"""# {name.title()}

## Status

Entwurf

## Beschreibung

Dieses Dokument wurde automatisch vom ZONVAA Builder erstellt.
"""

        Path(filename).write_text(
            content,
            encoding="utf-8"
        )

        print(f"✅ Dokument erstellt: {filename}")