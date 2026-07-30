# Architecture Integrator

Der Architecture Integrator ist die deterministische Beratungsstufe zwischen
externem Architekturentwurf und Chief-Architect-Entscheidung.

## Rollen

- Externe Modelle liefern nur Entwürfe.
- Der Architecture Integrator lädt und vergleicht den verbindlichen Stand.
- Der Chief Architect entscheidet `ADOPT`, `ADOPT_WITH_CHANGES`, `REJECT`
  oder `DEFER`.
- Codex implementiert ausschließlich einen bestätigten, eigenständigen
  Auftrag.

Der Integrator genehmigt keine Architektur, publiziert keine MDRs oder ADRs
und verändert während der Analyse keine Architekturdateien.

## Standard-Workflow

Architecture Workflow v2 macht die Integrator-Kette über einen einzigen
zustandsbasierten Einstieg wiederaufnehmbar und unterstützt mehrere Proposals:

```bash
python3 -m builder.main architecture run \
  --topic "Artifact authorization" \
  --proposal proposal-a.json \
  --proposal proposal-b.json

python3 -m builder.main architecture run \
  --workflow-id workflow-0123456789abcdef \
  --decision decision-a.json \
  --no-create-commit \
  --decision decision-b.json
```

Der erste Aufruf speichert Proposals, Analysen und eine gemeinsame kompakte
Entscheidungsvorlage unter `knowledge/architecture_workflows/`. Ohne
bestätigte Entscheidung bleibt er in `WAITING_FOR_DECISION`. Der zweite
Aufruf speichert ausschließlich explizite Chief-Architect-Entscheidungen,
erzeugt den Codex-Prompt und startet die autorisierte lokale Feedback-Kette,
sobald für jedes Proposal eine passende Entscheidung vorliegt. Codex darf
dabei Tests, Doctor und Handover ausführen. Ein Commit ist nur mit
`create_commit: true` zulässig; Codex darf niemals die nachgelagerte
Chief-Architect-Entscheidung ersetzen.

Der erzeugte Prompt besitzt einen Hash- und Decision-Proof. Die
[lokale Execution Bridge](../codex_execution/README.md) kann ausschließlich
diesen bestätigten kanonischen Auftrag an `codex exec` übergeben.

Die Commit-Berechtigung ist ein eigenständiges boolesches Feld der Execution
Authorization. Ohne `--create-commit` gilt `create_commit: false`; allgemeine
Allowed Actions erteilen keine Commit-Berechtigung. `--create-commit`
autorisiert höchstens einen Commit nach erfolgreicher Orchestrator-Validierung,
niemals einen Push.

Prompt Proof Schema 1.1 bindet dieselbe Semantik an den gehashten Prompt:
`create_commit_authorized`, `commit_instruction` und `push_forbidden`.
Commitlose Prompts verbieten Commit und Staging ausdrücklich; commitfähige
Prompts erlauben genau einen Commit nach den erforderlichen Validierungen.
Prompt, Proof und Authorization werden vor jedem Prozessstart verglichen.
Widersprüche blockieren mit `PROMPT_AUTHORIZATION_MISMATCH`.

Die bisherigen `architecture workflow analyze`, `decide` und
`generate-codex`-Befehle bleiben für vorhandene Abläufe kompatibel, sind aber
nicht mehr der Standardpfad.

## Architecture-to-Codex Feedback

Der bestätigte Workflow persistiert unter `feedback/` eine typisierte
Execution-Autorisierung. Laufzeitliche Transitions, Intake und Review liegen
im bereits ignorierten `executions/feedback/`-Bereich. Die Autorisierung bindet
Architecture-Run, Entscheidungen, Prompt
und Hash, Repository, Basis-Commit, erlaubte Aktionen und erwartete
Abschlussartefakte. Die bestehende Execution Bridge bleibt die einzige
Ausführungsgrenze.

Nach erfolgreicher Ausführung wird genau das im Execution Record referenzierte
JSON-Handover gegen Execution-ID, Basis-/Ergebnis-Commit, Tests, Doctor,
Git-Status und Push-Grenze geprüft. Der Integrator erzeugt daraus eine
nicht bindende Entscheidungsvorlage und stoppt immer bei
`CHIEF_ARCHITECT_DECISION_REQUIRED`.

Der maschinenlesbare Gesamtstatus ist abrufbar mit:

```bash
python3 -m builder.main architecture workflow feedback-status \
  --workflow-id workflow-0123456789abcdef
```

## Architecture Operations

Der read-only Architecture Operations Agent leitet den aktuellen Stand bei
jedem Aufruf neu aus den bestehenden Workflow-, Feedback-, Execution- und
Handover-Artefakten ab. Er persistiert keinen eigenen Zustand, startet keine
Ausführung und trifft keine Entscheidung.

```bash
python3 -m builder.main architecture status \
  --topic "Guardian Succession"
python3 -m builder.main architecture next \
  --workflow-id workflow-0123456789abcdef
python3 -m builder.main architecture artifacts \
  --execution-id reconstructed-execution-0123456789abcdef
python3 -m builder.main architecture reviews --json
```

`status`, `next` und `artifacts` akzeptieren außerdem Architecture-Run-,
Review-, Commit-, Handover-, Proposal- und Decision-Referenzen. Mehrdeutige
Suchen werden mit `AMBIGUOUS_QUERY` abgebrochen. Fehlende erwartete Artefakte
werden ausdrücklich als `MISSING` ausgewiesen; ihre Pfade werden nicht
erfunden. `reviews` zeigt ausschließlich persistierte Integrator-Reviews im
Zustand `CHIEF_ARCHITECT_DECISION_REQUIRED`.

Historische Workflows ohne Prompt-Proof bleiben sichtbar, werden als Legacy
gekennzeichnet und durch diese Leseschicht nicht ausführbar gemacht. Ein
Review oder eine Empfehlung ersetzt niemals die Entscheidung des Chief
Architect.

## Chief Architect Review Decisions

Eine ausdrückliche Entscheidung über ein validiertes Implementierungsreview
verwendet einen eigenen Vertrag:

```bash
python3 -m builder.main architecture review decide \
  --review-id review-0123456789abcdef \
  --decision /tmp/review-decision.json
```

Die Eingabedatei enthält ausschließlich:

```json
{
  "decision": "ADOPT",
  "reason": "Explicit Chief Architect decision."
}
```

Workflow, Architecture Run, Execution-Herkunft, Commit und
Integrator-Empfehlung werden aus den validierten Review-Artefakten abgeleitet.
Sie können nicht über die Eingabe gesetzt werden. Pro Review ist genau ein
Decision-Artefakt unter `executions/feedback/` zulässig. Eine identische
Wiederholung ist idempotent; eine abweichende Entscheidung oder Begründung
wird nicht überschrieben.

Der Befehl startet weder Execution noch Attempt. Die read-only
Operations-Befehle zeigen Entscheidung, Begründung und Zeitpunkt anschließend
separat von der Integrator-Empfehlung an.

## Kontextreihenfolge

`C1 → MDR → C2 → Institution/Interaction → ADR → C3 → historische ADRs`

Der letzte Handover ist nur ergänzender Laufzeitkontext. MDR-0001 bleibt die
verbindliche Detailquelle für Guardian Conversation and Continuity.

## CLI

Analyse mit menschen- und maschinenlesbarer Ausgabe:

```bash
python3 -m builder.main architecture integrate \
  --input examples/architecture_integrator/proposal.json \
  --output /tmp/zonvaa-architecture-analysis.json
```

Codex-Auftrag nach bestätigter Chief-Architect-Entscheidung:

```bash
python3 -m builder.main architecture codex-prompt \
  --analysis examples/architecture_integrator/analysis.json \
  --decision examples/architecture_integrator/decision.json \
  --output /tmp/zonvaa-codex-prompt.md
```

Der zweite Befehl scheitert ohne ein valides Entscheidungsobjekt oder bei
nicht passender `proposal_id`. Ausgabedateien sind Arbeitsartefakte, keine
automatische Veröffentlichung verbindlicher Architektur.

Die Dateien unter `examples/architecture_integrator/` sind kleine,
schema-valide Beispiele. `analysis.json` ist bewusst kompakt und kein Ersatz
für eine frisch gegen den aktuellen Repository-Stand erzeugte Analyse.

## Analysegrenze

Der Vergleich ist lexikalisch und deterministisch. Er erkennt nur
ausdrückliche textliche Gleichheit oder Gegenläufigkeit; er verwendet keine
LLMs und erfindet keine semantischen Beziehungen. Nicht eindeutig belegbare
Inhalte bleiben Ergänzungen oder offene Entscheidungen.
