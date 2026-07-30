# ADR-0042 – Branch-bound Execution Authorization

## Status

Beschlossen

## Kontext

ADR-0035 bindet eine Execution Authorization an Workflow, Architecture Run,
Prompt Proof, Repository und Basis-Commit. ADR-0041 prüft den Branch vor einer
orchestrierten Codex-Ausführung, dokumentiert aber ausdrücklich, dass der
Authorization-Vertrag selbst keinen Branch enthält.

Ein Commit kann auf mehreren Branches erreichbar sein. Eine Bindung nur an
Repository und Commit beweist deshalb nicht, dass Codex im ausdrücklich
freigegebenen Arbeitszweig startet.

## Entscheidung

Execution Authorization Schema 1.1 enthält verpflichtend
`authorized_branch`. Der lokale Branch wird bei der Erzeugung der
Authorization ausdrücklich aus Git gelesen, validiert, in die deterministische
Authorization-ID einbezogen und im versionierten Authorization-Artefakt
persistiert.

Eine Execution darf nur starten, wenn:

```text
current_branch == authorized_branch
```

Der Basis-Commit bleibt eine zusätzliche, unabhängige Bedingung. Ein passender
Commit kompensiert weder Branchabweichung noch Detached HEAD.

## Branchvertrag

`authorized_branch` ist ein nichtleerer, normalisierter lokaler Branchname.
Unzulässig sind insbesondere:

- `HEAD` und Detached-HEAD-Platzhalter,
- Remote- und Ref-Schreibweisen wie `origin/main`, `refs/...` oder
  `remotes/...`,
- Wildcards und Git-Ref-Steuerzeichen,
- führende oder abschließende Trennzeichen,
- doppelte Schrägstriche, `..`, `@{` und `.lock`-Endungen.

Es gibt keinen Defaultbranch. `main` darf nur gespeichert werden, wenn Git bei
der Authorization-Erzeugung ausdrücklich `main` liefert.

## Blocker

Vor Prozessauflösung, PID-Erzeugung und Codex-Start gelten:

- fehlendes Branchfeld in historischer Authorization:
  `AUTHORIZED_BRANCH_MISSING`,
- Detached HEAD: `DETACHED_HEAD_NOT_ALLOWED`,
- Branchabweichung: `AUTHORIZED_BRANCH_MISMATCH`.

Der Mismatch-Bericht enthält autorisierten und tatsächlichen Branch,
Workflow-ID, Authorization-ID und Repository-Pfad. Kein Blocker wechselt oder
erzeugt einen Branch.

## Historische Authorizations

Schema 1.0 bleibt unverändert lesbar und serialisierbar. Es wird als Legacy
erkannt und besitzt `authorized_branch = None`. Ein neuer automatisierter
Codex-Lauf ist damit nicht zulässig.

Beim Lesen, bei Statusabfragen und beim Start wird kein Branch ergänzt,
abgeleitet oder als `main` angenommen. Eine spätere Bindung erfordert einen
separaten ausdrücklich autorisierten Migrations- oder Rekonstruktionsvertrag.
Historische Artefakte werden durch diese Entscheidung nicht verändert.

## Orchestration und Operations

Der Orchestration Record führt getrennt:

- `authorized_branch`,
- `current_branch`,
- `branch_match`.

Status, Liste und Architecture Operations zeigen diese Werte
maschinenlesbar. Für eine noch nicht gestartete Authorization ist der
autorisierte Branch sichtbar; ein aktueller Branch oder Match wird nicht
erfunden. Read-only-Abfragen schreiben oder migrieren keine Artefakte.

Die bestehende Execution Bridge prüft Schema-1.1-Authorizations ebenfalls vor
Attempt- oder Prozessstart. Damit kann der ältere direkte Bridge-Einstieg die
Branchgrenze nicht umgehen.

## Sicherheitsgrenzen

- kein Branchwechsel und keine Brancherzeugung,
- keine Remote-Ref-Normalisierung,
- kein Default auf `main`,
- keine automatische Authorization oder Migration,
- keine Mutation historischer Authorizations,
- kein Codex-Start, Attempt oder PID bei Branchblockern,
- keine Änderung der Commit-, Retry-, Queue- oder Push-Regeln aus ADR-0041.

## Konsequenzen

Neue bestätigte Architecture Workflows erzeugen Schema-1.1-Authorizations.
Bestehende Schema-1.0-Artefakte bleiben auditierbar, müssen vor einer neuen
Ausführung jedoch ausdrücklich neu autorisiert werden.

## Teststrategie

Fokussierte Tests prüfen passende und abweichende Branches, Detached HEAD,
Legacy-Lesen ohne Mutation, leere und unsichere Branchnamen, unabhängige
Commit-/Branch-Prüfung, ausbleibenden Prozess/PID/Attempt, Status- und
Operations-Anzeige, read-only Listen sowie unveränderte Fake-Codex-
Erfolgsausführung. Produktive Codex-Ausführung ist ausgeschlossen.
