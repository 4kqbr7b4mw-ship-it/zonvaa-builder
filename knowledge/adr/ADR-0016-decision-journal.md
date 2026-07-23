# ADR-0016 – Decision Journal

## Status

Beschlossen

## Kontext

Der Goal-CLI-Flow liefert eine vollständige, maschinenlesbare Entscheidung mit Plan und Execution-Status, persistiert sie bisher aber nicht. ZONVAA besitzt mit `knowledge/protocols` bereits die Ablage für bestätigte Laufzeitprotokolle. Eine optionale Aufzeichnung darf weder das bestehende Runtime Journal überschreiben noch eine parallele Wissensstruktur einführen.

## Entscheidung

`goal run` erhält die optionale Flagge `--record`. Ohne Flag bleibt der bestehende Flow frei von Journal-Schreibvorgängen. Mit Flag speichert ein `DecisionJournal` nach einem vollständig abgeschlossenen Application-Service-Flow genau einen JSON-Record direkt unter `knowledge/protocols`.

Jeder Record verwendet Schema-Version `1.0`, einen UTC-Zeitpunkt und einen kollisionsarmen Dateinamen nach der bestehenden Zeitstempelkonvention mit zusätzlicher Mikrosekundenauflösung. Die Datei wird im exklusiven Erstellungsmodus geschrieben; eine vorhandene Datei wird niemals überschrieben.

Der Record enthält das vollständige Goal, explizite Invocation-Daten, Identity-Quelle und -Version, optionales WhyAssessment, Decision, Plan, Execution und den aufgelösten Pfad der Eingabedatei. Der vollständige WHY-Inhalt, Umgebungsvariablen, Tokens und Zugangsdaten werden nicht gespeichert.

Die CLI erzeugt keine Zusammenfassung und keine neue fachliche Ergebnisstruktur. Sie ergänzt nur bei erfolgreicher Aufzeichnung den `record_path` in ihrer JSON-Ausgabe. Ein Schreibfehler ist ein CLI-Fehler und wird nicht als Decision-Status dargestellt. Ohne vollständiges Orchestrator-Ergebnis wird kein Record angelegt.

## Konsequenzen

- Aufzeichnung bleibt ausdrücklich optional.
- Bestehende Protocol- und Session-Dateien werden nicht verändert.
- Decision Records sind einzeln nachvollziehbar und maschinenlesbar.
- WHY-Identität bleibt über Quelle und Version referenziert, ohne ihren Inhalt zu duplizieren.
