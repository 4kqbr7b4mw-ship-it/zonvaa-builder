from pathlib import Path

from openai import OpenAI

from config.settings import OPENAI_API_KEY, OPENAI_MODEL


class DocumentAgent:

    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

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

        prompt = f"""
Erstelle ein professionelles Markdown-Dokument für ZONVAA.

Dokumenttyp: {name}

ZONVAA ist eine intelligente Decision Factory.
Der Nutzer beschreibt ein Ziel.
ZONVAA analysiert Informationen, plant Schritte, erzeugt Empfehlungen,
Dokumente, Aufgaben, Workflows und nachvollziehbare Entscheidungen.

Schreibe das Dokument auf Deutsch.
Nutze klare Überschriften.
Keine Platzhalter.
Keine Meta-Kommentare.
"""

        response = self.client.responses.create(
            model=OPENAI_MODEL,
            input=prompt,
        )

        content = response.output_text

        Path(filename).write_text(
            content,
            encoding="utf-8"
        )

        print(f"✅ Dokument erstellt: {filename}")