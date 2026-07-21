# ADR-0010 – Goal Engine

## Status

Beschlossen

## Kontext

ZONVAA besitzt eine zentrale Runtime, ein klassifiziertes Memory-System sowie getrennte Decision- und Execution-Engines. Vor einer Entscheidung fehlt jedoch ein verbindlicher, strukturierter Bezug zwischen Ziel, Projekt, aktiver Rolle, relevanten Memory-Klassen, geltenden Regeln und bestätigtem Zustand.

Die Goal Engine implementiert keine neue KI und trifft keine Entscheidung. Sie schafft ausschließlich die belastbare Kontextgrundlage für eine spätere Übergabe an die Decision Engine.

## Entscheidung

ZONVAA führt eine kleine, typisierte Goal Engine ein. Sie besteht aus:

- `Goal`: Identität, Beschreibung, Projektbezug, Priorität, Status, Owner und Erstellungszeitpunkt eines Ziels.
- `GoalContext`: aktive Rolle, relevante Memory-Klassen, Constitution-Regeln, verifizierte Fakten und Projektzustand.
- `GoalDecision`: typisierter Vertrag für eine spätere begründete Entscheidung; wird von der Goal Engine noch nicht erzeugt.
- `GoalEngine`: validiert Eingaben und erstellt ausschließlich einen `GoalContext`.

Die zentrale Runtime lädt genau eine `GoalEngine`. Dadurch bleibt sie gemäß ADR-0004 Single Source of Truth. Es wird kein eigener globaler Zustand und keine Persistenz eingeführt.

## Ablauf

Runtime
→ Goal Engine
→ GoalContext
→ Decision Engine (vorbereitet, noch ohne Goal-Auswertung)
→ Planner
→ Execution Engine

Vor einer späteren zielbezogenen Entscheidung muss der Kontext nachvollziehbar beantworten:

1. Welches Ziel wird verfolgt?
2. Zu welchem Projekt gehört es?
3. Welche Rolle arbeitet?
4. Welche Memory-Klassen sind relevant?
5. Welche Constitution-Regeln und bestätigten Fakten gelten?
6. Auf welcher Grundlage kann die Decision Engine später die beste Unterstützung des WHY bestimmen?

## Regeln

1. Die Goal Engine trifft keine Entscheidung und bewertet keine Handlungsoptionen.
2. Relevante Memory-Klassen verwenden ausschließlich die Typen aus ADR-0009; unbekannte Typen werden abgelehnt.
3. Ein Goal benötigt eine stabile ID, einen Projektbezug, einen Owner und einen Erstellungszeitpunkt mit Zeitzone.
4. `verified_facts` enthält ausschließlich bereits von der bestehenden Runtime bereitgestellte bestätigte Fakten.
5. Die Decision Engine akzeptiert den neuen Kontext zunächst nur als optionalen Übergabepunkt; ihr bestehendes Verhalten bleibt unverändert.
6. Es entstehen keine zweite Runtime, keine neue Wissensstruktur und keine zusätzliche Persistenz.

## Konsequenzen

- Ziele und ihr Entscheidungskontext werden explizit und testbar.
- Goal-, Decision- und Execution-Verantwortung bleiben getrennt.
- Bestehende Aufrufer der Decision Engine bleiben kompatibel.
- Die konkrete Bewertung eines GoalContext gegen das WHY ist ein späterer Meilenstein.
