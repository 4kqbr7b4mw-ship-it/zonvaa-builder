# ADR-0012 – WHY Assessment Model

## Status

Beschlossen

## Kontext

ADR-0011 definiert das WHY Assessment als getrenntes, maschinenlesbares Ergebnis mit den Statuswerten `aligned`, `conflicting` und `not_evaluable`. Die Decision Engine erzeugt diese Bewertung nicht selbst; technische und fachliche Bewertung bleiben getrennt.

Noch nicht verbindlich festgelegt sind die Struktur des Assessment-Modells, seine Bindung an das konkrete `Goal` und die geladene WHY-Version, stabile Reason-Codes, gültige Status-/Reason-Kombinationen sowie das Verhalten bei veralteten oder unpassenden Assessments.

## Entscheidung

ZONVAA führt in einem folgenden Implementierungsschritt die öffentlichen Begriffe `WhyAssessment`, `WhyAssessmentStatus` und `WhyAssessmentReason` ein. Die tatsächliche Moduldatei wird anhand der dann bestehenden Paketkonvention festgelegt.

Das Modell wird als kleine, typisierte und unveränderliche Datenstruktur umgesetzt. Es transportiert eine bereits getroffene strukturierte Bewertung, erzeugt aber selbst keine Bewertung. Es interpretiert weder Zieltext noch WHY-Inhalt, verändert weder `Goal` noch `IdentityContext` und enthält weder eine Decision-Engine-Gesamtentscheidung noch technische Blocker.

Die spätere Erzeugung erfolgt durch eine getrennte Komponente oder einen expliziten menschlichen Prüfschritt. Die konkrete Erzeugungsmethode ist nicht Bestandteil dieses ADR.

## Modellstruktur

`WhyAssessment` besitzt folgende Pflichtfelder:

- `goal`: direkte Referenz auf das bestehende verbindliche `goal.models.Goal`. Ein Goal-Dictionary, eine Goal-ID als alleinige Bindung, eine Kopie oder eine Umformulierung des Goal-Inhalts sind nicht zulässig.
- `identity_version`: exakte SHA-256-Versionskennung des geladenen `IdentityContext`. Zeitstempel, Git-Commit-ID und Dateipfad sind kein Versionsersatz.
- `status`: Wert aus `WhyAssessmentStatus`.
- `reason`: Wert aus `WhyAssessmentReason`.

Optional besitzt `WhyAssessment`:

- `evidence`: unveränderliche Folge aus Textbelegen mit einer leeren Folge als Standardwert. Evidence ersetzt weder Status noch Reason-Code und wird von der Decision Engine nicht semantisch ausgewertet.

Nicht aufgenommen werden Score, Wahrscheinlichkeit, Konfidenzwert, Zeitstempel, automatisch erzeugte Zusammenfassung, freier Ersatzstatus, technische Blocker, Decision-Engine-Gesamtstatus, LLM-Modellname oder Embedding-Daten.

## Statuswerte

`WhyAssessmentStatus` besitzt in Version 1 exakt folgende stabilen String-Werte:

- `aligned`
- `conflicting`
- `not_evaluable`

Es gibt keine Aliase, keinen Defaultstatus, keinen booleschen Ersatzwert und keinen zusätzlichen Wert wie `unknown`.

## Reason-Codes

`WhyAssessmentReason` besitzt in Version 1 exakt folgende stabilen String-Werte:

- `explicit_alignment_confirmed`: Eine getrennte Bewertungsinstanz hat ausdrücklich festgestellt, dass das konkrete Goal mit der geladenen WHY-Version vereinbar ist. Der Code legt nicht fest, wie diese Feststellung erzeugt wurde.
- `explicit_conflict_confirmed`: Eine getrennte Bewertungsinstanz hat ausdrücklich festgestellt, dass das konkrete Goal der geladenen WHY-Version widerspricht. Der Code legt nicht fest, wie diese Feststellung erzeugt wurde.
- `insufficient_assessment_basis`: Für das konkrete Goal und die geladene WHY-Version liegt keine ausreichende Grundlage für eine belastbare Aussage vor. Dieser Code ist keine stillschweigende Zustimmung.

## Gültige Kombinationen

| Status | Zulässiger Reason-Code |
| --- | --- |
| `aligned` | `explicit_alignment_confirmed` |
| `conflicting` | `explicit_conflict_confirmed` |
| `not_evaluable` | `insufficient_assessment_basis` |

Alle anderen Kombinationen sind ungültig und werden bei der späteren Modellkonstruktion explizit abgelehnt. Es gibt keine automatische Korrektur, kein stilles Umschreiben und keinen Fallback auf `not_evaluable`.

## Bindung an Goal und WHY-Version

Ein `WhyAssessment` gilt ausschließlich für genau das enthaltene vollständige `Goal` und genau die angegebene `identity_version`.

- Dieselbe Goal-ID allein reicht nicht als Bindung aus.
- Nach einer Änderung des Goals darf ein vorhandenes Assessment nicht wiederverwendet werden.
- Nach einer Änderung der WHY-Version darf ein vorhandenes Assessment nicht wiederverwendet werden.
- Ein Assessment mit einem nicht passenden Goal oder einer nicht passenden Identity-Version ist nicht anwendbar.
- Ein nicht anwendbares Assessment darf für den aktuellen Kontext nicht als `aligned`, `conflicting` oder `not_evaluable` konsumiert werden.
- Ein Bindungsfehler ist ein Eingabe- oder Integritätsfehler und kein fachlicher Assessment-Status.

Die konkrete Exception und ein möglicher späterer Decision-Engine-Status für Bindungsfehler werden erst im Integrationsentscheid festgelegt.

## Validierungsregeln

Die spätere Datenstruktur erzwingt deterministisch:

1. `goal` ist eine Instanz des bestehenden `Goal`-Modells.
2. `identity_version` ist nicht leer.
3. `status` ist ein gültiger `WhyAssessmentStatus`.
4. `reason` ist ein gültiger `WhyAssessmentReason`.
5. Status und Reason entsprechen der festgelegten Kombinationstabelle.
6. `evidence` enthält ausschließlich Strings.
7. Das Modell erzeugt keine fehlenden Werte selbst.
8. Es findet keine automatische Textnormalisierung oder Evidence-Erzeugung statt.

Eine kleine deterministische Konstruktor- oder Dataclass-Validierung ist dafür zulässig.

## Abgrenzung zur Decision Engine

Die Decision Engine wird in einem späteren Schritt:

- ein bereits bestehendes `WhyAssessment` konsumieren,
- die Goal-Bindung prüfen,
- die Identity-Version prüfen,
- technische Blocker getrennt behandeln,
- die Prioritätsregeln aus ADR-0011 anwenden.

Die Decision Engine wird nicht:

- Goal oder WHY semantisch analysieren,
- Evidence interpretieren,
- Status oder Reason erraten,
- ein fehlendes Assessment automatisch als `aligned` behandeln,
- ein unpassendes Assessment automatisch umschreiben.

Dieser ADR ändert die Decision Engine noch nicht.

## Rückwärtskompatibilität

- Bestehende Goal-, `GoalContext`-, Identity- und Decision-Modelle bleiben zunächst unverändert.
- Das Assessment-Modell wird erst im folgenden Implementierungsschritt ergänzt.
- Das Verhalten der Decision Engine ohne `GoalContext` bleibt gemäß ADR-0011 unverändert.
- Das Verhalten mit `GoalContext`, aber ohne `WhyAssessment`, wird erst bei der späteren Integration verbindlich geregelt.
- Dieser ADR ändert keine bestehende Schnittstelle.

## Reihenfolge der nächsten Implementierungsschritte

1. `WhyAssessmentStatus`, `WhyAssessmentReason` und `WhyAssessment` implementieren.
2. Fokussierte Modelltests ergänzen.
3. Noch keine Assessment-Erzeugung implementieren.
4. Anschließend einen separaten Integrationsvertrag für `GoalContext`, `IdentityContext` und `WhyAssessment` prüfen.
5. Erst danach die Decision Engine deterministisch erweitern.
6. Danach Orchestrator- und Integrationstests ergänzen.

## Nicht Bestandteil dieses ADR

- semantische WHY-Bewertung
- Schlüsselwortregeln
- Textähnlichkeit
- LLM-Aufrufe
- Embeddings
- automatische Assessment-Erzeugung
- menschliche Prüfoberflächen
- Persistenz des Assessments
- Datenbankmodell
- API-Transportformat
- Decision-Engine-Implementierung
- neue Gesamtstatuswerte
- Änderungen am Goal-Modell
- Änderungen am Identity Loader

## Konsequenzen

- Ein Assessment ist eindeutig an Goal und WHY-Version gebunden.
- Status und Reason sind stabil, maschinenlesbar und widerspruchsfrei validierbar.
- Fehlende oder unpassende Assessments können nicht als fachliche Zustimmung behandelt werden.
- Bewertungsentstehung, Assessment-Daten und Decision-Engine-Gesamtentscheidung bleiben getrennte Verantwortlichkeiten.
- Produktionslogik und bestehende Schnittstellen bleiben durch diesen ADR unverändert.
