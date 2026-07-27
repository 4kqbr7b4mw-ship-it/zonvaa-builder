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
  --decision decision-b.json
```

Der erste Aufruf speichert Proposals, Analysen und eine gemeinsame kompakte
Entscheidungsvorlage unter `knowledge/architecture_workflows/`. Ohne
bestätigte Entscheidung bleibt er in `WAITING_FOR_DECISION`. Der zweite
Aufruf speichert ausschließlich explizite Chief-Architect-Entscheidungen,
erzeugt den Codex-Prompt und startet die autorisierte lokale Feedback-Kette,
sobald für jedes Proposal eine passende Entscheidung vorliegt. Codex darf
dabei Tests, Doctor, Commit und Handover ausführen, aber niemals die
nachgelagerte Chief-Architect-Entscheidung ersetzen.

Der erzeugte Prompt besitzt einen Hash- und Decision-Proof. Die
[lokale Execution Bridge](../codex_execution/README.md) kann ausschließlich
diesen bestätigten kanonischen Auftrag an `codex exec` übergeben.

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
