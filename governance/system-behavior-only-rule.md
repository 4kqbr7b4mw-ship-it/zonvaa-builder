# System Behavior Only Rule

Regel-ID: `GOV-SYSTEM-BEHAVIOR-ONLY-1`

Status: kanonische C2-Architekturreferenz

Version: 1.0

## Herkunft und Rang

Diese Regel konsolidiert am 02.08.2026 den gemeinsamen Kern bereits
ratifizierter Grenzen aus ADR-0047 und ADR-0053 bis ADR-0058. Sie ist keine
historische Regel `I4`, keine C1-Verfassungsänderung und keine rückwirkende
Umbenennung. C1, Institution, Governance Charter und strengere ADR-Regeln
behalten unverändert Vorrang.

## Kanonische Mindestgrenze

Technische Betriebsnachweise dürfen ausschließlich Systemverhalten abbilden.
Sie dürfen nicht verwendet werden für:

- Nutzerprofilbildung,
- Beobachtung oder Auswertung von Nutzerverhalten,
- Nutzersegmente,
- Nutzungsstatistik oder Häufigkeitsauswertung pro Nutzer,
- themen- oder lebensbereichsbezogene Nutzeranalyse,
- Aggregation von Gesprächsinhalten,
- Zweckentfremdung technischer Betriebsnachweise für Nutzeranalyse.

Strengere Daten-, Observation-, Audit-, Memory-, Persistence-, Metrics-,
Notifications- und B2-Grenzen bleiben vollständig erhalten.

## Wirkung und Nicht-Wirkung

Die Regel vereinheitlicht Referenzen. Sie beobachtet, analysiert, klassifiziert,
persistiert oder aktiviert nichts. Sie autorisiert keine Runtime, keinen
Provider, keine Capability und keine B2-Implementierung.

## Referenz-Mapping

| Dokument | Bisherige Regelquelle | Kanonische Referenz | Status |
|---|---|---|---|
| ADR-0047 | D6 | `GOV-SYSTEM-BEHAVIOR-ONLY-1` zusätzlich zu D6 | UNVERÄNDERT |
| ADR-0053 | eigene absolute Nutzergrenze | `GOV-SYSTEM-BEHAVIOR-ONLY-1` | GEERBT |
| ADR-0054 | ADR-0053 und eigene Audit-Grenze | `GOV-SYSTEM-BEHAVIOR-ONLY-1` | VERSCHÄRFT |
| ADR-0055 | ADR-0053/0054 und eigener Artefaktkatalog | `GOV-SYSTEM-BEHAVIOR-ONLY-1` | VERSCHÄRFT |
| ADR-0056 | Operational-Memory-Artefaktgrenze | `GOV-SYSTEM-BEHAVIOR-ONLY-1` | GEERBT |
| ADR-0057 | absolute Nutzergrenze | `GOV-SYSTEM-BEHAVIOR-ONLY-1` | VERSCHÄRFT |
| ADR-0058 | inhaltsblinder B2-Betriebsblock | `GOV-SYSTEM-BEHAVIOR-ONLY-1` | VERSCHÄRFT |
| AAV/UODL | Autorisierung, Zweckbindung, Minimalität | keine fachliche Ersetzung; ergänzende Governance-Grenze | UNVERÄNDERT |

`NEU` ist ausschließlich die gemeinsame Referenz-ID. Keine der materiellen
Einzelgrenzen wird neu erzeugt oder abgeschwächt.
