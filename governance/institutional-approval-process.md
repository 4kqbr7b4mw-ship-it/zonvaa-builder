# Institutioneller Freigabeablauf vor B2

Dokument-ID: `GOV-B2-APPROVAL-PROCESS-V1`

Status: verbindliche Prozessdokumentation ohne Ausführungsmacht

## Rollen- und Gate-Trennung

| Schritt | Zuständige Rolle | Erforderliches Eingabedokument | Zulässiges Ergebnis | Unzulässige Wirkung | Nächstes Gate |
|---|---|---|---|---|---|
| 1. Gutachterliche Analyse | beauftragte Gutachterrolle | kanonischer Repository-Stand und Prüfauftrag | begründeter Befund, Varianten und Empfehlung | Architekturentscheidung, Freigabe oder Implementierung | Chief-Architect-Entscheidung |
| 2. Chief-Architect-Entscheidung | Chief Architect | Gutachten und bindendes Recht | Annahme, Änderung, Ablehnung oder Vertagung der Architekturvorlage | Vertrauensrats-Kenntnisnahme, C1-Änderung oder Implementierungsfreigabe | gegebenenfalls GOV-40, sonst Vertrauensrat |
| 3. GOV-40-Verfassungsentscheidung | operative Leitung, Vertrauensrat und Nutzer-Konvent nach C1/C2 | ausdrücklicher C1-Änderungsvorschlag | mehrseitig legitimierte Verfassungsentscheidung oder Ablehnung | automatische C1-Änderung durch Gutachten, ADR oder Einzelrolle | Vertrauensrats-Kenntnisnahme |
| 4. Vertrauensrats-Kenntnisnahme | Vertrauensrat | vollständige Kenntnisnahmeunterlage und bindende Architektur | dokumentierte Kenntnisnahme, Vorbehalte, Auflagen oder Veto | Runtime-, Produkt-, Provider- oder Implementierungsfreigabe | institutionelle Implementierungsfreigabe |
| 5. Institutionelle Implementierungsfreigabe | zuständige institutionelle Entscheidungsinstanz | dokumentierte Kenntnisnahme, erfüllte Auflagen und begrenzter Scope | gesonderte, scopegebundene Freigabe oder Ablehnung | Codex-Ausführung, Commit, Push oder pauschale B2-Freigabe | Codex-Implementierungsauftrag |
| 6. Codex-Implementierungsauftrag | Chief Architect innerhalb der Freigabe | gesonderte institutionelle Freigabe und ausführbarer begrenzter Auftrag | Implementierung, Tests und Bericht im freigegebenen Scope | Erweiterung des Scopes, Commit oder Push ohne getrennte Freigabe | Review, danach getrennte Commit-/Push-Freigaben |

GOV-40 ist nur erforderlich, wenn eine echte C1-Änderung beschlossen werden
soll. Die I4-Analyse hat für die aktuelle Konsolidierung keine C1-Änderung
gewählt; Schritt 3 wird daher nicht simuliert oder nachträglich behauptet.

## Machtgrenze

Diese Dokumentation ist keine Workflow-Engine. Sie erzeugt keine Entscheidung,
Kenntnisnahme, Freigabe, Runtime, Autorisierung oder Implementierung. Kein
Schritt darf aus dem erfolgreichen Abschluss eines vorherigen Schritts
automatisch abgeleitet werden.

## Dokumentierter Übergangsstand für ADR-0059

- Schritt 4 wurde für ADR-0058 am 02.08.2026 durch Michael Giese als
  Institutionsgründer in konstituierender Funktion dokumentiert.
- Diese Gründer-Kenntnisnahme gilt nur bis zur erstmaligen Konstituierung des
  ordentlichen Vertrauensrats und muss in dessen erster ordentlicher Sitzung
  bestätigt, geändert oder ersetzt werden.
- Schritt 5 wurde ausschließlich für `Guardian B2 Data Corridor and Consent
  Boundary v1` durch
  `GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0059-V1` erteilt.
- Die dokumentierte Freigabe erlaubt keinen anderen B2-Baustein und keine
  B2-Runtime. Jeder weitere Scope beginnt erneut am jeweils erforderlichen
  institutionellen Gate.

## Übergangsstand für ADR-0060

- ADR-0060 wurde durch den eigenständigen Beschlussnachweis
  `GOV-RATIFICATION-ADR-0060-V1` ratifiziert.
- Architekturvalidierung und Ratifizierung erzeugen keine Implementierungsfreigabe.
- Das eigene institutionelle Implementierungsfreigabedokument
  `GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0060-V1` wurde gesondert erstellt und
  menschlich bestätigt.
- Der getrennte scopegebundene Codex-Auftrag, Implementierung, Review, Commit
  und Push sind abgeschlossen.
- Der bisherige gestoppte Implementierungsauftrag hat diese Schritte nicht
  ersetzt; es wurde keine Änderung, Freigabe, Implementierung oder Runtime
  daraus abgeleitet.

## Übergangsstand für ADR-0061

- ADR-0061 wurde durch den eigenständigen Beschlussnachweis
  `GOV-RATIFICATION-ADR-0061-V1` ratifiziert.
- Die Ratifizierung bestätigt ausschließlich die nicht personenbezogene und
  nicht autorisierende Provider-Identity-Architektur.
- Sie ist keine institutionelle Implementierungsfreigabe und trägt keinen
  Codex-Implementierungsauftrag.
- Die gesonderte institutionelle Implementierungsfreigabe
  `GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0061-V1` wurde als eigenständiger
  menschlicher Beschluss dokumentiert.
- Der erste lokale Implementierungsbeginn erfolgte vor dem kanonischen Push des
  Freigabe-Commits. Dieser bekannte Prozessvorfall wird nicht rückwirkend als
  governancekonform umgedeutet.
- Nach dem Freigabe-Push wurde ein neuer Implementierungsauftrag erteilt, der
  Arbeitsstand vollständig geprüft und erst danach separat committed und
  gepusht.
- Ein eigenständiger kanonischer Governance-Incident-Zielort existiert nicht;
  der Vorfall bleibt in diesem Ablauf und der ADR-0062-Freigabe referenziert.
- ADR-0058, ADR-0059, ADR-0060 und alle bestehenden Sperren bleiben
  unverändert.

## Allgemeine Beschluss-Scope-Regel

Jeder künftige institutionelle Beschluss folgt verbindlich
`GOV-INSTITUTIONAL-DECISION-SCOPE-1` und enthält getrennte Abschnitte
`Freigegeben` sowie `Ausdrücklich nicht freigegeben`. Eine fehlende Nennung ist
keine stillschweigende Freigabe.

## Übergangsstand für ADR-0062

- ADR-0062 wurde durch den eigenständigen Beschlussnachweis
  `GOV-RATIFICATION-ADR-0062-V1` ratifiziert.
- Die Ratifizierung bestätigt ausschließlich die Anwendung der bestehenden
  ADR-0060-Autorisierungsverfassung auf eine unverändert referenzierte B2
  Provider Identity aus ADR-0061.
- Die Ratifizierung erzeugt keine neue Autorisierungssemantik und war keine
  institutionelle Implementierungsfreigabe.
- Die gesonderte institutionelle Implementierungsfreigabe
  `GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0062-V1` wurde als eigenständiger
  menschlicher Beschluss dokumentiert.
- Freigabe-Push, separater Codex-Implementierungsauftrag, Implementierung,
  Review sowie getrennte Commit- und Push-Freigaben sind abgeschlossen. Die
  Reihenfolge verhinderte eine Wiederholung des bei ADR-0061 dokumentierten
  Prozessvorfalls.
- ADR-0058 bis ADR-0061 und alle bestehenden Sperren bleiben unverändert.

## Maintenance-Review ADR-0059 bis ADR-0062

`GOV-B2-CONSTITUTIONAL-REVIEW-0059-0062-V1` prüft die abgeschlossene
nicht ausführende Grundlage. Es ist kein neuer institutioneller Beschluss und
besitzt keine Freigabewirkung. Für ADR-0059 bleibt der fehlende eigenständige
Ratifikationsnachweis als historische Dokumentationslücke sichtbar; für
ADR-0061 bleibt der Prozessvorfall ohne erfundenes Incident-Ledger sichtbar.

## Paket B – ADR-0064 Governance Decision and Incident Evidence

`GOV-DECISION-INCIDENT-EVIDENCE-PROPOSAL-V1` klassifiziert den
ADR-0059-Stand als **nur indirekte Governance-Evidenz**. Datum, Uhrzeit,
Zeitzone und Rolle einer historischen Ratifikation bleiben unbekannt. Eine
heutige Bestätigung müsste als neue gegenwärtige Entscheidung mit eigenem
Zeitpunkt dokumentiert werden und dürfte keine rückwirkende Lückenlosigkeit
behaupten.

ADR-0064 ratifiziert die getrennte Architektur für Governance Decision Record
und Governance Incident Evidence. Der ADR ist nicht
implementierungsfreigegeben oder implementiert. Bis zu einer gesonderten
Implementierungsfreigabe bleiben
ADR-0061-Prozessvorfall und fehlende ADR-0059-Evidenz an ihren bestehenden
Fundstellen sichtbar; ADR-0052 wird nicht zweckentfremdet.

## Ratifizierungsstand ADR-0063

ADR-0063 ist durch `GOV-RATIFICATION-ADR-0063-V1` ausschließlich als
Architektur ratifiziert. Die davon getrennte institutionelle
Implementierungsfreigabe `GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0063-V1` ist als
gegenwärtiger menschlicher Beschluss dokumentiert. Sie implementiert nichts.
Ein separater Implementierungsauftrag setzt den nachweisbaren Push ihres
Freigabe-Commits voraus. ADR-0064 bleibt unabhängig und nicht
implementierungsfreigegeben.
