# runtime_integration_test

## Kurzüberblick

Der ZONVAA Builder ist ein wissensgetriebenes Python/Typer-CLI-System zur Planung, Entwicklung, Prüfung, Dokumentation und Übergabe von Softwareprojekten. Verbindliche Grundlage ist die `constitution/constitution.md` in Version 1.0. Der aktuelle Lauf wurde mit `python3 -m builder.main handover runtime_integration_test` gestartet. Dabei wurden `builder.main`, der `handover`-Command, `ContextCollector.collect()` und `build_handover_task()` erfolgreich ausgeführt. `agents/handover.md` wurde durch `RoleAgent` erfolgreich geladen. `OPENAI_API_KEY` und `OPENAI_MODEL` konnten verwendet werden; die OpenAI Responses API hat die Anfrage angenommen. Der Handover-Agent erzeugt aktuell diese Übergabe. Der Git-Branch ist `main`. Der aktuelle Git-Status enthält eine unversionierte Session-Datei: `knowledge/sessions/2026-07-19_12-28-02_runtime_integration_test.md`. Ein vollständiger aktueller `pytest`-Lauf ist nicht bestätigt.

## Letzte Session

- **heute umgesetzt**
  - Der Handover-Lauf `python3 -m builder.main handover runtime_integration_test` wurde gestartet.
  - Der Handover-Workflow läuft bis zur aktuellen Agentenantwort erfolgreich.
  - Die zuletzt vorhandene Session-Datei `knowledge/sessions/2026-07-19_12-28-02_runtime_integration_test.md` wurde durch die Runtime als aktuelle Session geladen und dem Kontext bereitgestellt.
  - Laut Git-Historie wurden zuletzt Runtime- und Session-Integrationen umgesetzt:
    - `Use runtime session in context collector`
    - `Use shared runtime during startup`
    - `Add shared runtime provider`
    - `Add latest session content to runtime`
    - `Add latest session lookup to knowledge manager`

- **getestete Funktionen**
  - Bestätigt durch die aktuelle Ausführung:
    - `builder.main` konnte gestartet werden.
    - Der `handover`-Command wurde erfolgreich aufgerufen.
    - `ContextCollector.collect()` wurde erfolgreich ausgeführt.
    - `build_handover_task()` wurde erfolgreich ausgeführt.
    - `agents/handover.md` wurde durch `RoleAgent` erfolgreich geladen.
    - `OPENAI_API_KEY` und `OPENAI_MODEL` konnten verwendet werden.
    - Die OpenAI Responses API hat die Anfrage angenommen.
    - Der Handover-Agent erzeugt aktuell diese Übergabe.

- **aufgetretene Probleme**
  - Der Arbeitsstand ist nicht vollständig versioniert: `knowledge/sessions/2026-07-19_12-28-02_runtime_integration_test.md` ist untracked.
  - Ein vollständiger aktueller `pytest`-Lauf ist nicht bestätigt.
  - Die Rollenstruktur ist uneinheitlich: `RoleAgent` lädt aus `agents/`, `role create` erzeugt unter `roles/`.
  - Die Risikoerkennung meldet Prüfbedarf bei Build- und Release-Commands.

- **gelöste Probleme**
  - Die gemeinsame Runtime wird beim CLI-Start über `get_runtime()` initialisiert.
  - Der Context Collector nutzt die gemeinsame Runtime und erhält die aktuelle Session aus ihr.
  - Der Handover-Pfad funktioniert bis zur aktuellen OpenAI-Antwortgenerierung.

## Bestätigter technischer Stand

- Projektpfad: `/Users/michaelgiese/zonvaa-builder`
- Git-Branch: `main`
- Git-Status: eine unversionierte Datei unter `knowledge/sessions/`.
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
  - die Constitution über `ConstitutionManager().load()`
  - die Knowledge-Struktur über `KnowledgeManager().load()`
  - die neueste Session über `KnowledgeManager.latest_session()`
  - den Inhalt der neuesten Session, falls vorhanden
- `ContextCollector.collect()` nutzt `get_runtime()` und übernimmt die neueste Session aus der Runtime.
- `commands/handover.py` sammelt Projektkontext, analysiert ihn, erstellt eine Handover-Aufgabe, ruft `RoleAgent` mit Rolle `handover` auf und schreibt das Ergebnis nach `knowledge/sessions`.
- `RoleAgent` lädt Rollenprompts aus `agents/{role_name}.md` und nutzt die OpenAI Responses API.
- `constitution/constitution.md` existiert mit Version 1.0 und ist verbindlich.
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
   - `knowledge/sessions/2026-07-19_12-28-02_runtime_integration_test.md` ist untracked.
   - Risiko: Die letzte Session-Übergabe ist noch nicht Bestandteil des versionierten Projektstands.

2. **Kein bestätigter vollständiger Testlauf**
   - `tests/test_builder.py` existiert.
   - Ein aktuelles `pytest`-Ergebnis ist nicht bereitgestellt.
   - Risiko: Die aktuelle Laufzeit bestätigt den Handover-Pfad, aber nicht die gesamte Testbasis.

3. **Uneinheitliche Rollenstruktur**
   - `RoleAgent` lädt Rollen aus `agents/`.
   - `role create` erzeugt Rollen unter `roles/`.
   - Risiko: Unklare Quelle der Wahrheit für Rollenprompts.

4. **Build-/Release-Commands nur begrenzt bestätigt**
   - `build` und `release` sind in `builder/main.py` registriert.
   - Bestätigt ist anhand der Dateien nur vorbereitete Konsolenausgabe, nicht ein produktiver Build- oder Release-Prozess.

5. **Aktuelle Übergabe-Datei noch nicht bestätigt geschrieben**
   - Bestätigt ist die aktuelle Antwortgenerierung.
   - Nicht bestätigt ist das anschließende Schreiben dieser konkret erzeugten Übergabe nach `knowledge/sessions`.

## Nächster konkreter Schritt

Einen vollständigen Testlauf mit `pytest` ausführen und anschließend den Git-Status prüfen.

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
  ?? knowledge/sessions/2026-07-19_12-28-02_runtime_integration_test.md
  ```

- **Letzte Commits**
  ```text
  9082b4a Use runtime session in context collector
  e2889eb Use shared runtime during startup
  2751660 Add shared runtime provider
  a6aa955 Add latest session content to runtime
  f93c951 Add latest session lookup to knowledge manager
  ```

- **Relevante Befehle**
  ```bash
  python3 -m builder.main handover runtime_integration_test
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
  - `knowledge/sessions/2026-07-19_12-28-02_runtime_integration_test.md`
  - `tests/test_builder.py`

## Nicht bestätigt

- Ergebnis eines vollständigen aktuellen `pytest`-Testlaufs.
- Inhalt und Testabdeckung von `tests/test_builder.py`.
- Ob `roles/` oder `agents/` langfristig die verbindliche Rollenstruktur ist.
- Ob `build` und `release` über vorbereitende Konsolenausgaben hinaus fachlich ausgebaut werden sollen.
- Ob die aktuell erzeugte Übergabe-Datei nach Abschluss dieser Antwort erfolgreich nach `knowledge/sessions` geschrieben wurde.