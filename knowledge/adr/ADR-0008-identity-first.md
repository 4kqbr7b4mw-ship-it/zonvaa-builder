# ADR-0008 – Identity First

## Status

Accepted

## Kontext

Die Identität von ZONVAA ist kein Dokument, sondern ein zentraler Bestandteil der Architektur.

WHY, Constitution, Vision, Mission, Manifest und Values bilden gemeinsam die unveränderliche Identität des Systems.

Alle Entscheidungen, Empfehlungen, Pläne und Ausführungen müssen sich an dieser Identität orientieren.

## Entscheidung

Die Runtime lädt die Identität von ZONVAA vor allen anderen Komponenten.

Kein Agent, keine Engine und kein Skill darf arbeiten, bevor die Identität vollständig geladen wurde.

Die Identität besitzt Vorrang vor Wissen, Kontext und Entscheidungen.

## Konsequenzen

- Identity wird Bestandteil der Runtime.
- Alle Komponenten erhalten Zugriff auf dieselbe Identität.
- WHY ist die höchste fachliche Instanz.
- Neue Funktionen werden gegen die Identität geprüft.
