# Life Decisions

## Zweck

Life Decisions ist ein ZONVAA-Baustein für bedeutende persönliche Vorsorge- und Lebensentscheidungen. Er hilft Menschen, komplexe Themen verständlich zu strukturieren, fehlende Angaben und Widersprüche zu erkennen, Gründe nachvollziehbar festzuhalten und Gespräche mit qualifizierten Fachleuten vorzubereiten.

## Themenbereiche

- Testament und Nachlass
- Vorsorgevollmacht
- Patientenverfügung
- Betreuungsverfügung
- Notfallzuständigkeiten
- Familienvermögen
- Immobilien- und Unternehmensnachfolge
- digitale Konten und digitaler Nachlass
- persönliche Wünsche und Familienwissen

## Leistungsgrenzen

ZONVAA ersetzt keine Rechtsanwälte, Notare, Steuerberater, Ärzte oder sonstigen Fachleute. Es erstellt keine verbindliche Rechts-, Steuer- oder Medizinberatung und erklärt Dokumente nicht ungeprüft für wirksam oder vollständig. Fachlich ungeprüfte Inhalte, Unsicherheiten und offene Fragen bleiben ausdrücklich gekennzeichnet.

## Unterstützungsfunktionen

Life Decisions soll verständlich informieren, strukturiert Fragen stellen, fehlende Angaben erkennen, Widersprüche und Unsicherheiten sichtbar machen, Entscheidungen und Gründe dokumentieren, Fachgespräche vorbereiten, an Prüf- und Aktualisierungstermine erinnern und Dokumente mit den zugehörigen Entscheidungen verknüpfen.

## Guardian Life Decision Conversation v1

Der erste produktnahe V2-Gesprächsfall bereitet das Thema Vorsorgevollmacht
ausschließlich aus einem vorhandenen `UnderstandingState` und ausdrücklich
typisierten Fachreferenzen vor. Er interpretiert keine natürliche Sprache,
wählt keine Person oder Vertretungsbereiche, erzeugt keine Vollmacht und
aktiviert keinen Workflow. Hypothesen, offene Punkte und Widersprüche bleiben
getrennt sichtbar; nur ausdrücklich übergebene organisatorische Schritte und
Fachprüfungen erscheinen in der Vorbereitung.

Die v2-Gesprächsführung erzeugt daraus jeweils genau einen referenzierbaren
Turn. Mehrere wesentliche Lücken werden ausschließlich in ihrer dokumentierten
Tupelreihenfolge bearbeitet. Eine weiterhin offene, bereits identisch gestellte
Frage wird als `QUESTION_UNRESOLVED` ausgewiesen und weder umformuliert noch
automatisch beantwortet; dabei wird die gesamte explizit übergebene
Turn-Historie geprüft. Erst ein extern kontrolliert revidierter
Understanding State kann zur nächsten Lücke führen. Readiness bedeutet nur,
dass keine ausdrücklich markierte wesentliche Lücke mehr unbearbeitet ist;
sichtbare Widersprüche bleiben erhalten.

## Guardian Life Decision Journey v1

Die Vorsorgevollmacht-Journey verbindet die vorhandenen Understanding-,
Preparation-, Turn-, Resolution- und Revision-Artefakte zu einem
deterministischen, zustandslosen Produktablauf. Ein statischer typisierter
Fragenkatalog liefert höchstens eine neutrale Frage für die erste wesentliche
offene Lücke in Preparation-Reihenfolge. Fehlt eine kontrollierte Frage, wird
sichtbar blockiert; es gibt keine freie Formulierung oder automatische
Interpretation.

Unveränderte Fragen werden nicht wiederholt. Offengehaltene und verworfene
Proposal-Klärungen bleiben zurückgestellt, ohne Änderung geschlossene Punkte
bleiben getrennt von Facts, und Widersprüche bleiben sichtbar. Nur eine extern
vollständig belegte Proposal-Auswahl samt Understanding Revision kann den
aktualisierten State für den nächsten Journey-Schritt liefern.

Bei ausreichendem Stand kann auf ausdrückliche Anforderung ein
Professional-Review-Vorbereitungspaket entstehen. Es übernimmt ausschließlich
typisierte vorhandene Inhalte und enthält keine Standardcheckliste. Die beiden
Readiness-Status sind keine juristische, notarielle, medizinische, steuerliche
oder sonstige fachliche Freigabe. Der Service persistiert nichts, analysiert
keine Dokumente, nutzt kein Netzwerk und aktiviert weder Workflow noch
Capability.

## Guardian Life Decision Experience v1

Die Vorsorgevollmacht-Experience überführt eine vollständig konsistente Journey
deterministisch in ein UI-neutrales Darstellungsmodell. Sie zeigt den aktuellen
Stand, höchstens die bereits kontrollierte Frage, getrennte offene,
zurückgestellte und geschlossene Punkte, Hypothesen, Widersprüche, zulässige
nächste Handlungen und sichtbare Fachgrenzen. Diese Handlungen führen nichts
aus und stellen weder Empfehlung noch Entscheidung dar.

Die Experience interpretiert keine Sprache, ergänzt keine Personen,
Vertretungsbereiche, Checklisten oder Fachprüfbedarfe und erzeugt keine
Resolution oder Understanding Revision. Ein vorhandenes Professional-Review-
Paket wird ausschließlich aus seinen vorhandenen Inhalten dargestellt.
Inkonsistente Artefakte liefern eine sachliche Blockademeldung ohne teilweise
Fachinhalte; technische Prüfinformationen bleiben davon getrennt. Die
Darstellung ist kanonisch deutsch, zustandslos und ohne Persistenz, Netzwerk,
LLM, Dokumentgenerator oder Benutzeroberfläche.

## Guardian Life Decision v1: Patientenverfügung

Die Patientenverfügungs-Journey ist der zweite vollständige V2-Life-Decisions-
Anwendungsfall. Sie übernimmt nur explizit typisierte Situationen, Maßnahmen,
Haltungen, Bedingungen, Wünsche, Werte, Personen, Dokumente, Schritte und
Prüfbedarfe aus einem referenzierten `UnderstandingState` und fachlichen
Eingaben. Ein statischer Katalog stellt höchstens eine kontrollierte Frage zur
ersten wesentlichen Lücke; die vollständige Turn-Historie verhindert eine
unbemerkte Wiederholung.

Externe Antworten werden nicht gedeutet. Nur vollständige, explizite
Clarification- und Revision-Ketten können mit einer aktualisierten Preparation
fortfahren. Widersprüche, Unknowns und Hypothesen bleiben getrennt sichtbar.
Das Professional-Review-Paket und die kanonische deutsche Experience ergänzen
weder medizinische Inhalte noch Checklisten oder Empfehlungen. Der Baustein
erstellt keine Patientenverfügung, bewertet keine Behandlung,
Einwilligungsfähigkeit, Person oder Wirksamkeit und nutzt weder Persistenz,
Netzwerk, LLM noch Dokumentgenerator.

## Guardian Cross-Domain Life Situation v1: Pflegefall in der Familie

Der erste fachübergreifende V2-Fall verbindet einen gemeinsamen
`UnderstandingState` mit ausschließlich explizit übergebenen Contributions aus
Pflege und Versorgung, Gesundheit und medizinischer Organisation, Life
Decisions und Vertretung, Wohnen und Immobilie, Finanzen und Kosten, Familie
und Rollen sowie Dokumenten und Organisation. Für Nutzer bleibt ein Guardian
sichtbar; Contributions sind keine Fachagenten, führen kein eigenes Gespräch
und besitzen keinen konkurrierenden State.

Explizite offene Punkte und Abhängigkeiten werden unverändert validiert und in
stabiler Eingabereihenfolge dargestellt. Sie werden nicht automatisch
abgeleitet, gewichtet oder priorisiert. Ein kontrollierter deutscher Katalog
liefert genau eine Frage zur ersten aktiven wesentlichen Lücke. Externe
Antworten werden nicht interpretiert; Conversation und Journey können nur eine
vollständige Clarification-/Revision-Kette referenzieren. Widersprüche bleiben
sichtbar und werden nicht aufgelöst.

Professional-Review-Paket und UI-neutrale Experience spiegeln ausschließlich
belegte Inhalte. Sie beraten weder pflegerisch, medizinisch, rechtlich,
steuerlich, finanziell noch zu Immobilien, bewerten keine Personen, berechnen
weder Pflegegrad noch Leistungen und erzeugen keinen Maßnahmenplan. Der
Baustein ist deterministisch und zustandslos, ohne Persistenz, Netzwerk, LLM,
Routing, automatische Domain-Aktivierung oder Multi-Agenten-Framework.

### Scenario Validation v1

Zwölf anonymisierte, vollständig typisierte Lebenslagen prüfen den bestehenden
Family-Care-Vertrag von der Situation bis zur Experience. Die Matrix umfasst
plötzliche und schleichende Pflegeverläufe, ungeklärte Vertretung, familiäre
Widersprüche, Wohnen und Finanzierung, medizinische Hypothesen,
Dokumentreferenzen, mehrere wesentliche Lücken, revisionsbeantwortete Punkte
und einen möglichen Interessenkonflikt. Ergänzende Robustheitstests decken
fremde Referenzen, unvollständige Artefaktketten und Bindungsfehler ab.

Die Validierung erzeugt keine Laufzeitlogik und interpretiert keine realen
Freitexte. Sie bestätigt ausschließlich, dass typisierte Eingaben unverändert,
quellenbezogen und ohne automatische Empfehlung oder Entscheidung verarbeitet
werden. Die vollständige Matrix und verbleibende Risiken stehen in
`knowledge/project/family-care-scenario-validation.md`.

### End-to-End Reference Journey v1

Ein anonymisierter Referenzfall verbindet die bereits bestehenden Verträge
über sechs kontrollierte Gesprächszüge. Jede Frage bleibt an den ersten aktiven
wesentlichen Punkt gebunden; jede Antwort wird über Proposal, ausdrückliche
Clarification Resolution und gegebenenfalls bestehende Understanding Revision
quellenbezogen weitergeführt. Ausgewählte Proposals verändern ihre Operation
nicht. Punkte ohne ausreichende Klärung bleiben ausdrücklich offen und lösen
keine Revision aus.

Die Validierung ergänzt keinen Produktservice und interpretiert keine Sprache.
Sie bestätigt die chronologische Revisionskette, den Schleifenschutz, höchstens
eine aktive Frage, explizite Review-Bindungen und eine konsistente UI-neutrale
Experience. Der vollständige Fall steht in
`knowledge/project/family-care-end-to-end-reference-journey.md`.

## Datenprinzip

Nutzer bestimmen den Speicherort ihrer Originaldateien. Originale verbleiben möglichst lokal, auf einem NAS oder im persönlichen Cloudspeicher. ZONVAA ist eine Intelligenz- und Entscheidungsschicht und kein zentraler Besitzer der Originale. Nur ausdrücklich freigegebene Inhalte dürfen verarbeitet werden. Sensible Inhalte müssen vor externer Verarbeitung löschbar oder schwärzbar sein. Originale, extrahierte Fakten, Interpretationen und Entscheidungen werden getrennt behandelt. Freigaben und Löschungen bleiben nachvollziehbar; eine stillschweigende Wiederverwendung findet nicht statt.

## Qualitätsprinzipien

- Quellen und Bearbeitungsstand sind nachvollziehbar.
- Fehlende Angaben werden nicht erfunden.
- Unsicherheit wird nicht als bestätigte Tatsache dargestellt.
- Fachliche Prüfung besitzt einen sichtbaren Status.
- Zugriffe und Freigaben folgen dem Prinzip der minimalen Berechtigung.
- Aktualisierungsbedarf wird erkennbar und erinnerbar.
