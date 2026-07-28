# ADR-0038 – Architecture Operations Agent

## Status

Accepted

## Kontext

ZONVAA persistiert Architecture Proposals, Workflows, Entscheidungen,
Codex-Prompts, Execution-Autorisierungen, Execution Records, Handovers,
Feedback-Transitions und Integrator-Reviews in bereits getrennten
Komponenten. Diese Artefakte bilden den verbindlichen Zustand, waren jedoch
nicht über eine gemeinsame, rein lesende Operations-Sicht auffindbar.

Operative Fragen wie „Wo steht ein Architekturthema?“, „Welcher Schritt ist
zulässig?“ oder „Welche Reviews benötigen eine Entscheidung?“ erforderten
deshalb Kenntnis einzelner Ablagen. Eine zusätzliche Statuspersistenz würde
hingegen eine konkurrierende Wahrheit neben Workflow, Execution Bridge und
Feedback Loop erzeugen.

## Entscheidung

Der Architecture Operations Agent ist eine deterministische, rein lesende
Projektion über die vorhandenen Stores. Er:

- entdeckt bestehende Workflows über den Workflow Store,
- liest Authorization, Execution, Attempt History, Handover Intake,
  Feedback Loop und Integrator Review über deren bestehende Verträge,
- ordnet Artefakte anhand persistierter IDs und Referenzen zu,
- meldet Widersprüche und fehlende Erwartungen maschinenlesbar,
- leitet genau den nächsten zulässigen Schritt ab,
- stellt entscheidungsreife Reviews zusammen.

Der Agent persistiert keinen eigenen Status. Gleicher Repository-Zustand und
gleiche Query ergeben dieselbe sortierte Ausgabe.

## Suche und Eindeutigkeit

Unterstützt werden Topic, Workflow-ID, Architecture-Run-ID, Execution-ID,
Review-ID, Commit, Handover-Pfad, Proposal-ID und Decision-ID.

IDs und Referenzen werden exakt verglichen. Topics verwenden ausschließlich
eine case-insensitive Teilzeichenfolgensuche. Commit-Präfixe sind ab sieben
hexadezimalen Zeichen zulässig. Eine Suche mit mehreren Treffern wird als
`AMBIGUOUS_QUERY` abgebrochen; es gibt keine heuristische Auswahl des
„wahrscheinlichsten“ Vorgangs.

## Zustands- und Artefaktvertrag

Der typisierte Operations-Status enthält mindestens:

- Workflow-, Run-, Authorization-, Execution- und Review-Identitäten,
- Workflow-, Execution- und Feedback-Status,
- Execution-Herkunft und Attempt-Anzahl,
- Result-Commit und Handover-Referenzen,
- Konflikte, Abweichungen und offene Risiken,
- vorhandene, fehlende oder unsichere Artefakte,
- Legacy- und Ausführbarkeitskennzeichen,
- genau einen nächsten Schritt.

Fehlende Artefakte erhalten keinen erfundenen Pfad. Symlinks an
Architekturartefakten gelten nicht als vertrauenswürdige Nachweise.

## Next-Step-Regeln

Die Ableitung folgt den vorhandenen Zustandsgrenzen:

- unvollständige oder widersprüchliche Evidenz → `BLOCKED`,
- unentschiedener Workflow → `CHIEF_ARCHITECT_DECISION_REQUIRED`,
- bestätigte Entscheidung ohne Prompt → `GENERATE_CODEX_PROMPT`,
- vollständiger Prompt ohne Autorisierung → `EXECUTION_AUTHORIZED`,
- autorisierte, noch nicht gestartete Execution → `EXECUTION_REQUIRED`,
- laufende Execution → `EXECUTION_RUNNING`,
- fehlgeschlagene Execution → `EXECUTION_RETRY_REQUIRED`,
- erfolgreiche Execution ohne Handover → `HANDOVER_REQUIRED`,
- Handover ohne validierten Intake → `HANDOVER_VALIDATION_REQUIRED`,
- Intake ohne Review → `INTEGRATOR_REVIEW_REQUIRED`,
- Review im Feedback-Endzustand →
  `CHIEF_ARCHITECT_DECISION_REQUIRED`.

Die Operations-Schicht führt keinen dieser Schritte aus.

## Legacy-Kompatibilität

Historische Workflows mit Codex-Prompt, aber ohne den später eingeführten
Prompt-Proof bleiben lesbar. Sie werden ausdrücklich als Legacy und nicht
ausführbar ausgewiesen. Die Operations-Schicht erzeugt weder fehlende Proofs
noch Autorisierungen und lockert die Watcher-Grenze nicht.

Rekonstruierte Executions bleiben anhand ihrer bestehenden
`RECONSTRUCTED`-Herkunft erkennbar. Es werden keine historischen Attempts,
Zeitpunkte oder Push-Zustände erfunden.

## Autorität und Sicherheitsgrenze

Der Operations Agent:

- trifft keine Architekturentscheidung,
- startet keine Execution und keinen Retry,
- erzeugt keine Autorisierung,
- verändert weder Workflow noch Review,
- schreibt keine Architektur-, Runtime- oder Handover-Datei,
- ersetzt weder Chief Architect noch Architecture Integrator,
- führt keinen Commit, Merge oder Push aus.

Ein Integrator-Review bleibt eine nicht bindende Empfehlung. Nur der Chief
Architect entscheidet.

> Der Architecture Operations Agent trifft keine Architekturentscheidung.

> Der Agent darf fehlende Artefakte oder IDs nicht erfinden.

> Persistierte Workflow-, Execution-, Handover- und Review-Artefakte bleiben
> die Source of Truth.

> Der Agent zeigt den nächsten zulässigen Schritt, führt ihn jedoch in Version
> 1 nicht aus.

## CLI

Die bestehende Architecture CLI erhält:

- `architecture status`
- `architecture next`
- `architecture artifacts`
- `architecture reviews`

Alle Befehle besitzen eine deterministisch sortierte JSON-Ausgabe. Die
menschenlesbare Ausgabe ist eine kompakte Projektion desselben Modells.

## Konsequenzen

Der operative Architekturstand wird ohne zweite Zustandsarchitektur
auffindbar und prüfbar. Inkonsistenzen wie Execution ohne Autorisierung,
Review ohne Intake, Result-Commit-Abweichungen oder doppelte Artefakte werden
sichtbar, aber nicht automatisch repariert.

Die Genauigkeit bleibt durch die vorhandenen Persistenzverträge begrenzt.
Fehlende historische Referenzen werden als fehlend oder Legacy ausgewiesen;
semantische Ähnlichkeit und automatische Rekonstruktion sind nicht Teil
dieser Leseschicht.

## Teststrategie

Fokussierte Tests prüfen alle Suchschlüssel, Mehrdeutigkeit, stabile
Sortierung, Unveränderlichkeit, Next-Step-Stufen, Inkonsistenzen,
Symlink-Abwehr, Legacy-Lesen, rekonstruierte Executions, Attempt-Anzahl,
entscheidungsreife Reviews und JSON-/Textausgaben. Zusätzlich bleiben
Workflow-, Feedback-, Execution- und vollständige Repository-Tests
verbindlich.
