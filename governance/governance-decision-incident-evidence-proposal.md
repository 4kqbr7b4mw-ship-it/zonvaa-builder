# Governance Decision and Incident Evidence – Analyse und Entscheidungsvorlage v1

Dokument-ID: `GOV-DECISION-INCIDENT-EVIDENCE-PROPOSAL-V1`

Status: `VORGESCHLAGEN – NICHT RATIFIZIERT – NICHT IMPLEMENTIERUNGSFREIGEGEBEN – NICHT IMPLEMENTIERT`

Stand: 03.08.2026

## Grenze

Dieses Dokument trennt den historischen ADR-0059-Nachweisbefund von einer
zukünftigen allgemeinen Governance-Incident-Architektur. Es erzeugt weder
einen historischen Beschluss noch einen Vorfallrecord. Es ist keine
Ratifizierung, Implementierungsfreigabe, Runtime-Incident-Regel, Überwachung,
Sanktion oder Operational-Memory-Erweiterung.

## Historische Analyse ADR-0059

### Untersuchte Artefakte

- ADR-0058 und ADR-0059 sowie ihre Git-Historie;
- `GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0059-V1`;
- Gründer-Kenntnisnahme zu ADR-0058;
- B2 Readiness, Architekturkarte, institutioneller Prozess, Projektstatus,
  `PLANS.md` und Handover;
- Implementierung, Tests und Git-Commits für den Data Corridor;
- Repository-Suche nach Ratifikation, Beschlusszeit, Entscheidungsrolle und
  eigenständigem ADR-0059-Nachweis.

### Tatsächlich vorhandene Evidenz

- Commit `55a04f2ad3cc075f0aad720a75460a9438570e15` vom
  02.08.2026 um 20:10:49 CEST dokumentiert die institutionelle
  Implementierungsfreigabe für ADR-0059. Das Dokument nennt Datum und Rolle
  der Freigabe, aber keine getrennte Ratifikationsentscheidung für ADR-0059.
- Commit `77539c727b488dba345b1e1c516e4ed2f895964c` vom
  02.08.2026 um 20:37:10 CEST implementiert den Data Corridor.
- ADR-0059 und spätere Statusdokumente bezeichnen die Architektur als
  ratifiziert beziehungsweise implementiert.
- Es existiert kein eigenständiges `ratification-adr-0059`-Dokument und kein
  davon gleichwertiger kanonischer Beschlussnachweis.

Die Git-Topologie belegt, dass der Freigabe-Commit ein Vorfahr des
Implementierungscommits ist und beide heute auf `origin/builder-reset-v2`
enthalten sind. Git belegt jedoch keinen Zeitpunkt eines damaligen Pushs. Ein
Pushzeitpunkt oder eine vollständige Push-vor-Auftrag-Sequenz ist daher aus den
Repository-Artefakten nicht rekonstruierbar.

Commitzeiten belegen Repository-Handlungen, nicht den Zeitpunkt einer externen
institutionellen Ratifikation. Implementierung, Tests, Status und Handover
belegen keine Ratifikation.

### Exakter Nachweisstatus

Klassifikation: **3. nur indirekte Governance-Evidenz vorhanden.**

Eine eigenständige historische Ratifizierung von ADR-0059 ist nicht
nachweisbar. Datum, Uhrzeit, Zeitzone und Entscheidungsrolle einer solchen
Ratifikation sind **UNBEKANNT**. Die Implementierungsfreigabe beweist ihren
eigenen begrenzten Beschluss, darf aber nicht in einen früheren oder getrennten
Ratifikationsbeschluss umgedeutet werden.

### Erforderliche heutige Entscheidung

Erforderlich wäre eine neue, gegenwärtige institutionelle
Bestätigungsentscheidung. Sie müsste den aktuellen Architekturinhalt von
ADR-0059 ausdrücklich bestätigen, die historische Nachweislücke offenlegen und
ihren eigenen tatsächlichen Beschlusszeitpunkt sowie ihre Rolle dokumentieren.
Sie dürfte nicht rückdatiert werden und auch nicht behaupten, bereits vor Implementierung
gegolten zu haben. Ob zusätzlich der bestehende Implementierungsstand
institutionell anerkannt oder gesondert neu geprüft werden muss, bleibt eine
eigene Entscheidungsfrage.

Dieses Paket trifft diese Entscheidung nicht.

## Governance-Prozess- und Gate-Vorfälle

### Abgrenzung

Governance Incidents sind dokumentierte Abweichungen in institutionellen
Entscheidungs-, Freigabe-, Commit-, Push- oder Scope-Sequenzen. Sie sind keine
Runtime Incidents nach ADR-0052, keine Sicherheits- oder fachlichen Vorfälle,
keine Testfehler und keine Nutzerbeobachtung. Sie dürfen nicht in Operational
Memory, Nutzerprofile, Personalbewertung, Sanktionen oder Überwachung
umgedeutet werden.

### Zu erfassende Klassen

- Implementierung vor dokumentierter Ratifizierung;
- Implementierung vor institutioneller Implementierungsfreigabe;
- Implementierung vor Push des Freigabe-Commits;
- Commit ohne Commit-Freigabe;
- Push ohne Push-Freigabe;
- Scope-Überschreitung;
- fehlender Governance-Nachweis;
- falsche oder unvollständige Statusdarstellung;
- nachträgliche Umdeutung eines Arbeitsstands;
- nicht dokumentierter Entscheidungszeitpunkt;
- fehlende Trennung von Beschluss- und Dokumentationszeitpunkt.

Der bekannte ADR-0061-Vorfall fällt in die Klasse „Implementierung vor Push
des Freigabe-Commits“. Bestehende Dokumente belegen Korrektur durch den
nachträglichen Push und eine neue Prüfung nach separatem Auftrag. Der
ursprüngliche Beginn wird nicht rückwirkend legitimiert. Ein kanonischer
eigenständiger Zielort fehlt weiterhin.

## Architekturvarianten

| Variante | Stärken | Grenzen und Risiko |
|---|---|---|
| 1. neue allgemeine Governance-Regel | bindende Semantik an einer Stelle | allein kein typisierter Einzelbeleg; Gefahr einer zu breiten Meta-Regel |
| 2. Governance Decision Record | Entscheidungen mit Zeit, Rolle und Scope rekonstruierbar | Prozessabweichungen und fehlende Evidenz benötigen eigenen Gegenstand |
| 3. eigener Governance-ADR | sauber von ADR-0052 und Runtime getrennte Verfassung | ADR allein speichert keine einzelnen Vorfälle |
| 4. institutioneller Prozessvertrag | bindet Gates und zulässige Folgen | kann ohne Evidence-Artefakt Abweichungen nicht vollständig belegen |
| 5. Kombination aus Governance-ADR, Decision Record und Incident Evidence | eine kanonische Semantik, getrennte Entscheidungs- und Abweichungsnachweise, Prozessreferenz | benötigt Ratifizierung und spätere getrennte Implementierungsfreigabe |

## Bevorzugte Variante

**Vorgeschlagen ist Variante 5.** Ein eigener zukünftiger Governance-ADR soll
die Semantik und Grenze festlegen. Ein immutable Governance Decision Record
soll ausschließlich tatsächlich gefasste Entscheidungen belegen. Ein davon
getrenntes immutable Governance Incident Evidence soll nachweisbare
Prozessabweichungen abbilden. Der institutionelle Prozess referenziert beide,
ohne sie selbst zu erzeugen oder auszuwerten.

Diese Präferenz ist **nicht ratifiziert, nicht implementierungsfreigegeben und
nicht implementiert**. Der ratifizierungsreife Inhalt wurde ohne
Freigabewirkung in den formalen Vorschlag ADR-0064 überführt; Capability
Invocation und Runtime wurden nicht begonnen.

## Vorgeschlagenes Governance Incident Evidence

Ein späteres immutable Artefakt dürfte ausschließlich enthalten:

- Incident-ID;
- geschlossene Incident-Klasse;
- betroffenen Governance-Schritt;
- betroffenen ADR- oder Paketbezug;
- typisierte beobachtete Abweichung;
- vorhandene Evidenzreferenzen;
- ausdrücklich fehlende Evidenz;
- erkannte, nicht personenbezogene Auswirkung;
- dokumentierte Korrekturfolge;
- aktuellen Dokumentationsstand;
- nicht personenbezogene Provenienz;
- expliziten Erfassungszeitpunkt;
- Ereigniszeitpunkt nur, wenn nachweisbar, andernfalls `UNBEKANNT`;
- offene Entscheidungsfrage.

Es darf keine natürliche Person als Schuldige führen und keine Profile,
Leistungsbewertungen, Sanktionen, Sperren, Autorisierung, Runtime-Wirkung,
automatische Korrektur, automatische Governance-Entscheidung, Widerruf,
Permission, Token, Session, Cache, Observation oder Überwachung bewirken.
Vermutungen sind keine Tatsachen. Provenienz ersetzt keine fehlende Evidenz.
Das Artefakt legitimiert nichts rückwirkend.

## Entscheidungs- und Dokumentationszeit

Ein Decision Record muss externen Beschlusszeitpunkt und Zeitpunkt der
Repository-Dokumentation getrennt führen. Ein Governance Incident darf einen
Ereigniszeitpunkt nur ausweisen, wenn er durch Evidenz getragen wird. Ist er
nicht belegt, bleibt er ausdrücklich `UNBEKANNT`; der spätere
Erfassungszeitpunkt darf ihn nicht ersetzen.

## Offene Entscheidungsfragen

1. Soll die bevorzugte Kombination durch einen eigenen Governance-ADR
   ratifiziert werden?
2. Welche geschlossenen Codes gelten für Governance-Schritte,
   Incident-Klassen, Auswirkungen und Dokumentationsstände?
3. Welcher institutionelle Ort verwahrt Decision Records und Incident
   Evidence, ohne Operational Memory oder Überwachung zu werden?
4. Welche heutige Bestätigung und welche Prüfung des bestehenden
   ADR-0059-Implementierungsstands sind erforderlich?

## Vorgeschlagener späterer Paketschnitt

Die zukünftige allgemeine Governance-Semantik benötigt einen eigenen
Governance-ADR, dessen Nummer erst nach ausdrücklichem Architekturauftrag aus
dem dann aktuellen ADR-Stand bestimmt werden darf. Decision Record und
Governance Incident Evidence wären getrennte, durch diese ADR begrenzte
Dokumentationsverträge. Ein weiterer institutioneller Prozessschritt müsste
erst danach ihre Verwendung festlegen.

Der gegenwärtige ADR-0059-Nachweisbefund bleibt ein historischer Befund und
darf nicht in die allgemeine Regel hineingeschrieben werden. Eine heutige
Bestätigung von ADR-0059 wäre ein eigener menschlicher Beschluss. Keine dieser
Arbeiten ist Teil dieses Pakets.

## Prüffrage Null

> Kann die vorgeschlagene Architektur einen fehlenden Nachweis als vorhanden
> darstellen, einen Prozessvorfall rückwirkend legitimieren, eine natürliche
> Person profilieren oder sanktionieren oder Autorisierung, Invocation,
> Runtime-Macht beziehungsweise einen unerlaubten personenbezogenen Zustand
> erzeugen?

Antwort: **Nein.** Unbekannte Tatsachen bleiben unbekannt, Evidence bleibt
nicht personenbezogen und rein deklarativ, und jede bindende Einführung
verlangt einen späteren gesonderten Architektur- und Institutionenprozess.
