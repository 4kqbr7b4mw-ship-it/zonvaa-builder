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
