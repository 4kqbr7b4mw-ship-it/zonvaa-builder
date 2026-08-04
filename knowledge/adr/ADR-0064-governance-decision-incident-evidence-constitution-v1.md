# ADR-0064 – Governance Decision and Incident Evidence Constitution v1

Status: **RATIFIZIERT – IMPLEMENTIERUNG BEGRENZT FREIGEGEBEN – IMPLEMENTIERT UND VALIDIERT**

Ratifizierungsnachweis: `GOV-RATIFICATION-ADR-0064-V1`

Implementierungsfreigabe: `GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0064-V1`

Recovery- und Implementierungsnachweis: `GOV-ADR-0064-IMPLEMENTATION-RECOVERY-V1`

Die Ratifizierung bestätigt ausschließlich diese Governance-Architektur und
den dokumentierten ADR-0059-Nachweisstatus. Sie ist keine institutionelle
Implementierungsfreigabe, erzeugt kein Decision- oder Incident-Artefakt und
bestätigt ADR-0059 weder rückwirkend noch gegenwärtig.

## 1. Kontext

Institutionelle Entscheidungen und nichttechnische Governance-Prozessvorfälle
werden bisher in einzelnen Governance-Dokumenten sichtbar gehalten. ADR-0052
ist ausschließlich Runtime Incidents vorbehalten. Das Review
`GOV-B2-CONSTITUTIONAL-REVIEW-0059-0062-V1` weist für ADR-0059 nur indirekte
Governance-Evidenz und für Governance-Gate-Vorfälle keinen kanonischen
Verwahrort nach.

## 2. Problemstellung

Fehlende Nachweise dürfen weder erfunden noch aus Implementierung, Commit,
Push, Status oder Handover abgeleitet werden. Zugleich müssen belegte
institutionelle Entscheidungen und Prozessabweichungen typisiert,
rekonstruierbar und ohne personenbezogene Schuld-, Sanktions- oder
Machtwirkung dokumentierbar sein.

## 3. Abgrenzung zu Runtime Incidents

Governance Incident Evidence ist kein Runtime Incident nach ADR-0052. Sie
beobachtet keinen Runtime-Zustand, bewertet keinen technischen Ausfall und
erzeugt keine Incident-Erkennung, Eskalation oder Wiederherstellung.

## 4. Abgrenzung zu Audit, Observation und Operational Memory

Die vorgeschlagenen Artefakte gehören nicht zu Runtime Observation, Runtime
Audit oder Operational Memory. Sie sammeln nichts automatisch, lesen keine
Nutzer- oder Mitarbeiterdaten und dürfen nicht in Betriebsprofile, Metrics
oder Notifications einfließen.

## 5. Governance Decision Record

Ein später implementierbarer immutable Decision Record darf ausschließlich
typisiert enthalten:

- Decision-ID;
- geschlossene Decision-Class;
- betroffenen ADR- oder Paketbezug;
- Entscheidungsrolle als institutionelle Rolle;
- Beschlussdatum;
- Beschlusszeit;
- Zeitzone;
- Repository-Dokumentationszeit;
- abschließend freigegebenen Scope;
- ausdrücklich nicht freigegebenen Scope;
- Evidenzreferenzen;
- nicht personenbezogene Provenienz;
- typisierten Status der Dokumentation.

Er dokumentiert einen bereits außerhalb des Artefakts gefassten menschlichen
Beschluss und fällt selbst keine Entscheidung.

## 6. Governance Incident Evidence

Ein später implementierbares immutable Incident-Evidence-Artefakt darf
ausschließlich typisiert enthalten:

- Incident-ID;
- geschlossene Incident-Class;
- betroffenen Governance-Schritt;
- betroffenen ADR- oder Paketbezug;
- beobachtete Abweichung als geschlossenen Code;
- vorhandene Evidenzreferenzen;
- fehlende Evidenz als typisierte Deklaration;
- nachweisbaren Ereigniszeitpunkt oder ausdrücklich `UNBEKANNT`;
- Erfassungszeitpunkt;
- Repository-Dokumentationszeitpunkt;
- erkannte Auswirkung als geschlossenen Code;
- dokumentierte Korrekturfolge;
- aktuellen Dokumentationsstand;
- nicht personenbezogene Provenienz;
- offene Entscheidungsfrage als typisierte Referenz.

Es ist eine Quittung über belegten Beobachtungsumfang, kein Urteil.

## 7. Geschlossene Incident-Klassen

Die geschlossene Menge v1 lautet:

- `IMPLEMENTATION_BEFORE_RATIFICATION_EVIDENCE`;
- `IMPLEMENTATION_BEFORE_IMPLEMENTATION_APPROVAL`;
- `IMPLEMENTATION_BEFORE_APPROVAL_PUSH`;
- `COMMIT_WITHOUT_COMMIT_APPROVAL`;
- `PUSH_WITHOUT_PUSH_APPROVAL`;
- `SCOPE_EXCEEDED`;
- `GOVERNANCE_EVIDENCE_MISSING`;
- `STATUS_MISREPRESENTED`;
- `WORK_STATE_RETROACTIVELY_REINTERPRETED`;
- `DECISION_TIME_NOT_DOCUMENTED`;
- `DECISION_AND_DOCUMENTATION_TIME_NOT_SEPARATED`.

Neue Klassen erfordern einen neuen institutionellen Architekturakt. Freie
Incident-Kategorien sind unzulässig.

## 8. Entscheidungsprovenienz

Entscheidungsprovenienz referenziert ausschließlich institutionelle Rollen,
Decision- und Governance-IDs sowie nicht personenbezogene Quellen. Sie ist
nicht selbstbestätigend und ersetzt weder den externen Beschluss noch dessen
Evidenz. Natürliche Personen werden nicht als fachliche
Entscheidungsträgerobjekte modelliert.

## 9. Incident-Provenienz

Incident-Provenienz benennt ausschließlich typisierte, nicht personenbezogene
Artefakt- und Git-Evidenzreferenzen sowie explizite Zeitpunkte. Sie weist keine
Schuld zu, bewertet keine Leistung und ersetzt keine fehlende Evidenz.

## 10. Ereigniszeit und Dokumentationszeit

Externer Beschluss- oder Ereigniszeitpunkt und Repository-Dokumentationszeit
sind getrennte Felder und dürfen nicht ausgetauscht werden. Eine spätere
Erfassung verändert den historischen Zeitpunkt nicht.

## 11. Unbekannte historische Zeitpunkte

Ist ein historischer Zeitpunkt nicht durch Evidenz belegt, lautet sein Wert
ausdrücklich `UNBEKANNT`. Erfassungszeit oder Repository-Zeit dürfen ihn nicht
ersetzen. Es gibt keine Wanduhr, implizite Zeitquelle oder Rekonstruktion aus
Vermutungen.

## 12. Evidenzreferenzen

Evidenzreferenzen sind typisiert, nicht personenbezogen und auf vorhandene
kanonische Artefakte begrenzt. Git-Topologie belegt Reihenfolge, aber ohne
weiteren Nachweis keinen damaligen Push- oder externen Beschlusszeitpunkt.

## 13. Fehlende Evidenz

Fehlende Evidenz bleibt als solche sichtbar. Provenienz, Statusdokumente,
Implementierung, Commit, Push und Handover dürfen sie nicht ersetzen.

## 14. Korrekturfolge

Eine Korrekturfolge dokumentiert nur bereits angeordnete oder durchgeführte
Schritte. Incident Evidence startet keinen Workflow, korrigiert nichts
automatisch und legitimiert keinen früheren Vorgang rückwirkend.

## 15. Offene Entscheidungsfragen

Offene Fragen bleiben getrennte institutionelle Gates. Ein Artefakt darf
weder Ratifizierung noch Freigabe, Widerruf oder Sanktion aus ihnen ableiten.

## 16. Negative Rules

Unzulässig sind natürliche Personen als Schuldige oder Incident-Subjekte,
personenbezogene Identitäten und Profile, Mitarbeiter- oder
Leistungsbewertung, Sanktion, Sperre, Widerruf, Autorisierung, automatische
Ratifizierung oder Implementierungsfreigabe, Scope-Erweiterung, automatische
Korrektur oder Governance-Entscheidung, rückwirkende Legitimierung,
Vermutungen als Tatsachen, erfundene Evidenz, Runtime, Observation,
Überwachung, Audit-Wirkung, Operational Memory, Metrics, Notifications, Token,
Permission, Session und Cache.

## 17. Prüffrage Null

Kann diese Architektur fehlende Evidenz als vorhanden darstellen, historische
Entscheidungen erfinden, Vorfälle rückwirkend legitimieren, natürliche
Personen profilieren, bewerten oder sanktionieren oder Sperr-, Autorisierungs-,
Überwachungs-, Runtime-, Observation- oder Operational-Memory-Wirkung erzeugen?

Antwort: **Nein.** Die Artefakte sind immutable, deklarativ, evidenzgebunden
und ohne automatische Entscheidung oder Wirkung.

## 18. Kanonischer Verwahrort

Vorgeschlagen werden getrennte kanonische Dokumentationsbereiche:

- Governance Decision Records unter `governance/decisions/`;
- Governance Incident Evidence unter `governance/incidents/`;
- unterstützende Evidenz verbleibt an ihrem vorhandenen kanonischen Ort und
  wird ausschließlich referenziert.

Diese ADR legt keine Verzeichnisse, Datenbank, Sammlung oder Runtime an. Die
ratifizierten Verwahrorte sind kanonisch und bleiben strikt von
ADR-0052 Runtime Incidents, Operational Memory sowie Nutzer- oder
Mitarbeiterakten getrennt.

## 19. Institutioneller Prozess

Decision Record, Incident Evidence und Prozessdokumentation bleiben getrennt.
Ein Decision Record folgt `GOV-INSTITUTIONAL-DECISION-SCOPE-1`. Incident
Evidence verweist auf einen Prozessschritt, entscheidet ihn aber nicht. Jeder
nachfolgende Beschluss benötigt weiterhin seinen eigenen menschlichen Akt,
Dokumentationsauftrag, Commit und Push.

## 20. Auswirkungen auf bestehende Governance-Dokumente

ADR-0052, Observation, Audit, Operational Memory und bestehende
Entscheidungsdokumente bleiben unverändert. Bei späterer Ratifizierung dient
ADR-0064 ausschließlich als Verfassung künftiger Governance Decision Records
und Governance Incident Evidence. `GOV-NO-FABRICATION-1` bleibt ein offener,
nicht ratifizierter, nicht implementierungsfreigegebener und nicht
implementierter Konsolidierungskandidat; diese ADR ratifiziert ihn nicht.

## 21. Status des ADR-0059-Nachweises

Klassifikation: **Kategorie 3 – nur indirekte Governance-Evidenz vorhanden.**

- kein eigenständiger historischer Ratifikationsnachweis;
- historisches Beschlussdatum: `UNBEKANNT`;
- historische Beschlusszeit: `UNBEKANNT`;
- historische Zeitzone: `UNBEKANNT`;
- historische Entscheidungsrolle: `UNBEKANNT`;
- Implementierungsfreigabe-Commit und Implementierungscommit sind
  nachweisbar;
- die Freigabe liegt in der Git-Topologie vor der Implementierung;
- heutige Repository-Synchronisation beweist keinen damaligen Pushzeitpunkt;
- Implementierung, Commit, Push, Status und Handover ersetzen keinen
  Ratifikationsbeschluss;
- keine rückwirkende Ratifikation und keine erfundene historische Entscheidung.

Eine mögliche heutige institutionelle Bestätigung ist nicht Bestandteil
dieser ADR, wird jetzt weder gefasst noch dokumentiert und müsste später als
eigenständige menschliche Entscheidung mit realem Datum, realer Uhrzeit,
Zeitzone und institutioneller Entscheidungsrolle erfolgen. Historischer
Projektverlauf und gegenwärtiger Beschluss wären strikt zu trennen; erforderlich
wären eigener Dokumentationsauftrag, Commit und Push.

## 22. Ausdrücklich ausgeschlossene Wirkungen

Diese ADR und ihre gesonderte Implementierungsfreigabe sind keine
Implementierung. Sie erzeugen keine automatische Sammlung, Entscheidung,
Korrektur, Sanktion, Sperre, Autorisierung, Runtime, Observation, Audit,
Operational Memory, Metrics, Notifications, personenbezogene Verarbeitung
oder Überwachung.

## 23. Ratifikationsanforderungen

Eine Ratifizierung muss Artefakttrennung, geschlossene Klassen, Zeittrennung,
fehlende Evidenz, Verwahrort, sämtliche Negativregeln und den unveränderten
ADR-0059-Nachweisstatus ausdrücklich bestätigen. Sie darf keine heutige
ADR-0059-Bestätigung enthalten.

## 24. Implementierungsfreigabe

Die getrennte Implementierungsfreigabe
`GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0064-V1` ist gültig. Sie begrenzt eine
spätere Implementierung auf die ratifizierten immutable Verträge,
geschlossenen Typen, Validatoren, Exporte, Tests und kanonische
Dokumentationsanpassungen. Sie erlaubt keine automatische Sammlung,
Workflow-Engine oder Erweiterung bestehender Incident-Architektur.

## 25. Test- und Evidenzanforderungen

Erforderlich sind Tests für Pflichtfelder, geschlossene Klassen,
Immutability, getrennte Zeitpunkte, `UNBEKANNT`, fehlende Evidenz,
nicht personenbezogene Provenienz, getrennte Artefakte und sämtliche
Negativwirkungen. Der historische ADR-0059-Befund muss exakt und ohne
Rekonstruktion erhalten bleiben.

## 26. Konsequenzen und Risiken

Die Architektur schafft einen eindeutigen, nichttechnischen Zielort, ohne
Runtime-Incident- oder Betriebsarchitektur zu vermischen. Das
Risiko einer Verwendung als Mitarbeiterakte oder automatische Sanktion wird
strukturell ausgeschlossen. Zielorte und Verträge sind ausschließlich als
nicht ausführende, immutable Governance-Evidenzgrundlage implementiert.

## 27. Implementierungsstand

ADR-0064 und die Ergänzung ADR-0064-A1 sind vollständig in
`governance/governance_decision_incident_evidence.py` implementiert und
validiert. Enthalten sind die elf Incident-Klassen, `UNBEKANNT`, alle
ratifizierten geschlossenen Taxonomien, immutable Decision Records und
Incident Evidence, Scope-, Evidence-, Missing-Evidence-, Zeit-, Provenienz-
und Fragenverträge sowie deterministische zustandslose Validatoren. Die
kanonischen Dokumentationsorte enthalten keine historischen Records.

Der gesicherte partielle Arbeitsstand wurde kontrolliert angewendet, jede
Komponente gegen ADR-0064 und ADR-0064-A1 neu geprüft und erforderlichenfalls
angepasst oder ersetzt. Der Stash bleibt unverändert als Recovery-Evidence
erhalten; seine Anwendung war keine automatische Übernahme oder Genehmigung.
