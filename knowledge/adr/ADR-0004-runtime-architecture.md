# ADR-0004: Runtime Architecture

Status: beschlossen
Datum: 2026-07-19

## Entscheidung

Der Builder verwendet eine zentrale Runtime als Single Source of Truth.

Die Runtime lädt genau einmal:

- Constitution
- Knowledge
- neueste Session
- Sessioninhalt

Alle Komponenten greifen ausschließlich über `get_runtime()` auf diese Daten zu.

## Architektur

Runtime
→ ContextCollector
→ ContextAnalyzer
→ Planner
→ Commands

## Regeln

- Kein mehrfaches Laden derselben Daten.
- Keine Dateizugriffe außerhalb der Runtime.
- Collector liest ausschließlich aus der Runtime.
- Analyzer verarbeitet ausschließlich den Collector-Kontext.
- Neue globale Zustände werden über die Runtime eingeführt.

## Konsequenzen

- deterministischer Kontext
- weniger doppelte Logik
- einfach testbar
- zentrale Erweiterbarkeit (Journal, Cache, Events)
