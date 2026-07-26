# ADR-0020 – Codex Context and Handover

## Status

Beschlossen

## Kontext

Die zentrale Runtime lädt bereits Constitution, Knowledge-System, Verified
Facts, Project State und die neueste Session. Context Collector und Context
Analyzer verdichten diesen Bestand. Für Codex-Aufgaben fehlten jedoch ein
verbindlicher, strukturell prüfender Einstieg sowie ein lokaler,
maschinenlesbarer Staffelstab. Der bisherige Handover-Command erzeugte
Markdown über einen externen Modellaufruf und war deshalb weder rein lokal
noch deterministisch.

## Entscheidung

`python3 -m builder.main preflight` verwendet ausschließlich die bestehende
`RuntimeManager`-Instanz. Der Command validiert Constitution, die bekannten
Knowledge-Bereiche, Verified Facts, Project State und Git-Identität. Er weist
fehlende letzte Sessions oder Handovers ausdrücklich als `missing` aus und
liefert einen kompakten Mission Context als JSON. Strukturell unvollständiger
Pflichtkontext führt zu einem Exit-Code ungleich null.

`KnowledgeManager` bleibt die einzige Schnittstelle zur Knowledge-Struktur. Er
bestimmt zusätzlich den neuesten Handover und den neuesten verfügbaren Kontext
aus Session oder Handover. Historische Dateien werden nicht verändert oder
gelöscht.

Der `handover`-Command verarbeitet einen expliziten, validierten JSON-Input mit
zeitzonenbewusstem Zeitstempel und
erzeugt unter `knowledge/handovers/` aus demselben Datensatz eine
maschinenlesbare JSON- und menschenlesbare Markdown-Datei. Die Ausgabe enthält
nur Zusammenfassungen und Metadaten, kein Feld für Dokumentinhalte. Beide
Dateien werden lokal, exklusiv und atomar veröffentlicht. Der Command führt
keinen Netzwerkaufruf, Commit oder Push aus.

Root-`AGENTS.md` macht Preflight, Architekturprüfung, Tests, Handover und das
Push-Verbot für Projektaufgaben verbindlich. `PLANS.md` definiert das
fortlaufend zu pflegende Format für längere Arbeitspakete.

## Grenzen

- Der Preflight bewertet keine fachliche Richtigkeit geladener Inhalte.
- Fehlende optionale Sessions oder Handovers blockieren den Preflight nicht.
- Handover-Inhalte stammen ausschließlich aus dem expliziten Input und
  tatsächlich erfassten Laufzeitdaten; sie werden nicht semantisch ergänzt.
- Der Handover erzeugt keinen Commit und kann daher einen Abschlusscommit nur
  angeben, wenn dieser beim Erzeugen bereits existiert.
- Keine Cloud-, Netzwerk-, Datenbank- oder UI-Funktion wird eingeführt.

## Konsequenzen

- Neue Sitzungen erhalten einen reproduzierbaren lokalen Einstiegspunkt.
- Unvollständiger Pflichtkontext scheitert früh und maschinenlesbar.
- Nachfolgende Sitzungen benötigen keinen vorherigen Chat.
- Der frühere modellbasierte Handover-Pfad wird durch den lokalen,
  deterministischen Vertrag ersetzt; die bestehende Knowledge-Ablage bleibt
  erhalten.
