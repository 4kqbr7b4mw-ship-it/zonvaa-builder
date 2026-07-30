# ADR-0039 – Chief Architect Review Decision Architecture

## Status

Accepted

## Kontext

Der Architecture-to-Codex Feedback Loop endet mit einem typisierten
`ArchitectureImplementationReview` und
`CHIEF_ARCHITECT_DECISION_REQUIRED`. Der Architecture Integrator spricht nur
eine Empfehlung aus. `architecture workflow decide` entscheidet dagegen
Architecture Proposals vor einer Implementierung und ist weder an eine
Review-ID noch an das validierte Implementierungsergebnis gebunden.

Rekonstruierte Executions können ein vollständiges Review besitzen, obwohl
historische Workflow-, Proposal-, Prompt- oder Authorization-Artefakte
fehlen. Eine Review-Entscheidung darf diese Daten nicht erfinden und den
Proposal-Vertrag nicht semantisch verbiegen.

## Entscheidung

ZONVAA erhält einen eigenständigen, unveränderlichen und versionierten
`ArchitectureImplementationReviewDecision`-Vertrag. Das Implementierungsreview
ist der Entscheidungsanker.

Die Chief-Architect-Eingabe enthält ausschließlich `decision` und `reason`.
Der Application Service leitet alle kanonischen Zuordnungsfelder aus Review,
Feedback Record und Execution Record ab:

- Decision- und Review-ID,
- Topic,
- Workflow- und Architecture-Run-ID,
- Execution-ID und Execution-Herkunft,
- geprüfter Result-Commit,
- getrennt gespeicherte Integrator-Empfehlung,
- timezone-aware Entscheidungszeitpunkt.

Eingabedateien mit zusätzlichen Zuordnungsfeldern werden abgelehnt.

## Entscheidungswerte

Der Vertrag verwendet die bestehende `DecisionChoice`-Wertmenge `ADOPT`,
`ADOPT_WITH_CHANGES`, `REJECT` und `DEFER`. Die Review-Entscheidung bleibt
ein anderer Domänenvertrag als eine Proposal-Entscheidung. Eine
Integrator-Empfehlung wird niemals automatisch übernommen.

## Validierung

Vor Persistierung müssen:

- die Review-ID eindeutig auf genau ein gültiges Review zeigen,
- der Feedback-Status eine Chief-Architect-Entscheidung verlangen,
- Review, Feedback und Execution bei Workflow, Run, Execution und Review
  übereinstimmen,
- die Execution erfolgreich abgeschlossen sein,
- Review-Commit und Execution-Result-Commit übereinstimmen,
- Attempt-Referenzen exakt übereinstimmen,
- Konflikte und strukturierte Abweichungen leer sein,
- das Topic eindeutig aus Workflow oder validiertem JSON-Handover folgen.

Offene Risiken bleiben sichtbar, sind aber nicht automatisch ein
strukturierter Blocker. Der Chief Architect entscheidet ausdrücklich unter
Kenntnis dieser Risiken.

`RECONSTRUCTED` ist zulässig. Ein fehlendes `workflow.json`, Proposal,
ursprüngliche Architecture Decision, Prompt-Proof oder eine normale Execution
Authorization blockiert nicht, wenn Review, Feedback, Execution, Commit und
Handover-Referenzen widerspruchsfrei sind.

## Persistenz und Idempotenz

Das kanonische Artefakt liegt unter:

```text
knowledge/architecture_workflows/<workflow-id>/executions/feedback/
chief-architect-review-decision.json
```

Pro Review ist in Version 1 genau ein Artefakt zulässig:

- gleiche Entscheidung und gleiche Begründung → idempotent,
- abweichende Entscheidung oder Begründung → `DECISION_CONFLICT`,
- beschädigtes vorhandenes Artefakt → strukturierter Fehler,
- keine Überschreibung und keine automatische Revision.

Nach Persistierung wird der append-only Feedback Record um
`CHIEF_ARCHITECT_DECISION_RECORDED` ergänzt. Das Integrator-Review bleibt
unverändert.

## Status- und Operations-Integration

Der Architecture Operations Agent zeigt Integrator-Empfehlung,
Chief-Architect-Entscheidung, Entscheidungs-ID, Begründung und Zeitpunkt
getrennt. Entschiedene Reviews verschwinden aus `architecture reviews`. Ihr
nächster Schritt ist `COMPLETE`; insbesondere startet `ADOPT` keine
Execution. `architecture artifacts` weist das Decision-Artefakt aus.

`status`, `next`, `reviews` und `artifacts` bleiben read-only. Ausschließlich
folgender expliziter Befehl darf persistieren:

```text
architecture review decide --review-id REVIEW_ID --decision FILE
```

## Sicherheitsgrenzen

Der Mechanismus:

- erzeugt keine Proposal-Entscheidung,
- startet keine Execution und keinen Retry,
- erzeugt keinen Attempt oder Execution Authorization,
- verändert kein Integrator-Review, Handover oder historisches Artefakt,
- trifft keine automatische Entscheidung,
- übernimmt keine Integrator-Empfehlung,
- führt keinen Commit oder Push aus.

## Konsequenzen

Chief-Architect-Entscheidungen über Implementierungsergebnisse werden
eindeutig und ohne semantische Vermischung persistiert. Rekonstruierte
Vorgänge bleiben entscheidbar, ohne erfundene Historie.

Version 1 erlaubt keine Revision. Aufhebung oder Weiterverarbeitung nach
`REJECT` beziehungsweise `DEFER` benötigt eine eigene Architekturentscheidung.

## Teststrategie

Fokussierte Tests prüfen Bridge- und Reconstruction-Herkunft, fehlendes
Workflow-Manifest, eindeutige Bindung, unbekannte und beschädigte Reviews,
Blocker, Referenz- und Eingabemanipulation, Idempotenz, Konflikte,
unveränderte Reviews und Executions, Operations-Anzeigen, CLI-Hilfe und den
echten CLI-Servicepfad. Gesamttests, Doctor und `git diff --check` bleiben
verbindlich.
