# ADR-0022 – Power of Attorney Preparation Workflow

## Status

Beschlossen

## Kontext

ADR-0018 definiert Life Decisions als strukturierte Wissens- und
Entscheidungsunterstützung ohne Rechts-, Steuer- oder Medizinberatung.
ADR-0019 führt `LifeDecisionCase` als unveränderliches Aggregat mit
ID-basierten Referenzen ein. ADR-0021 sperrt den bestehenden Goal Application
Service durch einen validierten Mission Context.

Für den ersten realen Anwendungsfall „Vorsorgevollmacht vorbereiten und
überprüfen“ fehlt eine fachlich neutrale, ausführbare Verbindung dieser
Bausteine. Es gibt keine bestehende generische Intake-, Checklist-, Review-
oder Recommendation-Architektur, die dafür erweitert werden könnte.

## Entscheidung

Der Workflow wird im bestehenden Paket `life_decisions` implementiert und
komponiert den vorhandenen `GoalApplicationService`. Dadurch bleibt die Kette
aus Preflight, Mission Context, Goal-Entscheidung, Planung und Ausführung
verbindlich. Der vorhandene Goal-CLI-Pfad erhält eine optionale, typisierte
Life-Decisions-Eingabe; es entsteht kein zweiter Application- oder CLI-Baum.

`LifeDecisionCase` bleibt die Aggregatgrenze. Workflow-Eingaben sind
unveränderlich und referenzieren Teilnehmer, Dokumente, bestätigte Fakten,
offene Fragen, Unsicherheiten, Fachprüfungen und Review-Termine ausschließlich
über stabile IDs des Falls. Alle zehn festgelegten Regelungsbereiche müssen
genau einmal und mit explizitem Status erfasst sein. Unbekannte oder nicht
bestätigte Angaben dürfen nicht auf Fakten verweisen, sondern müssen durch
offene Fragen beziehungsweise Unsicherheiten sichtbar bleiben.
Eine unbekannte Einzel- oder Gesamtvertretung ist deshalb ein eigener Status
und benötigt eine referenzierte offene Frage. Mehrere vorhandene Vollmachten
werden als primäre und zusätzliche Dokument-IDs derselben Dokumentprüfung
zugeordnet; der Workflow liest oder vergleicht ihre Inhalte nicht.

Eine abgeschlossene Fachprüfung benötigt eine explizite Referenz auf einen
professionell bestätigten Fakt. Eine Nutzerbehauptung allein kann keinen
Prüfabschluss belegen. Der Abschluss entfernt keine offenen Unsicherheiten.
Ärztliche, notarielle oder anwaltliche Prüfbedarfe werden nicht automatisch
erzeugt; sie müssen als nutzerkontrollierte Anforderungen im Fall vorliegen.

Nach einer freigegebenen Goal-Entscheidung erzeugt der Workflow einen
unveränderlichen fachlichen `DecisionRecord` für die strukturierte
Fallübersicht. Er behauptet weder Wirksamkeit noch fachliche Prüfung. Da diese
Ausbaustufe keine neue Persistenz einführt, wird der Record gegen das Aggregat
validiert und über seine stabile ID in der Ausgabe referenziert.

Die maschinenlesbare Ausgabe enthält ausschließlich Fall-, Status- und
Referenz-IDs. Personenbezeichnungen, Dokument-Speicherverweise,
Dokumentinhalte, Faktenaussagen und Begründungstexte werden nicht ausgegeben.
Der Workflow unterstützt in dieser Ausbaustufe weder Knowledge-Artefakte noch
`--apply` oder Decision-Journal-Records.

## Grenzen

- Der Workflow leistet keine Rechtsberatung und bewertet keine individuellen
  Rechtsfolgen oder rechtliche Wirksamkeit.
- Er erzeugt und verändert keine Vorsorgevollmacht und empfiehlt keine
  Formulierung.
- `DocumentReference` enthält nur einen nutzerkontrollierten Speicherverweis;
  der Workflow liest das Dokument nicht.
- Es gibt keine Persistenz-, Netzwerk-, Cloud-, Datenbank- oder UI-Funktion.
- Organisatorische nächste Schritte sind explizite Eingaben und keine
  automatisch erzeugten fachlichen Empfehlungen.

## Konsequenzen

- Unvollständigkeit und Widersprüche bleiben als Fragen und Unsicherheiten
  nachvollziehbar.
- Fakten, Interpretation, Entscheidung und professionelle Prüfung bleiben
  getrennt.
- Der erste fachliche Workflow nutzt dieselben Preflight- und
  Ausführungsgrenzen wie bestehende Goals.
- Eine spätere Persistenz oder Dokumentanalyse benötigt eine eigene
  Architekturentscheidung.
