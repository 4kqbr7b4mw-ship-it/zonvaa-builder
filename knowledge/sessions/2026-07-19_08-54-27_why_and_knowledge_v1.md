# why_and_knowledge_v1

## Kurzüberblick

ZONVAA ist als wissensgetriebener Builder für Planung, Entwicklung, Prüfung, Dokumentation und Übergabe von Softwareprojekten angelegt. Die verbindliche Arbeitsgrundlage ist die `constitution/constitution.md` in Version 1.0. Der Builder nutzt eine modulare Typer-CLI mit Commands wie `handover`, `doctor`, `init` und `role create`. In der aktuellen Ausführung wurde der Handover-Workflow erfolgreich gestartet und bis zur Erzeugung dieser Übergabe ausgeführt. Der Projektkontext wird über `ContextCollector` gesammelt, über `ContextAnalyzer` verdichtet und anschließend an den Handover-Agenten übergeben. Der Handover-Agent wird aus `agents/handover.md` geladen und nutzt die OpenAI Responses API. Der Git-Arbeitsstand ist nicht sauber: Es gibt 12 geänderte bzw. unversionierte Dateien. Relevante Risiken bestehen bei nicht versioniertem Arbeitsstand, parallelen Rollenordnern `roles/` und `agents/`, sowie bei vorhandenen, aber nicht vollständig bestätigten bzw. nicht registrierten Build-/Release-Strukturen.

## Letzte Session

- **heute umgesetzt**
  - Der aktuelle Handover-Lauf wurde mit `python3 -m builder.main handover why_and_knowledge_v1` gestartet.
  - `ContextCollector.collect()` wurde erfolgreich ausgeführt.
  - `build_handover_task()` wurde erfolgreich ausgeführt.
  - `agents/handover.md` wurde durch `RoleAgent` erfolgreich geladen.
  - Die OpenAI Responses API hat die Anfrage angenommen.
  - Der Handover-Agent erzeugt aktuell diese Übergabe.
  - Im Arbeitsstand vorhanden, aber noch nicht versioniert: u. a. `builder/runtime.py`, `knowledge/manager.py`, `knowledge/adr/ADR-0002-knowledge-system.md`, `commands/build.py`, `commands/release.py`, `agents/architect.md`, `roles/architect.md`.

- **getestete Funktionen**
  - Bestätigt durch aktuelle Ausführung:
    - `builder.main` kann gestartet werden.
    - Der `handover`-Command kann erfolgreich aufgerufen werden.
    - Kontextsammlung und Task-Erstellung für den Handover funktionieren.
    - Der Rollen-Agent kann `agents/handover.md` laden.
    - `OPENAI_API_KEY` und `OPENAI_MODEL` konnten verwendet werden.
    - Die OpenAI Responses API nimmt die Anfrage an.
  - Keine separaten Testläufe wie `pytest` sind in den bereitgestellten Daten bestätigt.

- **aufgetretene Probleme**
  - Der Git-Arbeitsstand ist dirty und enthält unversionierte Dateien.
  - Rollen liegen gleichzeitig unter `roles/` und `agents/`.
  - `commands/build.py` existiert, ist laut `builder/main.py` aber nicht als CLI-Command registriert.
  - `commands/release.py` existiert laut Kontext, ist in den bereitgestellten Dateiinhalten leer und ebenfalls nicht in `builder/main.py` registriert.

- **gelöste Probleme**
  - Keine explizit dokumentierten gelösten Probleme in den bereitgestellten Daten.
  - Bestätigt ist nur, dass der aktuelle Handover-Workflow erfolgreich bis zur Agentenantwort läuft.

## Bestätigter technischer Stand

- Projektpfad: `/Users/michaelgiese/zonvaa-builder`.
- Git-Branch: `main`.
- Die CLI wird über `builder/main.py` mit Typer definiert.
- Registrierte Commands in `builder/main.py`:
  - `handover`
  - `doctor`
  - `init`
  - `role create`
- `builder/main.py` initialisiert beim CLI-Callback `RuntimeManager().boot()`.
- `commands/handover.py`:
  - sammelt Projektkontext mit `ContextCollector`,
  - analysiert ihn mit `ContextAnalyzer`,
  - baut eine Handover-Aufgabe,
  - ruft `RoleAgent` mit Rolle `handover` auf,
  - schreibt das Ergebnis nach `knowledge/sessions`.
- `RoleAgent` lädt Rollenprompts aus `agents/{role_name}.md`.
- `RoleAgent` nutzt `OPENAI_API_KEY`, `OPENAI_MODEL` und `OpenAI(...).responses.create(...)`.
- `ContextCollector` sammelt:
  - Dateien,
  - wichtige Dateiinhalte,
  - Session-Dateien,
  - Git-Branch,
  - Git-Status,
  - letzte Commits.
- `ContextAnalyzer` verdichtet:
  - geänderte Dateien,
  - relevante Dateien,
  - Summary-Zahlen,
  - einfache Risiken.
- Die Constitution existiert und ist verbindlich mit Version 1.0.
- Foundation-Dokumente zu Vision, Mission, Values und Manifest sind vorhanden; `foundation/mission.md` ist als Entwurf markiert.

## Entscheidungen

- Die Constitution ist verbindliche Arbeitsgrundlage des Builders.
- Wissen, Entscheidungen und Arbeitsregeln werden dauerhaft im Projekt gespeichert; der Chat ist kein Langzeitspeicher.
- Vor wissensabhängigen Workflows muss die Builder-Runtime laut Constitution die Constitution, Protokolle, ADRs, Übergaben und Projektkontext berücksichtigen.
- Es wird immer nur ein klarer Schritt gleichzeitig ausgeführt.
- Aussagen müssen zwischen bestätigt, Annahme und nicht bestätigt unterscheiden.
- Architekturentscheidungen trifft der Produktarchitekt; KI-Agenten analysieren, empfehlen und bereiten vor.
- Der Handover-Agent liegt unter `agents/handover.md` und ist die bestätigte Rolle für Übergaben.
- Aktueller CLI-Einstieg ist `builder/main.py`.
- Rollenverwaltung erzeugt Rollen aktuell unter `roles/`; Agentenausführung lädt Rollen aktuell aus `agents/`.

## Offene Punkte und Risiken

1. **Arbeitsstand nicht versioniert**
   - 12 Dateien sind geändert oder untracked.
   - Risiko: Aktueller funktionierender Stand kann verloren gehen oder nicht sauber nachvollzogen werden.

2. **Rollenstruktur doppelt**
   - `roles/architect.md` und `agents/architect.md` existieren parallel.
   - Risiko: Unklare Quelle der Wahrheit für Rollen.

3. **Runtime-Datei vorhanden, aber Inhalt nicht bestätigt**
   - `builder/main.py` importiert `RuntimeManager` aus `builder/runtime.py`.
   - `builder/runtime.py` ist untracked; sein Inhalt wurde nicht bereitgestellt.
   - Gleichzeitig ist durch aktuelle Ausführung bestätigt, dass `builder.main` starten konnte.

4. **Build-/Release-Commands inkonsistent**
   - `commands/build.py` existiert und enthält einen vorbereiteten Build-Command.
   - `commands/release.py` existiert, ist aber in den bereitgestellten Inhalten leer.
   - Beide sind in `builder/main.py` nicht registriert.

5. **Kein bestätigter vollständiger Testlauf**
   - Es gibt eine Datei `tests/test_builder.py`, aber kein aktuelles Testergebnis in den bereitgestellten Daten.

6. **Neue Wissenssystem-Dateien untracked**
   - `knowledge/manager.py` und `knowledge/adr/ADR-0002-knowledge-system.md` sind untracked.
   - Inhalte und Status sind nicht bestätigt.

## Nächster konkreter Schritt

Den aktuellen Arbeitsstand gezielt prüfen und danach entscheiden, welche der unversionierten Runtime-/Knowledge-/Command-Dateien committed werden sollen.

## Startanweisung für den nächsten Chat

Prüfe zuerst den unversionierten Arbeitsstand und den Inhalt der zentralen neuen Dateien mit folgendem Befehl:

```bash
git status --short --untracked-files=all && printf '\n--- builder/runtime.py ---\n' && sed -n '1,220p' builder/runtime.py && printf '\n--- knowledge/manager.py ---\n' && sed -n '1,220p' knowledge/manager.py && printf '\n--- knowledge/adr/ADR-0002-knowledge-system.md ---\n' && sed -n '1,220p' knowledge/adr/ADR-0002-knowledge-system.md && printf '\n--- commands/release.py ---\n' && sed -n '1,220p' commands/release.py
```

## Technischer Anhang

- **Git-Branch**
  - `main`

- **Git-Status**
  - `M builder/main.py`
  - `?? agents/architect.md`
  - `?? builder/runtime.py`
  - `?? commands/build.py`
  - `?? commands/release.py`
  - `?? knowledge/adr/ADR-0002-knowledge-system.md`
  - `?? knowledge/manager.py`
  - `?? knowledge/sessions/2026-07-17_14-12-39_runtime_v1.md`
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
  python3 -m builder.main handover why_and_knowledge_v1
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

- Inhalt und Verhalten von `builder/runtime.py`.
- Inhalt und Zweck von `knowledge/manager.py`.
- Inhalt und Beschlussstatus von `knowledge/adr/ADR-0002-knowledge-system.md`.
- Ob `commands/build.py` und `commands/release.py` künftig registriert werden sollen.
- Ob `roles/` oder `agents/` langfristig die verbindliche Rollenstruktur ist.
- Ergebnis eines vollständigen Testlaufs.
- Inhalt von `tests/test_builder.py`.
- Ob der aktuelle dirty Arbeitsstand vollständig beabsichtigt ist.