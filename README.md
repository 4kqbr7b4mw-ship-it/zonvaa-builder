# ZONVAA Builder

## Goal ausführen

Ein vorhandenes Goal kann programmgesteuert über den Goal Application Service ausgeführt werden:

```text
python3 -m builder.main goal run --input goal.json
```

Die UTF-8-JSON-Datei enthält alle expliziten Laufdaten. Das bestehende Goal-Modell verlangt `priority`, `status` und einen zeitzonenbehafteten ISO-8601-Zeitpunkt für `created_at`. Mindestens ein gültiger Memory-Typ ist erforderlich.

Ohne WHY-Assessment:

```json
{
  "goal": {
    "id": "goal-001",
    "title": "Beispielziel",
    "description": "Beschreibung",
    "project": "ZONVAA",
    "priority": "high",
    "status": "active",
    "owner": "Michael",
    "created_at": "2026-07-23T10:00:00+02:00"
  },
  "role": "builder",
  "memory_types": ["project_memory"],
  "constitution_rules": [],
  "why_assessment": null
}
```

Mit einem bereits ausdrücklich festgelegten Assessment:

```json
{
  "goal": {
    "id": "goal-001",
    "title": "Beispielziel",
    "description": "Beschreibung",
    "project": "ZONVAA",
    "priority": "high",
    "status": "active",
    "owner": "Michael",
    "created_at": "2026-07-23T10:00:00+02:00"
  },
  "role": "builder",
  "memory_types": ["project_memory"],
  "constitution_rules": ["Explizit ausgewählte Regel"],
  "why_assessment": {
    "status": "aligned",
    "reason": "explicit_alignment_confirmed",
    "evidence": ["Manuell bestätigte Bewertung"]
  }
}
```

Die CLI erzeugt keine WHY-Bewertung. Status, Reason und Evidence stammen ausschließlich aus der Eingabedatei; Goal-Bindung und Identity-Version werden aus dem aktuellen Lauf hergestellt. Das Ergebnis wird als JSON mit `decision`, `plan` und `execution` ausgegeben.
