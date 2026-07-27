# ADR-0037 – Execution Reconstruction Architecture

## Status

Beschlossen

## Kontext und Problem

ADR-0034 und ADR-0035 bilden den normalen Weg von einer bestätigten
Architecture-Workflow-Entscheidung über Execution Bridge, Execution Record,
Handover-Validierung und Architecture-Integrator-Review ab. Ein ausdrücklich
vom Chief Architect autorisierter Direktauftrag kann jedoch bereits einen
belegten Basis- und Result-Commit, zwei Handovers und maschinenlesbare Checks
besitzen, ohne von der Bridge gestartet worden zu sein. Dann fehlen Execution-
und Architecture-Run-Kontext, obwohl die vorhandenen Artefakte prüfbar sind.

Execution Reconstruction erzeugt keine Autorisierung. Ein Handover allein ist
kein Beweis einer autorisierten Ausführung.

## Entscheidung

ZONVAA erhält einen `ExecutionReconstructionService`. Er konsumiert einen
separaten, typisierten und bestätigten
`ExecutionReconstructionAuthorization`-Vertrag und rekonstruiert daraus
zusammen mit Repository-, Git- und Handover-Evidenz deterministisch genau
einen abgeschlossenen Execution Record.

Rekonstruierte Execution Records müssen als rekonstruiert erkennbar bleiben.
Sie tragen `origin = RECONSTRUCTED`; reguläre und historische Bridge-Records
tragen beziehungsweise erhalten `origin = EXECUTION_BRIDGE`.

Die bestehende Architecture Feedback Loop bleibt der einzige Weg zum
Integrator-Review:

```text
Reconstruction Authorization + verifizierte Evidenz
→ Reconstructed Execution Record
→ bestehende Handover-Validierung
→ bestehender CodexHandoverIntake
→ bestehendes Integrator-Review
→ CHIEF_ARCHITECT_DECISION_REQUIRED
```

## Abgrenzung zur Execution Bridge und zu Recovery

Reconstruction startet Codex nicht und behauptet keinen Bridge-Attempt. Der
Record enthält daher keine Start- oder Endzeit, keinen Exit-Code und
`attempts = ()`. Auch historischer Branch und damaliger Git-Status bleiben
unbekannt. `reconstructed_at` bezeichnet ausschließlich den Zeitpunkt der
Rekonstruktion.

Recovery eines unterbrochenen Bridge-Prozesses ist nicht Gegenstand dieser
Entscheidung. Reconstruction wiederholt, repariert oder setzt keine
Ausführung fort.

## Autorisierungsmodell

Das separate Autorisierungsartefakt bindet mindestens:

- Autorisierungs- und Chief-Architect-Entscheidungsreferenz,
- Repository sowie erwarteten Basis- und Result-Commit,
- ausdrücklich erwartete JSON- und Markdown-Handover-Pfade,
- erlaubte Rekonstruktionsaktion, Autorisierungszeitpunkt und Status
  `CONFIRMED`,
- optional den belegten Prompt-Hash.

Commit, Handover oder Check-Ergebnisse erzeugen für sich allein keine
Autorisierung. Fehlende oder widersprüchliche Autorisierung blockiert.

## Rekonstruktionsquellen und Identität

Zulässig sind ausschließlich die bestätigte Autorisierung, lokale
Repository-Dateien, read-only Git-Prüfungen, die Commit-Parent-Beziehung und
maschinenlesbare Handover-Checks. Der Result-Commit muss existieren und sein
direkter Parent muss der autorisierte Basis-Commit sein. Beide Handovers
müssen reguläre, symlinkfreie Dateien innerhalb des Repositorys und Teil des
Result-Commits sein.

Die stabile ID mit Präfix `reconstructed-execution-` wird aus
Autorisierungs-ID, Basis-Commit, Result-Commit, JSON-Handover-Pfad und
vorhandenem Prompt-Hash abgeleitet. Architecture-Run-, Workflow-, Intake- und
Review-IDs entstehen ausschließlich aus diesen deterministischen Grundlagen.

## Herkunft, Idempotenz und Persistenz

Execution Record Schema 1.3 ergänzt Herkunft, Rekonstruktionszeitpunkt und
Autorisierungsreferenz rückwärtskompatibel. Alte Schema-1.0-, 1.1- und
1.2-Records werden ohne erfundene Historie als Bridge-Records gelesen.

Der bestehende `ExecutionStore` bleibt Persistenzgrenze. Ein identischer
Record wird unverändert zurückgegeben. Ein abweichender Record unter derselben
Identität blockiert; er wird niemals überschrieben. Der bestehende
Feedback-Store verhindert doppelte Intakes, Reviews und Transitionen.

## Handover- und Legacy-Grenze

Ein erfolgreich rekonstruierter Record entsteht nur bei vorhandenem validen
JSON-Handover, verlangtem Markdown-Handover sowie bestandenen Tests, Doctor
und `git diff --check`. Fehlende Pflichtfelder oder Checks blockieren.

Ein Schema-1.0-Handover darf `ending_commit = null` behalten, wenn der
Result-Commit extern über Git verifiziert, der Pfad ausdrücklich autorisiert
und das Handover eindeutig Bestandteil dieses Result-Commits ist. Historische
Handovers werden nicht verändert. Diese eng gebundene Rekonstruktion lockert
die allgemeine Handover-Akzeptanz nicht.

## Sicherheitsgrenzen

- Nur read-only Git-Unterprozesse; keine Shell-Interpolation.
- Keine Codex-Ausführung, Retries, Commits, Pushes oder Merges.
- Keine automatische Ergänzung oder Änderung historischer Handovers.
- Keine erfundenen Decisions, Attempts, Zeiten, Checks oder Result-Commits.
- Keine externe Persistenz, Netzwerke oder neuen Abhängigkeiten.
- Fehler enthalten begrenzte feste Ursachen und keine Handover-Inhalte oder
  ungefilterten Git-Ausgaben.
- Das Integrator-Review ist nicht bindend und trifft keine
  Chief-Architect-Entscheidung.

## Konsequenzen und offene Risiken

Autorisierte Direktaufträge können wieder in den bestehenden, auditierbaren
Feedback-Pfad eintreten. Die Herkunft bleibt sichtbar und darf nicht mit dem
Nachweis eines tatsächlichen Bridge-Prozesses verwechselt werden.

Die Rekonstruktion belegt Commit-Kette, Artefakte und gemeldete Checks, nicht
die historische Prozessumgebung. Ein Prompt-Hash kann fehlen; dies bleibt
sichtbar und ist Bestandteil der deterministischen Identität. Ein natives
Handover-Schema mit Execution-ID sowie Recovery laufender Attempts bleiben
separate Architekturfragen.

## Teststrategie

Fokussierte Tests prüfen Autorisierung, Commit-Kette, Pfad- und Symlinkgrenzen,
Handover-JSON, Pflichtchecks, Herkunft, fehlende Attempts, deterministische
IDs, Append-only-Konflikte, Idempotenz, Legacy-Lesen, CLI-Ausgabe sowie die
einmalige Weitergabe an Handover-Validierung und Integrator-Review. Der reale
Guardian-Succession-Fall validiert zusätzlich Schema 1.0 mit fehlendem
`ending_commit` im ausdrücklich autorisierten Rekonstruktionskontext.
