# ZONVAA Work Plans

Für längere Arbeitspakete wird dieser Plan während der Umsetzung aktualisiert.
Er dokumentiert bestätigte Fakten und ersetzt keine ADR.

## Aktiver Plan: Codex Context and Handover

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
