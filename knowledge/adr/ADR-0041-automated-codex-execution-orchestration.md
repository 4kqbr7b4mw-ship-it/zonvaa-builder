# ADR-0041 – Automated Codex Execution Orchestration

## Status

Beschlossen

## Kontext

ADR-0034 stellt die sichere lokale Codex Execution Bridge mit typisiertem
Fehlervertrag, Redaction, Attempt History und argv-basierter Prozessausführung
bereit. ADR-0035 bindet bestätigte Architecture Runs an Prompt Proof und
Execution Authorization. Es fehlt eine darüberliegende, explizite
Orchestration, die Startvoraussetzungen, Prozesszustand, Validierung und eine
optional autorisierte Commit-Grenze als zusammenhängenden Vertrag abbildet.

## Entscheidung

ZONVAA führt Automated Codex Execution Orchestration v1 ein. Sie erweitert die
bestehende Bridge und verwendet deren Subprozess-, Fehler- und
Redaktionsmechanismen. Sie trifft keine Architekturentscheidung, erzeugt keine
Authorization oder Prompt Proof und pusht niemals.

### Zustandsmodell

Der erfolgreiche Ablauf lautet:

```text
AUTHORIZED → QUEUED → STARTING → RUNNING → VALIDATING
→ VALIDATION_SUCCEEDED → COMMIT_READY → COMPLETED
```

`QUEUED` bezeichnet einen explizit persistierbaren Wartezustand; synchrone
lokale Ausführung darf nach `AUTHORIZED` unmittelbar zu `STARTING` wechseln.
Ohne Commit-Freigabe ist `COMMIT_READY` terminal. Mit ausdrücklicher
`create_commit`-Freigabe folgt nach Validierung `COMPLETED`.

Fehlerzustände sind `BLOCKED`, `START_FAILED`, `EXECUTION_FAILED`,
`VALIDATION_FAILED`, `COMMIT_FAILED`, `CANCELLED` und `RECOVERY_REQUIRED`.
Status und aktueller Schritt werden typisiert persistiert und niemals aus
Logtext abgeleitet.

### Autorisierter Eingang

Ein Start verlangt einen existierenden Architecture Workflow und Architecture
Run, einen kanonischen Codex Prompt, einen passenden Prompt Proof sowie eine
bestätigte Execution Authorization. Workflow-, Prompt-, Proof-, Repository-,
Base-Commit-, Execution- und Authorization-Identitäten müssen übereinstimmen.

Der aktuelle Branch wird vor dem Start eindeutig ermittelt und zusammen mit
HEAD, Git-Status und `origin/main`-Divergenz persistiert. Version 1 führt nur
auf `main` aus. Der Authorization-Vertrag bindet den Basis-Commit; der
Orchestration Record bindet zusätzlich den tatsächlich geprüften Branch.
Rekonstruierte historische Executions werden nicht erneut gestartet.

### Prozessvertrag

Die Orchestration verwendet `SubprocessCommandRunner` ohne Shell-
Interpolation. Der validierte Prompt wird ausschließlich über stdin an die
installierte Codex CLI übergeben. Programm und Argumente werden als Liste
persistiert; Arbeitsverzeichnis, Exit-Code sowie getrennte, redigierte stdout-
und stderr-Dateien bleiben nachvollziehbar. Timeout und Prozessfehler verwenden
den bestehenden strukturierten Bridge-Fehlervertrag.

Der konkrete Aufruf bleibt der durch ADR-0034 und die installierte CLI-Hilfe
bestätigte lokale `codex exec`-Aufruf. Es werden keine Optionen erfunden.

### Exklusivität und Idempotenz

Workflow, Authorization und Prompt Hash ergeben eine deterministische
Orchestration-ID. Ein aktiver oder terminaler identischer Auftrag startet
keinen zweiten Codex-Prozess. Ein anderer aktiver Lauf für denselben Workflow
oder dieselbe Authorization blockiert. Terminale Records sind unveränderlich.

### Arbeitsbaum und Validierung

Vor Start müssen Repository, `main`, autorisierter Basis-Commit und sauberer
Arbeitsbaum bestätigt sein. Nach einem Codex-Exit null führt die Orchestration
automatisch aus:

```text
python3 -m pytest -q
python3 -m builder.main doctor
git diff --check
git status --short
```

Zusätzlich werden Branch, HEAD, geänderte Dateien, geschützte Governance-,
Authorization- und Prompt-Proof-Pfade sowie ein unerwarteter Remote-Stand
geprüft. Eine Abweichung erzeugt `VALIDATION_FAILED`; es gibt keine
automatische Löschung, Rücksetzung oder Reparatur.

### Commit- und Push-Grenze

Standard ist `commit_allowed: false`. Nur `create_commit` in der bestätigten
Execution Authorization erlaubt nach vollständiger Validierung einen Commit.
Ohne Freigabe endet der Lauf bei `COMMIT_READY` und weist Änderungen,
Prüfergebnisse und vorgeschlagene Commit-Nachricht aus. Mit Freigabe wird genau
der validierte Umfang committed, die Commit-ID gespeichert und ein sauberer
Arbeitsbaum verlangt.

Ein Push ist in v1 ausnahmslos verboten. Selbst ein Prompt, der Push verlangt,
erweitert die Authorization nicht.

### Persistenz und Recovery

Orchestration JSON, stdout und stderr liegen im bestehenden ignorierten
Workflow-Laufzeitbereich:

```text
knowledge/architecture_workflows/<workflow-id>/executions/orchestrations/
```

Prompt Proof und Execution Authorization bleiben die versionierten
Governance-Quellen. Verbindliche Abschlussnachweise werden über die bestehenden
Handover- und Feedback-Verträge referenziert. Architekturentscheidungen werden
nicht ausschließlich im Runtime-Baum gespeichert.

Ein nach Neustart nichtterminaler Record wird nicht automatisch erneut
gestartet. Ist der reale Prozess nicht eindeutig belegbar, wird
`RECOVERY_REQUIRED` persistiert. Ein noch nachweislich laufender Prozess bleibt
unverändert unter Beobachtung.

### Operations und CLI

Die CLI ergänzt:

```text
python3 -m builder.main architecture execution run --workflow-id ID
python3 -m builder.main architecture execution status --orchestration-id ID
python3 -m builder.main architecture execution list
```

Die read-only Status- und Listenansicht kann nach Orchestration, Workflow,
Architecture Run, Execution, Authorization und Status suchen. Sie startet und
verändert keinen Prozess.

## Sicherheitsgrenzen

- keine automatische Architekturentscheidung oder Integrator-Übernahme,
- keine Erzeugung oder Änderung von Authorization und Prompt Proof,
- keine Brancherstellung und kein Branchwechsel,
- keine automatische Wiederholung unbekannter oder abgebrochener Prozesse,
- keine Ausführung rekonstruierter historischer Executions,
- keine Shell-Interpolation und keine unredigierten Secrets,
- keine Veränderung historischer Governance-Artefakte,
- kein Push, Force-Push oder Remote-Schreibzugriff.

## Konsequenzen und Grenzen

Ein bestätigter Auftrag erhält einen reproduzierbaren lokalen Laufvertrag und
eine prüfbare Abschlussgrenze. Die Runtime kann nach einem Absturz nicht den
Exit-Code eines bereits verschwundenen Kindes rekonstruieren; dieser Fall
verlangt manuelle Prüfung. Der Authorization-Vertrag besitzt in Version 1 kein
eigenes Branchfeld. Diese ADR ändert ihn nicht rückwirkend, sondern bindet den
beim Start geprüften Branch im Orchestration Record.

## Teststrategie

Tests verwenden temporäre Git-Repositories, kontrollierte Workflow-Artefakte
und Fake-Codex-Runner. Sie prüfen Autorisierung und Proof, Git-Grenzen,
Idempotenz, doppelte Läufe, Prozessstart, Exit, getrennte Ausgaben, Redaction,
Timeout, Recovery, vollständige Validierung, geschützte Pfade, Commit-Grenze,
No-Push, CLI-Hilfe und read-only Operations. Eine reale Codex CLI oder
produktive Execution wird nicht gestartet.
