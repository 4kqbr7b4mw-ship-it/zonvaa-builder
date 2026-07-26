# ZONVAA Work Plans

Für längere Arbeitspakete wird dieser Plan während der Umsetzung aktualisiert.
Er dokumentiert bestätigte Fakten und ersetzt keine ADR.

## Aktiver Plan: Mission Context Workflow Integration

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
