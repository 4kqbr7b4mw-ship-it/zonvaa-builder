# ADR-0035 – Architecture-to-Codex Feedback Loop

## Status

Beschlossen

## Kontext

ADR-0028 bis ADR-0031 trennen Architecture Integrator, Chief Architect,
Architecture Workflow und Codex. ADR-0034 transportiert bestätigte Aufträge
bereits sicher zur lokalen Execution Bridge und prüft deren Ergebnis.

Nach einem erfolgreichen Codex-Lauf endet die maschinenlesbare Kette jedoch am
Execution Record. Das Handover muss manuell zum Integrator zurückgetragen
werden. Diese Transportlücke ist weder eine notwendige menschliche
Entscheidung noch eine Schutzgrenze.

## Entscheidung

ZONVAA schließt den lokalen Artefaktfluss:

```text
bestätigte Entscheidung
→ Execution-Autorisierung
→ bestehende Execution Bridge
→ Result-Commit und Handover
→ validierter Handover-Intake
→ nicht bindende Integrator-Review
→ Chief-Architect-Entscheidung erforderlich
```

Der Chief Architect bleibt die einzige Instanz, die Architektur annimmt,
ändert, ablehnt oder vertagt. Weder Workflow, Bridge noch Integrator geben das
Implementierungsergebnis automatisch frei.

### Autorisierungsartefakt

Ein bestätigter Workflow erzeugt unter seinem bestehenden Workflow-Ordner eine
typisierte, versionierte Autorisierung. Sie bindet:

- Architecture-Run, Workflow, Entscheidungen und Freigabestatus,
- erwartete Execution-ID, kanonischen Prompt und dessen Hash,
- Repository und erwarteten Basis-Commit,
- erlaubte Aktionen und erwartete Abschlussartefakte.

Die Bridge prüft das Artefakt zusätzlich zum bestehenden Prompt-Proof, sofern
es vorhanden ist. Eine Abweichung des Basis-Commits blockiert vor Codex.
Historische bestätigte Workflows ohne Feedback-Artefakt bleiben unter dem
bisherigen ADR-0034-Vertrag kompatibel.

Der bestätigte Architecture-Workflow kann seine eigenen noch uncommittierten
Kontrollartefakte unter dem exakt zugeordneten Workflow-Ordner mitführen.
Diese eng begrenzte Ausnahme ersetzt nicht die Clean-Tree-Regel: jede Änderung
außerhalb dieses Ordners blockiert weiterhin vor Codex. Der resultierende
Codex-Commit und die abschließende Clean-Tree-Prüfung bleiben unverändert.

### Persistierter Zustand

Der Feedback-Vertrag verwendet ausschließlich typisierte Zustände:

- `DECISION_CONFIRMED`
- `EXECUTION_AUTHORIZED`
- `EXECUTION_RUNNING`
- `EXECUTION_COMPLETED`
- `HANDOVER_DISCOVERED`
- `HANDOVER_VALIDATED`
- `INTEGRATOR_REVIEW_READY`
- `CHIEF_ARCHITECT_DECISION_REQUIRED`
- `FAILED`

Übergänge werden geordnet und append-only im Workflow gespeichert.
Wiederholungen verwenden identische Autorisierung, Intake und Review; sie
starten keine erfolgreiche Execution erneut und erzeugen keine zweite
Entscheidungsvorlage.

### Handover-Zuordnung und Validierung

Die Zuordnung erfolgt nicht über den neuesten Dateinamen. Ausgangspunkt sind
Execution-ID, Result-Commit und die expliziten Handover-Pfade des bestehenden
Execution Records. Das JSON-Handover muss Basis- und Ergebnis-Commit,
geänderte Dateien, Checks, Git-Status, Risiken und Push-Status enthalten.

Vor dem Intake werden Autorisierung, Execution, Commit-Kette, Test-, Doctor-
und Diff-Ergebnis sowie die No-Push-Grenze geprüft. Fehlende oder
widersprüchliche Angaben werden als strukturierte Abweichungen gespeichert.
Sie erzeugen keine automatische Freigabe.

Schema 1.0 des bestehenden Handovers enthält keine Execution-ID. Bis zu einer
separat beschlossenen Schemaentwicklung wird die Zugehörigkeit deshalb über
den Execution Record und den belegten Commit-Diff hergestellt; es werden keine
IDs nachträglich erfunden.

### Integrator-Review

Der Architecture Integrator verarbeitet den validierten Intake als eigene
Eingabeart. Seine Entscheidungsvorlage enthält ursprüngliche Decisions,
Codex-Prompt-Referenz, Execution und Attempts, Result-Commit, Änderungen,
Checks, Git-Status, Abweichungen, Konflikte und Risiken.

Die Ausgabe ist eine Empfehlung. Sie enthält immer eine ausdrückliche neue
Chief-Architect-Entscheidungspflicht und niemals ein Decision Record.

### CLI und Watcher

`python3 -m builder.main architecture run` bleibt der Standard-Einstieg und
stößt nach vollständiger bestätigter Entscheidung die lokale Kette an. Der
Watcher kann nach erfolgreicher Bridge-Ausführung denselben idempotenten
Feedback-Schritt auslösen.

Der Gesamtzustand ist maschinenlesbar über
`architecture workflow feedback-status` abrufbar.

## Sicherheitsgrenzen

- Keine automatische Architekturfreigabe oder Änderung bestätigter Decisions.
- Keine parallele Execution-, Queue- oder Audit-Infrastruktur.
- Kein Push ohne ausdrückliche Autorisierung; der Standard erlaubt keinen Push.
- Keine Verarbeitung fremder, nicht im Execution Record referenzierter
  Handovers.
- Keine Shell-Interpolation, Cloud-Persistenz, externe KI-Konflikterkennung
  oder Netzwerklogik.
- Handover und Review übernehmen nur strukturierte Metadaten, keine Prompt-
  Inhalte, Secrets oder vollständigen Dokumentinhalte.

## Folgen und offene Grenzen

Der Nutzer ist nicht länger Datei-Transportweg zwischen Architecture Workflow,
Codex und Integrator. Die notwendige menschliche Grenze bleibt ausschließlich
die Chief-Architect-Entscheidung.

Recovery eines nichtterminalen Attempts, Capability Verification,
Login-Shell-/PATH-Härtung und ein Handover-Schema mit nativer Execution-ID sind
separate mögliche Architekturbausteine.
