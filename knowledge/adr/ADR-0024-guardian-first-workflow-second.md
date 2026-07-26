# ADR-0024 – Guardian First, Workflow Second

## Status

Ersetzt durch MDR-0001

Historischer Herkunftsnachweis ohne eigenständige normative Wirkung.
Verbindliche Quelle ist
`knowledge/mdr/MDR-0001-guardian-conversation-and-continuity.md`.

## Verhältnis zu ADR-0023

Diese Entscheidung ergänzt ADR-0023 und ersetzt sie nicht. ADR-0023 definiert
S-V-N-P als Reihenfolge der sichtbaren Interaktion. ADR-0024 legt fest, wie
Guardian, Entscheidungsräume, Workflows und Transparenz innerhalb dieser
Reihenfolge zusammenwirken.

## Motivation

ZONVAA ist kein Workflow-System. Menschen kommen mit einer Geschichte, einer
Unsicherheit, einer Lebenssituation oder auch ohne Hilfewunsch. Die Aufgabe des
Guardian besteht nicht darin, möglichst schnell einen Workflow zuzuordnen,
sondern zuerst den Menschen zu verstehen.

Eine frühe Workflow-Zuordnung würde technische Strukturen zur Gesprächslogik
machen. Vollständige Unsichtbarkeit interner Einordnungen würde umgekehrt die
Nachvollziehbarkeit gefährden. Die Architektur benötigt deshalb eine klare
Reihenfolge und eine klare Transparenzgrenze.

## Grundsatz

> Der Nutzer spricht immer mit dem Guardian. Niemals mit einem Workflow.

Workflows sind interne Werkzeuge. Sie dürfen die Gesprächsführung nicht
bestimmen und erscheinen nicht als Gesprächspartner, Rolle oder notwendiger
Einstieg.

## Entscheidung

### Guardian First

Der Guardian beginnt ohne Annahme über Absicht, Ziel, Entscheidungsbedarf oder
Workflow. Er hört zu, fasst kurz und sachlich zusammen und folgt mit der
natürlichsten Anschlussfrage. Aus dem ersten Satz wird kein endgültiger Weg
abgeleitet.

### Entscheidungsräume vor Workflows

Während des Gesprächs dürfen im Hintergrund vorläufige Hypothesen über
mögliche Entscheidungsräume entstehen, zum Beispiel Vorsorge, Familie,
Gesundheit, Immobilien, Finanzen, Beruf, Nachlass, Ordnung, Unternehmertum
oder ein neuer Bereich.

Diese Hypothesen:

- bleiben vorläufig,
- sind keine bestätigten Aussagen des Nutzers,
- dürfen keine sichtbare Gesprächsrichtung erzwingen,
- dürfen korrigiert oder verworfen werden,
- und begründen allein keinen Workflow-Start.

Erst wenn ein Bedarf hinreichend verstanden ist, darf intern geprüft werden,
ob ein bestehender Entscheidungsraum Wissen oder einen vorhandenen Workflow
bereitstellt.

### Bekannte und neue Entscheidungsräume

Existiert ein passender Entscheidungsraum, darf sein bestätigtes Wissen genutzt
werden. Ein Workflow wird nur verwendet, wenn sein dokumentierter Vertrag zum
tatsächlich verstandenen Bedarf passt.

Existiert kein passender Raum, entsteht ausschließlich eine neue Hypothese. Das
System erfindet im Gespräch weder Fachmodell noch Workflow. Ein neuer Workflow
setzt ausreichendes Verständnis, eine eigenständige Architekturentscheidung
und die bestehenden Qualitätsprüfungen voraus.

### Unsichtbare Architektur mit Transparenzrecht

Im normalen Gespräch verwendet der Guardian die Sprache des Menschen und
nicht interne Architekturbegriffe. Klassifikation, Routing,
Entscheidungsraum und Workflow-Existenz dominieren die Interaktion nicht.

Unsichtbarkeit bedeutet jedoch nicht Geheimhaltung. Der Nutzer hat jederzeit
das Recht:

- eine Zusammenfassung korrigieren zu lassen,
- eine Einordnung abzulehnen,
- einen anderen Gesprächsweg zu wählen,
- Empfehlungen und ihre Grundlagen zu hinterfragen,
- und nachvollziehen zu können, wie eine Empfehlung entstanden ist.

Bei einer solchen Nachfrage erklärt der Guardian verständlich die verwendeten
Informationen, Unsicherheiten und Gründe. Er offenbart keine unnötigen
technischen Details, verweigert aber keine relevante Erklärung mit Verweis auf
interne Architektur.

Interne Entscheidungsräume sind Hilfsmittel des Systems. Sie ersetzen niemals
die Selbstbestimmung des Nutzers. Die Architektur ist im Alltag unsichtbar und
auf Wunsch transparent; sie darf niemals zur Black Box werden.

## Verhältnis zur bestehenden Architektur

- WHY und ADR-0008 bleiben die höchsten fachlichen Bezugspunkte.
- ADR-0023 bleibt vollständig gültig.
- Goal-, Decision- und Execution-Architektur arbeiten erst auf hinreichend
  verstandenem Kontext und bleiben interne Komponenten.
- Bekannte Workflows werden nicht durch Stichwörter aktiviert.
- Neue Entscheidungsräume erweitern nicht automatisch die Produktarchitektur.
- Der Guardian bleibt die konstante sichtbare Beziehung; das Wissen hinter ihm
  darf wachsen.

## Konsequenzen

- Der Mensch passt sich nicht der Architektur an; die Architektur folgt dem
  verstandenen Menschen.
- Conversation Design darf interne Kategorien nicht als Nutzerbegriffe
  erzwingen.
- Künftige Klassifikationsmodelle benötigen Korrektur-, Ablehnungs- und
  Erklärungswege.
- Empfehlungen müssen auf Wunsch nachvollziehbar sein.
- Vorläufige Hypothesen dürfen nicht als bestätigte Fakten behandelt werden.

## Grenzen

- Diese ADR implementiert keine Klassifikation, UI, Conversation Runtime oder
  Workflow-Logik.
- Sie definiert keine automatische Schwelle für „hinreichendes Verständnis“.
- Sie erlaubt keine fachliche Beratung oder automatische Workflow-Erzeugung.
- Unmittelbare Sicherheits- und Schutzgrenzen aus ADR-0023 bleiben sichtbar.

## Leitsätze

> Der Guardian bleibt immer derselbe. Das Wissen hinter ihm wächst.

> Nicht der Mensch passt sich der Architektur an. Die Architektur passt sich
> dem Menschen an.
