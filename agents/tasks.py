import json
from datetime import datetime


def build_handover_task(
    title: str,
    project_context: dict,
) -> str:
    """Erstellt die konkrete Aufgabe für den Handover-Agenten."""

    runtime_evidence = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "command": f"python3 -m builder.main handover {title}",
        "confirmed_during_current_execution": [
            "builder.main konnte gestartet werden",
            "der handover-Command wurde erfolgreich aufgerufen",
            "ContextCollector.collect() wurde erfolgreich ausgeführt",
            "build_handover_task() wurde erfolgreich ausgeführt",
            "agents/handover.md wurde durch RoleAgent erfolgreich geladen",
            "OPENAI_API_KEY und OPENAI_MODEL konnten verwendet werden",
            "die OpenAI Responses API hat die Anfrage angenommen",
            "der Handover-Agent erzeugt aktuell diese Übergabe",
        ],
    }

    return f"""
Erstelle eine vollständige, präzise und faktenbasierte Chatübergabe
für den aktuellen Stand des ZONVAA Builders.

Titel: {title}

Verwende ausschließlich die bereitgestellten Projektdaten und die
automatisch bestätigten Laufzeitfakten.

Erfinde keine Funktionen, Dateien, Entscheidungen, Tests oder Fortschritte.

Wichtige Regel:

Die unter „Automatisch bestätigte Laufzeitfakten“ aufgeführten Punkte
sind durch die aktuell laufende Ausführung bestätigt und dürfen nicht
als unbestätigt bezeichnet werden.

Priorisiere:

1. Was wurde in der letzten Session umgesetzt?
2. Was funktioniert nachweislich?
3. Welche Entscheidungen wurden getroffen?
4. Welche Probleme oder Risiken bestehen?
5. Was ist exakt der nächste Schritt?

Die Übergabe soll kompakt bleiben.
Keine Wiederholungen.
Keine allgemeine Projektdokumentation.
Keine unnötige Beschreibung jeder einzelnen Datei.
Keine widersprüchlichen Aussagen.

## Automatisch bestätigte Laufzeitfakten

{json.dumps(runtime_evidence, ensure_ascii=False, indent=2)}

## Projektkontext

{json.dumps(project_context, ensure_ascii=False, indent=2)}
"""
