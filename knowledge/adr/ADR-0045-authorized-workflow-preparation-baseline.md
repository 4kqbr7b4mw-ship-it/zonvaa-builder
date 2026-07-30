# ADR-0045 – Authorized Workflow Preparation Baseline

## Status

Accepted

## Kontext

Der Architecture Workflow erzeugt vor einer Codex-Ausführung versionierbare
Workflow-, Prompt-, Proof- und Authorization-Artefakte. Solange diese noch
nicht committed sind, ist der Arbeitsbaum absichtlich nicht leer. Der bisherige
Orchestrator-Schutz blockierte jeden nicht leeren Arbeitsbaum, konnte aber
autorisierte Vorbereitung nicht von unbekannten Änderungen unterscheiden.

## Entscheidung

Der Ausführungs-Preflight unterscheidet verbindlich:

- `CLEAN_WORKING_TREE`
- `AUTHORIZED_PREPARATION_CHANGES`
- `UNAUTHORIZED_DIRTY_WORKING_TREE`

Ein Dirty Tree ist ausschließlich dann startfähig, wenn ein expliziter
`ArchitectureExecutionPreparationBaseline`-Nachweis alle vorhandenen
Änderungen vollständig und unverändert bindet. Die Baseline ist an Workflow,
Architecture Run, Execution Authorization, Repository, lokalen Branch und
Base Commit gebunden.

Der offizielle Befehl
`python3 -m builder.main architecture execution prepare --workflow-id ...`
validiert Workflow, Prompt Proof und Authorization, liest den vollständigen
Git-Status und erfasst ausschließlich die konkreten, aus dem Workflow-Manifest
abgeleiteten Vorbereitungsdateien. Für jede Datei werden Pfad, Git-Zustand,
SHA-256 und Größe gespeichert.

## Invarianten

- Freie Pfadangaben autorisieren keine Datei.
- V1 akzeptiert nur neue, ungetrackte Artefakte des konkreten Workflows.
- Bestehende ADRs, Handovers, Quellcode, Tests, Konfiguration und fremde
  Workflow-Verzeichnisse sind keine Vorbereitung.
- Gestagte Dateien sind in V1 verboten
  (`PREPARATION_STAGED_CHANGES_NOT_ALLOWED`).
- Fehlende, zusätzliche oder geänderte Pfade sowie falsche Identitätsbindung
  blockieren mit `PREPARATION_BASELINE_MISMATCH`.
- Ohne Baseline bleibt ein Dirty Tree mit `WORKING_TREE_DIRTY` blockiert.
- Identische Vorbereitung ist idempotent; eine bestehende Baseline wird nicht
  still aktualisiert.

## Schutz während und nach Codex

Preparation-Dateien sind während der Ausführung unveränderlich. Nach dem
Prozess trennt die Validierung `PREPARATION_BASELINE_FILES` von
`CODEX_RESULT_CHANGES`. Eine geänderte oder fehlende Preparation-Datei führt zu
`VALIDATION_FAILED` mit `PREPARATION_ARTIFACT_MODIFIED`. Bei
`create_commit: false` ist Staging vor und während des Laufs unzulässig.

Es erfolgen keine automatische Reparatur, keine Baseline-Erweiterung und kein
zweiter Prozessstart.

## Persistenz und Grenzen

Die Baseline ist ein technischer Runtime-Nachweis und liegt im weiterhin
ignorierten Pfad
`knowledge/architecture_workflows/<workflow-id>/executions/preparation-baseline.json`.
Sie ist keine Governance- oder Chief-Architect-Entscheidung. Die verbindlichen
Workflow-, Prompt-, Proof- und Authorization-Artefakte bleiben versionierbar.
Read-only Statusbefehle erzeugen oder verändern keine Baseline.

Nicht Bestandteil sind reale Codex-Ausführung, produktive Baselines, Commit,
Push, Branchwechsel, Migration historischer Workflows oder eine Erweiterung
des fachlichen Änderungsscopes.

## Teststrategie

Temporäre Git-Repositories prüfen Git-Status, Hashes, Pfadbindung, Staging,
Idempotenz, fremde und veränderte Dateien sowie die Trennung von Vorbereitung
und Fake-Codex-Ergebnis. Kein Test benötigt Netzwerk oder eine reale Codex CLI.
