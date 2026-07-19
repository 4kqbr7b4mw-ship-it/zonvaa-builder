# runtime_knowledge_system_v1

## Kurzüberblick

Der ZONVAA Builder ist ein wissensgetriebenes Python/Typer-CLI-System zur Planung, Entwicklung, Prüfung, Dokumentation und Übergabe von Softwareprojekten. Verbindliche Arbeitsgrundlage ist die `constitution/constitution.md` in Version 1.0. Der aktuelle Lauf wurde mit `python3 -m builder.main handover runtime_knowledge_system_v1` gestartet. In dieser Ausführung wurden `builder.main`, der `handover`-Command, `ContextCollector.collect()`, `build_handover_task()` und der Handover-Agent erfolgreich bis zur aktuellen Übergabe-Erzeugung ausgeführt. `agents/handover.md` wurde durch `RoleAgent` geladen. `OPENAI_API_KEY` und `OPENAI_MODEL` konnten verwendet werden, und die OpenAI Responses API hat die Anfrage angenommen. Der aktuelle Git-Branch ist `main`. Der aktuelle Git-Status zeigt nur zwei untracked Runtime-Protokolldateien. Der letzte Commit lautet `dae23ea Add runtime knowledge system`.

## Letzte Session

- **heute umgesetzt**
  - Der aktuelle Handover-Lauf wurde mit `python3 -m builder.main handover runtime_knowledge_system_v1` gestartet.
  - Der Handover-Workflow wurde bis zur aktuellen Agentenantwort erfolgreich ausgeführt.
  - Laut letztem Commit wurde ein Runtime-Knowledge-System hinzugefügt: `dae23ea Add runtime knowledge system`.

- **getestete Funktionen**
  - Bestätigt durch die aktuelle Ausführung:
    - Start von `builder.main`
    - erfolgreicher Aufruf des `handover`-Commands
    - erfolgreiche Ausführung von `ContextCollector.collect()`
    - erfolgreiche Ausführung von `build_handover_task()`
    - erfolgreiches Laden von `agents/handover.md` durch `RoleAgent`
    - Verwendung von `OPENAI_API_KEY` und `OPENAI_MODEL`
    - Annahme der Anfrage durch die OpenAI Responses API
    - laufende Erzeugung dieser Übergabe durch den Handover-Agenten

- **aufgetretene Probleme**
  - Der Git-Arbeitsstand ist nicht vollständig sauber: Zwei Dateien unter `knowledge/protocols/` sind untracked.
  - Rollen liegen weiterhin gleichzeitig unter `roles/` und `agents/`.
  - `commands/build.py` existiert, ist aber laut `builder/main.py` nicht als CLI-Command registriert.
  - `commands/release.py` existiert, ist aber leer und ebenfalls nicht registriert.
  - Ein aktueller vollständiger Testlauf, z. B. `pytest`, ist nicht bestätigt.

- **gelöste Probleme**
  - Der aktuelle Handover-Workflow läuft nachweislich bis zur Agentenantwort.
  - Der zuvor unversionierte Runtime-Knowledge-Stand scheint mindestens teilweise versioniert zu sein, da der letzte Commit `Add runtime knowledge system` lautet und der aktuelle Git-Status nur zwei untracked Protokolldateien zeigt.

## Bestätigter technischer Stand

- Projektpfad: `/Users/michaelgiese/zonvaa-builder`
- Git-Branch: `main`
- Die CLI wird über `builder/main.py` mit Typer definiert.
- `builder/main.py` registriert:
  - `handover`
  - `doctor`
  - `init`
  - `role create`
- `builder/main.py` ruft im CLI-Callback `RuntimeManager().boot()` auf.
- `RuntimeManager.boot()` lädt:
  - die Constitution über `ConstitutionManager().load()`
  - die Knowledge-Struktur über `KnowledgeManager().load()`
  - und protokolliert `Runtime gestartet` über `RuntimeJournal`
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
- Die Constitution existiert und ist verbindlich mit Version 1.0.
- `knowledge/adr/ADR-0002-knowledge-system.md` existiert mit Status `beschlossen`.

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

1. **Untracked Runtime-Protokolle**
   - `knowledge/protocols/2026-07-19_10-04-33_runtime.md`
   - `knowledge/protocols/2026-07-19_10-05-15_runtime.md`
   - Risiko: Runtime-Protokolle sind noch nicht versioniert.

2. **Doppelte Rollenstruktur**
   - Rollen liegen gleichzeitig unter `roles/` und `agents/`.
   - Risiko: Unklare Quelle der Wahrheit für Rollenprompts.

3. **Build-/Release-Commands inkonsistent**
   - `commands/build.py` existiert, ist aber nicht registriert.
   - `commands/release.py` existiert, ist leer und nicht registriert.

4. **Kein bestätigter vollständiger Testlauf**
   - `tests/test_builder.py` existiert.
   - Ein aktuelles Testergebnis ist nicht bereitgestellt.

5. **Aktuelle Übergabe-Datei noch nicht bestätigt geschrieben**
   - Bestätigt ist die aktuelle Antwortgenerierung, nicht das anschließende Schreiben der Datei nach `knowledge/sessions`.

## Nächster konkreter Schritt

Die zwei untracked Runtime-Protokolldateien prüfen und entscheiden, ob sie versioniert oder entfernt werden sollen.

## Startanweisung für den nächsten Chat

Prüfe im Projektverzeichnis `/Users/michaelgiese/zonvaa-builder` ausschließlich den aktuellen Git-Status und den Inhalt der zwei untracked Runtime-Protokolle:

```bash
git status --short --untracked-files=all && printf '\n--- runtime protocol 10-04-33 ---\n' && sed -n '1,220p' knowledge/protocols/2026-07-19_10-04-33_runtime.md && printf '\n--- runtime protocol 10-05-15 ---\n' && sed -n '1,220p' knowledge/protocols/2026-07-19_10-05-15_runtime.md
```

## Technischer Anhang

- **Git-Branch**
  - `main`

- **Git-Status**
  - `?? knowledge/protocols/2026-07-19_10-04-33_runtime.md`
  - `?? knowledge/protocols/2026-07-19_10-05-15_runtime.md`

- **Letzte Commits**
  ```text
  dae23ea Add runtime knowledge system
  9b8d589 Add WHY defining Zonvaa's mission
  d80efbc Load Constitution and session knowledge
  b845b71 Add Constitution runtime
  d7002d1 Implement modular CLI and AI handover workflow
  ```

- **Relevante Befehle**
  ```bash
  python3 -m builder.main handover runtime_knowledge_system_v1
  git status --short --untracked-files=all
  git log -5 --oneline
  ```

- **Relevante Dateien**
  - `builder/main.py`
  - `builder/runtime.py`
  - `builder/journal.py`
  - `commands/handover.py`
  - `agents/handover.md`
  - `agents/role_agent.py`
  - `agents/tasks.py`
  - `brain/context_collector.py`
  - `brain/context_analyzer.py`
  - `constitution/constitution.md`
  - `knowledge/manager.py`
  - `knowledge/adr/ADR-0002-knowledge-system.md`
  - `knowledge/protocols/2026-07-19_10-04-33_runtime.md`
  - `knowledge/protocols/2026-07-19_10-05-15_runtime.md`

## Nicht bestätigt

- Inhalt und Zweck der zwei untracked Runtime-Protokolldateien.
- Ob die zwei Runtime-Protokolle committed werden sollen.
- Ob `commands/build.py` und `commands/release.py` künftig registriert werden sollen.
- Ob `roles/` oder `agents/` langfristig die verbindliche Rollenstruktur ist.
- Ergebnis eines vollständigen Testlaufs.
- Inhalt von `tests/test_builder.py`.
- Ob die aktuell erzeugte Übergabe-Datei nach Abschluss dieser Antwort erfolgreich nach `knowledge/sessions` geschrieben wurde.