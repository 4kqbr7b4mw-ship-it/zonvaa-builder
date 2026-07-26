# ADR-0029 – Architecture Workflow Orchestrator

## Status

Beschlossen

## Kontext

ADR-0028 trennt Architecture Integrator, Chief Architect und Codex bereits
verbindlich. Die bestehenden Einzelbefehle analysieren jedoch jeweils ein
Proposal oder erzeugen aus zwei bereitgestellten Dateien einen Prompt. Ein
reproduzierbarer Standardprozess für mehrere Entwürfe, getrennte
Zwischenartefakte und das ausdrückliche Warten auf alle erforderlichen
Chief-Architect-Entscheidungen fehlt.

## Entscheidung

ZONVAA führt den Architecture Workflow Orchestrator als Standardprozess für
Architekturentscheidungen ein:

```text
Proposal(s)
→ Architecture Integrator
→ Decision Proposal
→ Chief Architect
→ Decision Record
→ Architecture Integrator
→ Codex Prompt
→ Codex
→ Tests
→ Commit
```

Der Orchestrator verantwortet ausschließlich den Prozess bis zur Erzeugung
des Codex-Auftrags. Codex-Ausführung, Tests und Commit bleiben Inhalt des
erzeugten Auftrags und werden vom Workflow weder gestartet noch überwacht.

### Autoritätsgrenze

Der Orchestrator:

- nimmt ein oder mehrere typisierte Proposals entgegen,
- ruft für jedes Proposal den bestehenden Architecture Integrator auf,
- persistiert dessen Analyse und kompakte Entscheidungsvorlage,
- wartet auf je ein separates passendes `ChiefArchitectDecision`,
- und erzeugt erst dann einen gemeinsamen eigenständigen Codex-Auftrag.

Er trifft keine Empfehlung zusätzlich zum Integrator, bestätigt keine
Architektur, verändert keine MDRs oder ADRs, startet Codex nicht und erzeugt
keinen Commit. Eine strukturvalide Entscheidung bleibt eine ausdrücklich
bereitgestellte Chief-Architect-Entscheidung; der Workflow leitet sie nicht
selbst ab.

### Reproduzierbarkeit und Reihenfolge

Proposal-IDs müssen stabil, eindeutig und dateisicher sein. Mehrere Proposals
werden nach ID kanonisch geordnet. Die Workflow-ID ist der gekürzte SHA-256
der kanonischen vollständigen Proposal- und Analyse-Daten einschließlich der
geladenen Architekturquellen und ihrer Hashes. Der Erstellungszeitpunkt ist
der späteste bereits in den Proposals bestätigte Einreichungszeitpunkt und
keine neue Laufzeitzufälligkeit.

Gleiche Proposal-Inhalte und gleicher Architekturstand erzeugen dieselbe
Workflow-ID, Reihenfolge, Analyse und Entscheidungsvorlage. Eine identische
Wiederholung nimmt den vorhandenen Workflow wieder auf. Abweichende Artefakte
unter derselben ID werden nicht überschrieben.

### Getrennte Ablage

Nicht bindende Arbeitsartefakte liegen ausschließlich unter:

`knowledge/architecture_workflows/<workflow_id>/`

Jeder Workflow trennt:

- `proposals/`,
- `analyses/`,
- `decision_proposals/`,
- `decisions/`,
- `prompts/`,
- sowie ein versioniertes `workflow.json`.

Die initiale Gruppe wird vor ihrer Sichtbarkeit in einem temporären
Verzeichnis vollständig erstellt und als Verzeichnis veröffentlicht.
Entscheidungen und Prompt sind write-once und überschreiben keine bestehenden
Artefakte. Kanonische Pfade und Symlink-Grenzen werden beim Lesen und
Schreiben geprüft.

Diese Ablage ist weder MDR noch ADR und entfaltet keine normative Wirkung.

### Zustände und Gate

Der berechnete, nicht frei gesetzte Status ist:

- `WAITING_FOR_DECISION`: mindestens eine Entscheidung fehlt,
- `READY_FOR_CODEX`: jede Proposal-ID besitzt genau einen validierten
  Decision Record,
- `CODEX_PROMPT_GENERATED`: der gemeinsame Prompt wurde write-once erzeugt.

`generate-codex` scheitert, solange eine Entscheidung fehlt. Eine
fallfremde, doppelte oder nach Prompt-Erzeugung eingereichte Entscheidung wird
abgelehnt. Der Workflow löst keine Konflikte und verändert keine
Integrator-Analyse.

### CLI

Der Standardpfad lautet:

```text
architecture workflow analyze
architecture workflow decide
architecture workflow generate-codex
```

Die bestehenden Integrator-Einzelbefehle bleiben für direkte Analyse und
validierte Einzelprompt-Erzeugung kompatibel.

## Folgen

- Der gesamte vorbereitende Architekturprozess ist lokal nachvollziehbar und
  wiederaufnehmbar.
- Mehrere Entwürfe teilen denselben verbindlichen Kontext, behalten aber
  getrennte Analysen und Entscheidungen.
- Fehlende Chief-Architect-Entscheidungen sind ein sichtbarer Wartezustand,
  kein Anlass für automatische Freigabe.
- RuntimeManager und KnowledgeManager bleiben die Quellen des
  Architekturkontexts; der Orchestrator baut keine zweite Analyse.

## Nicht-Ziele

Nicht implementiert werden automatische Freigabe, Abstimmung,
Repository-Integration, Codex-Ausführung, Testausführung, Commit oder Push,
externe KI-Aufrufe, Netzwerkzugriffe oder UI.
