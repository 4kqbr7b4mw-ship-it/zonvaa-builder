# ADR-0043 – Explicit Commit Authorization

## Status

Beschlossen

## Kontext

ADR-0041 erlaubt dem Codex Execution Orchestrator einen Commit nur nach
erfolgreicher Validierung. Der bisherige Execution-Authorization-Vertrag
leitete diese Befugnis jedoch aus dem allgemeinen Eintrag `create_commit` in
`allowed_actions` ab. Der offizielle Feedback-Loop fügte diesen Eintrag
pauschal jeder neuen Authorization hinzu.

Damit konnte ein Auftrag nicht ausdrücklich als nicht commitfähig autorisiert
werden. Allgemeine Tätigkeitsrechte und die irreversible Git-Handlung waren
nicht hinreichend getrennt.

## Entscheidung

Execution Authorization Schema 1.2 enthält das verpflichtende boolesche Feld
`create_commit`.

- `false`: Der Orchestrator darf nicht stagen oder committen.
- `true`: Der Orchestrator darf nach vollständig erfolgreicher Validierung
  genau einen Commit erzeugen.

Der offizielle Erzeugungspfad verwendet ohne ausdrückliche Option
`create_commit: false`. Nur `--create-commit` erteilt die Befugnis;
`--no-create-commit` dokumentiert die Ablehnung ausdrücklich.

`create_commit` ist Bestandteil der deterministischen Authorization-ID.
Unterschiedliche Commit-Freigaben erzeugen deshalb unterschiedliche
Authorization-Identitäten. Eine bestehende Authorization wird niemals
nachträglich umgeschrieben.

## Trennung allgemeiner Aktionen

`create_commit` ist kein Element der statischen `ALLOWED_ACTIONS`. Schema 1.2
lehnt eine solche Vermischung ab. Die Commit-Berechtigung darf weder aus
allgemeinen Aktionen noch aus Prompttext, Workflowstatus oder einem
erfolgreichen Testlauf abgeleitet werden.

Push ist eine unabhängige Handlung. Der Orchestrator v1 führt auch mit
`create_commit: true` keinen Push aus.

## Orchestrator-Vertrag

Bei `create_commit: false` persistiert der Orchestrator erfolgreiche
Validierung, geänderte Dateien, Diff-Zusammenfassung und vorgeschlagene
Commit-Nachricht. Er endet terminal bei `COMMIT_READY`; `commit_attempted`
bleibt `false` und `result_commit` bleibt leer.

Bei `create_commit: true` gilt folgende Reihenfolge:

1. Codex-Prozess erfolgreich,
2. Tests, Doctor und `git diff --check` erfolgreich,
3. Branch-, Push-, Pfad- und Änderungsumfangprüfung erfolgreich,
4. `COMMIT_READY` persistiert,
5. genau ein Commit-Versuch,
6. Commit-ID persistiert und Abschluss mit `COMPLETED`.

Ein bereits während der Codex-Ausführung entstandener Commit ist kein
nachgelagerter Orchestrator-Commit. Er führt unabhängig von der Freigabe zu
`VALIDATION_FAILED`.

## Historische Authorizations

Schema 1.0 und 1.1 bleiben unverändert lesbar. Fehlendes `create_commit` wird
beim Lesen sicher als `false` behandelt, ohne das historische Artefakt zu
verändern. Legacy-Authorizations können keine Commit-Befugnis aus früheren
`allowed_actions` erben.

Eine abweichende Freigabe erfordert eine neue ausdrücklich autorisierte
Authorization. Es gibt keine automatische Migration und keinen Default auf
`true`.

## Status und Operations

Orchestration JSON und read-only Architecture Operations zeigen getrennt:

- `create_commit_authorized`,
- `commit_attempted`,
- `result_commit`.

Status- und Listenabfragen erzeugen oder verändern keine Authorization,
Orchestration oder Git-Historie.

## Sicherheitsgrenzen

- keine Commit-Ableitung aus `ALLOWED_ACTIONS`,
- kein Commit vor erfolgreicher Validierung,
- höchstens ein Commit-Versuch je Orchestration,
- kein Push,
- keine Mutation historischer Authorizations,
- keine produktive Codex-Ausführung durch diese Architekturänderung,
- keine Änderung von Retry-, Queue-, Branch- oder Authorization-Grenzen.

## Konsequenzen

Der erste produktive Orchestrator-Test kann ausdrücklich mit
`create_commit: false` vorbereitet werden und muss bei Erfolg bei
`COMMIT_READY` enden. Commitfähige Aufträge benötigen eine sichtbare,
eigenständige Freigabe.

## Teststrategie

Tests prüfen Default, explizites `false` und `true`, unterschiedliche
Authorization-IDs, die Trennung von allgemeinen Aktionen, das terminale
`COMMIT_READY` ohne Commit, genau einen Commit nach Validierung, blockierte
Commits bei Validierungsfehlern, Legacy-Lesen ohne Mutation, CLI-Hilfe,
Operations-Ausgabe und das unveränderte Push-Verbot. Alle Prozessprüfungen
verwenden Fake-Codex und temporäre Git-Repositories.
