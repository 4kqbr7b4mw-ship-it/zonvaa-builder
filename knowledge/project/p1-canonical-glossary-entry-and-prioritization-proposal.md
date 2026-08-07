# P1 – Glossareintragstruktur und Priorisierung bestehender B2-Begriffe

Status: **ANALYSE UND STRUKTURVORSCHLAG – KEINE BEGRIFFSDEFINITIONEN – KEINE KANONISIERUNG**

## 1. Grenze

Dieses Dokument definiert ausschließlich mögliche Felder und priorisiert
bereits verwendete Begriffskandidaten. Es erstellt keine Einträge, Definitionen
oder neue Taxonomie. Die genannten ADRs bleiben die materiellen Regelinhaber.

## 2. Vorgeschlagene Eintragstruktur

| Feld | Zweck und Bedeutung | Begründung |
| --- | --- | --- |
| Identifier | stabiler, sprachneutraler Schlüssel des Begriffs | trennt Identität von Benennung, Datei und Sprache |
| Eintragsversion | veröffentlichter Bedeutungsstand | macht Bedeutungsänderungen referenzierbar |
| Status | Kandidat, später kanonisch oder deprecated; konkrete verbindliche Werte sind noch zu beschließen | verhindert, dass Entwürfe als kanonisch erscheinen |
| Semantische Domäne | fachlicher Verwendungsbereich | begrenzt gleichlautende Begriffe ohne globale Bedeutungsbehauptung |
| Bevorzugte Benennung | primäre sprachmarkierte Bezeichnung | trennt menschliche Anzeige vom Identifier |
| Kanonische Definition | später freigegebene, knappe Bedeutung | schafft einen eindeutigen Bezugspunkt; bleibt in P1 leer |
| Aussageumfang | was die Definition leisten darf | schützt vor stiller Erweiterung |
| Abgrenzungen | ausdrücklich nicht erfasste Bedeutungen | macht negative Grenzen prüfbar |
| Nicht identisch mit | leicht verwechselbare Begriffe | verhindert semantische Gleichsetzung |
| Verwandte Begriffe | reine Navigationsbeziehungen mit benannter Art | vermeidet unbestimmte oder priorisierende Links |
| Materielle Regelinhaber | ADRs, Governance-Regeln oder andere Quellen mit tatsächlicher Zuständigkeit | verhindert, dass das Glossar Normquelle wird |
| Unterstützende Referenzen | nicht normative Kontextquellen | trennt Hilfe von Regelwirkung |
| Historische Verwendungen | frühere Benennungen und Zeitstände | erhält historische Wahrheit ohne aktuelle Mehrdeutigkeit |
| Nicht zuständige Quellen | bekannte falsche Zuständigkeitszuschreibungen | schützt gegen Referenzdrift |
| Lokalisierungen | Benennung und Definition je BCP-47-Tag mit eigenem Prüfstand | Übersetzung ist nicht automatisch Bedeutungsgleichheit |
| Synonyme und Suchformen | alternative sprachmarkierte Benennungen | hält Suchhilfe von der bevorzugten Benennung getrennt |
| Provenienz | Autorenschaft, Prüfnachweise und Quellen des Eintrags | macht Entstehung und Aussagebasis nachvollziehbar |
| Gültigkeits-/Veröffentlichungszeit | expliziter dokumentarischer Zeitpunkt | trennt Bedeutungsversionen und historische Stände |
| Änderungshistorie | unveränderte Liste veröffentlichter Änderungen | verhindert stilles Umschreiben |
| Deprecation | Grund, Zeitpunkt und optionaler Nachfolger | erhält stabile Referenzen nach Ablösung |
| Offene Punkte | bekannte ungeklärte Bedeutungs- oder Übersetzungsfragen | verhindert erfundene Vollständigkeit |

Nicht aufgenommen werden technische Datentypen, Runtime-Bindings,
Ausführungsadressen, Nutzerbezüge, personenbezogene Beispiele oder
automatische Ableitungsregeln.

## 3. Implizit kanonische B2-Begriffskandidaten

„Implizit kanonisch“ bedeutet hier nur: Der Ausdruck besitzt bereits eine
geschlossene oder klar abgegrenzte Bedeutung in einem vorhandenen materiellen
Regelinhaber. Es ist kein Glossarstatus.

| Kandidatengruppe | Vorhandener Regelinhaber | Analysegrund |
| --- | --- | --- |
| Data Corridor, Consent Boundary, Data Classification, Depersonalization Boundary | ADR-0059 | eröffnet und begrenzt die B2-Datenkette |
| Authority, Grant, Authorization, Purpose Scope, Evaluation Evidence | ADR-0060 | trennt Befugnis, gebundene Autorisierung und mechanische Auswertung |
| Provider Identity, Provider Class, Responsibility Area, Capability Descriptor | ADR-0061 | trennt nicht personenbezogene Providerbeschreibung von Autorisierung und Runtime |
| Provider Authorization, Provider Authorization Evidence | ADR-0062 | bindet Provider und vorhandene Befugnis ohne Ausführung |
| Purpose Binding, Purpose Halbordnung, UODL Mapping | ADR-0063 | begrenzt Zweckbewegung und ordnet das bestehende UODL-Paar zu |
| Governance Decision Record, Governance Incident Evidence, Provenienz, Ereigniszeit, Dokumentationszeit | ADR-0064 und ADR-0064-A1 | hält institutionelle Entscheidung, Abweichung, Zeit und Nachweis getrennt |
| Capability Invocation Intent, Binding, Request, Decision, Evidence, Receipt, Resolution Snapshot, Controlled Stop | ADR-0065 | beschreibt die nicht ausführende Invocation-Vertragsfamilie |
| Runtime Air Gap, Transition, Runtime Preparation, Runtime Discussion Preconditions | ADR-0066 | erklärt die Abwesenheit eines Übergangs; keine technische Komponente |

Die generischen Wörter `Identity`, `Capability`, `Evidence`, `Provider` und
`Authorization` dürfen nicht isoliert kanonisiert werden, bevor ihre Domäne
und ihre Abgrenzung zu B1, B2 und Governance ausdrücklich geklärt sind.

## 4. Priorisierung ohne Definition

### Priorität 1 – Kettengrenzen und Machttrennung

- Data Corridor
- Authority
- Grant
- Authorization
- Provider Identity
- Provider Authorization
- Purpose Binding
- UODL Mapping
- Capability Invocation
- Controlled Stop
- Runtime Air Gap

Begründung: Diese Begriffe bestimmen den lesbaren Schutzfluss und verhindern
die gefährlichsten Gleichsetzungen zwischen Datenzulässigkeit, Befugnis,
Aufrufabsicht und Ausführung. Ihre Quellen sind vorhanden und geschlossen.

### Priorität 2 – Nachweis, Zeit und Abschlussartefakte

- Evidence
- Provenienz
- Ereigniszeit
- Dokumentationszeit
- Evaluation Evidence
- Invocation Decision
- Invocation Receipt
- Invocation Resolution Snapshot
- Governance Decision Record
- Governance Incident Evidence

Begründung: Diese Begriffe sichern Nachweis- und Zeitkonsistenz, sind aber ohne
die Priorität-1-Kette schwer korrekt abzugrenzen. `Evidence` benötigt
domänenspezifische Einträge oder eine ausdrücklich geprüfte Oberbeziehung.

### Priorität 3 – geschlossene Unterbegriffe

- Consent Boundary
- Data Classification
- Depersonalization Boundary
- Purpose Scope
- Capability Descriptor
- Provider Class
- Responsibility Area
- Runtime Preparation
- Runtime Discussion Preconditions

Begründung: Sie stabilisieren Detailkommunikation, setzen aber die
übergeordneten Kettengrenzen voraus.

### Nicht priorisiert

Produktbegriffe außerhalb der belegten B2-Regelinhaber, freie Synonyme und
ruhende Architekturkandidaten werden durch P1 nicht priorisiert. Eine
Priorisierung ist keine Freigabe zur Definition oder Kanonisierung.

## 5. Prüffragen für spätere Einträge

- Ist der Begriff Produktsemantik, Architekturbegriff oder Governancebegriff?
- Welches vorhandene Artefakt besitzt materielle Zuständigkeit?
- Sind B1- und B2-Bedeutungen getrennt?
- Würde die Definition eine bestehende Regel auslegen oder erweitern?
- Sind negative Abgrenzungen und leicht verwechselbare Begriffe vollständig?
- Sind alle Quellen auflösbar und nach Aussageart getrennt?
- Sind Übersetzungen bedeutungsgleich oder nur angenähert?
- Entsteht durch den Eintrag irgendeine Aktivierungs-, Runtime-, Observation-
  oder Personenbezugsaussage?

Nur ein eindeutiges Nein auf die letzte Frage wahrt den P1-Scope.

