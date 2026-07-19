# verified_runtime_facts_v1

## Kurzüberblick

Der ZONVAA Builder ist ein wissensgetriebenes Python/Typer-CLI-System zur Planung, Entwicklung, Prüfung, Dokumentation und Übergabe von Softwareprojekten. Verbindliche Grundlage ist die `constitution/constitution.md` in Version 1.0. Der aktuelle Git-Branch ist `feat/decision-engine-v1`; laut bereitgestelltem Git-Status gibt es keine geänderten Dateien. Seit der letzten Session wurden laut Git-Historie bestätigte Laufzeitfakten eingeführt, in Runtime und ProjectState verfügbar gemacht und in der Kontextsammlung priorisiert. Die aktuelle Ausführung `python3 -m builder.main handover verified_runtime_facts_v1` bestätigt den Handover-Pfad bis zur laufenden Agentenantwort. Bestätigt sind Start von `builder.main`, erfolgreicher Handover-Command, Kontextsammlung, Task-Erstellung, Laden des Handover-Agenten, Nutzung der OpenAI-Konfiguration und Annahme der Anfrage durch die OpenAI Responses API. Ein aktueller vollständiger `pytest`-Lauf ist weiterhin nicht bestätigt. Nächster Schritt ist die technische Validierung des aktuellen Stands durch einen vollständigen Testlauf.

## Letzte Session

- **heute umgesetzt**
  - Laut jüngsten Commits:
    - Verified-Runtime-Facts-Store wurde ergänzt.
    - Verified Facts wurden in den ProjectState geladen.
    - Verified Facts wurden in der Runtime verfügbar gemacht.
    - Bestätigte Fakten wurden in der Kontextsammlung priorisiert.
    - Eine Knowledge-Priority-Handover-Session wurde hinzugefügt.
  - In der aktuellen Ausführung wurde `python3 -m builder.main handover verified_runtime_facts_v1` gestartet.
  - `ContextCollector.collect()` wurde erfolgreich ausgeführt.
  - `build_handover_task()` wurde erfolgreich ausgeführt.
  - `agents/handover.md` wurde durch `RoleAgent` erfolgreich geladen.
  - `OPENAI_API_KEY` und `OPENAI_MODEL` konnten verwendet werden.
  - Die OpenAI Responses API hat die Anfrage angenommen.
  - Der Handover-Agent erzeugt aktuell diese Übergabe.

- **getestete Funktionen**
  - Durch die aktuelle Ausführung bestätigt:
    - `builder.main` konnte gestartet werden.
    - Der `handover`-Command wurde erfolgreich aufgerufen.
    - `ContextCollector.collect()` wurde erfolgreich ausgeführt.
    - `build_handover_task()` wurde erfolgreich ausgeführt.
    - `agents/handover.md` wurde durch `RoleAgent` erfolgreich geladen.
    - `OPENAI_API_KEY` und `OPENAI_MODEL` konnten verwendet werden.
    - Die OpenAI Responses API hat die Anfrage angenommen.
    - Der Handover-Agent erzeugt aktuell diese Übergabe.

- **aufgetretene Probleme**
  - Kein aktueller vollständiger `pytest`-Lauf ist bestätigt.
  - Die Rollenstruktur ist uneinheitlich: `RoleAgent` lädt Rollen aus `agents/`, `role create` erzeugt Rollen unter `roles/`.
  - `build` und `release` existieren; ihr fachlicher Ausbau ist nicht bestätigt.

- **gelöste Probleme**
  - Der Git-Arbeitsstand ist laut `changed_files: []` sauber.
  - Der Handover-Pfad funktioniert in der aktuellen Ausführung bis zur Agentenantwortgenerierung.
  - Aktuelle bestätigte Laufzeitfakten werden in der Aufgabe an den Handover-Agenten explizit übergeben und dürfen nicht als unbestätigt behandelt werden.

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
- `RuntimeManager.boot()` lädt Constitution, Knowledge-Struktur, neueste Session, Session-Inhalt, ProjectState und `verified_facts`.
- `KnowledgeManager.load()` lädt Wissensbereiche und bindet `verified_facts` ein.
- `ContextCollector.collect()` sammelt Projekt-, Datei-, Git-, Session-, ProjectState- und Runtime-Kontext.
- `ContextCollector` berücksichtigt wichtige Architektur-ADRs, darunter:
  - `ADR-0002-knowledge-system.md`
  - `ADR-0005-decision-engine.md`
  - `ADR-0006-execution-engine.md`
  - `ADR-0007-knowledge-priority.md`
- `commands/handover.py` sammelt und analysiert Kontext, erstellt eine Handover-Aufgabe, ruft den `RoleAgent` mit Rolle `handover` auf und schreibt das Ergebnis nach `knowledge/sessions`.
- `RoleAgent` lädt Rollenprompts aus `agents/{role_name}.md` und nutzt die OpenAI Responses API.
- `constitution/constitution.md` existiert mit Version 1.0.
- ADR-0002, ADR-0005, ADR-0006 und ADR-0007 existieren mit beschlossenem Status bzw. verbindlicher Entscheidung.

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

## Offene Punkte und Risiken

1. **Kein bestätigter vollständiger Testlauf**
   - Es existieren Testdateien für Runtime, Kontext, Decision Engine, Execution Engine, Orchestrator und Knowledge Manager.
   - Ein aktuelles `pytest`-Ergebnis ist nicht bereitgestellt.
   - Risiko: Die jüngsten Änderungen an Verified Facts, Runtime, ProjectState und Kontextsammlung sind nicht vollständig validiert.

2. **Knowledge-Priority-System nur teilweise als Laufzeitverhalten bestätigt**
   - ADR-0007 ist beschlossen.
   - Aktuelle bestätigte Laufzeitfakten werden in dieser Handover-Ausführung berücksichtigt.
   - Eine vollständige priorisierte Konfliktauflösung über alle Wissensquellen ist nicht bestätigt.

3. **Uneinheitliche Rollenstruktur**
   - `RoleAgent` nutzt `agents/`.
   - `role create` erzeugt Rollen unter `roles/`.
   - Risiko: unklare Quelle der Wahrheit für Rollenprompts.

4. **Build-/Release-Commands nur vorbereitet bestätigt**
   - Beide Commands sind registriert.
   - Bestätigt sind anhand der Dateien nur vorbereitete Konsolenausgaben, kein fachlicher Build- oder Release-Prozess.

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
  c04753b Add knowledge priority handover session
  f0b9588 Prioritize verified facts in context collection
  244c9de Expose verified facts in runtime
  c670a67 Load verified facts into project state
  42c1962 Add verified runtime facts store
  ```

- **Relevante Befehle**
  ```bash
  python3 -m builder.main handover verified_runtime_facts_v1
  pytest && git status --short --untracked-files=all
  git log -5 --oneline
  ```

- **Relevante Dateien**
  - `constitution/constitution.md`
  - `knowledge/adr/ADR-0002-knowledge-system.md`
  - `knowledge/adr/ADR-0005-decision-engine.md`
  - `knowledge/adr/ADR-0006-execution-engine.md`
  - `knowledge/adr/ADR-0007-knowledge-priority.md`
  - `builder/main.py`
  - `builder/runtime.py`
  - `builder/project_state.py`
  - `knowledge/manager.py`
  - `brain/context_collector.py`
  - `brain/context_analyzer.py`
  - `commands/handover.py`
  - `agents/handover.md`
  - `agents/role_agent.py`
  - `agents/tasks.py`

## Nicht bestätigt

- Ergebnis eines aktuellen vollständigen `pytest`-Laufs.
- Vollständige priorisierte Konfliktauflösung über alle Wissensquellen hinweg.
- Konkrete Testabdeckung der vorhandenen Testdateien.
- Ob `roles/` oder `agents/` langfristig die verbindliche Rollenstruktur ist.
- Ob `build` und `release` über vorbereitete Konsolenausgaben hinaus fachlich ausgebaut werden sollen.
- Ob die aktuell erzeugte Übergabe-Datei nach Abschluss dieser Antwort erfolgreich nach `knowledge/sessions` geschrieben wurde.