# runtime_context_test

## Kurzüberblick

Der ZONVAA Builder ist ein wissensgetriebenes Python/Typer-CLI-System zur Planung, Entwicklung, Prüfung, Dokumentation und Übergabe von Softwareprojekten. Verbindliche Arbeitsgrundlage ist die `constitution/constitution.md` in Version 1.0. Der aktuelle Lauf wurde mit `python3 -m builder.main handover runtime_context_test` gestartet. Dabei wurden `builder.main`, der `handover`-Command, `ContextCollector.collect()`, `build_handover_task()` und der Handover-Agent erfolgreich bis zur aktuellen Antwortgenerierung ausgeführt. `agents/handover.md` wurde durch `RoleAgent` geladen. `OPENAI_API_KEY` und `OPENAI_MODEL` konnten verwendet werden, und die OpenAI Responses API hat die Anfrage angenommen. Der aktuelle Git-Arbeitsstand ist dirty: 17 Dateien sind geändert oder untracked. Relevante Risiken sind der nicht versionierte Arbeitsstand, parallele Rollenstrukturen unter `roles/` und `agents/`, sowie ungeklärte Build-/Release-Strukturen.

## Letzte Session

- **heute umgesetzt**
  - Der aktuelle Handover-Lauf wurde mit `python3 -m builder.main handover runtime_context_test` gestartet.
  - `builder.main` konnte gestartet werden.
  - Der `handover`-Command wurde erfolgreich aufgerufen.
  - `ContextCollector.collect()` wurde erfolgreich ausgeführt.
  - `build_handover_task()` wurde erfolgreich ausgeführt.
  - `agents/handover.md` wurde durch `RoleAgent` erfolgreich geladen.
  - `OPENAI_API_KEY` und `OPENAI_MODEL` konnten verwendet werden.
  - Die OpenAI Responses API hat die Anfrage angenommen.
  - Der Handover-Agent erzeugt aktuell diese Übergabe.

- **getestete Funktionen**
  - Bestätigt durch aktuelle Ausführung:
    - CLI-Start über `builder.main`
    - Aufruf des `handover`-Commands
    - Kontextsammlung über `ContextCollector.collect()`
    - Task-Erstellung über `build_handover_task()`
    - Laden der Rolle `handover` aus `agents/handover.md`
    - Nutzung von `OPENAI_API_KEY` und `OPENAI_MODEL`
    - Annahme der Anfrage durch die OpenAI Responses API
  - Ein separater Testlauf wie `pytest` ist nicht bestätigt.

- **aufgetretene Probleme**
  - Der Git-Arbeitsstand ist nicht sauber.
  - `brain/context_analyzer.py`, `brain/context_collector.py` und `builder/main.py` sind geändert.
  - Mehrere zentrale Dateien sind untracked, darunter `builder/runtime.py`, `commands/build.py`, `commands/release.py`, `knowledge/manager.py` und `knowledge/adr/ADR-0002-knowledge-system.md`.
  - Rollen liegen parallel unter `roles/` und `agents/`.
  - `commands/build.py` und `commands/release.py` existieren, sind aber laut `builder/main.py` nicht als CLI-Commands registriert.
  - `commands/release.py` ist in den bereitgestellten Dateiinhalten leer.

- **gelöste Probleme**
  - Keine konkret dokumentierten gelösten Probleme in den bereitgestellten Daten.
  - Bestätigt ist, dass der aktuelle Handover-Workflow bis zur Agentenantwort läuft.

## Bestätigter technischer Stand

- Projektpfad: `/Users/michaelgiese/zonvaa-builder`
- Git-Branch: `main`
- Die CLI wird über `builder/main.py` mit Typer definiert.
- `builder/main.py` importiert `RuntimeManager` aus `builder/runtime.py` und ruft im CLI-Callback `RuntimeManager().boot()` auf.
- Registrierte Commands in `builder/main.py`:
  - `handover`
  - `doctor`
  - `init`
  - `role create`
- `RuntimeManager.boot()` lädt laut bereitgestelltem Code:
  - Constitution über `ConstitutionManager().load()`
  - Knowledge-Struktur über `KnowledgeManager().load()`
- `ConstitutionManager` lädt `constitution/constitution.md` und bricht bei fehlender Datei mit `FileNotFoundError` ab.
- `KnowledgeManager` sammelt Pfade aus:
  - `knowledge/adr`
  - `knowledge/protocols`
  - `knowledge/handovers`
  - `knowledge/project`
  - `knowledge/sessions`
  - `knowledge/sources`
- `commands/handover.py` sammelt Projektkontext, analysiert ihn, erstellt eine Handover-Aufgabe, ruft `RoleAgent` mit Rolle `handover` auf und schreibt das Ergebnis nach `knowledge/sessions`.
- `RoleAgent` lädt Rollenprompts aus `agents/{role_name}.md` und nutzt die OpenAI Responses API mit `OPENAI_MODEL`.
- `ContextCollector` sammelt Dateien, wichtige Dateiinhalte, Session-Dateien, Git-Branch, Git-Status und letzte Commits.
- `ContextAnalyzer` verdichtet Projektkontext, geänderte Dateien, relevante Dateien, Summary-Zahlen und Risiken.
- `commands/build.py` enthält einen vorbereiteten Build-Command mit Hinweis-Ausgabe.
- `commands/release.py` ist leer.
- Die Constitution existiert und ist verbindlich mit Version 1.0.
- `knowledge/adr/ADR-0002-knowledge-system.md` existiert im Arbeitsstand mit Status `beschlossen`, ist aber untracked.

## Entscheidungen

- Die Constitution Version 1.0 ist verbindliche Arbeitsgrundlage.
- Wissen, Entscheidungen und Arbeitsregeln werden dauerhaft im Projekt gespeichert; der Chat ist kein Langzeitspeicher.
- Vor wissensabhängigen Workflows muss die Builder-Runtime laut Constitution Constitution, Protokolle, Architekturentscheidungen, relevante Übergaben und Projektkontext laden.
- Fehlt die Constitution oder kann sie nicht gelesen werden, darf kein wissensabhängiger Workflow ausgeführt werden.
- ADR-0002 legt fest, dass der Builder wissensbasiert arbeitet und zwischen Quellen, dauerhaftem Projektwissen, Architekturentscheidungen, Protokollen, Übergaben und kurzfristigen Sessions unterscheidet.
- Quellen unter `knowledge/sources/` werden laut ADR-0002 nicht ungeprüft als verbindliche Wahrheit übernommen.
- Agentenrollen werden aktuell durch `RoleAgent` aus `agents/` geladen.
- Rollenverwaltung erzeugt neue Rollen aktuell unter `roles/`.

## Offene Punkte und Risiken

1. **Arbeitsstand nicht versioniert**
   - 17 Dateien sind geändert oder untracked.
   - Risiko: Der aktuelle funktionierende Stand ist nicht sauber nachvollziehbar oder gesichert.

2. **Zentrale Runtime-/Knowledge-Dateien sind untracked**
   - Betroffen sind unter anderem `builder/runtime.py`, `knowledge/manager.py` und `knowledge/adr/ADR-0002-knowledge-system.md`.
   - Risiko: Die aktuell genutzte Runtime- und Wissensstruktur ist noch nicht dauerhaft versioniert.

3. **Geänderte Kontextlogik**
   - `brain/context_analyzer.py` und `brain/context_collector.py` sind geändert.
   - Risiko: Auswirkungen auf Kontextsammlung, Risikoerkennung und Übergabequalität müssen vor Commit geprüft werden.

4. **Doppelte Rollenstruktur**
   - Rollen liegen gleichzeitig unter `roles/` und `agents/`.
   - Risiko: Unklare Quelle der Wahrheit für Rollenprompts.

5. **Build-/Release-Commands inkonsistent**
   - `commands/build.py` existiert, ist aber nicht registriert.
   - `commands/release.py` existiert, ist leer und nicht registriert.

6. **Kein bestätigter vollständiger Testlauf**
   - `tests/test_builder.py` existiert, aber ein aktuelles Testergebnis ist nicht bereitgestellt.

7. **Aktuelle Übergabe-Datei noch nicht bestätigt geschrieben**
   - Bestätigt ist die aktuelle Antwortgenerierung, nicht das anschließende Schreiben der Datei nach `knowledge/sessions`.

## Nächster konkreter Schritt

Den unversionierten Arbeitsstand der zentralen Runtime-, Knowledge-, Command- und Kontextdateien prüfen und dokumentieren.

## Startanweisung für den nächsten Chat

Führe im Projektverzeichnis `/Users/michaelgiese/zonvaa-builder` genau diese Prüfung aus und berichte danach nur Git-Status, relevante Inhalte und erkennbare Risiken:

```bash
git status --short --untracked-files=all && printf '\n--- builder/runtime.py ---\n' && sed -n '1,220p' builder/runtime.py && printf '\n--- knowledge/manager.py ---\n' && sed -n '1,220p' knowledge/manager.py && printf '\n--- knowledge/adr/ADR-0002-knowledge-system.md ---\n' && sed -n '1,220p' knowledge/adr/ADR-0002-knowledge-system.md && printf '\n--- commands/release.py ---\n' && sed -n '1,220p' commands/release.py && printf '\n--- brain/context_collector.py diff ---\n' && git diff -- brain/context_collector.py && printf '\n--- brain/context_analyzer.py diff ---\n' && git diff -- brain/context_analyzer.py
```

## Technischer Anhang

- **Git-Branch**
  - `main`

- **Git-Status**
  - `M brain/context_analyzer.py`
  - `M brain/context_collector.py`
  - `M builder/main.py`
  - `?? agents/architect.md`
  - `?? builder/runtime.py`
  - `?? commands/build.py`
  - `?? commands/release.py`
  - `?? knowledge/adr/ADR-0002-knowledge-system.md`
  - `?? knowledge/manager.py`
  - `?? knowledge/sessions/2026-07-17_14-12-39_runtime_v1.md`
  - `?? knowledge/sessions/2026-07-19_08-54-27_why_and_knowledge_v1.md`
  - `?? knowledge/sessions/2026-07-19_09-15-06_knowledge_activation_test.md`
  - `?? knowledge/sessions/2026-07-19_09-28-09_runtime_state_test.md`
  - `?? mein-projekt/.env.example`
  - `?? mein-projekt/.gitignore`
  - `?? mein-projekt/README.md`
  - `?? roles/architect.md`

- **Letzte Commits**
  ```text
  9b8d589 Add WHY defining Zonvaa's mission
  d80efbc Load Constitution and session knowledge
  b845b71 Add Constitution runtime
  d7002d1 Implement modular CLI and AI handover workflow
  5181936 Create vision
  ```

- **Relevante Befehle**
  ```bash
  python3 -m builder.main handover runtime_context_test
  git status --short --untracked-files=all
  git log -5 --oneline
  ```

- **Relevante Dateien**
  - `builder/main.py`
  - `builder/runtime.py`
  - `commands/handover.py`
  - `commands/build.py`
  - `commands/release.py`
  - `agents/handover.md`
  - `agents/role_agent.py`
  - `agents/tasks.py`
  - `brain/context_collector.py`
  - `brain/context_analyzer.py`
  - `constitution/constitution.md`
  - `knowledge/manager.py`
  - `knowledge/adr/ADR-0002-knowledge-system.md`

## Nicht bestätigt

- Grund und Auswirkung der Änderungen an `brain/context_collector.py`, `brain/context_analyzer.py` und `builder/main.py`.
- Ob `commands/build.py` und `commands/release.py` künftig registriert werden sollen.
- Ob `roles/` oder `agents/` langfristig die verbindliche Rollenstruktur ist.
- Ergebnis eines vollständigen Testlaufs.
- Inhalt von `tests/test_builder.py`.
- Ob der aktuelle dirty Arbeitsstand vollständig beabsichtigt ist.
- Ob die aktuell erzeugte Übergabe-Datei nach Abschluss dieser Antwort erfolgreich geschrieben wurde.