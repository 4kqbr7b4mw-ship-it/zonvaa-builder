# ADR-0034 – Automated Codex Execution Bridge

## Status

Beschlossen

## Kontext

ADR-0028 und ADR-0029 trennen Architecture Integrator, Chief Architect,
Architecture Workflow und Codex. Workflow 2.0 erzeugt nach vollständigen
Decision Records einen eigenständigen `codex-prompt.md`. Der Nutzer muss diesen
Auftrag bislang manuell erneut an Codex übergeben.

Eine automatische Übergabe darf die menschliche Architekturfreigabe nicht
umgehen, keine fremden Texte ausführen, nicht auf andere Repositorys zugreifen
und weder Commit-Erfolg noch Tests nur annehmen. Ausführung ist lokaler
Betriebszustand und keine neue Architekturentscheidung.

## Entscheidung

ZONVAA führt eine lokale Automated Codex Execution Bridge ein.

> Der Chief Architect entscheidet.
>
> Der Architecture Workflow erzeugt den freigegebenen Auftrag.
>
> Die Execution Bridge transportiert und startet ihn.
>
> Codex implementiert.

Die Bridge trifft keine Architekturentscheidung, verändert keine Decision
Records und pusht niemals.

### Freigabe und Prompt-Proof

`ArchitectureWorkflowStore.write_prompt` erzeugt neben dem kanonischen Prompt
einen maschinenlesbaren Proof. Er bindet Workflow-ID, kanonischen relativen
Pfad, SHA-256 und sämtliche Decision-IDs.

Nur `CODEX_PROMPT_GENERATED` mit vollständigen parsebaren Decisions und
übereinstimmendem Proof ist ausführbar. Chattext, Downloads, temporäre Dateien,
Proposals, Entscheidungsvorlagen, Symlinks und Pfade außerhalb des aktiven
Repositorys sind keine Auftragsquelle.

### Execution Record

Jeder Prompt-Hash erhält innerhalb eines Workflows eine deterministische
Execution-ID. Das unveränderliche, versionierte Modell enthält Workflow,
Prompt, Repository, Startbranch, Startcommit, Git-Status, Status, Zeitpunkte,
Codex-Exit-Code, Test-, Doctor- und Diff-Status, Result-Commit, Handover,
Fehler, Retry-Zähler und Push-Status.

Status sind ausschließlich `PENDING`, `RUNNING`, `SUCCEEDED`, `FAILED`,
`BLOCKED`, `WAITING_FOR_CAPACITY` und `CANCELLED`.

Fehler sind keine freien Statusmeldungen. Schema 1.1 enthält einen typisierten
Fehlervertrag mit Ausführungsschritt, Fehlerklasse, Programm und separater
Argumentliste, Arbeitsverzeichnis, Exit-Code, stdout, stderr, Exception-Typ
und -Nachricht, technischer Ursache, timezone-aware Zeitstempel und
Execution-ID. Unterschieden werden fehlendes Programm, fehlendes
Arbeitsverzeichnis, fehlender Auftrag, Startfehler, Prozess-Exit ungleich null,
Timeout und unerwarteter interner Fehler. Ein gestarteter Prozess behält seine
redigierten Ausgaben auch im Fehlerfall; ein Fehler vor dem Prozessstart hat
keinen erfundenen Exit-Code.

Fehlerausgaben, technische Ursachen und Argumente werden begrenzt und vor
Persistenz redigiert. stdin und Umgebungsvariablen werden nie in den Record
übernommen. Bekannte Token-, API-Key-, Passwort-, Credential-, Secret- und
Authorization-Muster sowie explizit bekannte sensible Werte werden ersetzt.
Diese deterministische Redaktion ist keine allgemeine Inhaltsklassifikation;
unbekannte sensible Freitextformen bleiben eine dokumentierte Grenze.

Execution JSON und Markdown liegen im `executions`-Unterordner des Workflows.
Dieser lokale Laufzeitbereich wird nicht committed. Dadurch kann die Bridge den
finalen Status nach dem von Codex erzeugten Result-Commit dokumentieren, ohne
den Arbeitsbaum erneut zu verändern.

### Lokale Ausführung

Die installierte CLI wurde gegen `codex --help`, `codex exec --help` und
`codex login --help` geprüft. Die Bridge nutzt eine feste Argumentliste ohne
Shell:

```text
codex exec --cd /Users/michaelgiese/zonvaa-builder \
  --sandbox workspace-write --ask-for-approval never -
```

Der geprüfte Prompt wird über stdin übergeben. Vorher werden Installation,
`codex login status`, Git-Root, Arbeitsbaum und exklusiver Workflow-Lock
geprüft. Es gibt keine Codex Cloud API.

### Ergebnisfreigabe

`SUCCEEDED` ist nur zulässig, wenn Codex Exit-Code null liefert, vollständige
Tests, Doctor und `git diff --check` bestehen, ein neuer Commit mit JSON- und
Markdown-Handover vorliegt und der Arbeitsbaum sauber ist.

Die Bridge erzeugt keinen Commit und keinen Push. Fehlschläge erhalten den
Zwischenstand. Ein möglicherweise bereits durch Codex erzeugter Commit wird
bei späterem Prüfversagen nicht freigegeben, nicht zurückgesetzt und nicht
verändert.

### Idempotenz, Retry und Lock

Gleicher Workflow und Prompt-Hash ergeben dieselbe Execution-ID. Ein
erfolgreicher Lauf kann nicht wiederholt werden. Fehler, Blocker oder
Kapazitätsgrenzen benötigen denselben unveränderten Prompt; manuelle
Wiederholung ist ausdrücklich. Nur Kapazitätsgrenzen dürfen nach der
versionierten C3-Regel `codex_execution/policy.md` begrenzt automatisch erneut
versucht werden.

Ein exklusiver lokaler Lock verhindert parallele Läufe desselben Workflows.
Die Bridge verwirft keine vorhandenen Änderungen. Ein Retry verlangt denselben
Branch und Startcommit; uncommittierte Zwischenstände dürfen bestehen.

### Watcher und CLI

Der Watcher ist ein endlicher, idempotenter Scan. Ein versioniertes
`launchd`-Template startet ihn periodisch und nach einem Mac-Neustart. Es gibt
keine Busy-Wait-Schleife. Installation und Entfernung bleiben ausdrückliche
Nutzerhandlungen; der Nutzer kann den Watcher jederzeit stoppen.

Der bestehende Architecture-CLI-Baum erhält `architecture execute` sowie
`architecture execution status`, `retry`, `cancel` und `watch-once`.

## Sicherheitsgrenzen

- Produktions-CLI ist fest auf `/Users/michaelgiese/zonvaa-builder` begrenzt.
- Metadaten werden nie als Shell-Befehl interpretiert.
- Fehlerberichte enthalten strukturierte Argumentlisten und niemals einen
  nachträglich zusammengesetzten Shell-Befehl.
- Prompt-Pfad, Symlinks, Proof, Decisions, Git-Root und Lock werden geprüft.
- Keine automatische Entscheidung, Änderung von Decisions, Rücksetzung,
  Commit-Erzeugung, Push- oder PR-Erzeugung.
- Keine externe Modellorchestrierung und kein Netzwerkdienst außerhalb der
  durch den freigegebenen Auftrag gestarteten Codex CLI.

## Folgen und offene Grenze

Der manuelle Prompt-Transport entfällt nach einmaliger lokaler
Watcher-Einrichtung. Codex-Authentifizierung, Nutzungskapazität und das
Verhalten des ausgeführten Codex-Prozesses bleiben externe Zustände.

Die Bridge kann einen bereits von Codex erzeugten Commit nach einem späteren
Testfehler nicht sicher und nicht zerstörungsfrei entfernen. Sie markiert ihn
nicht als Result-Commit und führt keinen weiteren Commit aus.

## Nicht-Ziele

Nicht eingeführt werden automatische Chief-Architect-Entscheidungen, Gemini-
oder Kimi-Orchestrierung, Codex Cloud API, andere Repositorys, Serverdienst,
UI, GitHub-Push, Force-Push, Pull Request, automatische Konfliktauflösung oder
automatische Änderung freigegebener Prompts.
