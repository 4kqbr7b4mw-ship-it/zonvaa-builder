# ADR-0013 – Decision WHY Integration

## Status

Beschlossen

## Kontext

ADR-0011 definiert die Priorität technischer Blocker und strukturierter WHY-Bewertungen. ADR-0012 definiert `WhyAssessment` als bereits erzeugtes, an ein vollständiges `Goal` und eine Identity-Version gebundenes Ergebnis. Die bestehende Decision Engine verarbeitet bisher ausschließlich technischen Projektkontext und muss für bestehende Aufrufer kompatibel bleiben.

## Entscheidung

Die bestehende `DecisionEngine` erhält zwei optionale Keyword-Parameter: `identity_context` und `why_assessment`. Zusammen mit dem bereits optionalen `goal_context` bilden sie einen getrennten Goal-basierten Modus. Es entsteht keine zweite Decision-Struktur.

### Legacy-Modus

Ohne `goal_context` bleibt das bisherige Verhalten und Rückgabeformat exakt erhalten. In diesem Modus dürfen weder `identity_context` noch `why_assessment` übergeben werden. Solche Teilübergaben werden als Integrationsfehler mit `ValueError` abgelehnt.

### Goal-basierter Modus

Mit `goal_context` ist ein `identity_context` verpflichtend. Ein fehlendes `why_assessment` führt ohne technischen Blocker zu `needs_review`; es wird weder ein Assessment erzeugt noch eine Freigabe abgeleitet.

Vor der Verwendung eines Assessments prüft die Decision Engine:

- `why_assessment.goal == goal_context.goal`
- `why_assessment.identity_version == identity_context.version`

Abweichungen sind Integritätsfehler und werden mit `ValueError` abgelehnt. Sie werden nicht in einen fachlichen WHY-Status umgewandelt.

## Status und Priorität

Die Decision Engine verwendet intern die typisierten String-Statuswerte `blocked`, `needs_review` und `approved`. Das Gesamtergebnis wird deterministisch gebildet:

1. Ein vorhandener technischer Blocker führt zu `blocked`.
2. WHY `conflicting` führt ohne technischen Blocker zu `blocked`.
3. WHY `not_evaluable` führt ohne technischen Blocker zu `needs_review`.
4. Ein fehlendes Assessment führt im Goal-basierten Modus ohne technischen Blocker zu `needs_review`.
5. WHY `aligned` führt nur ohne technischen Blocker zu `approved`.

`git_dirty` und seine bestehende technische Reason bleiben unverändert wirksam. Ein gültiges WHY-Ergebnis bleibt auch bei technischer Blockierung separat sichtbar.

## Ergebnisstruktur

Der Legacy-Modus liefert weiterhin ausschließlich `goal`, `status`, `next_action` und `reasons`.

Der Goal-basierte Modus behält diese Felder und ergänzt:

- `technical_reasons`: ausschließlich technische Blockierungsgründe
- `why_status`: verwendeter WHY-Status oder `None`, wenn kein Assessment vorliegt
- `why_reason`: verwendeter WHY-Reason-Code oder `None`, wenn kein Assessment vorliegt

`reasons` bleibt aus Kompatibilitätsgründen die bestehende technische Reason-Liste. `next_action` bleibt bei technischer Blockierung `clean_repository`, bei Freigabe `plan` und ist bei fachlicher Blockierung oder Review `review`.

Evidence wird nicht interpretiert und erscheint nicht im Decision-Ergebnis.

## Abgrenzung

Die Decision Engine erzeugt kein Assessment, analysiert weder Goal- noch WHY-Text, interpretiert keine Evidence und errät keine Status- oder Reason-Werte. Goal, `IdentityContext` und `WhyAssessment` werden nicht verändert.

Die bestehende Orchestrator-Schnittstelle bleibt im Legacy-Modus. Eine vollständige Goal-basierte Orchestrator-Anbindung und automatische Assessment-Erzeugung sind nicht Bestandteil dieser Entscheidung.

## Konsequenzen

- Bestehende öffentliche Aufrufe bleiben kompatibel.
- Goal-basierte Entscheidungen können nicht ohne Identity-Kontext stillschweigend freigegeben werden.
- Technische und fachliche Ergebnisse bleiben gleichzeitig maschinenlesbar.
- Bindungsfehler bleiben von fachlichen Assessment-Statuswerten getrennt.
