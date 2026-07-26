# ADR-0028 – Architecture Integrator Agent

## Status

Beschlossen

## Kontext

Externe Modelle und interne Autoren können Architekturentwürfe liefern.
Constitution, MDR-0001, Governance, Institution, Interaction und aktuelle
ADRs bilden jedoch bereits einen priorisierten verbindlichen Stand. Ohne
einen deterministischen Vergleich können Entwürfe versehentlich historische
Regeln reaktivieren, geltende Normen überschreiben oder aus einer Empfehlung
eine scheinbar bestätigte Entscheidung machen.

## Entscheidung

ZONVAA führt einen rein beratenden Architecture Integrator ein.

> Der Integrator berät. Der Chief Architect entscheidet. Codex implementiert.

Externe Modelle liefern ausschließlich Entwürfe. Keine KI außer Codex
verändert das Repository, und Codex darf aus einem nicht bestätigten
Architekturvorschlag keinen Implementierungsauftrag erhalten.

### Autoritätsgrenze

Der Integrator darf Quellen laden, Entwürfe vergleichen, Redundanzen,
Ergänzungen, Konflikte und offene Fragen ausweisen, Integrationspunkte
vorschlagen und eine kompakte Entscheidungsvorlage erzeugen. Seine Empfehlung
ist nicht verbindlich.

Nur ein separates, validiertes `ChiefArchitectDecision` mit `ADOPT`,
`ADOPT_WITH_CHANGES`, `REJECT` oder `DEFER` autorisiert die Erzeugung eines
Codex-Auftrags. Der Integrator:

- markiert keine ADR oder MDR selbst als beschlossen,
- löst keinen Konflikt automatisch,
- implementiert keine Produktlogik,
- ändert während einer Analyse keine Architekturdatei,
- und erfindet keine fehlenden Inhalte.

### Normpriorität

Der Kontext-Lader verwendet RuntimeManager und KnowledgeManager. Er ordnet:

1. C1 Constitution,
2. verbindliche MDRs,
3. C2 Governance Charter,
4. aktuelle Institution- und Interaction-Spezifikationen,
5. aktuelle ADRs,
6. C3 Operative Rules,
7. historische oder ersetzte ADRs,
8. den letzten Handover als ergänzenden Laufzeitkontext.

Der externe Entwurf wird erst nach diesem Kontext als Eingabe bewertet und
steht damit an letzter Stelle. Er ist keine Normquelle und überschreibt keine
der geladenen Quellen. Historische ADRs werden geladen und nachgewiesen, aber
nicht als aktuelle Normen bewertet. MDR-0001 bleibt die verbindliche
Detailquelle für Guardian Conversation and Continuity.

### Deterministische Analysegrenze

Quellen werden mit stabiler ID, Repository-Pfad, Version oder Dokument-ID,
SHA-256-Hash, Normstufe, Status und Relevanz nachgewiesen.

Der Integrator zerlegt Markdown deterministisch in ausdrückliche Aussagen.
Exakte normalisierte Gleichheit gilt als Redundanz. Gleiche Proposition mit
gleicher Polarität gilt als Übereinstimmung; gleiche Proposition mit
entgegengesetzter ausdrücklicher Polarität gilt als Konflikt. Alles andere
bleibt Ergänzung oder offene Entscheidung. Diese lexikalische Grenze ist
absichtlich enger als freie semantische Interpretation und wird im Ergebnis
als Risiko ausgewiesen.

Jeder Konflikt verweist auf die bestehende Quelle und verlangt ausdrücklich
eine Chief-Architect-Entscheidung. Es gibt keine automatische
Konfliktauflösung.

### Artefakte und CLI

`architecture integrate` liest ein unveränderliches Proposal, lädt den
Runtime-Kontext und gibt exakt eine kompakte Entscheidungsvorlage sowie
maschinenlesbares JSON aus. Eine optionale Analysedatei ist ein getrenntes
Arbeitsartefakt und keine Architekturpublikation.

`architecture codex-prompt` benötigt eine persistierte Analyse und ein
separates bestätigtes Chief-Architect-Entscheidungsobjekt. Der erzeugte Prompt
enthält den vollständigen Entwurf, angenommene, geänderte, abgelehnte und
vertagte Inhalte, Quellen, Schichten, Schutzziele, Nicht-Ziele, Tests,
Doctor-, Diff-, Status-, Commit- und Handover-Anforderungen. Er benötigt
keinen Chatverlauf.

Eine Chief-Architect-Entscheidung wird nicht automatisch als MDR oder ADR
veröffentlicht. Verbindliche Integration bleibt ein separater Codex-Auftrag.

## Folgen

- Gleicher Repository-Stand und gleiche Eingabe erzeugen dasselbe
  strukturierte Analyseergebnis.
- Fehlende Pflichtquellen stoppen die Analyse klar.
- Neue Entwürfe können keine aktuelle Norm still überschreiben.
- Die Analyse ist nachvollziehbar, aber bewusst kein Ersatz für menschliches
  Architekturverständnis.
- KnowledgeManager entdeckt `knowledge/mdr` als bestehenden Knowledge-Bereich;
  RuntimeManager bleibt technische Single Source of Truth.

## Nicht-Ziele

Nicht eingeführt werden autonome Abstimmung, automatische Freigabe, externe
KI-Aufrufe, Netzwerkzugriffe, UI, semantische Modellinferenz, automatische
Repository-Änderungen, Produkt- oder Workflow-Änderungen oder ein Ersatz des
Chief Architect.
