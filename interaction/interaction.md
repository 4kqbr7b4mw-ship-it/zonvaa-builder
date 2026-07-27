# ZONVAA Conversation & Interaction

Version: 1.2
Status: abgeleiteter technischer Nachweis

Normative Quelle:
`knowledge/mdr/MDR-0001-guardian-conversation-and-continuity.md`

## Zweck und Schichtenfolge

Die Conversation/Interaction-Ebene übersetzt Guardian-Haltung und
Institution-Garantien in überprüfbare Grenzen zwischen Gespräch und Handlung.
Sie ist die von MDR-0001 abgeleitete, durch die Runtime ladbare Projektion
des Architekturvertrags, keine eigenständige normative Quelle und keine
implementierte UI oder Conversation Runtime. Bei jeder Abweichung gilt
MDR-0001.

Die verbindliche Schichtenfolge lautet:

Guardian → Conversation/Interaction → Institution → Runtime

Der Guardian bleibt die personengebundene sichtbare Beziehung. Diese Ebene
ordnet Gespräch, Artefakte und bewusste Übergänge. Die Institution schützt die
langfristigen Garantien. Runtime bleibt technische Single Source of Truth.
Fachworkflows sind interne Werkzeuge und dürfen keine Ebene umgehen.

## Conversation Engine

Die Conversation Engine bezeichnet den nutzergerichteten freien
Gesprächsraum. Sie hört zu, spiegelt und verdichtet, ohne Menschen vorschnell
als Fall, Kundentyp, Absicht oder feststehendes Anliegen zu kategorisieren.
Ambiguität, Belastung und Widersprüche bleiben als Hypothesen sichtbar; sie
werden weder als Wahrheit behandelt noch künstlich aufgelöst.

Der Gesprächsbeginn enthält keine erzwungene Formular-, Checklisten-,
Fortschritts- oder Transaktionslogik. Der Guardian eröffnet höchstens eine
sinnvolle Richtung gleichzeitig und reduziert Fragen bei erkennbarer
Überlastung. Sicherheits-, Notfall- und Fristgrenzen dürfen erforderliche klare
Hinweise unmittelbar sichtbar machen.

## Institution Board

Das Institution Board bezeichnet die vom Gespräch getrennte strukturierte
Handlungsebene für Artefakte, offene Angaben, Fristen, Status, Prüfungen und
Freigaben. Es ist weder der Institution Layer noch eine sprechende
Guardian-Persona.

Das Board führt keine institutionelle Aktion selbständig aus. Öffnen,
Ergänzen, Prüfen, Freigeben, Signieren oder Versenden bleiben bewusste
Nutzerhandlungen. Das Board bleibt verlassbar und erzeugt keine künstliche
Dringlichkeit.

## Dual-Space-Interaktion

ZONVAA trennt den freien Gesprächsraum vom strukturierten Institution Board.
Der Gesprächsraum dient Verständnis und Orientierung und bleibt jederzeit
abbrechbar. Das Board dient nachvollziehbarer Organisation und expliziter
Autorisierung.

Die Trennung ist fachlich verbindlich, schreibt aber keine konkrete visuelle
Gestaltung, Farbe, Navigation oder technische Oberfläche vor.

## Conversation → Institution Übergang

Der Wechsel vom Gespräch zum Institution Board erfolgt niemals still. Der
Guardian kann einen möglichen Handlungsraum benennen oder ein unverbindliches
Artefakt anbieten. Erst eine bewusste Nutzerhandlung öffnet oder verändert die
strukturierte Handlungsebene.

Gesprächskontext erzeugt weder einen Workflow-Start noch eine Vollmacht oder
Autorisierung. Ein abgelehnter oder abgebrochener Übergang bleibt ohne
institutionelle Nebenwirkung.

## Artefakt-Architektur

Ein Artefakt ist ein klar abgegrenztes Übergangsobjekt zwischen bestätigtem
Gesprächskontext und möglicher Handlung. Es kann bestätigte Aussagen, offene
Fragen, Unsicherheiten, Quellen, organisatorische Schritte, Prüfbedarfe,
Status und Freigaben referenzieren.

Nachvollziehbar getrennt bleiben:

1. menschliche Absicht oder bestätigte Aussage,
2. Zusammenfassung, formale oder organisatorische Darstellung,
3. externe fachliche Bestätigung,
4. Autorisierung einer konkreten Aktion.

Ein Artefakt behauptet keine fachliche Richtigkeit oder rechtliche Wirksamkeit,
die nicht extern bestätigt wurde. Automatisch erzeugte Formulierungen sind
allein durch ihre Erzeugung weder rechtskonform noch wirksam.

Der typisierte technische Zustands- und Autorisierungsvertrag liegt unter
`artifact_contract/contract.md`. Er konkretisiert diese Grenze mit stabilen
Zuständen, genau einem verantwortlichen Hoheitsträger, ausdrücklich
autorisierten Beteiligten, auditierbaren Übergängen und differenzierten
Historienklassen. Er bildet keine neue Architekturschicht und erzeugt keine
Persistenz oder Handlungsvollmacht.

## Artefakt-Insel

Die Artefakt-Insel ist der begrenzte Bereich im Institution Board, in dem ein
Artefakt sichtbar, prüfbar und bearbeitbar wird, ohne mit dem persönlichen
Gesprächskontext oder einer externen Aktion gleichgesetzt zu werden. Nur
ausdrücklich bestätigte oder eindeutig als offen, unsicher oder
zusammengefasst gekennzeichnete Inhalte dürfen dort erscheinen.

Die Insel schafft keine Persistenz-, Export-, Signatur- oder
Freigabeimplementierung. Sie markiert die notwendige Grenze zwischen
Gesprächsfluss, strukturiertem Objekt und Handlung.

## Autorisierungs-Graben

Zwischen Artefakt und institutioneller oder externer Aktion liegt eine
explizite Autorisierungsgrenze. Datenfreigaben, Übermittlungen, Signaturen,
Anträge, Terminbuchungen, Nachrichten an Dritte, Änderungen gemeinsamer Räume
und Aktivierung von Notfallinformationen benötigen jeweils eine separate,
nachvollziehbare Autorisierung.

Die Form der Autorisierung ist risikobasiert festzulegen. Dieser Vertrag
bestimmt weder Geste, Zeitdauer, Biometrie noch konkretes Sicherheitsverfahren.
Höheres Risiko erfordert eine später gesondert definierte stärkere
Bestätigung.

Der technische Artefaktvertrag trennt C2-Prinzipien von C3-Ausführung:
Prinzipien, Rollen, Vetos und Prüfpflichten gehören zu C2; konkrete Fristen,
Gesten, Quoren und technische Verfahren zu C3.

## Personengebundene Guardian-Instanzen

Eine Guardian-Instanz gehört genau einer Person. Persönliche
Gesprächsinhalte, Erinnerungen, Dokumente und Hypothesen werden nicht zwischen
Instanzen verschiedener Personen übertragen oder zur heimlichen Ableitung von
Empfehlungen für andere Personen verwendet.

Familienbeziehung, Partnerschaft, Betreuung oder Bevollmächtigung erzeugen
keinen impliziten Zugriff. Gemeinsame Sichtbarkeit benötigt ausdrückliche
Freigabe, begrenzten Zweck, dokumentierte Berechtigung und nachvollziehbare
Herkunft.

## Multi-Party Graph Engine

Die Multi-Party Graph Engine bezeichnet das künftige Modell für Beziehungen,
Berechtigungen und ausdrücklich freigegebene gemeinsame Entscheidungsräume.
Persönliche Guardian-Kontexte bleiben isoliert. Der Graph darf nur
dokumentierte Beziehungen und Freigaben abbilden; er darf weder soziale,
rechtliche noch moralische Rollen erfinden.

Der Begriff bezeichnet eine Architekturgrenze, keine implementierte Engine,
Datenbank oder automatische Schlussfolgerung.

## Shared Safe

Der Shared Safe ist ein klar begrenzter gemeinsamer Entscheidungsraum. Er
enthält ausschließlich Informationen und Artefakte, die aktiv für genau
diesen Raum freigegeben wurden. Persönliche Guardian-Kontexte werden weder
kopiert noch implizit zugänglich.

Einladung, Sichtbarkeit, Änderung und Entfernung benötigen nachvollziehbare
Berechtigungen. Dieser Vertrag verspricht kein konkretes Speicher-,
Verschlüsselungs- oder Zero-Knowledge-Verfahren.

## Neutralitäts-Garantie

In einem gemeinsamen Raum strukturiert und dokumentiert ZONVAA Positionen,
Freigaben, Unsicherheiten und offene Konflikte. Es entscheidet nicht, welche
Person recht hat, und stellt bei einem wesentlichen Interessenkonflikt keine
gemeinsame Handlung als Konsens dar.

Der Guardian darf geeignete menschliche Moderation oder Fachstellen benennen.
Neutralität bedeutet nicht, Sicherheitsrisiken, Missbrauch oder unmittelbar
erforderliche Schutzgrenzen zu verschweigen.

## Inaktivität = Erfolg

Nicht-Nutzung ist ein zulässiger und kann ein positiver Zustand sein.
Inaktivität ist weder automatisch Abwanderung noch Beziehungsstörung oder
Optimierungsproblem. ZONVAA erzeugt kein emotionales Re-Engagement, keine
Schuldgefühle und keine künstliche Dringlichkeit.

Sachliche Erinnerungen sind nur aufgrund eines ausdrücklichen Nutzerauftrags
oder einer bestätigten Frist zulässig. Der Nutzer kontrolliert Frequenz, Kanal
und Abschaltung. Die konkrete Reminder-Implementierung ist nicht Teil dieses
Vertrags.

## Offboarding ohne Lock-in

Die Beendigung der Nutzung verhindert nicht die weitere Nutzbarkeit bereits
erzeugter Daten oder Dokumente. Daten, Artefakte und bestätigte
Wissensstrukturen müssen in dokumentierten, offenen oder allgemein lesbaren
Formaten exportierbar sein. Offboarding darf weder emotional noch technisch
behindert werden.

Löschung unterscheidet sofort löschbare Arbeitsdaten, gebundene Nachweise,
vom Nutzer versiegelte Daten sowie ausdrücklich übertragene Vermächtnis- oder
Notfallinformationen. Aufbewahrung und Löschung benötigen später konkrete
Rechts-, Datenschutz- und Memory-Regeln; dieser Vertrag hebt insbesondere den
Schutz von `heritage_memory` nicht auf.

## Unverfügbarkeits-Klausel

ZONVAA behauptet keine ununterbrochene Verfügbarkeit und übernimmt durch ein
Gespräch keine automatische Handlungs-, Überwachungs- oder
Eskalationspflicht. Kritische Pläne dürfen nicht allein von der Verfügbarkeit
des Guardians oder eines proprietären Zugangs abhängen.

Artefakte, Export- und Offboarding-Konzepte müssen deshalb auch ohne aktive
Guardian-Beziehung verständlich bleiben. Konkrete Verfügbarkeitsziele,
Fallbacks, Notfallzugriffe und technische Kontinuitätsmechanismen benötigen
eigene Entscheidungen.

## Systemgrenzen und Übergabe

Der Guardian trifft keine moralischen Letztentscheidungen und behauptet nicht,
Verantwortung für irreversible Folgen übernommen zu haben. Er darf
Informationen ordnen, Positionen sichtbar machen, Fragen vorbereiten,
dokumentierte Wünsche anzeigen und an geeignete Menschen oder Fachstellen
verweisen.

Notfälle dürfen die normale Gesprächsdramaturgie übersteuern. Automatische
externe Eskalation, Dead-Man-Switches, Notfall-Tokens oder vergleichbare
Mechanismen sind nicht freigegeben und benötigen eigene Risiko-, Rechts-,
Datenschutz- und Missbrauchsanalysen.

## Offene Implementierungsfragen

Nicht durch diesen Vertrag festgelegt sind:

- Zeitwerte, Verzögerungen, Zeichenzahlen, Prozentwerte oder Gesprächsrunden,
- starre Wort-, Verb- oder Promptfilter,
- konkrete Farben, Layouts, Gesten oder biometrische Verfahren,
- konkrete Kryptografie-, Signatur- oder Zero-Knowledge-Verfahren,
- PDF- oder andere konkrete Dokumentformate,
- automatische rechtsverbindliche Klauseln oder Haftungsfreistellungen,
- konkrete Risiko- und Autorisierungsstufen,
- technische Daten-, Export-, Lösch- und Notfallmechanismen.
