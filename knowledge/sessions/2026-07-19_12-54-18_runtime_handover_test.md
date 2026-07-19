# runtime_handover_test

## Kurzüberblick

Der ZONVAA Builder ist ein wissensgetriebenes Python/Typer-CLI-System zur Planung, Entwicklung, Prüfung, Dokumentation und Übergabe von Softwareprojekten. Verbindliche Grundlage ist die `constitution/constitution.md` in Version 1.0. In der aktuellen Ausführung wurde `python3 -m builder.main handover runtime_handover_test` gestartet. Der Handover-Command läuft bis zur aktuellen Agentenantwort erfolgreich. Die Runtime-, Session- und Kontextpipeline ist nach aktueller Ausführung funktionsfähig bis zur Übergabe-Erzeugung durch den Handover-Agenten. Der Git-Branch ist `main`. Der Arbeitsstand ist nicht sauber: `requirements.txt` ist geändert, zwei Session-Dateien sind untracked. Ein vollständiger aktueller `pytest`-Lauf ist nicht bestätigt.

## Letzte Session

- **heute umgesetzt**
  - Der Handover-Lauf `python3 -m builder.main handover runtime_handover_test` wurde gestartet.
  - `builder.main`, der `handover`-Command, `ContextCollector.collect()` und `build_handover_task()` wurden erfolgreich ausgeführt.
  - `agents/handover.md` wurde durch `RoleAgent` erfolgreich geladen.
  - `OPENAI_API_KEY` und `OPENAI_MODEL` konnten verwendet werden.
  - Die OpenAI Responses API hat die Anfrage angenommen.
  - Laut Git-Historie wurden zuletzt Runtime- und Kontextpipeline-Änderungen umgesetzt, insbesondere:
    - `Pass latest session through context pipeline`
    - `Use runtime session in context collector`
    - `Use shared runtime during startup`
    - `Add shared runtime provider`
    - `Add latest session content to runtime`

- **getestete Funktionen**
  - Bestätigt durch die aktuelle Ausführung:
    - Start von `builder.main`
    - Aufruf des `handover`-Commands
    - Ausführung von `ContextCollector.collect()`
    - Ausführung von `build_handover_task()`
    - Laden von `agents/handover.md` durch `RoleAgent`
    - Nutzung von `OPENAI_API_KEY` und `OPENAI_MODEL`
    - Annahme der Anfrage durch die OpenAI Responses API
    - aktuelle Erzeugung dieser Übergabe durch den Handover-Agenten

- **aufgetretene Probleme**
  - Der Arbeitsstand ist nicht vollständig versioniert.
  - `requirements.txt` ist geändert.
  - Zwei Session-Dateien sind untracked.
  - Ein vollständiger aktueller `pytest`-Lauf ist nicht bestätigt.
  - Die Rollenstruktur ist uneinheitlich: `RoleAgent` lädt aus `agents/`, `role create` erzeugt unter `roles/`.

- **gelöste Probleme**
  - Die gemeinsame Runtime wird beim CLI-Start über `get_runtime()` initialisiert.
  - Der Context Collector nutzt die gemeinsame Runtime.
  - Die neueste Session wird über die Runtime in den Kontextpfad übernommen.
  - Der Handover-Pfad funktioniert bis zur aktuellen OpenAI-Antwortgenerierung.

## Bestätigter technischer Stand

- Projektpfad: `/Users/michaelgiese/zonvaa-builder`
- Git-Branch: `main`
- Die CLI wird über `builder/main.py` mit Typer definiert.
- `builder/main.py` registriert:
  - `build`
  - `handover`
  - `doctor`
  - `init`
  - `release`
  - `role create`
- `builder/main.py` ruft im Callback `get_runtime()` auf.
- `builder/runtime.py` stellt eine einmalig initialisierte gemeinsame Runtime über `get_runtime()` bereit.
- `RuntimeManager.boot()` lädt:
  - Constitution über `ConstitutionManager().load()`
  - Knowledge-Struktur über `KnowledgeManager().load()`
  - neueste Session über `KnowledgeManager.latest_session()`
  - Inhalt der neuesten Session, falls vorhanden
- `ContextCollector.collect()` nutzt `get_runtime()` und übernimmt Session-Inhalte aus der Runtime.
- `commands/handover.py` sammelt Projektkontext, analysiert ihn, erstellt eine Handover-Aufgabe, ruft `RoleAgent` mit Rolle `handover` auf und schreibt das Ergebnis nach `knowledge/sessions`.
- `RoleAgent` lädt Rollenprompts aus `agents/{role_name}.md` und nutzt die OpenAI Responses API.
- `constitution/constitution.md` existiert mit Version 1.0.
- `knowledge/adr/ADR-0002-knowledge-system.md` existiert mit Status `beschlossen`.

## Entscheidungen

- Die Constitution Version 1.0 ist verbindliche Arbeitsgrundlage.
- Wissen, Entscheidungen und Arbeitsregeln werden dauerhaft im Projekt gespeichert; der Chat ist kein Langzeitspeicher.
- Vor wissensabhängigen Workflows muss die Builder-Runtime Constitution, Protokolle, Architekturentscheidungen, relevante Übergaben und Projektkontext laden.
- Fehlt die Constitution oder kann sie nicht gelesen werden, darf kein wissensabhängiger Workflow ausgeführt werden.
- ADR-0002 legt fest, dass der Builder wissensbasiert arbeitet und zwischen Quellen, dauerhaftem Projektwissen, Architekturentscheidungen, Protokollen, Übergaben und kurzfristigen Sessions unterscheidet.
- Quellen unter `knowledge/sources/` werden nicht ungeprüft als verbindliche Wahrheit übernommen.
- Die aktuelle technische Richtung nutzt eine gemeinsame Runtime beim Start und stellt Session-Kontext daraus bereit.

## Offene Punkte und Risiken

1. **Arbeitsstand nicht vollständig versioniert**
   - `requirements.txt` ist geändert.
   - Zwei Session-Dateien sind untracked.
   - Risiko: Der aktuelle Projektstand ist nicht reproduzierbar versioniert.

2. **Kein bestätigter vollständiger Testlauf**
   - `tests/test_builder.py` existiert.
   - Ein aktuelles `pytest`-Ergebnis ist nicht bereitgestellt.
   - Risiko: Die aktuelle Laufzeit bestätigt den Handover-Pfad, aber nicht die gesamte Testbasis.

3. **Uneinheitliche Rollenstruktur**
   - `RoleAgent` lädt Rollen aus `agents/`.
   - `role create` erzeugt Rollen unter `roles/`.
   - Risiko: Unklare Quelle der Wahrheit für Rollenprompts.

4. **Build-/Release-Commands fachlich nicht ausgebaut bestätigt**
   - `build` und `release` sind registriert.
   - Bestätigt ist anhand der Dateien nur vorbereitete Konsolenausgabe, kein produktiver Build- oder Release-Prozess.

5. **Schreiben dieser konkreten Übergabe noch nicht bestätigt**
   - Bestätigt ist die aktuelle Antwortgenerierung.
   - Nicht bestätigt ist der nachgelagerte Schreibvorgang dieser konkreten Datei nach `knowledge/sessions`.

## Nächster konkreter Schritt

Einen vollständigen Testlauf mit `pytest` ausführen und danach den Git-Status prüfen.

## Startanweisung für den nächsten Chat

Führe im Projektverzeichnis `/Users/michaelgiese/zonvaa-builder` genau diesen Befehl aus und berichte nur Testergebnis, Fehlerausgaben und Git-Status:

```bash
pytest && git status --short --untracked-files=all
```

## Technischer Anhang

- **Git-Branch**
  - `main`

- **Git-Status**
  ```text
  M requirements.txt
  ?? knowledge/sessions/2026-07-19_12-28-02_runtime_integration_test.md
  ?? knowledge/sessions/2026-07-19_12-36-36_runtime_integration_test.md
  ```

- **Letzte Commits**
  ```text
  ebdde60 Pass latest session through context pipeline
  9082b4a Use runtime session in context collector
  e2889eb Use shared runtime during startup
  2751660 Add shared runtime provider
  a6aa955 Add latest session content to runtime
  ```

- **Relevante Befehle**
  ```bash
  python3 -m builder.main handover runtime_handover_test
  pytest && git status --short --untracked-files=all
  git log -5 --oneline
  ```

- **Relevante Dateien**
  - `builder/main.py`
  - `builder/runtime.py`
  - `commands/handover.py`
  - `agents/handover.md`
  - `agents/role_agent.py`
  - `agents/tasks.py`
  - `brain/context_collector.py`
  - `brain/context_analyzer.py`
  - `constitution/constitution.md`
  - `constitution/manager.py`
  - `knowledge/manager.py`
  - `knowledge/adr/ADR-0002-knowledge-system.md`
  - `tests/test_builder.py`
  - `requirements.txt`
  - `knowledge/sessions/2026-07-19_12-36-36_runtime_integration_test.md`

## Nicht bestätigt

- Ergebnis eines vollständigen aktuellen `pytest`-Testlaufs.
- Inhalt und Testabdeckung von `tests/test_builder.py`.
- Inhalt der Änderung an `requirements.txt`.
- Ob `roles/` oder `agents/` langfristig die verbindliche Rollenstruktur ist.
- Ob `build` und `release` über vorbereitende Konsolenausgaben hinaus fachlich ausgebaut werden sollen.
- Ob die aktuell erzeugte Übergabe-Datei nach Abschluss dieser Antwort erfolgreich nach `knowledge/sessions` geschrieben wurde.