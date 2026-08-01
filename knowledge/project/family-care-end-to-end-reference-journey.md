# Family Care End-to-End Reference Journey v1

## Zweck und Grenzen

Dieser anonymisierte, vollständig typisierte Referenzfall validiert die
bestehenden Verträge gemeinsam über sechs kontrollierte Gesprächszüge. Er ist
ein versioniertes Validierungsartefakt und weder Produktservice noch
Nutzertextgenerator. Er interpretiert keine natürliche Sprache, aktiviert
keine Domäne oder Fachprüfung und erzeugt weder Empfehlung noch Entscheidung.

## Anonymisierte Ausgangslage

Ein älterer Elternteil kehrt nach einem Krankenhausaufenthalt grundsätzlich in
das eigene Haus zurück. Mehrere erwachsene Angehörige sind beteiligt. Der
konkrete Unterstützungsbedarf, Rollen, Vertretungsgrundlage, medizinische
Nachsorge, dauerhafte Wohneignung und zusätzliche Kosten sind zunächst offen.
Eine mögliche kognitive Einschränkung bleibt ausdrücklich Hypothese. Zwei
Angehörige beschreiben den Unterstützungsbedarf widersprüchlich. Eine
möglicherweise vorhandene Vorsorgevollmacht ist nur über eine
nutzergesteuerte Dokumentreferenz sichtbar; ihr Inhalt wird nicht analysiert.

## Kontrollierter Verlauf

| Zug | Aktive Lücke | Kontrollierte Frage | Externe typisierte Antwort | Resolution | Revision | Resultierender Punktstatus |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Unterstützungsbedarf | Welcher konkrete Unterstützungsbedarf ist ausdrücklich bekannt? | Hilfe bei Mobilität, Mahlzeiten und Medikamentenorganisation wurde ausdrücklich genannt. | `SELECT_PROPOSAL` | vorhandene `ADD_FACT`-Operation unverändert angewendet | `ANSWERED_BY_REVISION` |
| 2 | Rollenverteilung | Welche aktuelle Rollenverteilung ist ausdrücklich vereinbart? | Angehörige A koordiniert Termine, Angehörige B Einkäufe; weitere Verantwortung ist nicht festgelegt. | `SELECT_PROPOSAL` | vorhandene `ADD_FACT`-Operation unverändert angewendet | `ANSWERED_BY_REVISION` |
| 3 | Vertretungsgrundlage | Welche vertretungsberechtigte Person ist ausdrücklich bekannt? | Eine Vorsorgevollmacht ist möglicherweise vorhanden; Stand und Vertretungsberechtigung bleiben ungeklärt. | `KEEP_OPEN` | keine Revision | zurückgestellt und weiterhin offen |
| 4 | medizinische Organisation | Welche medizinische Ansprechperson ist ausdrücklich bekannt? | Die Hausarztpraxis ist ausdrücklich benannt; Nachsorgetermine sind noch nicht vollständig vereinbart. | `SELECT_PROPOSAL` | vorhandene `ADD_FACT`-Operation unverändert angewendet | `ANSWERED_BY_REVISION` |
| 5 | Wohnen und Versorgung | Welche aktuelle Wohnform ist ausdrücklich bekannt? | Das eigene Haus bleibt vorgesehen; ein möglicher Anpassungsbedarf soll extern geprüft werden. | `KEEP_OPEN` | keine Revision | zurückgestellt und weiterhin offen |
| 6 | Kosten | Welche wesentliche finanzielle Belastung ist ausdrücklich bekannt? | Laufende Wohnkosten sind bekannt; zusätzliche Pflegekosten und Finanzierung bleiben offen. | `KEEP_OPEN` | keine Revision | zurückgestellt und weiterhin offen |

Jeder Turn referenziert den vorherigen Turn. Frage und Gap, Antwort und
Nutzeraussage, Resolution und Proposal sowie ausgewählte Revision und
resultierender State bleiben jeweils eindeutig gebunden. Beantwortete Fragen
werden nicht erneut gestellt; zu jedem Zeitpunkt existiert höchstens eine
aktive Guardian-Frage. `KEEP_OPEN` wird weder als Fact noch als beantworteter
Lebenssachverhalt dargestellt.

## Abschluss

Der Endstatus lautet `CROSS_DOMAIN_REVIEW_PREPARATION_READY`, weil keine
unbearbeitete aktive wesentliche Lücke verbleibt und das Review-Paket
ausdrücklich angefordert wurde. Dies ist keine fachliche Freigabe. Die drei
offen gehaltenen Punkte bleiben im Journey-Ergebnis sichtbar.

Das Professional-Review-Paket enthält ausschließlich die explizit gebundenen
Prüfbedarfe für bestehende Dokumente, medizinische Nachsorge, Wohnen und
Finanzen. Die UI-neutrale Experience zeigt bekannte Ausgangslage, beantwortete
und offene Punkte, Hypothese, Widerspruch, Contributions, Abhängigkeiten,
organisatorische Schritte, Fachgrenzen und den Status. Sie ergänzt keine
Person, Rolle, Diagnose, Berechnung, Fachprüfung oder Handlungsempfehlung.

## Bestätigte Sicherheitsgrenzen

- keine natürliche Sprachinterpretation oder dynamische Frage,
- keine automatische Domain Contribution oder Dependency,
- keine automatische Proposal-Auswahl, Resolution oder Revision,
- keine Personenbewertung, Rollenvergabe oder Konfliktentscheidung,
- keine Diagnose, Pflegegrad-, Leistungs-, Finanzierungs- oder
  Immobilienberechnung,
- keine Rechts-, Steuer-, Finanz-, Immobilien- oder Medizinberatung,
- keine Dokumentinhaltsanalyse,
- keine State-Mutation außerhalb der ausdrücklich ausgewählten bestehenden
  Revision,
- keine automatische Professional-Review-Aktivierung,
- keine Persistenz, Netzwerk-, LLM-, Routing-, Agenten- oder
  Ausführungslogik.

## Verbleibende Risiken

Der Referenzfall beweist die technische und fachliche Konsistenz vollständig
typisierter Eingaben, nicht die Richtigkeit realer Aussagen. Semantische
Zuordnung, Proposal-Erstellung und Auswahl bleiben externe kontrollierte
Schritte. Ein `KEEP_OPEN`-Punkt kann in einem späteren ausdrücklich
übergebenen Verlauf erneut geklärt werden; dieser Referenzfall führt keine
automatische Wiederaufnahme aus.
