# ZONVAA Work Plans

Für längere Arbeitspakete wird dieser Plan während der Umsetzung aktualisiert.
Er dokumentiert bestätigte Fakten und ersetzt keine ADR.

## Aktiver Plan: Institution Layer

### Ziel und Nicht-Ziele

Eine eigenständige, unveränderliche Institution-Ebene zwischen Guardian und
Runtime etablieren. Sie enthält ausschließlich langfristige Systemgarantien
für Governance, Nutzerhoheit, Guardian Continuity, Transparenz, Verantwortung,
Schutz, Würde und Vertrauen. Keine Fachlogik, UI, Workflow- oder
Monetarisierungsfunktion.

### Geprüfter Ausgangszustand

- Preflight auf `main` und Commit `9221193` war erfolgreich.
- WHY, Constitution, Values und ADRs enthalten einzelne Schutz- und
  Vertrauensregeln, aber keinen eigenständigen Garantievertrag.
- Runtime lädt Identity, Constitution und Knowledge zentral; eine
  Institution-Ebene fehlt.
- Guardian ist architektonisch definiert, aber noch keine
  Laufzeitkomponente.
- Es existiert keine parallele Governance- oder Policy-Struktur.

### Arbeitsschritte und Fortschritt

- [x] Preflight, Identity, Constitution, Runtime, Preflight und ADRs prüfen.
- [x] Kanonischen Institution-Vertrag und typisiertes Modell erstellen.
- [x] Institution Layer in Runtime und Mission Context integrieren.
- [x] Constitution und neue Architekturentscheidung konsistent ergänzen.
- [x] Modell-, Loader-, Runtime- und Preflight-Tests ergänzen.
- [x] Vollständige Tests, Doctor und `git diff --check` ausführen.
- [in Arbeit] Handover und geprüften Commit erzeugen.

### Entscheidungen und Begründungen

- Institution ist ein eigener, versionierter Garantievertrag; Identity und
  Constitution bleiben unverändert in ihrer jeweiligen Verantwortung.
- Runtime bleibt Single Source of Truth und lädt genau einen unveränderlichen
  `InstitutionContext`.
- Mission Context muss die geladene Institution strukturell nachweisen, damit
  kein freigegebener Workflow ohne Garantien startet.
- Garantien definieren Grenzen, aber keine operative Entscheidung oder
  Ausführung.

### Risiken

- Institution darf nicht zu einer zweiten Constitution oder Policy Engine
  anwachsen.
- „Vertrauen nicht verbrauchen“ benötigt konkrete Architekturtests, darf aber
  nicht als behauptete Messgröße dargestellt werden.

### Teststrategie

- Exakte, stabile Garantietypen und unveränderlicher Kontext.
- Fehlende, unvollständige oder ungültige Institution verhindert Boot.
- Runtime lädt Identity vor Institution und Institution vor operativem
  Kontext.
- Preflight enthält und validiert Institution.
- Vollständige Regression, Doctor, Python 3.9 und `git diff --check`.

### Abweichungen und Abschlusszustand

Der Institution Layer ist als kanonischer Vertrag, typisierter Kontext und
verbindlicher Runtime-Boot-Schritt umgesetzt. Der Mission Context 1.1 weist
Version, Hash und Garantien nach, ohne den Vertrag an operative Komponenten
weiterzureichen. 352 Tests bestehen; Doctor und `git diff --check` sind
erfolgreich. Eine operative Policy Engine war wegen der bewusst
nicht-operativen Garantieebene nicht erforderlich.

## Abgeschlossener Plan: Guardian First, Workflow Second

### Ziel und Nicht-Ziele

Die aus dem Conversation Lab abgeleitete Guardian-First-Erkenntnis als
verbindliche Ergänzung zu ADR-0023 verankern. Interne Entscheidungsräume
bleiben im Alltag unsichtbar, müssen auf Wunsch aber nachvollziehbar,
korrigierbar und ablehnbar sein. Keine Implementierung, UI, Produktlogik oder
Workflow-Änderung.

### Geprüfter Ausgangszustand

- Preflight auf `main` und Commit `c37adbd` war erfolgreich.
- Constitution 1.1 und ADR-0023 priorisieren bereits Guardian und S-V-N-P.
- Das Conversation Lab unterscheidet Bedarf, Entscheidungsraum und
  Workflow-Match im Hintergrund.
- Die bisherige Regel „unsichtbar“ definiert noch nicht verbindlich das Recht
  auf spätere Erklärung, Korrektur und Ablehnung.
- ADR-0023 bleibt gültig; die neue Entscheidung präzisiert ihre
  Transparenzgrenze.

### Arbeitsschritte und Fortschritt

- [x] Preflight, ADR-0023, Constitution und Lab-Regeln prüfen.
- [x] Ergänzende Architekturentscheidung ADR-0024 dokumentieren.
- [x] Verbindliche Transparenzrechte in der Constitution verankern.
- [x] Lab-Dokumentation widerspruchsfrei aktualisieren.
- [x] Vollständige Tests, Doctor und `git diff --check` ausführen.
- [x] Handover und geprüften Commit erzeugen.

### Entscheidungen und Begründungen

- ADR-0024 ergänzt ADR-0023 und ersetzt sie ausdrücklich nicht.
- Entscheidungsräume entstehen als vorläufige Hypothesen vor jeder
  Workflow-Prüfung.
- Unsichtbarkeit bedeutet störungsfreie Alltagserfahrung, nicht Geheimhaltung
  oder Black Box.
- Ein neuer Workflow entsteht niemals dynamisch im Gespräch, sondern erst
  nach ausreichendem Verständnis und einer späteren Architekturentscheidung.

### Risiken

- Transparenz darf den natürlichen Gesprächseinstieg nicht in einen
  technischen Audit-Dialog verwandeln.
- Vorläufige Hypothesen dürfen nicht als bestätigte Selbstaussage des Menschen
  gespeichert oder verwendet werden.

### Teststrategie

- Dokumente auf Rangfolge und Widerspruch zu ADR-0023 prüfen.
- Vollständige Regression, Doctor und `git diff --check`.

### Abweichungen und Abschlusszustand

ADR-0024 ergänzt ADR-0023 ausdrücklich und definiert Guardian First,
Entscheidungsraum-Hypothesen vor Workflow-Prüfung sowie „im Alltag
unsichtbar, auf Wunsch transparent“. Constitution 1.2 verankert
Korrektur-, Ablehnungs-, Wahl- und Nachvollziehbarkeitsrechte. Das Lab wurde
konsistent präzisiert. Es gab keine Implementierung oder Workflow-Änderung.
334 Tests, Doctor und `git diff --check` waren erfolgreich.

## Abgeschlossener Plan: Guardian Conversation Lab

### Ziel und Nicht-Ziele

ADR-0023 mit 100 anonymisierten, deterministischen Gesprächssimulationen
fachlich validieren und daraus Style Guide, Regeln, Anti-Patterns, Taxonomie
und offene Fragen ableiten. Keine UI, Sprachschnittstelle, Fachberatung,
Workflow-Änderung oder neue Laufzeitkomponente.

### Geprüfter Ausgangszustand

- Preflight auf `main` und Commit `2850492` war erfolgreich.
- Constitution 1.1 und ADR-0023 definieren S-V-N-P verbindlich.
- Es gibt noch kein Conversation Lab, keine Simulationsmatrix und keinen
  automatisierten Abdeckungstest.
- Es existiert keine geeignete generische Lab- oder Conversation-Struktur.
  Projektwissen und Sources sind die vorhandenen Ablagen für Dokumentation und
  maschinenlesbare Testdaten.

### Arbeitsschritte und Fortschritt

- [x] Preflight, ADR-0023, Knowledge-Struktur und Testkonventionen prüfen.
- [x] Deterministische Matrix mit 100 diversen Fällen erstellen.
- [x] Style Guide, Regeln, Taxonomie und Anti-Patterns dokumentieren.
- [x] Stabile S-V-N-P-, Datenschutz- und Abdeckungsregeln testen.
- [x] Vollständige Tests, Doctor und `git diff --check` ausführen.
- [x] Handover und geprüften Commit erzeugen.

### Entscheidungen und Begründungen

- Das Lab bleibt Test- und Wissensartefakt; Produktcode wird nur bei einem
  belegten Modellmangel verändert.
- Hintergrundklassifikation bleibt unsichtbare Metadaten und erzeugt keinen
  Workflow.
- Qualität wird über explizite Kriterien und Coverage-Invarianten geprüft,
  nicht durch LLM-Selbsteinschätzung.

### Risiken

- Simulationen beweisen kein reales Nutzervertrauen und ersetzen keine spätere
  Forschung mit freiwilligen Teilnehmenden.
- Regelbasierte Tests können Gesprächsqualität nur strukturell, nicht
  semantisch vollständig bewerten.

### Teststrategie

- Exakt 100 eindeutige Fälle mit breiter Themen-, Stil-, Alters-, Bildungs-
  und Emotionsabdeckung.
- Keine Workflow-Sichtbarkeit, Fachberatung, Preislogik oder sensiblen Daten.
- Zusammenfassung, Anschlussfrage, Klassifikation, Risiken und Verbesserung
  sind pro Fall explizit.
- Vollständige Regression, Doctor und `git diff --check`.

### Abweichungen und Abschlusszustand

Die Matrix enthält 100 eindeutige Einstiege über 25 Themen, vier
Kommunikationsstile, fünf Altersgruppen, vier sprachliche Bildungskontexte,
acht emotionale Zustände, alle Bedarfsklassen sowie bekannte, neue und nicht
vorhandene Entscheidungsräume. Neun deterministische Lab-Tests prüfen
Abdeckung, S-V-N-P-Grenzen, Datenschutz und unsichtbares Workflow-Routing.
Kein Produktcode und kein fachlicher Workflow mussten geändert werden.
334 Tests, Doctor und `git diff --check` waren erfolgreich.

## Abgeschlossener Plan: Guardian Conversation Principles

### Ziel und Nicht-Ziele

S-V-N-P als verbindliche Reihenfolge für Guardian-Interaktion,
Gesprächsführung und UX in die bestehende Identity- und
Constitution-Architektur einordnen. Keine UI, kein neuer Workflow, keine
fachliche Life-Decisions-Änderung und keine Monetarisierungsimplementierung.

### Geprüfter Ausgangszustand

- Preflight auf `main` und Commit `7886bbb` war erfolgreich.
- WHY priorisiert den Menschen und Vertrauen bereits vor Wachstum.
- Constitution regelt Kommunikation, enthält aber keine menschengeführte
  Gesprächsreihenfolge.
- Manifest und Values beginnen fachliche Entscheidungsarbeit mit Ziel und
  Nutzen; sie unterscheiden den Gesprächseinstieg noch nicht ausdrücklich vom
  internen Entscheidungszyklus.
- Es existiert keine Guardian- oder Conversation-ADR und keine parallele
  Interaction-Architektur.

### Arbeitsschritte und Fortschritt

- [x] Preflight, Identity-Dokumente, ADRs und Interaktionsregeln prüfen.
- [x] Constitution um das verbindliche Kernprinzip erweitern.
- [x] Guardian Conversation Principles als ADR dokumentieren.
- [x] Values konsistent abgrenzen und Verhaltensbeispiele ergänzen.
- [x] Vollständige Tests, Doctor und `git diff --check` ausführen.
- [x] Handover und geprüften Commit erzeugen.

### Entscheidungen und Begründungen

- S-V-N-P wird unterhalb des WHY und innerhalb der Constitution verankert; es
  entsteht keine zweite Philosophie.
- Die Reihenfolge gilt für sichtbare Interaktion und UX. Bestehende Goal-,
  Decision- und Workflow-Architektur darf nach hinreichendem Verständnis im
  Hintergrund vorbereitet werden.
- Sympathie bedeutet respektvolle menschliche Anschlussfähigkeit, nicht
  Manipulation oder erzwungene Zustimmung.

### Risiken

- „Hinreichendes Vertrauen“ ist kontextabhängig und darf nicht durch ein
  mechanisches Pflichtdialog-Schema vorgetäuscht werden.
- Fachlich notwendige Sicherheitswarnungen dürfen nicht aus Höflichkeit
  verzögert werden.

### Teststrategie

- Dokumente auf Widersprüche, Rangfolge und klare Grenzen prüfen.
- Vollständige Regression, Doctor und `git diff --check`.

### Abweichungen und Abschlusszustand

S-V-N-P ist in Constitution 1.1 verbindlich und durch ADR-0023 in die
Identity-First-Architektur eingeordnet. Values grenzt den menschlichen
Gesprächseinstieg vom internen Goal- und Entscheidungszyklus ab. Es wurden
keine UI, kein Workflow, keine Preislogik und keine Life-Decisions-Fachregel
implementiert. 325 Tests, Doctor und `git diff --check` waren erfolgreich.

## Abgeschlossener Plan: Power of Attorney Workflow Validation

### Ziel und Nicht-Ziele

Den bestehenden Vorsorgevollmacht-Workflow mit acht realistischen,
anonymisierten Fällen sowie Missbrauchs- und Grenzanfragen fachlich
validieren. Nur belegte Modellmängel korrigieren. Keine Persistenz,
Dokumentanalyse, Rechtsberatung, Netzwerk- oder Cloudfunktion.

### Geprüfter Ausgangszustand

- Preflight auf `main` und Commit `c64854d` war erfolgreich.
- Der Workflow erzeugt eine unveränderliche, ID-basierte Übersicht und gibt
  keine Personenbezeichnungen, Dokumentreferenzen oder Dokumentinhalte aus.
- Professionelle Prüfungen werden nicht automatisch abgeleitet.
- Zwei belegbare Lücken bestehen: eine unklare Einzel-/Gesamtvertretung kann
  nicht explizit modelliert werden; mehrere relevante Dokumentreferenzen
  können nicht vollständig an die Dokumentprüfung gebunden werden.
- Eine abgeschlossene Fachprüfung akzeptiert bisher jeden bestätigten Fakt,
  nicht ausschließlich eine professionell bestätigte Abschlussgrundlage.

### Arbeitsschritte und Fortschritt

- [x] Preflight, Architektur und bestehende Tests prüfen.
- [x] Acht anonymisierte Fall-Fixtures und Erwartungsmatrix erstellen.
- [x] Belegte Modelllücken minimal schließen.
- [x] Missbrauchs- und Grenztests ergänzen.
- [x] Fokussierte und vollständige Prüfungen ausführen.
- [x] Validierungsdokument, Handover und Commit abschließen.

### Entscheidungen und Begründungen

- Die Validierung erweitert ausschließlich bestehende Workflow-Modelle und
  Tests; es entsteht keine zweite Fach- oder Workflow-Architektur.
- Unklare Vertretungsart erhält einen expliziten `unknown`-Status mit
  verpflichtender Frage.
- Weitere vorhandene Vollmachten werden als zusätzliche ID-Referenzen an
  derselben Dokumentprüfung modelliert.
- Ein Prüfabschluss benötigt einen `professionally_confirmed` Fakt.

### Risiken

- Freitext kann nicht vollständig semantisch klassifiziert werden. Er wird
  deshalb nicht in die maschinenlesbare Ausgabe übernommen.
- Der Workflow erkennt keine Dokumentwidersprüche selbst; sie müssen als
  explizite Fragen und Unsicherheiten erfasst werden.

### Teststrategie

- Acht Fallkonstellationen mit expliziten erwarteten IDs und Statuswerten.
- Missbrauchsanfragen dürfen keine verbotene Aussage in der Ausgabe bewirken.
- Invarianten für unklare Vertretung, mehrere Dokumente und Prüfabschluss.
- Regression, Doctor, Python 3.9 und `git diff --check`.

### Abweichungen und Abschlusszustand

Die acht Fallkonstellationen und sechs Missbrauchskategorien wurden gegen den
tatsächlichen Workflow ausgeführt. Drei belegte Modelllücken wurden ohne neue
Architekturschicht geschlossen: unbekannte Vertretungsart, zusätzliche
Dokumentreferenzen und professionell bestätigte Abschlussgrundlage. Die
vollständige Regression umfasst 325 erfolgreiche Tests. Doctor,
Python-3.9-Kompilierung und `git diff --check` waren erfolgreich.

## Abgeschlossener Plan: Power of Attorney Preparation Workflow

### Ziel und Nicht-Ziele

Den ersten realen Life-Decisions-Workflow für die strukturierte Vorbereitung
und Überprüfung einer Vorsorgevollmacht auf dem bestehenden Goal Application
Service aufbauen. Keine Rechtsberatung, Wirksamkeitsprüfung,
Dokumenterstellung, Persistenz, Cloud- oder Netzwerkfunktion.

### Geprüfter Ausgangszustand

- `LifeDecisionCase` bildet Teilnehmer, Dokumentreferenzen, Fakten, Fragen,
  Unsicherheiten, Fachprüfungen, Decision Records und Review Schedules bereits
  als unveränderliches Aggregat mit stabilen IDs ab.
- Der Goal Application Service erzwingt Mission Context und führt über
  Orchestrator, Decision Engine, Planner und Execution Engine.
- Es existiert kein generischer Intake-, Checklist- oder Recommendation-
  Workflow. Die vorhandene Goal-Kette und das Life-Decisions-Aggregat sind die
  Erweiterungspunkte.
- Der Goal-CLI-Pfad unterstützt bereits typisierte optionale Artefakte und
  maschinenlesbare Ergebnisse.

### Arbeitsschritte und Fortschritt

- [x] Preflight und vollständige Bestandsaufnahme durchführen.
- [x] Fachlich neutrale Workflow-Eingabe und Invarianten modellieren.
- [x] Workflow mit Goal Application Service integrieren.
- [x] Bestehenden Goal-CLI-Pfad minimal erweitern.
- [x] Fach-, Sicherheits-, CLI- und Regressionstests ergänzen.
- [x] ADR, vollständige Prüfung, Handover und Commit abschließen.

### Entscheidungen und Begründungen

- Der neue Domänenworkflow wird im bestehenden Paket `life_decisions`
  implementiert und komponiert den vorhandenen Goal Application Service.
- `LifeDecisionCase` bleibt das Aggregat; Workflow-Modelle referenzieren seine
  Objekte nur über IDs.
- Die Ausgabe enthält ausschließlich stabile IDs und Statuswerte.
- Fehlende oder unbekannte Angaben erzeugen Fragen und Unsicherheiten, niemals
  erfundene Fakten.

### Risiken

- Professionelle Prüfbedarfe dürfen nur explizit vorgegeben oder aus klaren
  nutzerkontrollierten Statuswerten abgeleitet werden.
- Personenbezeichnungen und Dokumentinhalte dürfen nicht in Ergebnis,
  Decision Journal oder Handover gelangen.

### Teststrategie

- Vollständige, fehlende und ungeprüfte Fälle sowie Konflikte.
- Aggregatfremde und doppelte IDs.
- Fachprüfungs- und Unsicherheitssemantik.
- Determinismus, Unveränderlichkeit, Mission-Context-Gate und CLI.
- Vollständige Regression, Doctor, Preflight und `git diff --check`.

### Abweichungen und Abschlusszustand

Keine parallele Workflow- oder Persistenzarchitektur wurde benötigt. Der
Workflow nutzt den bestehenden Goal-CLI-Pfad; `--apply`, `--record` und
Knowledge-Artefakte bleiben für diesen fachlichen Pfad bewusst ausgeschlossen.
Die vollständige Regression umfasst 307 erfolgreiche Tests. Doctor,
Python-3.9-Kompilierung und `git diff --check` waren erfolgreich. ADR-0022
dokumentiert die neue verbindliche Workflow-Grenze.

## Abgeschlossener Plan: Mission Context Workflow Integration

### Ziel und Nicht-Ziele

Den bestehenden Goal Application Service durch einen validierten Mission
Context sperren und dessen minimale Workflow-Sicht explizit bis zum
Orchestrator übergeben. Keine neue Fachlogik, kein neuer Workflow, keine
Netzwerk-, Cloud-, UI- oder Datenbankfunktion.

### Geprüfter Ausgangszustand

- Der Preflight erzeugt einen `MissionContext`, wurde aber vom Goal-Workflow
  noch nicht verwendet.
- `GoalApplicationService` injiziert bereits dieselbe Runtime in Collector,
  Goal Engine und Orchestrator.
- Der Orchestrator übergibt technischen Kontext, GoalContext, Identity und
  WHY-Assessment an die Decision Engine und ruft Planner sowie Execution Engine
  ausschließlich nach Freigabe auf.
- Planner und Execution Engine benötigen keinen vollständigen Mission Context.

### Arbeitsschritte und Fortschritt

- [x] Verpflichtenden Preflight ausführen und Mission Context prüfen.
- [x] Application-, Orchestrator-, Decision- und Execution-Verträge lesen.
- [x] Mission Context tief unveränderlich und zeitlich validierbar machen.
- [x] Goal Application Service durch Preflight-Validierung sperren.
- [x] Minimale typisierte Workflow-Sicht an den Orchestrator übergeben.
- [x] CLI- und Fehlerpfade integrieren.
- [x] Fokussierte Tests ausführen.
- [x] Vollständige Tests ausführen.
- [x] Handover erzeugen.
- [x] Geprüften Commit erzeugen.

### Entscheidungen und Begründungen

- Der bestehende Goal Application Service bildet die kleinste reale
  vollständige Kette und wird erweitert.
- Der vollständige Mission Context bleibt am Application-Service-Rand.
  Der Orchestrator erhält nur unveränderliche Git- und Herkunftsmetadaten.
- Decision Engine erhält weiterhin ausschließlich ihren technischen Kontext
  und Goal-Vertrag; Planner und Execution Engine erhalten keinen überflüssigen
  Projektkontext.
- Ein WorkflowContext kann nur aus einem MissionContext abgeleitet werden.

### Risiken

- Zeitliche Gültigkeit ist auf fünf Minuten begrenzt; lange Pausen vor dem
  Start eines Runs verlangen einen neuen Preflight.
- Bestehende direkte Legacy-Orchestrator-Aufrufe bleiben kompatibel; nur der
  Goal-basierte Pfad verlangt den WorkflowContext.

### Teststrategie

- Erfolgreicher vollständiger Goal-Workflow.
- Fehlender, strukturell ungültiger und veralteter Mission Context.
- Tiefe Unveränderlichkeit und deterministische Ableitung.
- Minimale Kontextweitergabe pro Komponente.
- Vollständige Regression, Doctor, Preflight und `git diff --check`.

### Abweichungen und Abschlusszustand

Keine Abweichung vom gewählten Goal-Workflow. Die vollständige Integration,
Fehlerpfade und Kontextgrenzen sind umgesetzt. 292 Tests, Doctor, produktiver
Preflight und `git diff --check` waren erfolgreich. Der lokale Handover ist
erzeugt und gehört zum geprüften Abschlusscommit. Es wurde nicht gepusht.

## Abgeschlossener Plan: Codex Context and Handover

### Ziel

Verbindlichen lokalen Preflight und einen deterministischen, lokalen Staffelstab
auf Basis der bestehenden Runtime- und Knowledge-Architektur bereitstellen.

### Nicht-Ziele

- Keine Netzwerk-, Cloud-, Datenbank- oder UI-Funktion.
- Keine Änderung fachlicher Domänenmodelle.
- Kein automatischer Commit oder Push.

### Geprüfter Ausgangszustand

- `RuntimeManager` lädt Constitution, Knowledge, letzte Session, Project State,
  Verified Facts, Identity und Goal Engine.
- `ContextCollector` und `ContextAnalyzer` verdichten Runtime- und Git-Kontext.
- `KnowledgeManager` kennt ADRs, Protokolle, Handovers, Projektwissen, Sessions,
  Quellen und Verified Facts.
- `ProjectState` persistiert lokalen Laufzeit- und Git-Zustand.
- Der bestehende `handover`-Command erzeugt Session-Markdown über einen
  Netzwerkaufruf; ein lokaler, strukturierter Handover-Vertrag fehlt.
- Ein `preflight`-Command, Root-`AGENTS.md` und Planformat fehlen.

### Arbeitsschritte und Fortschritt

- [x] Bestehende Architektur, ADRs, Runtime, Wissen und Tests prüfen.
- [x] Preflight und Mission Context auf der Runtime ergänzen.
- [x] Deterministischen Handover-Vertrag und atomaren Writer ergänzen.
- [x] Root-`AGENTS.md` und Architekturentscheidung dokumentieren.
- [x] Fehlerfälle, CLI und Rückwärtskompatibilität testen.
- [x] Vollständige Prüfung durchführen.
- [x] Finalen Handover erzeugen.
- [x] Geprüften Commit erzeugen.

### Entscheidungen und Begründungen

- Bestehende `RuntimeManager`-, `KnowledgeManager`-, `ContextCollector`- und
  `knowledge/handovers`-Struktur wird erweitert; es entsteht kein zweiter Store.
- Der neue Handover ist lokal und deterministisch. Der bisherige
  netzwerkabhängige Agentenaufruf ist für den verbindlichen Staffelstab
  ungeeignet.
- Maschinenlesbare JSON- und menschenlesbare Markdown-Sicht teilen denselben
  validierten Datensatz.

### Risiken

- Runtime-Initialisierung schreibt derzeit Project State und muss bei
  strukturellen Fehlern verständlich abbrechen.
- Git- und Teststatus sind Laufzeitdaten; fehlende Werte dürfen nicht erfunden
  werden.

### Teststrategie

- Unit-Tests für Mission Context, Validierung und atomare Handover-Ausgabe.
- CLI-Tests für erfolgreichen und strukturell fehlerhaften Preflight.
- Bestehende vollständige Testsuite, Doctor und `git diff --check`.

### Abweichungen

- Der bestehende modellbasierte Handover wurde nicht parallel beibehalten:
  ADR-0020 ersetzt ihn bewusst durch den lokalen deterministischen Vertrag.
- Statt einer einzelnen Mischdatei entstehen JSON und Markdown aus demselben
  Record, damit Maschinen- und Menschenlesbarkeit jeweils eindeutig bleiben.

### Abschlusszustand

Preflight, lokaler Handover-Vertrag, Arbeitsregeln, Planformat,
Architekturdokumentation und Tests sind umgesetzt. Die vollständige Suite
bestand mit 282 Tests; Doctor, produktiver Preflight und `git diff --check`
waren erfolgreich. Der lokale Handover gehört zum abschließenden Commit; es
wurde kein Push ausgeführt.
