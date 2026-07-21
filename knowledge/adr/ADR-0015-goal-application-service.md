# ADR-0015 – Goal Application Service

## Status

Beschlossen

## Kontext

Runtime, Goal Engine, Context-Pipeline und Goal-aware Orchestrator stellen bereits alle einzelnen Teile des deterministischen Anwendungsflusses bereit. Bisher fehlt ein programmgesteuerter Einstieg, der diese bestehenden Komponenten für ein vorhandenes Goal zusammensetzt. Rolle, relevante Memory-Typen und anzuwendende Constitution-Regeln sind laufbezogene Entscheidungen und keine automatisch ableitbaren Runtime-Werte.

## Entscheidung

Der öffentliche `builder.goal_application_service.GoalApplicationService` verbindet ausschließlich die vorhandene Runtime, Goal Engine, Context-Pipeline und den Orchestrator. Er erhält eine bereits gebootete `RuntimeManager`-Instanz im Konstruktor und bootet sie nicht selbst. Eine Runtime ohne `identity_context` oder Runtime-`goal_engine` wird als nicht gebootet mit `RuntimeError` abgelehnt.

Seine Methode `run` erhält explizit:

- ein vorhandenes `Goal`
- die aktive Rolle
- die relevanten Memory-Typen
- die ausgewählten Constitution-Regeln
- optional ein vorhandenes `WhyAssessment`

Der Service wählt oder erzeugt keinen dieser Werte. Er analysiert weder Goal-, WHY- noch Constitution-Text und erzeugt weder Assessment, Decision, Plan noch Execution-Struktur.

## Runtime und Context-Pipeline

Die Runtime liefert ausschließlich ihren geladenen und verifizierten Zustand: `verified_facts`, `project_state` und `identity_context`. Der `ContextCollector` akzeptiert optional eine konkrete Runtime-Instanz. Bei Injection verwendet er exakt diese Instanz; ohne Injection bleibt der bisherige Zugriff über `get_runtime()` kompatibel.

Der Application Service erzeugt seinen Standard-Collector mit der injizierten Runtime. Der `ContextAnalyzer` verarbeitet dessen Ergebnis unverändert nach seinem bestehenden Vertrag. Innerhalb dieses Standardflusses findet kein Zugriff auf eine zweite oder globale Runtime statt.

## Zusammensetzung

Der Ablauf ist:

1. `ContextCollector.collect()` erzeugt aus der injizierten Runtime den Projektkontext.
2. `ContextAnalyzer.analyze()` erzeugt den bestehenden technischen Orchestrator-Kontext.
3. Die bestehende Runtime-`GoalEngine` erzeugt aus Invocation-Daten sowie `runtime.verified_facts` und `runtime.project_state` den `GoalContext`.
4. Der Service übergibt `goal.title`, technischen Kontext, GoalContext, `runtime.identity_context` und das optionale Assessment an den bestehenden Orchestrator.
5. Die bestehende Orchestrator-Rückgabe wird unverändert zurückgegeben.

Die Decision Engine bleibt für Bindungsprüfung und Statuspriorität verantwortlich. Ohne Assessment entsteht `needs_review`; ein gültiges `aligned` kann nur ohne technischen Blocker zu `approved` führen; `conflicting` führt zu `blocked`, `not_evaluable` zu `needs_review`.

## Konsequenzen

- Laufbezogene Auswahl und dauerhafter Runtime-Zustand bleiben getrennt.
- Bestehende Singleton-Aufrufer der Context-Pipeline bleiben kompatibel.
- Der injizierte Service-Fluss verwendet konsistent genau eine Runtime.
- Es entstehen keine parallelen Fachmodelle, Ergebnisstrukturen, Persistenz oder semantische Bewertung.
