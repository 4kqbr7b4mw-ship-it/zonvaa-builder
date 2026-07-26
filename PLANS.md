# ZONVAA Work Plans

Für längere Arbeitspakete wird dieser Plan während der Umsetzung aktualisiert.
Er dokumentiert bestätigte Fakten und ersetzt keine ADR.

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
