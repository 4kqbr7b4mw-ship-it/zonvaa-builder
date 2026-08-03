# Institutionelle Implementierungsfreigabe – ADR-0061 Guardian B2 Provider Identity v1

Dokument-ID: `GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0061-V1`

Status: `INSTITUTIONELLE IMPLEMENTIERUNGSFREIGABE – GÜLTIG`

Zeitpunkt der externen Beschlussfassung: 03.08.2026, 11:28:19 Uhr
Europe/Berlin (CEST)

Dieser Zeitpunkt ist der Zeitpunkt der Auftragsübergabe und bezeichnet die
außerhalb des Repositories erfolgte Beschlussfassung. Er ist nicht der
Zeitpunkt der Repository-Dokumentation.

Handelnde Rolle: Institutionsgründer in konstituierender Funktion bis zur
ersten ordentlichen Sitzung des Vertrauensrats.

## Grundlage

Grundlage ist der kanonische Ratifizierungsbeschluss zu ADR-0061, dokumentiert
durch `GOV-RATIFICATION-ADR-0061-V1`. Ratifizierung und institutionelle
Implementierungsfreigabe sind zwei getrennte menschliche Beschlüsse.

Diese Freigabe betrifft ausschließlich den in ADR-0061 beschriebenen
Architekturumfang. Sie erweitert ADR-0058, ADR-0059 oder ADR-0060 und deren
Freigaben weder rückwirkend noch stillschweigend. Alle nicht ausdrücklich
freigegebenen Bereiche bleiben gesperrt.

## Freigegeben

Die spätere Implementierung ist ausschließlich freigegeben für:

- eine eigenständige B2 Provider Identity,
- die geschlossenen B2 Provider Classes aus ADR-0061,
- typisierte geschlossene Verantwortungsbereiche,
- typisierte geschlossene Capability-Descriptoren,
- typisierte nicht personenbezogene Provider-Provenienz,
- die strukturelle Trennung von B1 und B2,
- die strukturellen Ausschlüsse aus ADR-0061,
- die Negative Provider Identity Rules,
- synthetische nicht personenbezogene Referenzszenarien,
- notwendige öffentliche Architektur-, Vertrags- und Typdefinitionen,
- fokussierte Tests und notwendige Projektdokumentation.

## Ausdrücklich nicht freigegeben

- B2 Provider Authorization,
- B2 Capability Invocation,
- B2 Runtime und jede technische Ausführung,
- B2 Authority, Grants und Authorization Evaluation,
- natürliche oder personenbezogene Akteursbindung,
- personenbezogene Verarbeitung oder Speicherung personenbezogener Inhalte,
- Key Custody, Schlüsselverwaltung, Credentials oder Secrets,
- Sessions, Caches und Tokens,
- Observation und Runtime Audit,
- Operational Memory, Metrics und Notifications,
- externe Integrationen und produktive Provider-Anbindungen,
- jede Verbindung der B2 Provider Identity zu ausführbaren Systemteilen,
- jede Erweiterung von ADR-0058, ADR-0059, ADR-0060 oder ihrer bestehenden
  institutionellen Freigaben.

## Verfassungsinvarianten

- B2 Provider Identity ist ausschließlich beschreibend.
- Provider Identity besitzt keinerlei Autorisierungswirkung.
- Provider Identity besitzt keinerlei Runtime- oder Invocation-Semantik.
- Provider Classes beschreiben institutionelle Rollen oder Leistungseinheiten,
  niemals natürliche Personen.
- Verantwortungsbereiche und Capability-Descriptoren sind typisierte,
  geschlossene Beschreibungen ohne freie fachliche Semantik.
- Ein unerlaubter personenbezogener Zustand darf strukturell nicht
  modellierbar sein.

## Wirkung und nächste Grenze

Diese Freigabe implementiert nichts, aktiviert nichts und ist kein
Codex-Implementierungsauftrag. Ein separater, scopegebundener Codex-Auftrag
bleibt erforderlich. Commit und Push benötigen weiterhin jeweils eine eigene
ausdrückliche Freigabe. Sämtliche nicht ausdrücklich freigegebenen Bereiche
bleiben gesperrt.

## Provenienz

- Architektur: ADR-0061
- Ratifizierung: `GOV-RATIFICATION-ADR-0061-V1`
- Beschlussart: institutionelle Implementierungsfreigabe außerhalb des
  Repositories
- Beschlusszeit: Zeitpunkt der Auftragsübergabe am 03.08.2026, 11:28:19 Uhr
  Europe/Berlin (CEST)
- Repository-Ausgangsstand: `453ba10a5338a39887f37c9fc5f6d17e451f30ce`
- Scope-Regel: `GOV-INSTITUTIONAL-DECISION-SCOPE-1`
