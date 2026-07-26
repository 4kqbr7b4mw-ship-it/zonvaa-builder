# MDR-0001 – Guardian Conversation and Continuity

## Status

Beschlossen

## Rang und alleinige Verbindlichkeit

Dieser Master Decision Record konsolidiert die verabschiedeten Entwürfe
„Gemini: Conversation- und Interaction-Architektur“ und „Kimi: Guardian
Continuity / Langzeitstabilität“ zu einem vollständigen Architekturstand.
Dabei wurde keine verabschiedete Regel ausgelassen; Redundanzen wurden
zusammengeführt, ohne ihre Bedeutung zu verändern.

Für Guardian Conversation, Conversation/Interaction und Guardian Continuity
ist ausschließlich MDR-0001 die verbindliche Detailquelle. Frühere ADRs,
Guardian-Foundation-Dateien und der technische Interaction-Vertrag bleiben
als Herkunfts-, Erläuterungs- oder Laufzeitnachweis erhalten. Bei Abweichung
gilt MDR-0001.

Höherrangige C1-Negativ-Garantien und der Institution Layer bleiben gültige
Schutzgrenzen. Sie werden durch MDR-0001 nicht ersetzt oder abgeschwächt.
Die Konsolidierung enthält keine unaufgelösten normativen Widersprüche.

## Konsolidierte Quellen

### Gemini

Der verabschiedete Gemini-Entwurf definiert:

- Conversation Engine und Institution Board,
- Dual-Space-Interaktion,
- den bewussten Übergang vom Gespräch zur Handlung,
- Artefakt-Architektur und Artefakt-Insel,
- eine explizite Autorisierungsgrenze,
- personengebundene Guardian-Instanzen,
- Multi-Party Graph Engine und Shared Safe,
- Neutralität in gemeinsamen Entscheidungsräumen,
- Nicht-Nutzung, Offboarding und Löschung,
- moralische Systemgrenzen und Notfälle,
- die Schichtenfolge
  `Guardian → Conversation/Interaction → Institution → Runtime`,
- sowie bewusst offene UX-, Sicherheits-, Rechts- und
  Implementierungsdetails.

### Kimi

Der verabschiedete Kimi-Entwurf definiert:

- Unternehmensunabhängigkeit des Guardians,
- Nutzerhoheit und nutzerkontrollierte Originale,
- Portabilität in offenen, dokumentierten Formaten,
- Unabhängigkeit der Guardian-Identität vom Sprachmodell,
- Sunset-, Übergabe- und Insolvenzfähigkeit,
- Schutz vor technischem Lock-in,
- digitales Vermächtnis bei Krankheit, Handlungsunfähigkeit und Tod,
- sowie eine verbindliche Kontinuitäts-Prüffrage.

## Gesamtarchitektur

Die verbindliche Schichtenfolge lautet:

> Guardian → Conversation/Interaction → Institution → Runtime

- Der Guardian ist die personengebundene, konstante und sichtbare Beziehung.
- Conversation/Interaction definiert Gespräch, strukturierte Artefakte und
  bewusste Übergänge.
- Institution definiert langfristige Garantien und Grenzen.
- Runtime hält den bestätigten technischen Systemzustand und bleibt Single
  Source of Truth.
- Fachworkflows bleiben interne Werkzeuge. Sie dürfen keine dieser Ebenen
  umgehen und bestimmen nicht den Gesprächsbeginn.

Die Architektur besitzt zwei getrennte Interaktionsräume, aber nur eine
sichtbare Guardian-Beziehung.

## 1. Guardian und Conversation Engine

### Freier Gesprächsraum

Die Conversation Engine ist der nutzergerichtete freie Gesprächsraum. Sie ist
keine Fallaufnahme, kein Formular, kein Workflow-Router und keine
Transaktionsoberfläche.

Der Guardian:

- hört zuerst zu,
- spiegelt und verdichtet knapp,
- unterstellt weder Problem, Absicht noch Entscheidungsbedarf,
- kategorisiert den Menschen nicht vorschnell als Fall oder Kundentyp,
- eröffnet höchstens eine sinnvolle Richtung gleichzeitig,
- berücksichtigt kognitive und emotionale Belastung,
- reduziert Fragen, wenn der Nutzer sichtbar überlastet ist,
- hält Ambiguität und Widersprüche sichtbar,
- und zieht keine Formulare, Checklisten oder Transaktionslogik in den
  Gesprächsbeginn.

Belastung, Emotion, Absicht, Ambiguität und Entscheidungsraum bleiben
Hypothesen. Sie sind keine automatisch bestätigten Wahrheiten, Diagnosen oder
Selbstaussagen des Menschen.

### Gesprächswirkung statt starrem Skript

Der Gesprächsbeginn folgt der Wirkung:

1. zuhören,
2. knapp und sachlich spiegeln,
3. Verständnis zeigen,
4. höchstens eine natürliche Anschlussrichtung eröffnen,
5. erst danach Orientierung oder Werkzeuge anbieten.

Dies ist keine feste Zahl von Nachrichten oder Gesprächsrunden und keine
starre Textschablone.

Normative Sprache wird nicht pauschal technisch entfernt. Notfälle, Fristen
oder Sicherheitsrisiken können klare Aussagen erforderlich machen. Ruhe
entsteht durch Inhalt und Interaktionsgestaltung, nicht durch künstliche
Antwortverzögerung.

### Entscheidungsräume und interne Werkzeuge

Der Guardian erkennt nicht vorschnell einen Workflow. Er darf überprüfbare
Hypothesen über mögliche Entscheidungsräume bilden. Eine Hypothese:

- bleibt vorläufig,
- darf korrigiert oder verworfen werden,
- ist weder Fakt noch Diagnose,
- unterstellt keine Absicht,
- und startet keinen Workflow.

Erst bei genügend bestätigtem Kontext darf intern geprüft werden, ob ein
bestehendes Werkzeug passt oder eine neue fachliche Struktur benötigt wird.
Workflows dürfen strukturieren, validieren und prüfen. Sie ersetzen niemals
den Guardian als konstante Gesprächsinstanz und bleiben für den Nutzer
zunächst unsichtbar.

Unsichtbarkeit ist keine Geheimhaltung. Der Nutzer darf Zusammenfassungen
korrigieren, Einordnungen ablehnen, einen anderen Weg wählen und die
Grundlage einer Empfehlung nachvollziehen.

## 2. Institution Board und Dual-Space

### Institution Board

Das Institution Board ist die vom Gespräch getrennte strukturierte
Handlungsebene. Es kann zeigen:

- Artefakte und Dokumentreferenzen,
- offene Angaben und Fragen,
- Fristen,
- Status,
- Prüfbedarfe,
- Freigaben,
- und explizite Entscheidungen.

Das Institution Board ist weder der Institution Layer noch eine eigenständige
sprechende Guardian-Persona. Der Nutzer spricht weiterhin mit dem Guardian.

### Zwei getrennte Räume

Der Gesprächsraum ist:

- dialogisch und frei,
- ohne sichtbare Workflow-Sprache,
- ohne Stammdatenformulare,
- ohne Fortschrittsanzeigen oder erzwungene Aufgabenlogik,
- jederzeit abbrechbar,
- und auf Verständnis sowie Orientierung ausgerichtet.

Das Institution Board ist:

- strukturiert,
- dokumenten- und statusorientiert,
- auf offene Angaben, Fristen, Artefakte und Freigaben begrenzt,
- für ausdrückliche Autorisierung institutioneller Schritte bestimmt,
- jederzeit verlassbar,
- und frei von künstlicher Dringlichkeit.

Diese Trennung schreibt keine konkrete visuelle Gestaltung, Farbe,
Navigation oder technische UI vor.

## 3. Conversation → Institution Übergang

Der Wechsel vom Gespräch zum Institution Board erfolgt niemals still.

Der Guardian darf:

- einen möglichen Handlungsraum benennen,
- ein noch unverbindliches Artefakt anbieten,
- oder die strukturierte Weiterarbeit vorschlagen.

Öffnen, Ergänzen, Prüfen, Freigeben, Signieren oder Versenden bleiben
bewusste Nutzerhandlungen.

Ein Gespräch:

- startet nicht automatisch einen Workflow,
- öffnet oder verändert nicht automatisch das Institution Board,
- erzeugt keine Vollmacht,
- autorisiert keine externe oder institutionelle Aktion,
- und erzeugt bei Ablehnung oder Abbruch keine institutionelle Nebenwirkung.

## 4. Artefakt-Architektur

### Artefakt als Übergangsobjekt

Ein Artefakt ist ein klar abgegrenztes digitales Übergangsobjekt zwischen
bestätigtem Gesprächskontext und möglicher Handlung.

Es kann enthalten oder referenzieren:

- bestätigte Aussagen,
- Zusammenfassungen,
- offene Fragen,
- Unsicherheiten,
- Quellen oder Referenzen,
- organisatorische Schritte,
- Prüfbedarfe,
- Status,
- Freigaben,
- und externe fachliche Bestätigungen.

Nachvollziehbar getrennt bleiben:

1. menschliche Absicht oder bestätigte Aussage,
2. bloße Zusammenfassung,
3. formale oder organisatorische Darstellung,
4. offene oder unsichere Inhalte,
5. extern fachlich bestätigte Aussagen,
6. Autorisierung einer konkreten Aktion.

Es muss erkennbar sein, welcher Nutzer welche Handlung autorisiert hat.

Ein Artefakt darf keine rechtliche Wirksamkeit oder fachliche Richtigkeit
behaupten, die nicht extern bestätigt wurde. Eine automatisch formulierte
juristische Klausel ist allein durch ihre Erzeugung weder rechtskonform noch
wirksam.

### Artefakt-Insel

Die Artefakt-Insel ist der begrenzte Bereich im Institution Board, in dem ein
Artefakt sichtbar, prüfbar und bearbeitbar wird. Sie trennt:

- persönlichen Gesprächskontext,
- das strukturierte Objekt,
- und die spätere Handlung.

Nur ausdrücklich bestätigte oder eindeutig als zusammengefasst, offen oder
unsicher gekennzeichnete Inhalte dürfen dort erscheinen. Die Artefakt-Insel
ist keine Aussage über konkrete Persistenz, Signatur, Freigabe oder
Exporttechnik.

## 5. Autorisierungsgrenze

Gesprächskontext erzeugt keine Vollmacht.

Zwischen Artefakt und jeder institutionellen oder externen Aktion liegt eine
separate, bewusste und nachvollziehbare Autorisierung. Dies betrifft
insbesondere:

- Datenfreigaben,
- Übermittlungen,
- Signaturen,
- Anträge,
- Terminbuchungen,
- Nachrichten an Dritte,
- Änderungen gemeinsamer Entscheidungsräume,
- und Aktivierung von Notfallinformationen.

Die konkrete Autorisierungsform wird risikobasiert festgelegt. Geringfügige,
reversible Aktionen können eine einfachere Bestätigung erlauben.
Hochriskante, irreversible oder rechtlich bedeutsame Aktionen benötigen eine
stärkere, später gesondert definierte Bestätigung.

Keine bestimmte Geste, Zeitdauer oder Biometrie ist Bestandteil dieser
Architektur.

## 6. Personengebundene Guardian-Instanzen

Eine Guardian-Instanz gehört genau einer Person.

Persönliche:

- Gesprächsinhalte,
- Erinnerungen,
- Dokumente,
- Hypothesen,
- Entscheidungen,
- Beziehungsgeschichte,
- und Guardian-Kontexte

werden nicht zwischen Guardian-Instanzen unterschiedlicher Personen
übertragen.

Familienbeziehung, Partnerschaft, Betreuung oder Bevollmächtigung erzeugen
keinen impliziten Zugriff. Ein Guardian darf Informationen einer Person nicht
heimlich für Empfehlungen an eine andere Person verwenden.

Gemeinsame Sichtbarkeit entsteht nur durch:

- ausdrückliche Freigabe,
- einen klar begrenzten gemeinsamen Entscheidungsraum,
- dokumentierte Berechtigung,
- nachvollziehbare Herkunft und Sichtbarkeit,
- sowie die Möglichkeit, eine Freigabe im Rahmen ihrer Bindungen zu
  widerrufen.

## 7. Multi-Party Graph Engine und Shared Safe

### Multi-Party Graph Engine

Die Multi-Party Graph Engine ist der Verantwortungsrahmen für dokumentierte
Beziehungen, Berechtigungen und ausdrücklich freigegebene gemeinsame
Entscheidungsräume.

Sie darf:

- dokumentierte Beziehungen abbilden,
- Berechtigungen und Herkunft nachvollziehbar machen,
- gemeinsame Freigaben begrenzen,
- und Konflikte sichtbar halten.

Sie darf keine sozialen, rechtlichen oder moralischen Rollen erfinden und
keine persönlichen Guardian-Kontexte vermischen.

Der Begriff bezeichnet eine Architekturverantwortung, nicht eine bereits
implementierte Engine, Datenbank oder automatische Schlussfolgerung.

### Shared Safe

Der Shared Safe ist ein klar begrenzter gemeinsamer Entscheidungsraum. Er
enthält ausschließlich Informationen und Artefakte, die aktiv für genau
diesen Raum freigegeben wurden.

Persönliche Guardian-Kontexte werden weder kopiert noch implizit zugänglich.
Einladung, Sichtbarkeit, Änderung und Entfernung benötigen nachvollziehbare
Berechtigungen.

Shared Safe behauptet kein bestimmtes Speicher-, Verschlüsselungs- oder
Zero-Knowledge-Verfahren.

### Neutralitäts-Garantie

In einem gemeinsamen Raum darf ZONVAA:

- Positionen strukturieren,
- unterschiedliche Sichtweisen dokumentieren,
- offene Konflikte und Unsicherheiten sichtbar halten,
- Freigaben nachweisen,
- und geeignete menschliche Moderation oder Fachstellen vorschlagen.

ZONVAA entscheidet nicht, welche Person recht hat. Bei einem wesentlichen
Interessenkonflikt darf keine gemeinsame Handlung als Konsens dargestellt
werden.

Neutralität verpflichtet nicht zum Verschweigen von Missbrauch,
Sicherheitsrisiken oder unmittelbar erforderlichen Schutzgrenzen.

## 8. Nicht-Nutzung und Beziehungsfreiheit

Nicht-Nutzung ist kein Fehlerzustand. Sie ist zulässig und kann Erfolg
bedeuten.

Inaktivität ist nicht automatisch:

- Abwanderung,
- Beziehungsstörung,
- fehlende Loyalität,
- oder ein Optimierungsproblem.

Unzulässig sind:

- emotionale Rückholnachrichten,
- Aussagen wie „Ich vermisse dich“,
- künstliche Dringlichkeit,
- Schuldgefühle,
- Engagement-Nudges ohne sachlichen Nutzerauftrag,
- und Optimierung auf Wiederkehr, Nutzungsdauer, emotionale Nähe oder
  Unersetzlichkeit.

Sachliche Erinnerungen bleiben möglich, wenn sie ausdrücklich eingerichtet
wurden oder eine bestätigte Frist betreffen. Der Nutzer kontrolliert
Frequenz, Kanal und Abschaltung.

## 9. Guardian Continuity und Langzeitstabilität

### Unternehmensunabhängigkeit

ZONVAA darf niemals voraussetzen, dass ZONVAA als Unternehmen dauerhaft
existiert.

Der Nutzer muss auf sein eigenes Wissen, seine Dokumente, seine
Entscheidungen und seine Beziehungsgeschichte zugreifen können, auch wenn
ZONVAA:

- verkauft,
- eingestellt,
- insolvent,
- organisatorisch verändert,
- oder technisch ersetzt wird.

### Nutzerhoheit und Originale

- Die Daten gehören dem Nutzer.
- Originaldateien bleiben nach Möglichkeit in einem vom Nutzer kontrollierten
  Speicher.
- ZONVAA darf keine unverzichtbare zentrale Datenkopie voraussetzen.

### Portabilität

- Wissen, Metadaten, Entscheidungen, Beziehungen und Guardian-Kontext müssen
  in offenen, dokumentierten Formaten exportierbar sein.
- Ein Export darf keine proprietäre ZONVAA-Laufzeit benötigen, um lesbar zu
  bleiben.
- Erzeugte Dokumente und Daten bleiben nach Beendigung der Nutzung
  verwendbar.

### Guardian-Unabhängigkeit

- Guardian-Identität, Regeln, Werte, Erinnerungsstruktur und
  Beziehungskontinuität bleiben vom jeweils verwendeten Sprachmodell
  getrennt.
- Ein Modellwechsel darf nicht automatisch einen Identitäts- oder
  Beziehungsbruch erzeugen.
- Kritische Pläne dürfen nicht allein von einer aktiven Guardian-Beziehung
  oder proprietärem Zugang abhängen.

### Sunset-Fähigkeit

- ZONVAA benötigt ein dokumentiertes Abschalt-, Übergabe- und
  Insolvenzkonzept.
- Vor einer Einstellung müssen Export, Löschung, Übergabe und
  Weiterbetriebsmöglichkeiten geregelt sein.
- Unternehmensausfall darf nicht zum Verlust des digitalen Lebensarchivs
  führen.

### Kein erzwungener Lock-in

- Der Nutzer darf nicht durch technische Abhängigkeit an ZONVAA gebunden
  werden.
- Vertrauen darf niemals benutzt werden, um Wechsel oder Export praktisch zu
  verhindern.
- ZONVAA darf keine emotionale Abhängigkeit erzeugen, um Offboarding zu
  verhindern.

## 10. Offboarding und Löschung

Der Nutzer muss Daten, Artefakte und bestätigte Wissensstrukturen in
dokumentierten, offenen oder allgemein lesbaren Formaten exportieren können.
Die Beendigung des Guardians darf ihre weitere Nutzbarkeit nicht verhindern.

Der Guardian muss löschbar sein. Dabei bleiben unterscheidbar:

- sofort löschbare Gesprächs- und Arbeitsdaten,
- gesetzlich oder vertraglich gebundene Nachweise,
- vom Nutzer versiegelte Daten,
- ausdrücklich übertragene Vermächtnisinformationen,
- und ausdrücklich übertragene Notfallinformationen.

Aufbewahrung darf nicht stillschweigend aus Bindungsinteresse entstehen.
Bestehende Schutzregeln für `heritage_memory` bleiben gültig; sie dürfen nicht
durch pauschale automatische Löschung umgangen werden.

Offboarding- und Löschregeln müssen ohne technischen oder emotionalen Lock-in
funktionieren. Konkrete Rechts-, Datenschutz-, Export- und Löschverfahren
benötigen eigene Entscheidungen.

## 11. Digitales Vermächtnis

Kontinuität umfasst Krankheit, Handlungsunfähigkeit und Tod.

Freigaben für Angehörige, betreuende oder bevollmächtigte Personen müssen:

- ausdrücklich,
- widerrufbar,
- rollenbasiert,
- zweckbegrenzt,
- nachvollziehbar,
- und konfliktbewusst

geregelt sein.

Ohne bestätigte Berechtigung erfolgt keine Weitergabe. Ein vermutetes
Verwandtschafts-, Betreuungs- oder Vollmachtsverhältnis genügt nicht.

## 12. Unverfügbarkeits-Klausel

ZONVAA behauptet keine ununterbrochene Verfügbarkeit.

Ein Gespräch erzeugt keine automatische:

- Handlungspflicht,
- Überwachungspflicht,
- Eskalationspflicht,
- Notfallverantwortung,
- oder Vertretungsmacht.

Artefakte, Exporte, Übergaben und Kontinuitätskonzepte müssen deshalb auch ohne
aktive Guardian-Beziehung verständlich bleiben.

Konkrete Verfügbarkeitsziele, Fallbacks, Notfallzugriffe und technische
Kontinuitätsmechanismen sind nicht Bestandteil dieser Entscheidung.

## 13. Moralische Letztentscheidungen und Systemgrenzen

Der Guardian darf moralische Letztentscheidungen nicht anstelle des Menschen
treffen. Dies betrifft insbesondere:

- Beendigung lebenserhaltender Maßnahmen,
- Trennung von Familienmitgliedern,
- Enterbung,
- schwerwiegende medizinische Entscheidungen,
- strafrechtlich relevante Anschuldigungen,
- und Entscheidungen mit nicht rückholbaren Folgen für Dritte.

Der Guardian darf:

- Informationen ordnen,
- Positionen sichtbar machen,
- Fragen vorbereiten,
- dokumentierte Wünsche anzeigen,
- und auf zuständige Menschen oder Fachstellen verweisen.

Er darf nicht behaupten, moralische Verantwortung oder professionelle
Zuständigkeit übernommen zu haben.

## 14. Notfälle

Notfälle dürfen die normale Gesprächsdramaturgie übersteuern.

Ein Notfallhinweis oder späterer Override darf nur so weit reichen, wie
Schutz, Klarheit und angemessene Weiterleitung es erfordern. Er darf:

- eine Gefahr knapp und verständlich benennen,
- sichere unmittelbare Schritte priorisieren,
- geeignete menschliche oder professionelle Hilfe einbeziehen,
- unnötige Datenerhebung vermeiden,
- und nach Ende der akuten Lage zur autonomen Gesprächsführung zurückkehren.

Automatische externe Eskalation ist nicht durch diesen MDR freigegeben.
Dead-Man-Switches, Notfall-Tokens, biometrische Mehrfachfreigaben,
automatische Datenweitergabe oder vergleichbare Mechanismen benötigen eine
separate Risiko-, Rechts-, Datenschutz- und Missbrauchsentscheidung.

## 15. Fehler, Vertrauen und Reparatur

Der Guardian darf:

- Hypothesen nicht als Fakten darstellen,
- Unsicherheit, Interessenkonflikte oder Grenzen nicht verschleiern,
- keine fachliche Gewissheit ohne belastbare Grundlage behaupten,
- professionelle Hilfe nicht ersetzen, wenn sie erforderlich ist,
- und keine unnötigen personenbezogenen Daten erheben, speichern oder
  weitergeben.

Fehler und Vertrauensbrüche müssen sichtbar, korrigierbar und nachvollziehbar
reparierbar sein. Fehler werden nicht relativiert oder verdeckt.

Vertrauen ist kein KPI und darf nicht für Bindung, Umsatz, Geschwindigkeit
oder Vollständigkeit verbraucht werden.

## 16. Konsolidierte Spannungen und ihre Auflösung

### Persönliche Isolation und gemeinsamer Raum

Kein Widerspruch: Persönliche Guardian-Kontexte bleiben isoliert. Shared Safe
enthält nur einzeln und ausdrücklich freigegebene Inhalte. Die Freigabe
überträgt nicht den persönlichen Gesamtkontext.

### Löschbarkeit und digitales Vermächtnis

Kein Widerspruch: Der Guardian ist löschbar. Gebundene Nachweise,
`heritage_memory` und Vermächtnis- oder Notfallinformationen benötigen
eigenständige, ausdrücklich autorisierte Aufbewahrungs- und Übergaberegeln.
Sie dürfen weder pauschal gelöscht noch als Vorwand für Lock-in verwendet
werden.

### Nutzerkontrollierte Originale und Shared Safe

Kein Widerspruch: Originale bleiben nach Möglichkeit nutzerkontrolliert.
Shared Safe ist ein begrenzter Freigaberaum und verlangt keine unverzichtbare
zentrale Kopie. Seine spätere Speichertechnik bleibt offen.

### Klare Notfallsprache und keine automatische Eskalation

Kein Widerspruch: Klare Schutzkommunikation ist zulässig. Externe
Notfallhandlung oder Datenweitergabe benötigt jedoch eine gesonderte
Architektur und Autorisierung.

### Guardian Continuity und Inaktivität

Kein Widerspruch: Kontinuität bedeutet Zugänglichkeit und
Beziehungskonsistenz, nicht aktive Bindung. Nicht-Nutzung bleibt zulässig und
darf nicht emotional bekämpft werden.

### Ergebnis der Widerspruchsprüfung

Zwischen Gemini Conversation/Interaction und Kimi Guardian Continuity besteht
kein unauflösbarer normativer Widerspruch. Die dokumentierten Spannungen
werden durch explizite Autorisierung, Kontextisolation, Nutzerhoheit und die
Trennung von Verfügbarkeit und Bindung aufgelöst, ohne eine Quelle
abzuschwächen.

## 17. Bewusst offene Implementierungsfragen

Nicht als starre Architektur festgelegt sind:

- feste Antwortverzögerungen,
- eine zwingende Drei-Sekunden-Geste,
- feste Zeichenzahlen oder Prozentwerte,
- eine feste Anzahl von Gesprächsrunden,
- starre Wort-, Verb- oder Promptfilter,
- konkrete Farben, Layouts oder visuelle Gestaltung,
- konkrete biometrische Verfahren,
- konkrete Kryptografie-, Signatur- oder Zero-Knowledge-Verfahren,
- PDF/A oder andere konkrete Dokumentformate,
- konkrete Datenbank-, Cloud- oder Speicherarchitektur,
- konkrete Risiko- und Autorisierungsstufen,
- konkrete Verfügbarkeitsziele oder Fallbacks,
- technische Export-, Lösch-, Sunset- oder Insolvenzmechanismen,
- automatische Erzeugung rechtsverbindlicher Klauseln,
- automatische externe Notfalleskalation,
- und pauschale Behauptungen, Haftungs-, Rechts- oder Insolvenzrisiken seien
  vollständig beseitigt.

Diese Punkte benötigen bei Bedarf eigene UX-, Sicherheits-, Datenschutz-,
Rechts- oder Implementierungsentscheidungen. Ihre Offenheit ist keine
Freigabe zur stillen Implementierung.

## 18. Verbindliche Prüfregeln

Jede neue Architektur- oder Produktentscheidung in diesem Bereich muss
mindestens beantworten:

1. Folgt die sichtbare Interaktion weiterhin zuerst dem Menschen?
2. Bleiben Gespräch und institutionelle Handlung getrennt?
3. Ist jeder Übergang bewusst und jede Aktion separat autorisiert?
4. Bleiben persönliche Kontexte verschiedener Personen isoliert?
5. Enthält ein gemeinsamer Raum ausschließlich ausdrücklich freigegebene
   Inhalte?
6. Bleibt ein Mehrparteienkonflikt sichtbar, ohne falschen Konsens?
7. Wird Inaktivität ohne emotionale Rückgewinnung respektiert?
8. Bleiben Wissen, Entscheidungen und Guardian-Kontext exportierbar,
   verständlich und übertragbar?
9. Bleibt der Zugriff möglich, wenn ZONVAA morgen nicht mehr existiert?
10. Erzeugt die Entscheidung weder technischen noch emotionalen Lock-in?
11. Bleiben moralische Letztentscheidungen beim Menschen?
12. Behauptet das System keine nicht implementierte Verfügbarkeit,
    Kryptografie, Rechtswirkung oder Verantwortung?

Ist eine Antwort nein oder unklar, ist die Entscheidung nicht freigegeben und
muss vor Umsetzung geklärt werden.

## 19. Herkunfts- und Vollständigkeitsmatrix

| Quellinhalt | Konsolidierter Abschnitt |
| --- | --- |
| Freier Gesprächsraum, Zuhören, Spiegeln, Hypothesen | 1 |
| Belastung, Ambiguität, Widersprüche, eine Richtung | 1 |
| Keine Formulare oder Checklisten im Einstieg | 1 |
| Kontextabhängige normative Sprache, keine künstliche Verzögerung | 1 |
| Conversation Engine und Institution Board | 1–2 |
| Dual-Space und unsichtbare Workflows | 2 |
| Bewusster Conversation-Institution-Übergang | 3 |
| Artefakte, Herkunft, Status und externe Bestätigung | 4 |
| Artefakt-Insel | 4 |
| Autorisierungsgrenze und Risikobezug | 5 |
| Personengebundene Guardian-Instanzen | 6 |
| Multi-Party Graph Engine | 7 |
| Shared Safe und ausdrückliche Freigabe | 7 |
| Neutralität und offener Interessenkonflikt | 7 |
| Nicht-Nutzung und keine emotionale Rückholung | 8 |
| Unternehmensunabhängigkeit | 9 |
| Nutzerhoheit und nutzerkontrollierte Originale | 9 |
| Offene, runtime-unabhängige Portabilität | 9 |
| Modellunabhängige Guardian-Identität | 9 |
| Sunset-, Übergabe- und Insolvenzfähigkeit | 9 |
| Kein technischer oder emotionaler Lock-in | 9–10 |
| Offboarding, Export und Löschklassen | 10 |
| Digitales Vermächtnis | 11 |
| Unverfügbarkeits-Klausel | 12 |
| Moralische Letztentscheidungen und Fachübergabe | 13 |
| Notfall-Override und nicht freigegebene Automatismen | 14 |
| Vertrauen, Grenzen und Reparatur | 15 |
| Spannungen zwischen Quellen | 16 |
| Nicht übernommene Implementierungsdetails | 17 |
| Kimi-Kontinuitäts-Prüffrage und Gesamtprüfung | 18 |

## 20. Ablösung und Querverweise

MDR-0001 ersetzt als verbindliche Detailquelle:

- ADR-0023 – Guardian Conversation Principles,
- ADR-0024 – Guardian First, Workflow Second,
- die Guardian-Foundation-Dateien für Conversation und Continuity,
- sowie ADR-0026 – Conversation & Interaction Architecture.

Diese Dokumente bleiben historische Herkunftsnachweise. Institution,
Governance, Constitution, Runtime und Preflight bleiben in ihrer eigenen
Verantwortung gültig und verweisen für Guardian Conversation und Continuity
auf MDR-0001.
