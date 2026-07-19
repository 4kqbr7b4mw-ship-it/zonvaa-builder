# ADR-0005 – Decision Engine

## Status

Beschlossen

## Kontext

Runtime, ProjectState und ContextAnalyzer liefern eine belastbare Informationsbasis.
Der Planner erzeugte bisher unabhängig vom Projektzustand immer denselben Plan.

Es fehlte eine zentrale Instanz, die vor der Planung entscheidet, ob ein Workflow ausgeführt werden darf.

## Entscheidung

Eine eigenständige DecisionEngine bewertet den analysierten Projektkontext und liefert eine deterministische Entscheidung.

Der Orchestrator verwendet diese Entscheidung als verbindliche Grundlage.
Der Planner erstellt nur dann einen Plan, wenn die Entscheidung freigegeben wurde.

## Architektur

Runtime
→ ContextCollector
→ ContextAnalyzer
→ DecisionEngine
→ Planner
→ Orchestrator
→ Agents

## Konsequenzen

- Entscheidung und Planung bleiben getrennt.
- Entscheidungen sind deterministisch testbar.
- Blockierte Workflows erzeugen keinen Plan.
- Weitere Regeln können in der Decision Engine ergänzt werden.
- KI-basierte Entscheidungen dürfen später ergänzt werden, ohne Planner und Orchestrator grundlegend umzubauen.
