# ADR-0021 – Mission Context Workflow Integration

## Status

Beschlossen

## Kontext

ADR-0020 führt den validierten Mission Context als lokalen Einstieg für
Codex-Aufgaben ein. Der bestehende Goal Application Service bildet bereits die
kleinste reale Kette aus Runtime, Context Pipeline, Goal Engine, Orchestrator,
Decision Engine, Planner und Execution Engine. Bislang konnte diese Kette
jedoch ohne Mission Context gestartet werden.

## Entscheidung

Der Goal Application Service verlangt einen expliziten `MissionContext`. Er
validiert ihn beim Erzeugen des Service und unmittelbar vor jedem Lauf gegen
dieselbe `RuntimeManager`-Instanz. Pflichtstruktur, Project State, Verified
Facts, Git-Branch, Git-Commit, Projektwurzel und ein maximales Alter von fünf
Minuten werden geprüft. Fehlender, veränderter oder veralteter Kontext bricht
den Workflow mit `PreflightError` ab.

`MissionContext` ist tief unveränderlich: verschachtelte Mappings werden
read-only und Sequenzen zu Tupeln. Seine JSON-Sicht wird ausschließlich als
neue veränderbare Kopie erzeugt.

Der vollständige Mission Context bleibt am Rand des Application Service. Für
den Goal-basierten Orchestrator wird daraus deterministisch ein kleiner
`WorkflowContext` mit Schema-Version, Erzeugungszeit, Projektwurzel,
Git-Branch und Git-Commit abgeleitet. `WorkflowContext` kann nicht direkt
öffentlich konstruiert werden. Goal-basierte Orchestrierung ohne diese
validierte Sicht wird abgelehnt; Legacy-Orchestrierung bleibt kompatibel.

Decision Engine, Planner und Execution Engine erhalten keinen vollständigen
Mission Context. Die Decision Engine verwendet weiterhin nur technischen
Kontext, GoalContext, IdentityContext und WhyAssessment. Planner und Execution
Engine erhalten weiterhin ausschließlich Goal, Artefakte beziehungsweise
freigegebene Planschritte.

Der vorhandene CLI-Befehl `goal run` erzeugt den Mission Context nach dem Boot
aus derselben Runtime und übergibt ihn explizit an den Application Service.
Preflight-Fehler führen über den bestehenden CLI-Fehlerpfad zu einem Exit-Code
ungleich null.

## Grenzen

- Es wird kein neuer Application- oder Demonstrationsworkflow eingeführt.
- Die Integration erzeugt keine fachliche Bewertung und keine
  Life-Decisions-Regel.
- Der Kontext wird nicht global oder über einen zweiten Store übergeben.
- Es entstehen keine Netzwerk-, Cloud-, Datenbank- oder UI-Zugriffe.
- Die fünfminütige Gültigkeit gilt für den Start eines Runs, nicht als
  Abbruchsignal für eine bereits laufende sichere Ausführung.

## Konsequenzen

- Planung, Goal-Entscheidung und Ausführungsvorbereitung beginnen nur nach
  erfolgreicher Preflight-Validierung.
- Kontextänderungen zwischen Service-Erzeugung und Run werden erkannt.
- Komponenten erhalten nur den Kontext, den ihr vorhandener Vertrag benötigt.
- RuntimeManager und KnowledgeManager behalten ihre bestehenden Rollen als
  Single Source of Truth und einzige Knowledge-Schnittstelle.
