# ADR-0007 – Knowledge Priority System

## Status

Beschlossen

## Kontext

Der Builder verarbeitet verschiedene Wissensquellen:
Runtime-Zustand, Git-Informationen, Testergebnisse, Architekturentscheidungen, ProjectState und Sessions.

Bisher konnten ältere Sessions Unsicherheiten enthalten, die aktuelle bestätigte Zustände überlagern.

Für belastbare Entscheidungen benötigt ZONVAA eine definierte Priorität der Wissensquellen.

## Entscheidung

ZONVAA verwendet eine feste Wissenspriorität.

## Priorität

1. Aktueller Runtime-Zustand und bestätigte Ausführungsergebnisse
2. Git-Status und aktuelle Commits
3. Aktuelle Testergebnisse
4. Architekturentscheidungen (ADR)
5. Persistenter ProjectState
6. Sessions und Übergaben
7. Zusammenfassungen und Interpretationen

Niedrigere Prioritäten dürfen höhere Prioritäten nicht überschreiben.

## Konsequenzen

- Aktuelle Fakten werden gegenüber alten Annahmen bevorzugt.
- Handover und Agenten können Unsicherheiten besser einordnen.
- Architekturentscheidungen bleiben nachvollziehbar.
- Wissen wird nicht nur gespeichert, sondern bewertet.

## Nächster Ausbau

Die Prioritätslogik wird später in ContextAnalyzer und Knowledge Manager integriert.
