# knowledge_priority_v1

## Kurzüberblick

Der ZONVAA Builder ist ein wissensgetriebenes Python/Typer-CLI-System zur Planung, Entwicklung, Prüfung, Dokumentation und Übergabe von Softwareprojekten. Verbindliche Grundlage ist die `constitution/constitution.md` in Version 1.0. Der aktuelle Git-Branch ist `feat/decision-engine-v1`; der Arbeitsbaum ist laut bereitgestelltem Kontext sauber. Seit der letzten gespeicherten Übergabe wurden laut Git-Historie das Knowledge-Priority-System definiert und Architektur-ADRs in die Kontextsammlung aufgenommen. Die aktuelle Ausführung `python3 -m builder.main handover knowledge_priority_v1` bestätigt den funktionierenden Handover-Pfad bis zur laufenden Agentenantwort. Bestätigt sind Start von `builder.main`, Aufruf des `handover`-Commands, Kontextsammlung, Task-Erstellung, Laden des Handover-Agenten und Annahme der Anfrage durch die OpenAI Responses API. Ein aktueller vollständiger `pytest`-Lauf ist weiterhin nicht bestätigt. Nächster Schritt ist die Validierung des aktuellen Stands durch einen vollständigen Testlauf.

## Letzte Session

- **heute umgesetzt**
  - Laut jüngsten Commits:
    - `ADR-0007 – Knowledge Priority System` wurde definiert.
    - Architektur-ADRs wurden in die Kontextsammlung aufgenommen.
    - Eine Execution-Engine-Handover-Session wurde ergänzt.
  - In der aktuellen Ausführung wurde `python3 -m builder.main handover knowledge_priority_v1` gestartet.
  - `ContextCollector.collect()` und `build_handover_task()` wurden erfolgreich ausgeführt.
  - `agents/handover.md` wurde durch `RoleAgent` erfolgreich geladen.
  - `OPENAI_API_KEY` und `OPENAI_MODEL` konnten verwendet werden.
  - Die OpenAI Responses API hat die Anfrage angenommen.

- **getestete Funktionen**
  - Durch die aktuelle Ausführung bestätigt:
    - Start von `builder.main`
    - erfolgreicher Aufruf des `handover`-Commands
    - erfolgreiche Ausführung von `ContextCollector.collect()`
    - erfolgreiche Ausführung von `build_handover_task()`
    - Laden von `agents/handover.md`
    - Nutzung von `OPENAI_API_KEY` und `OPENAI_MODEL`
    - Annahme der Anfrage durch die OpenAI Responses API
    - laufende Erzeugung dieser Übergabe durch den Handover-Agenten

- **aufgetretene Probleme**
  - Kein aktueller vollständiger `pytest`-Lauf ist bestätigt.
  - Die Rollenstruktur ist uneinheitlich: `RoleAgent` lädt aus `agents/`, `role create` erzeugt unter `roles/`.
  - `build` und `release` existieren und sind registriert, sind anhand der bereitgestellten Inhalte aber nur als vorbereitete Konsolenausgaben bestätigt.

- **gelöste Probleme**
  - Der Git-Arbeitsstand ist sauber laut `changed_files: []`.
  - Der Handover-Pfad funktioniert in der aktuellen Ausführung bis zur Agentenantwortgenerierung.
  - Architektur-ADRs sind jetzt als wichtige Kontextdateien in `ContextCollector` enthalten.

## Bestätigter technischer Stand

- Projektpfad: `/Users/michaelgiese/zonvaa-builder`
- Git-Branch: `feat/decision-engine-v1`
- Git-Status: keine geänderten Dateien laut `changed_files: []`
- `builder/main.py` definiert die Typer-CLI und registriert:
  - `build`
  - `handover`
  - `doctor`
  - `init`
  - `release`
  - `role create`
- `builder/main.py` initialisiert über den Callback `get_runtime()`.
- `RuntimeManager.boot()` lädt Constitution, Knowledge-Struktur, neueste Session, Session-Inhalt und Project-State.
- `ContextCollector.collect()` sammelt Projekt-, Datei-, Git- und Session-Kontext.
- `ContextCollector` berücksichtigt relevante Architektur-ADRs, darunter:
  - `ADR-0002-knowledge-system.md`
  - `ADR-0005-decision-engine.md`
  - `ADR-0006-execution-engine.md`
  - `ADR-0007-knowledge-priority.md`
- `commands/handover.py` sammelt und analysiert Kontext, erstellt eine Handover-Aufgabe, ruft den `RoleAgent` mit Rolle `handover` auf und schreibt das Ergebnis nach `knowledge/sessions`.
- `RoleAgent` lädt Rollenprompts aus `agents/{role_name}.md` und nutzt die OpenAI Responses API.
- `constitution/constitution.md` existiert mit Version 1.0.
- `ADR-0007 – Knowledge Priority System` existiert mit Status `Beschlossen`.

## Entscheidungen

- Die Constitution Version 1.0 bleibt verbindliche Arbeitsgrundlage.
- Wissen, Entscheidungen und Arbeitsregeln werden dauerhaft im Projekt gespeichert; der Chat ist kein Langzeitspeicher.
- ADR-0002 legt das Wissenssystem fest: Quellen, dauerhaftes Projektwissen, Architekturentscheidungen, Protokolle, Übergaben und Sessions werden unterschieden.
- ADR-0005 legt fest: Eine eigenständige `DecisionEngine` bewertet den analysierten Projektkontext deterministisch; der Planner plant nur bei Freigabe.
- ADR-0006 legt fest: Eine eigenständige `ExecutionEngine` verarbeitet genehmigte Pläne und erzeugt in Version 1 kontrollierte Ausführungszustände ohne reale Änderungen.
- ADR-0007 legt die feste Wissenspriorität fest:
  1. aktueller Runtime-Zustand und bestätigte Ausführungsergebnisse
  2. Git-Status und aktuelle Commits
  3. aktuelle Testergebnisse
  4. Architekturentscheidungen
  5. persistenter ProjectState
  6. Sessions und Übergaben
  7. Zusammenfassungen und Interpretationen
- Niedrigere Wissensprioritäten dürfen höhere Prioritäten nicht überschreiben.
- Der spätere Ausbau der Prioritätslogik soll in `ContextAnalyzer` und `KnowledgeManager` erfolgen.

## Offene Punkte und Risiken

1. **Kein bestätigter vollständiger Testlauf**
   - Es existieren Testdateien für Runtime, Kontext, Decision Engine, Execution Engine, Orchestrator und Knowledge Manager.
   - Ein aktuelles `pytest`-Ergebnis ist nicht bereitgestellt.
   - Risiko: Die jüngsten Änderungen am Knowledge-Priority- und Kontextsystem sind nicht vollständig validiert.

2. **Knowledge-Priority-System noch nicht als Laufzeitlogik bestätigt**
   - ADR-0007 ist beschlossen.
   - Die Integration der Prioritätslogik in `ContextAnalyzer` und `KnowledgeManager` ist laut ADR als späterer Ausbau vorgesehen.
   - Eine tatsächliche priorisierte Konfliktauflösung im Code ist nicht bestätigt.

3. **Uneinheitliche Rollenstruktur**
   - `RoleAgent` nutzt `agents/`.
   - `role create` erzeugt Rollen unter `roles/`.
   - Risiko: unklare Quelle der Wahrheit für Rollenprompts.

4. **Build-/Release-Commands nur vorbereitet bestätigt**
   - Beide Commands sind registriert.
   - Bestätigt ist nur vorbereitete Konsolenausgabe, kein fachlicher Build- oder Release-Prozess.

5. **Schreiben dieser konkreten Übergabe noch nicht bestätigt**
   - Bestätigt ist die aktuelle Antwortgenerierung.
   - Der Schreibvorgang nach `knowledge/sessions` ist erst nach Abschluss des laufenden Commands bestätigt.

## Nächster konkreter Schritt

Den aktuellen Stand mit einem vollständigen `pytest`-Lauf validieren.

## Startanweisung für den nächsten Chat

Führe im Projektverzeichnis exakt diesen Befehl aus und berichte nur Testergebnis, Fehlerausgaben und Git-Status:

```bash
cd /Users/michaelgiese/zonvaa-builder && pytest && git status --short --untracked-files=all
```

## Technischer Anhang

- **Git-Branch**
  - `feat/decision-engine-v1`

- **Git-Status**
  - Keine geänderten Dateien laut `changed_files: []`

- **Letzte Commits**
  ```text
  110f749 Include architecture ADRs in context collection
  b5a4eea Define knowledge priority system
  a377384 Add execution engine handover session
  09d07c4 Add execution engine architecture
  40ea7bd Document decision engine architecture
  ```

- **Relevante Befehle**
  ```bash
  python3 -m builder.main handover knowledge_priority_v1
  pytest && git status --short --untracked-files=all
  git log -5 --oneline
  ```

- **Relevante Dateien**
  - `constitution/constitution.md`
  - `knowledge/adr/ADR-0002-knowledge-system.md`
  - `knowledge/adr/ADR-0005-decision-engine.md`
  - `knowledge/adr/ADR-0006-execution-engine.md`
  - `knowledge/adr/ADR-0007-knowledge-priority.md`
  - `brain/context_collector.py`
  - `brain/context_analyzer.py`
  - `knowledge/manager.py`
  - `commands/handover.py`
  - `agents/handover.md`
  - `agents/role_agent.py`
  - `agents/tasks.py`
  - `tests/test_context_collector.py`
  - `tests/test_context_analyzer.py`
  - `tests/test_knowledge_manager.py`

## Nicht bestätigt

- Ergebnis eines aktuellen vollständigen `pytest`-Laufs.
- Laufzeit-Implementierung der Wissenspriorität über die dokumentierte ADR hinaus.
- Konkrete Testabdeckung der vorhandenen Testdateien.
- Ob `roles/` oder `agents/` langfristig die verbindliche Rollenstruktur ist.
- Ob `build` und `release` über vorbereitete Konsolenausgaben hinaus fachlich ausgebaut werden sollen.
- Ob die aktuell erzeugte Übergabe-Datei nach Abschluss dieser Antwort erfolgreich nach `knowledge/sessions` geschrieben wurde.