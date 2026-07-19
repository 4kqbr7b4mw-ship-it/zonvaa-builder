# ADR-0003: Runtime Journal

Status: vorgeschlagen
Datum: 2026-07-19

## Problem

Der Builder speichert den Endzustand einer Session als Handover, kennt aber den Verlauf der aktuellen Arbeit nicht.

Dadurch gehen gelöste Probleme, Entscheidungen, Tests und Zwischenschritte verloren oder erscheinen später als "nicht bestätigt".

## Entscheidung

Der Builder führt während jeder Runtime ein Journal.

Das Journal enthält ausschließlich bestätigte Ereignisse.

Beispiele:

- gestartete Commands
- bestandene Tests
- fehlgeschlagene Tests
- Architekturentscheidungen
- geänderte Dateien
- bestätigte Fehlerbehebungen

Der Handover wird zukünftig nicht mehr ausschließlich aus Sessions erzeugt, sondern aus:

- Runtime Journal
- aktueller Session
- dauerhaftem Wissen
- Constitution
- ADRs

## Ziel

Der Builder erinnert sich nicht nur an Ergebnisse, sondern an den Weg dorthin.
