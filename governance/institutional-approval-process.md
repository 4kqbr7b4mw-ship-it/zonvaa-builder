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
