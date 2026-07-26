# ZONVAA Codex Rules

Für jede Projektaufgabe gilt:

1. Zuerst `python3 -m builder.main preflight` ausführen und den Mission Context berücksichtigen.
2. Bestehende Architektur, ADRs und betroffene Tests vor Änderungen lesen.
3. Fehlende Informationen ausdrücklich als fehlend behandeln; nicht spekulieren.
4. Bei längeren Arbeitspaketen `PLANS.md` während der Arbeit aktuell halten.
5. Vor jedem Commit fokussierte und vollständige Tests, Doctor sowie `git diff --check` ausführen.
6. Nach Abschluss mit dem lokalen `handover`-Command einen strukturierten Staffelstab unter `knowledge/handovers/` erzeugen.
7. Niemals ohne ausdrücklichen Auftrag pushen.

Ausführliche verbindliche Regeln stehen in `constitution/constitution.md`.
