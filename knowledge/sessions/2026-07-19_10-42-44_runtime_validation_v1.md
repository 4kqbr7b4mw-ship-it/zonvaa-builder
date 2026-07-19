# runtime_validation_v1

## Kurzüberblick

Der ZONVAA Builder ist ein wissensgetriebenes Python/Typer-CLI-System zur Planung, Entwicklung, Prüfung, Dokumentation und Übergabe von Softwareprojekten. Verbindliche Grundlage ist die `constitution/constitution.md` in Version 1.0. Der aktuelle Lauf wurde mit `python3 -m builder.main handover runtime_validation_v1` gestartet. Dabei wurden `builder.main`, der `handover`-Command, `ContextCollector.collect()` und `build_handover_task()` erfolgreich ausgeführt. `agents/handover.md` wurde durch `RoleAgent` geladen. `OPENAI_API_KEY` und `OPENAI_MODEL` konnten verwendet werden, und die OpenAI Responses API hat die Anfrage angenommen. Der Handover-Agent erzeugt aktuell diese Übergabe. Der Git-Branch ist `main`; der aktuelle Git-Status enthält keine geänderten Dateien. Seit der letzten Session wurden weitere Runtime-/Protokoll-Commits erstellt. Offene Risiken betreffen vor allem die doppelte Rollenstruktur und nicht bestätigte vollständige Tests.

## Letzte Session

- **heute umgesetzt**
  - Der aktuelle Handover-Lauf `python3 -m builder.main handover runtime_validation_v1` wurde gestartet.
  - Der Handover-Workflow läuft bis zur aktuellen Agentenantwort erfolgreich.
  - Laut aktueller Git-Historie wurden seit der letzten bereitgestellten Session weitere Commits erstellt:
    - `12df905 Remove runtime boot logging`
    - `f38f034 Use single runtime journal`
    - `0349a5c Add runtime protocol log`
    - `c1340ce Add runtime protocol log`
    - `099c5cc Add runtime protocol logs`

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
  - Keine Laufzeitfehler sind in den automatisch bestätigten Fakten enthalten.
  - Rollen liegen weiterhin gleichzeitig unter `roles/` und `agents/`.
  - Ein vollständiger aktueller Testlauf, z. B. `pytest`, ist nicht bestätigt.

- **gelöste Probleme**
  - Der aktuelle Git-Status ist sauber: `changed_files` ist leer.
  - Die in der letzten Session genannte untracked Runtime-Protokolldatei ist im aktuellen Git-Status nicht mehr als Änderung aufgeführt.
  - `build` und `release` sind im aktuell bereitgestellten `builder/main.py` als CLI-Commands registriert.

## Bestätigter technischer Stand

- Projektpfad: `/Users/michaelgiese/zonvaa-builder`
- Git-Branch: `main`
- Git-Arbeitsstand: keine geänderten Dateien laut aktuellem Projektkontext.
- Die CLI wird über `builder/main.py` mit Typer definiert.
- `builder/main.py` registriert:
  - `build`
  - `handover`
  - `doctor`
  - `init`
  - `release`
  - `role create`
- `builder/main.py` ruft im CLI-Callback `RuntimeManager().boot()` auf.
- `RuntimeManager.boot()` lädt laut bereitgestelltem Code:
  - die Constitution über `ConstitutionManager().load()`
  - die Knowledge-Struktur über `KnowledgeManager().load()`
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
- `commands/build.py` enthält einen vorbereiteten Build-Command mit Konsolenausgabe.
- `commands/release.py` enthält einen vorbereiteten Release-Command mit Konsolenausgabe.
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

1. **Doppelte Rollenstruktur**
   - `RoleAgent` lädt Rollen aus `agents/`.
   - `role create` erzeugt Rollen unter `roles/`.
   - Risiko: Unklare Quelle der Wahrheit für Rollenprompts.

2. **Kein bestätigter vollständiger Testlauf**
   - `tests/test_builder.py` existiert.
   - Ein aktuelles Testergebnis ist nicht bereitgestellt.

3. **Build-/Release-Commands fachlich nur vorbereitet**
   - `build` und `release` sind registriert.
   - Bestätigt ist nur die vorhandene einfache Ausgabe, nicht ein produktiver Build- oder Release-Prozess.

4. **Aktuelle Übergabe-Datei noch nicht bestätigt geschrieben**
   - Bestätigt ist die aktuelle Antwortgenerierung, nicht das anschließende Schreiben der Datei nach `knowledge/sessions`.

## Nächster konkreter Schritt

Einen vollständigen Testlauf mit `pytest` ausführen und das Ergebnis dokumentieren.

## Startanweisung für den nächsten Chat

Führe im Projektverzeichnis `/Users/michaelgiese/zonvaa-builder` genau diesen Testlauf aus und berichte nur Ergebnis, Fehlerausgaben und Git-Status:

```bash
pytest && git status --short --untracked-files=all
```

## Technischer Anhang

- **Git-Branch**
  - `main`

- **Git-Status**
  - Keine geänderten Dateien laut aktuellem Projektkontext (`changed_files: []`).

- **Letzte Commits**
  ```text
  12df905 Remove runtime boot logging
  f38f034 Use single runtime journal
  0349a5c Add runtime protocol log
  c1340ce Add runtime protocol log
  099c5cc Add runtime protocol logs
  ```

- **Relevante Befehle**
  ```bash
  python3 -m builder.main handover runtime_validation_v1
  pytest
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
  - `tests/test_builder.py`

## Nicht bestätigt

- Ergebnis eines vollständigen aktuellen Testlaufs.
- Inhalt und Testabdeckung von `tests/test_builder.py`.
- Ob `roles/` oder `agents/` langfristig die verbindliche Rollenstruktur ist.
- Ob `build` und `release` über vorbereitende Konsolenausgaben hinaus fachlich ausgebaut werden sollen.
- Ob die aktuell erzeugte Übergabe-Datei nach Abschluss dieser Antwort erfolgreich nach `knowledge/sessions` geschrieben wurde.