# ZONVAA Codex Rules

## Kanonischer Arbeitskontext

Dieses Dokument ist die einzige kanonische Quelle für die dauerhafte
Zusammenarbeit im aktiven ZONVAA-Repository.

- Der Mensch bestimmt das fachliche Ziel und die Produktgrenzen.
- Der Chief Architect formuliert Aufträge und bewertet Ergebnisse.
- Der Builder schützt und validiert, trifft aber keine fachlichen oder
  architektonischen Entscheidungen.
- Codex implementiert, testet und berichtet.
- Der Nutzer ist kein manueller Terminal-, Such-, Prüf- oder Transportweg;
  Codex führt notwendige Repository-Arbeiten aus und liefert Ergebnisse zurück.
- Commit und Push benötigen jeweils eine getrennte ausdrückliche menschliche
  Freigabe.
- ZONVAA V2 ist das einzige aktive Repository. ZONVAA V1 ist ausschließlich
  Archiv und weder Arbeitsverzeichnis noch Implementierungsquelle.
- Architekturentscheidungen dürfen nicht automatisch abgeleitet werden.
- Schreibende Git-Operationen erfolgen nie ungefragt.

Chatgedächtnis ist keine verlässliche Projektquelle. Das Repository ist die
verbindliche Quelle für Arbeitsweise und Produktstand. Für einen neuen Chat
führt Codex `python3 -m builder.main handover` aus und gibt den vollständigen
Text zurück; der Nutzer soll dafür keine Terminalbefehle ausführen. Dieser
Befehl ist ausschließlich read-only.

Für jede Projektaufgabe gilt:

1. Zuerst `python3 -m builder.main preflight` ausführen und den Mission Context berücksichtigen.
2. Bestehende Architektur, ADRs und betroffene Tests vor Änderungen lesen.
3. Fehlende Informationen ausdrücklich als fehlend behandeln; nicht spekulieren.
4. Bei längeren Arbeitspaketen `PLANS.md` während der Arbeit aktuell halten.
5. Vor jedem Commit fokussierte und vollständige Tests, Doctor sowie `git diff --check` ausführen.
6. Nach Abschluss den kanonischen Produktstand als Teil derselben Änderung
   aktualisieren und mit dem read-only `handover`-Command den Chat-Staffelstab
   ausgeben.
7. Niemals ohne ausdrücklichen Auftrag pushen.

Ausführliche verbindliche Regeln stehen in `constitution/constitution.md`.
