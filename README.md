# ZONVAA Builder

## Arbeitskontext für einen neuen Chat

Die verbindliche Arbeitsweise steht ausschließlich in [AGENTS.md](AGENTS.md),
der aktuelle fachliche Produktstand in
[knowledge/project/current-product-status.md](knowledge/project/current-product-status.md).
Chatgedächtnis ist keine Projektquelle. Codex führt für eine Übergabe

```text
python3 -m builder.main handover
```

aus und liefert den vollständigen Text zurück; der Nutzer muss dafür keine
Terminalbefehle ausführen. Der Befehl liest ausschließlich Repository-Dokumente
und lokalen Git-Zustand. Er schreibt keine Dateien, führt keine Tests aus und
stößt weder Staging, Commit noch Push an.

## Bestätigte Architektur lokal ausführen

Die [Automated Codex Execution Bridge](codex_execution/README.md) übergibt
ausschließlich vollständig bestätigte Architecture-Workflow-Prompts mit
Decision- und Hash-Nachweis an die lokale Codex CLI. Sie prüft das Ergebnis,
trifft aber keine Entscheidung, erstellt keinen Commit und pusht niemals.

## User-Owned Data

ZONVAA ist eine Intelligence Layer, keine Dokumentenplattform. Der
[User-Owned Data Layer](user_owned_data/README.md) definiert ausschließlich
providerneutrale, nutzerkontrollierte Referenzen auf Originaldaten. Runtime und
KnowledgeManager greifen in dieser Architektur weder direkt auf Dateien noch
auf Cloudspeicher zu; Kopie, Synchronisation und Original-Löschung benötigen
jeweils eine separate ausdrückliche Autorisierung.

## Architekturentwürfe integrieren

Der [Architecture Integrator](architecture_integrator/README.md) vergleicht
externe Architekturentwürfe deterministisch mit Constitution, MDRs,
Governance, Institution, Interaction und ADRs. Er berät ausschließlich; der
Chief Architect entscheidet, und erst eine bestätigte Entscheidung kann in
einen Codex-Auftrag überführt werden.

```text
python3 -m builder.main architecture integrate --input proposal.json
python3 -m builder.main architecture codex-prompt \
  --analysis analysis.json \
  --decision decision.json \
  --output codex-prompt.md
```

Die Befehle rufen keine externen KI-Dienste auf und veröffentlichen keine
Architekturentscheidung.

Der persistente Standardprozess für einen oder mehrere Entwürfe ist:

```text
python3 -m builder.main architecture workflow analyze --input proposal.json
python3 -m builder.main architecture workflow decide \
  --workflow-id workflow-0123456789abcdef \
  --decision decision.json
python3 -m builder.main architecture workflow generate-codex \
  --workflow-id workflow-0123456789abcdef
```

Die Artefakte bleiben getrennt unter `knowledge/architecture_workflows`.
Ohne bestätigte Entscheidung für jedes Proposal wird kein Codex-Auftrag
erzeugt. Der Workflow führt weder Codex noch Tests oder Git-Aktionen aus.

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

### Decision Record

Mit `--record` wird nach einem vollständig abgeschlossenen Lauf zusätzlich ein maschinenlesbarer Decision Record gespeichert:

```text
python3 -m builder.main goal run --input goal.json --record
```

Die unveränderliche JSON-Datei wird unter `knowledge/protocols` abgelegt. Sie enthält Record-Version und UTC-Zeitpunkt, das vollständige Goal, die expliziten Invocation-Daten, Identity-Quelle und -Version, das optionale Assessment sowie Decision, Plan und Execution. Der vollständige WHY-Inhalt wird nicht dupliziert. Der ausgegebene JSON-Wert `record_path` nennt die gespeicherte Datei.

Ohne `--record` bleibt die Ausgabe unverändert und es wird keine Journaldatei geschrieben.

### Wissensdokumente sicher anwenden

Ein Goal-Input kann optional `artifacts` mit vollständigen neuen Wissensdokumenten enthalten:

```json
{
  "artifacts": [
    {
      "action": "document.create",
      "path": "knowledge/project/example.md",
      "content": "# Example\n"
    }
  ]
}
```

Ohne weitere Flagge werden diese Schritte ausschließlich geplant und als `pending` ausgegeben. Erst die ausdrückliche Freigabe schreibt die Dokumente:

```text
python3 -m builder.main goal run --input proposal.json --apply
```

`--apply` akzeptiert ausschließlich neue relative Dateiziele unterhalb von `knowledge/`. Absolute Pfade, `..`-Traversal, Symlinks, `knowledge` selbst und vorhandene Dateien werden abgelehnt. Die gesamte Dokumentgruppe wird vor dem ersten Schreiben validiert und relativ zum bestätigten Git-Repository-Root ausgeführt. `git.sync` bleibt `pending`; es wird weder automatisch committed noch gepusht. `--apply` kann mit `--record` kombiniert werden; dann wird auch ein fehlgeschlagener Apply-Versuch ohne vollständige Dokumentinhalte nachvollziehbar aufgezeichnet.
