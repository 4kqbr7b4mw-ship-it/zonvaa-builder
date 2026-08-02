# ADR-0046 – ZONVAA Builder Reset v2

## Status

Accepted

## Context

The previous Builder architecture accumulated competing execution owners,
watchers, feedback-triggered execution, orchestration state machines, and
intermediate artifacts. A real interrupted Codex run demonstrated that this
complexity obstructed controlled development and left ambiguous ownership.

## Decision

The active Builder uses one local development path:

`IMMUTABLE TASK → GUARD → VETO GATE → REPOSITORY LOCK → SINGLE EXECUTION
OWNER → RUN RECEIPT → STRONG GIT GATE → HUMAN COMMIT APPROVAL → SEPARATE
HUMAN PUSH APPROVAL`

The immutable task binds task ID, repository, branch, start HEAD, goal, allowed
paths, non-goals, veto classification, and whether commit or push can later be
approved. Unclear veto classification blocks. A veto-domain task requires a
human plan approval.

An atomic repository lock contains only task ID, PID, start time, and
repository. Existing locks block; suspected stale locks are reported and never
removed automatically.

Only the Builder task runner may start Codex. It starts at most once, never
retries, and never stages, commits, or pushes. One immutable run receipt records
the technical outcome as `COMPLETED`, `FAILED`, or `INTERRUPTED`; it triggers
nothing.

The Git gate verifies branch, start HEAD, staging, changed-path scope, absence
of push, the full test suite, Doctor, `git diff --check`, and receipt
consistency. Commit approval is a separate human artifact bound to task,
branch, HEAD, diff hash, action, time, and approver. A changed diff invalidates
it. Push approval is later and separately bound to the exact commit, remote,
and remote branch. Force-push, rebase, merge, and amend are outside this path.

## Veto domains

The gate has exactly three results: `NO_VETO`, `VETO_REQUIRED`, and
`HUMAN_CLASSIFICATION_REQUIRED`. The latter blocks pending a human
classification. Veto domains include authorization, governance, data
sovereignty, and security-critical execution. A second AI is not mandatory.

Additional complexity requires either a documented incident or an immediately
credible, highly probable material harm. An incident need not already have
caused damage.

## Supersession

This ADR replaces the active execution behavior of ADR-0034, ADR-0035,
ADR-0041, ADR-0042, ADR-0043, ADR-0044, and ADR-0045. Their artifacts remain
historical and read-only. Feedback loops, watchers, the Architecture Operations
Agent, the legacy execution bridge, and the former orchestrator may inspect
history but may not start processes or attempts.

Still binding are the three minimum Builder protections: correct branch and
defined starting state, successful tests before commit, and no commit or push
without explicit human approval. ZONVAA product, Constitution, Guardian,
Institution, Governance, data-ownership, and domain decisions are untouched.

## Consequences

There is one process owner and one receipt rather than a distributed lifecycle.
Humans retain commit and push authority. The design intentionally accepts less
automation and requires explicit handling of stale locks and interrupted runs.

## E7a – Paket-Granularität

Mehrere architektonisch geklärte und fachlich zusammengehörige Teilbausteine
werden durch ChatGPT zu einem gemeinsamen Codex-Arbeitspaket gebündelt. Die
Paketgröße richtet sich nach fachlicher Kohäsion, nicht nach Dateianzahl,
künstlicher Sprintgröße, Kalenderdauer oder möglichst vielen Einzelfreigaben.

Ein Paket erhält einen Gesamtbericht mit getrennten Abschnitten je
Teilbaustein: fachliches Ergebnis, geänderte Dateien, fokussierte Tests sowie
Grenzen und Nicht-Ziele. Zusätzlich ist ein Integrationsabschnitt erforderlich.

Scheitert ein Teilbaustein, wird seine Spezifikation nicht eigenmächtig
verändert und keine Ersatzarchitektur improvisiert. Der konkrete Blocker wird
berichtet. Unabhängige Teile dürfen nur weitergeführt werden, wenn dadurch kein
inkonsistenter Gesamtzustand entsteht.

Ein Paket ist zu groß, sobald seine Teile fachlich nicht mehr eng
zusammengehören, der Diff nicht in einer ehrlichen Prüfsitzung bewertet werden
kann, unabhängige Macht- oder Risikogrenzen vermischt werden oder der
Gesamtbericht nicht mehr klar seziert werden kann.

Unverändert gelten die Freigabegrenzen: Implementierung ist keine
Commit-Freigabe, Commit ist keine Push-Freigabe, Tests und Diff-Prüfung erfolgen
vor dem Commit und der Push wird separat freigegeben.

## E7b – Codex-Aufträge

Ein Codex-Auftrag besteht ausschließlich aus dem direkt ausführbaren Auftrag.
Vor dem Auftrag stehen keine Einleitung, Begründung, Zusammenfassung oder
Meta-Kommentare. Die Architekturdiskussion endet mit der Architekturentscheidung.
Nach der Architekturentscheidung beginnt unmittelbar der Codex-Auftrag.

Bereits beschlossene Inhalte werden nicht erneut erklärt, sondern nur soweit
wiederholt, wie sie für die korrekte Implementierung erforderlich sind. Der
Auftrag ist so kurz wie möglich und so vollständig wie nötig. Jeder Satz im
Auftrag muss einen konkreten Implementierungswert besitzen. Prozesskommentare
gehören nicht in Codex-Aufträge.

ChatGPT trennt strikt zwischen Architekturdiskussion, Codex-Auftrag, Bewertung
des Codex-Berichts, Commit-Freigabe und Push-Freigabe. Diese Trennung verändert
weder die bestehenden Freigabegrenzen noch Builder- oder Produktlogik.
