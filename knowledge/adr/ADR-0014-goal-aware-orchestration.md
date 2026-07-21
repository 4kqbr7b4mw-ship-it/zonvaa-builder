# ADR-0014 – Goal-Aware Orchestration

## Status

Beschlossen

## Kontext

ADR-0013 erweitert die bestehende Decision Engine um einen Goal-basierten Modus mit `GoalContext`, `IdentityContext` und optionalem `WhyAssessment`. Der Orchestrator verwendet bisher ausschließlich den kompatiblen Legacy-Modus und kann diese bereits vorhandenen fachlichen Eingaben noch nicht an die Decision Engine übergeben.

Planner und Execution Engine arbeiten bereits ausschließlich nach einer freigegebenen Entscheidung. Die Execution Engine führt keine realen Seiteneffekte aus, sondern ergänzt die vorhandenen Planschritte um den Status `pending`.

## Entscheidung

Die bestehende Methode `Orchestrator.run` erhält die optionalen Parameter `goal_context`, `identity_context` und `why_assessment`. Der Orchestrator übergibt alle drei Werte unverändert an die bestehende `DecisionEngine.decide`-Methode.

Der Orchestrator erzeugt weder Goal noch GoalContext, lädt keine Identity, erzeugt kein WhyAssessment und interpretiert keine fachlichen Inhalte oder Evidence. Er dupliziert insbesondere nicht die Bindungs- und Statuslogik aus ADR-0013. Ungültige Eingabekombinationen werden unverändert durch die Decision Engine abgelehnt.

## Legacy-Orchestrierung

Aufrufe ohne GoalContext bleiben kompatibel. Die drei neuen Parameter haben den Standardwert `None`; die Decision Engine verwendet damit weiterhin ihre bisherigen technischen Regeln. Eine freigegebene Legacy-Entscheidung erzeugt wie bisher einen Plan und den vorbereiteten Execution-Status. Ein technischer Blocker erzeugt weder Plan noch Execution.

## Goal-basierte Orchestrierung

Im Goal-basierten Modus bestimmt ausschließlich die Decision Engine das Gesamtergebnis:

- `approved`: Der bestehende Planner erzeugt den unveränderten Plan aus dem übergebenen Goal-Text. Die bestehende Execution Engine bereitet diesen Plan vor.
- `blocked`: Planner und Execution Engine werden nicht aufgerufen.
- `needs_review`: Planner und Execution Engine werden nicht aufgerufen. Der Status bleibt vom blockierten Zustand unterscheidbar.

Der Orchestrator erzeugt kein Default-Assessment und verändert weder Status noch Reasons. Technische Reasons, WHY-Status und WHY-Reason bleiben Bestandteil des unveränderten Decision-Ergebnisses.

## Ergebnisstruktur

Die bestehende Orchestrator-Rückgabestruktur bleibt unverändert:

- `decision`: das vollständige Ergebnis der Decision Engine
- `plan`: der vorhandene Plan bei `approved`, sonst eine leere Liste
- `execution`: die vorbereiteten Planschritte bei `approved`, sonst eine leere Liste

Es wird keine parallele Ergebnisstruktur und kein zusätzliches Orchestrator-Modell eingeführt.

## Konsequenzen

- Legacy- und Goal-basierte Aufrufe verwenden denselben Orchestrator.
- Fachliche Integrität und Statuspriorität bleiben alleinige Verantwortung der Decision Engine.
- Planner und Execution Engine werden ausschließlich bei `approved` aufgerufen.
- Es entstehen keine automatische Assessment-Erzeugung, Persistenz, Seiteneffekt-Ausführung oder semantische Bewertung.
