from pathlib import Path

from openai import OpenAI

from config.settings import OPENAI_API_KEY, OPENAI_MODEL


class RoleAgent:

    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def run(self, role_name: str, task: str) -> str:

        role_file = Path(f"agents/{role_name}.md")

        if not role_file.exists():
            raise FileNotFoundError(
                f"Rollen-Datei nicht gefunden: {role_file}"
            )

        role_prompt = role_file.read_text(encoding="utf-8")

        prompt = f"""
{role_prompt}

## Konkrete Aufgabe

{task}

Bearbeite die Aufgabe vollständig.
Antworte auf Deutsch.
Keine Meta-Kommentare.
Keine Platzhalter.
"""

        response = self.client.responses.create(
            model=OPENAI_MODEL,
            input=prompt,
        )

        return response.output_text