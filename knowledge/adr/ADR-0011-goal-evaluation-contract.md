# ADR-0011 – Goal Evaluation Contract

## Status

Beschlossen

## Kontext

Die vorhandene Goal Engine erzeugt einen `GoalContext` mit Rolle, Memory-Typen, Constitution-Regeln, verifizierten Fakten und Projektzustand.

Dieser Kontext enthält kein konkretes Ziel, keine geladene WHY-Identität, keine Bewertungsregeln und keine maschinenlesbare WHY-Bewertung. Eine direkte WHY-Prüfung in der Decision Engine wäre deshalb nicht deterministisch und würde unzulässige semantische Annahmen erfordern.

## Entscheidung

ZONVAA trennt Goal Definition, Evaluation Context, Identity Context und WHY Assessment als eigenständige Verantwortlichkeiten.

### Goal Definition

Das bereits durch ADR-0010 festgelegte Objekt `Goal` beschreibt das konkrete Ziel getrennt vom `GoalContext`. Für die spätere Bewertung wird mindestens seine eindeutige textuelle Zielbeschreibung als expliziter Eingang übergeben. Dieser ADR führt kein zweites Goal-Modell und keine neue Benennung ein.

### Evaluation Context

Der bestehende `GoalContext` stellt den Kontext bereit, gegen den ein Ziel später bewertet werden kann. Der Name `GoalContext` bleibt zunächst aus Kompatibilitätsgründen bestehen. Eine mögliche spätere Umbenennung in `DecisionContext` oder `EvaluationContext` wird ausdrücklich zurückgestellt.

### Identity Context

Zur technischen Umsetzung von ADR-0008 stellt ein zukünftiger Identity-/WHY-Loader die verbindliche Identitätsgrundlage aus `WHY.md` bereit. Die Runtime darf `WHY.md` nicht durch freie Interpretation ersetzen. Quelle und Version der geladenen Identität müssen nachvollziehbar sein.

### WHY Assessment

Die WHY-Bewertung ist ein eigenes maschinenlesbares Ergebnis. Sie enthält mindestens einen Status und stabile Reason-Codes. Zulässige Statuswerte für Version 1 sind:

- `aligned`
- `conflicting`
- `not_evaluable`

Optional ergänzende Evidenz darf dokumentiert werden, ersetzt aber nicht den Status.

## Keine semantische Erfindung in der Decision Engine

Die Decision Engine darf nicht selbst aus einer freien Zielbeschreibung ableiten, ob ein Ziel zum WHY passt. Verboten sind insbesondere:

- Schlüsselwortheuristiken
- unscharfe Textähnlichkeit
- implizite Bedeutungsannahmen
- LLM-Aufrufe innerhalb der deterministischen Decision Engine
- automatische Freigabe bei fehlenden Daten

Die Decision Engine konsumiert eine bereits vorhandene strukturierte WHY-Bewertung. Deren Erzeugung ist Aufgabe einer getrennten zukünftigen Komponente oder eines expliziten menschlichen Prüfschritts.

## Getrennte Bewertungsergebnisse

Technische Bewertung und WHY-Bewertung werden getrennt ausgewiesen. Technische Blocker sind beispielsweise:

- `git_dirty`
- fehlende Runtime-Voraussetzungen
- nicht verifizierter Projektzustand

Die WHY-Bewertung darf bestehende technische Blocker nicht überschreiben. Technische Blocker dürfen die WHY-Bewertung ebenfalls nicht unsichtbar machen.

## Deterministische Priorität des Gesamtergebnisses

Der spätere Gesamtstatus wird in dieser Reihenfolge gebildet:

1. `blocked`, wenn mindestens ein technischer Blocker vorliegt.
2. `blocked`, wenn der WHY-Status `conflicting` ist.
3. `needs_review`, wenn der WHY-Status `not_evaluable` ist.
4. `approved` nur, wenn keine technischen Blocker vorliegen und der WHY-Status `aligned` ist.

Die interne Benennung von `needs_review` darf bei der Implementierung nur geändert werden, wenn im Repository bereits ein gleichbedeutender Status existiert. Dann wird der bestehende Status verwendet und die Abweichung dokumentiert.

## Verhalten ohne Goal

Das bisherige Verhalten der Decision Engine ohne Goal oder `GoalContext` bleibt zunächst unverändert. Dies ist eine explizite Kompatibilitätsregel und keine dauerhafte Zielarchitektur. Die spätere verpflichtende Zielübergabe benötigt einen eigenen Migrationsentscheid.

## Reihenfolge der nächsten Implementierungsschritte

1. Identity-/WHY-Loader und Runtime-Integration
2. bestehendes `Goal`-Definitionsmodell als expliziten Evaluierungseingang anbinden
3. maschinenlesbares WHY-Assessment-Modell
4. getrennte Übergabe an die Decision Engine
5. deterministische Zusammenführung der technischen und fachlichen Ergebnisse
6. fokussierte Unit- und Integrationstests

## Nicht Bestandteil dieses ADR

- konkrete semantische Bewertung eines Zieltextes
- LLM-basierte Bewertung
- Embeddings
- Keyword-Matching
- automatische Goal-Generierung
- Umbenennung des bestehenden `GoalContext`
- Änderung bestehender Produktionslogik

## Konsequenzen

- Die Decision Engine bleibt deterministisch und frei von impliziter Semantik.
- Ziel, Evaluationskontext, Identitätsgrundlage und Bewertung bleiben getrennt nachvollziehbar.
- Technische und fachliche Blocker bleiben gleichzeitig sichtbar.
- Eine automatische Freigabe ohne strukturierte WHY-Bewertung ist für den zukünftigen zielbezogenen Pfad ausgeschlossen.
- Bestehende Produktionslogik und kompatibles Verhalten bleiben durch diesen ADR unverändert.
