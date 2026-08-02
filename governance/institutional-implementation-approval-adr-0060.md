# Institutionelle Implementierungsfreigabe – ADR-0060

Dokument-ID: `GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0060-V1`

Status: `INSTITUTIONELLE IMPLEMENTIERUNGSFREIGABE – GÜLTIG`

Zeitpunkt der externen Beschlussfassung: 02.08.2026, 21:44:59 Uhr
Europe/Berlin (CEST)

Dieser Zeitpunkt bezeichnet die außerhalb des Repositories erfolgte
Beschlussfassung. Er ist nicht der Zeitpunkt der Repository-Dokumentation.

Handelnde Rolle: Institutionsgründer in konstituierender Funktion bis zur
ersten ordentlichen Sitzung des Vertrauensrats.

## Grundlage

Grundlage ist der kanonische Ratifizierungsbeschluss zu ADR-0060 vom
02.08.2026, dokumentiert durch `GOV-RATIFICATION-ADR-0060-V1`.
Ratifizierung und institutionelle Implementierungsfreigabe sind getrennte
menschliche Beschlüsse. Diese Freigabe autorisiert ausschließlich eine spätere
Implementierung innerhalb des nachfolgend geschlossenen Scopes.

## Freigegeben

- vollständige, eigenständige B2-Authority-Klassen gemäß ADR-0060,
- eigenständige immutable B2-Grants,
- D3-, T4-Erteilungsquittungs-, AAV- und UODL-Bindungen,
- geschlossene Purpose-Scope-Regeln,
- expliziter typisierter Auswertungszeitpunkt,
- zustandslose Authorization Evaluation,
- strukturelle Ausschlüsse unerlaubter Zustände,
- Negative Authority and Grant Rules,
- Evaluation Evidence ausschließlich als immutable Rekonstruktionsartefakt
  ohne autorisierende Wirkung,
- Negative Governance Evidence ausschließlich als nicht personenbezogene
  Verweigerungsquittung ohne Autorisierungszustand,
- öffentliche Architektur-, Vertrags- und Typdefinitionen, soweit sie für
  ADR-0060 erforderlich sind,
- fokussierte Referenzszenarien, Tests sowie notwendige Architektur- und
  Projektdokumentation.

## Ausdrücklich nicht freigegeben

- B2 Provider, Provider Identity und Provider Authorization,
- B2 Capability Invocation und B2 Runtime,
- jede technische Ausführung eines B2 Grants,
- Evaluation Evidence als Token, Cache oder fortwirkender
  Berechtigungsnachweis,
- personenbezogene Verarbeitung oder Speicherung personenbezogener Inhalte,
- B2 Observation und Runtime Audit,
- Operational Memory, Metrics und Notifications,
- Sessions, Caches und Tokens,
- externe Anbindungen und produktive Integrationen,
- jede Verbindung von ADR-0060-Objekten zu ausführbaren Systemteilen,
- automatische Entscheidungen außerhalb der in ADR-0060 definierten
  Evaluation,
- jede rückwirkende oder stillschweigende Erweiterung von ADR-0059 oder
  `GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0059-V1`.

## Verfassungsinvarianten

- D3 ist notwendig, aber niemals hinreichend.
- Kein Nachweis ersetzt einen anderen.
- Grant-Wirksamkeit entsteht ausschließlich zum expliziten
  Auswertungszeitpunkt.
- Grants besitzen keinen eigenen Aktiv-, Gültigkeits- oder Widerrufszustand.
- Evaluation Evidence besitzt keinerlei autorisierende Wirkung.
- Evaluation Evidence darf niemals Eingabe einer späteren Authorization
  Evaluation sein.
- Governance Evidence besitzt keinerlei autorisierende oder sperrende Wirkung.
- Governance Evidence dient ausschließlich der Rekonstruierbarkeit einer
  verweigerten Evaluation.
- Governance Evidence unterliegt ausschließlich den Governance-
  Aufbewahrungsregeln und darf niemals zur fachlichen Autorisierung oder
  Ablehnung zukünftiger Entscheidungen verwendet werden.
- Ein unerlaubter personenbezogener Zustand darf strukturell nicht
  modellierbar sein.

## Wirkung und nächste Grenze

Diese Freigabe implementiert nichts, aktiviert nichts und ist kein
Codex-Implementierungsauftrag. Ein separater Codex-Auftrag bleibt erforderlich.
Commit und Push benötigen weiterhin jeweils eine eigene ausdrückliche
Freigabe. Sämtliche nicht ausdrücklich freigegebenen Bereiche bleiben
gesperrt.

## Provenienz

- Architektur: ADR-0060
- Ratifizierung: `GOV-RATIFICATION-ADR-0060-V1`
- Beschlussart: institutionelle Implementierungsfreigabe außerhalb des
  Repositories
- Repository-Ausgangsstand: `99ed640d2d1ff838e4b996a6b120bad2370dabb4`
