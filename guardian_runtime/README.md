# Guardian Runtime

Die Guardian Runtime ist der unveränderliche, personengebundene
Wissenszustandsvertrag unterhalb von Guardian, Conversation/Interaction und
Institution.

## Komponenten

- `models.py`: Knowledge Types, Provenienz, Zeit, Guardian Memory, Konflikte,
  Retention, Snapshots und auditierbare Transitionen.
- `planner.py`: deterministische Planung genau einer autorisierten Transition
  ohne Persistenz oder Ausführung.
- `contract.md`: versionierter, durch Runtime und Preflight nachgewiesener
  Architekturvertrag.
- `loader.py`: strukturelle UTF-8-, Versions-, Vollständigkeits- und
  Hashprüfung des Vertrags.

## Grenze

RuntimeManager bleibt technische Single Source of Truth. KnowledgeManager
bleibt einzige Knowledge-Schnittstelle. Die Guardian Runtime speichert keine
Originaldokumente und führt keine Transition aus.

Ein ungebundener Snapshot ist vollständig leer. Ein gebundener Snapshot
isoliert genau eine Guardian-/Subject-Zuordnung. Mehrparteienfreigaben werden
nicht hier erzeugt, sondern bleiben am bestehenden Artefakt- und
Autorisierungsvertrag gesperrt.

## Nutzung

```python
from guardian_runtime import (
    GuardianRuntimeTransitionPlanner,
    KnowledgeTransitionRequest,
)

plan = GuardianRuntimeTransitionPlanner().plan(snapshot, request)
```

`plan` enthält den vollständigen Audit-Übergang und einen neuen
hash-validierten Snapshot. `snapshot` wird nicht verändert.

Es gibt bewusst kein JSON-CLI und keine Persistenz. Ein solcher Adapter
benötigt eine eigene bestätigte Entscheidung, sobald ein produktiver lokaler
Speichervertrag vorliegt.
