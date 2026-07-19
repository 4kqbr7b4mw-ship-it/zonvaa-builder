# ADR-0006 – Execution Engine

## Status

Beschlossen

## Kontext

Der Orchestrator verbindet aktuell DecisionEngine und Planner.
Der Planner erzeugt ausführbare Arbeitsschritte als strukturierte Beschreibung.

Es fehlt eine kontrollierte Schicht, die geplante Schritte übernimmt und für die Ausführung vorbereitet.

Die direkte Ausführung durch den Orchestrator würde Verantwortlichkeiten vermischen und die spätere Erweiterung um Agenten, Sicherheitsprüfungen und Protokollierung erschweren.

## Entscheidung

Eine eigenständige ExecutionEngine wird eingeführt.

Die ExecutionEngine übernimmt ausschließlich die Verarbeitung genehmigter Pläne.

Sie führt in der ersten Version keine realen Änderungen aus, sondern erzeugt einen kontrollierten Ausführungszustand für jeden Schritt.

## Architektur

Runtime
→ ContextCollector
→ ContextAnalyzer
→ Orchestrator
→ DecisionEngine
→ Planner
→ ExecutionEngine
→ Agents

## Konsequenzen

- Planung und Ausführung bleiben getrennt.
- Ausführungsstatus kann nachvollzogen und getestet werden.
- Sicherheitsprüfungen können vor tatsächlicher Ausführung ergänzt werden.
- Agenten bleiben austauschbare Ausführungskomponenten.
- Spätere Erweiterungen wie Patch-Systeme oder autonome Workflows können darauf aufbauen.
