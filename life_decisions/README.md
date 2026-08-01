# Guardian Life Decision Conversation v1: Vorsorgevollmacht

Der erste produktnahe Life-Decisions-Nutzerfall erstellt eine sachliche
Gesprächsvorbereitung aus einem bestehenden `UnderstandingState` und weiteren
ausdrücklich typisierten Referenzen. Er ist kein Intake, kein Workflow und
keine Rechtsberatung. Er erzeugt weder eine Vollmacht noch Vertrags- oder
Urkundentext und bewertet keine Person, Geschäftsfähigkeit, Wirksamkeit oder
Rechtsfolge.

Facts bilden nur die bekannte Ausgangslage, wenn sie ausdrücklich aus dem
verwendeten State referenziert sind. Hypotheses bleiben Hypothesen, Unknowns
bleiben offene Punkte und Contradictions bleiben sichtbar. Ziele, Personen,
Vertretungsbereiche, Dokumentreferenzen, fehlende Angaben, organisatorische
Schritte und Fachprüfungen werden nicht aus Text abgeleitet, sondern vollständig
typisiert übergeben.

Wesentliche fehlende Angaben benötigen genau eine ausdrücklich bereitgestellte
nächste Verständnisfrage. Der Service interpretiert die Frage oder Antwort
nicht und erzeugt keine `UnderstandingOperation`; der `UnderstandingState`
bleibt unverändert. Spätere Gesprächs- oder LLM-Komponenten dürfen nur
typisierte Eingaben vorbereiten. Der Service ist ein zustandsloses
Vorbereitungsartefakt und ersetzt nicht die Gesprächsführung des Guardians:
Das Understanding Model reift weiterhin über einzelne, ausdrücklich bestätigte
Gesprächszüge. Weder dieser Service noch eine spätere semantische Komponente
dürfen Verständnisfragen automatisch beantworten, Proposals auswählen oder
den Understanding State verändern. Sie dürfen außerdem weder unbekannte
Angaben ergänzen noch Personen, Bereiche, Schritte oder Prüfungen auswählen.

Vorhandene Dokumente bleiben `DocumentReference`-Objekte unter
nutzergesteuerter Speicherung. Der Baustein liest, kopiert, analysiert oder
persistiert keine Originaldatei.

## Mehrzügige Gesprächsführung v2

`GuardianPowerOfAttorneyConversationService` erzeugt aus einer vorhandenen
Preparation genau einen zustandslosen Conversation Turn. Bei mehreren
wesentlichen Lücken gilt ausschließlich deren Tupelreihenfolge in
`missing_information`: Die erste als `essential=True` markierte Lücke ist die
nächste. Diese stabile Reihenfolge ist keine Priorisierung oder Bewertung. Die
zugehörige Frage muss vollständig typisiert übergeben sein, zur ersten Lücke
passen und deren Quellenreferenz erhalten; der Service formuliert sie nicht.

Ein identischer Turn in der vollständig explizit übergebenen bisherigen
Turn-Historie mit weiterhin derselben offenen Lücke führt zu
`QUESTION_UNRESOLVED` — auch wenn andere Turns dazwischenliegen. Das Ergebnis
referenziert Frage und den relevanten früheren Turn, stellt
aber keine Ersatzfrage, interpretiert keine Antwort und ändert keinen State.
Eine Fortsetzung nach Klärung konsumiert nur eine extern erzeugte
`ClarificationResolution`, `UnderstandingRevision` und deren resultierenden
`UnderstandingState`. Der Service erzeugt oder führt keines dieser Artefakte
selbst aus.

`CONVERSATION_PREPARATION_READY` bedeutet nur, dass die ausdrücklich
übergebene Preparation keine unbearbeitete wesentliche Lücke enthält.
Widersprüche und Fachprüfbedarfe bleiben sichtbar; der Status behauptet weder
Widerspruchsfreiheit, Eignung, Empfehlung noch rechtliche Wirksamkeit.

Zustandslosigkeit ist eine Eigenschaft dieses Services, keine Entscheidung
gegen eine spätere nutzerkontrollierte Beziehungsschicht. Turn-Artefakte haben
stabile IDs und vollständige Referenzen und können außerhalb des Services
gespeichert werden. Der Service selbst persistiert sie nicht und deutet
Antworten niemals automatisch. Weil `UnderstandingState` noch keine native ID
besitzt, bindet der Turn die externe State-ID zusätzlich an einen
deterministischen SHA-256-Hash des kanonischen State-Inhalts. Strukturell
identische States besitzen absichtlich denselben Inhaltsnachweis.

## Vorsorgevollmacht-Journey v1

`GuardianPowerOfAttorneyJourneyService` verbindet den bestehenden
`UnderstandingState`, die Conversation Preparation, kontrollierte Fragen,
Conversation Turns sowie extern erzeugte Resolutions und Revisionen. Er
validiert und referenziert diese Artefakte, interpretiert aber weder
Nutzerantworten noch erzeugt er Proposals, Resolutions, Operations oder States.
Alle Historie wird ausdrücklich als Eingabe übergeben; der Service persistiert
nichts und greift nicht auf Netzwerk oder Dokumentinhalte zu.

Der kontrollierte Fragenkatalog enthält ausschließlich statische, neutrale
Fragen für bereits unterstützte Lückenarten. Eine `PowerOfAttorneyGapBinding`
bindet eine konkrete `MissingInformation` ausdrücklich an eine solche Art. Die
erste noch aktive, als wesentlich markierte Lücke in der Preparation-Reihenfolge
bestimmt die Frage. Fehlt die Bindung oder der Katalogeintrag, gilt
`BLOCKED_MISSING_CONTROLLED_QUESTION`; es entsteht keine freie Ersatzfrage.

Eine unverändert offene, bereits gestellte Frage führt unter Berücksichtigung
der gesamten Turn-Historie zu `QUESTION_UNRESOLVED`. KEEP_OPEN und
REJECT_PROPOSALS bleiben als zurückgestellte offene Punkte sichtbar;
CLOSE_WITHOUT_CHANGE wird getrennt dokumentiert und niemals als Fact
dargestellt. Nur eine vollständig übergebene SELECT_PROPOSAL-Kette mit externer
Revision kann einen aktualisierten State belegen. Widersprüche bleiben in jedem
Status sichtbar und blockieren nur über eine zugleich ausdrücklich vorhandene
wesentliche Lücke.

`CONVERSATION_PREPARATION_READY` bedeutet lediglich, dass keine unbearbeitete
wesentliche Gesprächslücke verbleibt. Erst die ausdrückliche Anforderung eines
deterministischen `PowerOfAttorneyProfessionalReviewPreparation` führt zu
`PROFESSIONAL_REVIEW_PREPARATION_READY`. Das Paket übernimmt ausschließlich
belegte Facts, Goals, Personen, Bereiche, Dokumentreferenzen, organisatorische
Schritte und Fachprüfbedarfe sowie getrennte Unknowns, Hypotheses und
Contradictions. Es ist keine Rechtsberatung, Vollmacht, Wirksamkeitsprüfung,
Personen- oder Geschäftsfähigkeitsbewertung und keine fachliche Freigabe.

## Vorsorgevollmacht-Experience v1

`GuardianPowerOfAttorneyExperienceService` projiziert eine vollständig
konsistente Journey in einen unveränderlichen, UI-neutralen Darstellungs- und
Interaktionsvertrag. Journey und Experience bleiben getrennt: Die Journey
enthält den fachlichen Ablaufzustand, die Experience ordnet ausschließlich
bereits vorhandene Inhalte, technische Referenzen und zulässige nächste
Handlungen für eine kanonische deutsche Darstellung. Sie interpretiert keine
Nutzeraussage, formuliert keine Frage dynamisch und verändert kein fachliches
Artefakt.

Jeder Journey-Status besitzt einen stabilen, sachlichen Darstellungstext.
`NEEDS_CLARIFICATION` zeigt exakt die vorhandene kontrollierte Frage;
`QUESTION_UNRESOLVED` wiederholt sie nicht. Offene wesentliche und sonstige
Punkte, zurückgestellte, verworfene und ohne Änderung geschlossene Punkte,
Hypothesen und Widersprüche bleiben getrennt. Eine Darstellungsaktion beschreibt
nur eine im bestehenden Modell zulässige menschlich kontrollierte Handlung;
sie ist weder Ausführung, Empfehlung, Resolution noch State-Änderung.

Ein vorhandenes Professional-Review-Paket wird ohne zusätzliche Checkliste,
Fachprüfung oder Bewertung gespiegelt und kann später auf einem Bildschirm, in
einer API oder in einem nutzerkontrollierten Export verwendet werden. Dieser
Baustein erzeugt jedoch weder Benutzeroberfläche noch PDF oder DOCX. Technische
Konsistenzfehler bleiben von der nutzerverständlichen Blockademeldung getrennt;
bei inkonsistenten Artefakten werden keine teilweisen Fachinhalte dargestellt.
Fachgrenzen wie fehlende Rechts-, Wirksamkeits-, Personen-, medizinische oder
steuerliche Bewertung sind sichtbar. Der Service ist zustandslos, persistiert
nichts, nutzt weder Netzwerk noch LLM und enthält keine dynamische
Sprachgenerierung.

## Guardian Life Decision v1: Patientenverfügung

Der zweite vollständige Life-Decisions-Anwendungsfall bildet eine eigenständige
vertikale Kette aus `UnderstandingState`, typisierter Preparation,
kontrollierten Conversation Turns, externen Clarification-/Revision-Artefakten,
Journey, Professional-Review-Paket und UI-neutraler Experience. Er verwendet
die bewährten Invarianten der Vorsorgevollmacht, verändert deren fachliche
Verträge aber nicht und führt keine allgemeine Life-Decisions-Engine ein.

Unterstützt werden ausschließlich ausdrücklich typisierte medizinische
Situationen, Maßnahmen, neutrale Haltungen, Bedingungen, persönliche Wünsche
und Werte, Personenrollen, Dokumentreferenzen, organisatorische Schritte und
Fachprüfbedarfe. `UNSPECIFIED` ist keine Zustimmung und `UNCERTAIN` keine
Ablehnung. Bedingte Haltungen benötigen ausdrücklich übergebene Bedingungen;
aus Zielen, Werten oder anderen Aussagen wird keine Haltung abgeleitet.

Der statische Fragenkatalog bindet genau eine neutrale deutsche Frage an eine
bereits typisierte wesentliche Lücke. Die gesamte Turn-Historie verhindert die
Wiederholung einer unverändert offenen Frage. Antworten, Proposals,
Resolutions, Revisionen und neue States entstehen außerhalb der Conversation-
und Journey-Services und werden nur als vollständige Referenzkette validiert.
Widersprüche bleiben sichtbar und werden weder medizinisch noch rechtlich
aufgelöst.

Das Professional-Review-Paket und die Experience spiegeln ausschließlich
vorhandene Inhalte; sie erzeugen keine Checkliste, Empfehlung, medizinische
Erklärung oder Patientenverfügung. Der Baustein leistet keine medizinische,
rechtliche oder steuerliche Beratung, beurteilt weder Einwilligungsfähigkeit
noch Personen oder Wirksamkeit und trifft keine Behandlungsentscheidung. Alle
Services sind deterministisch und zustandslos, ohne Persistenz, Netzwerk, LLM,
Dokumentanalyse, Exportgenerator oder Benutzeroberfläche.

## Guardian Cross-Domain Life Situation v1: Pflegefall in der Familie

`GuardianFamilyCarePreparationService` strukturiert eine ausdrücklich
typisierte familiäre Pflegesituation auf genau einem vorhandenen
`UnderstandingState`. Für den Nutzer bleibt ein Guardian sichtbar. Die sieben
fachlich getrennten Contributions besitzen weder einen eigenen State noch
Persönlichkeit oder Ausführungsbefugnis. Nur explizit übergebene Contributions
werden dargestellt; es gibt keine automatische Domain-Aktivierung und kein
Routing.

Offene Punkte und Cross-Domain-Abhängigkeiten sind unveränderliche, explizite
Eingaben. Sie werden validiert und referenziert, aber nicht abgeleitet,
bewertet oder priorisiert. Ein statischer deutscher Fragenkatalog bindet
höchstens eine Frage an die erste aktive wesentliche Lücke in stabiler
Eingabereihenfolge. Conversation und Journey interpretieren keine Antwort und
validieren nur vollständig übergebene externe Clarification-/Revision-Ketten.
Die gesamte Turn-Historie verhindert eine erneute Ausgabe derselben weiterhin
offenen Frage.

Professional-Review-Paket und UI-neutrale Experience spiegeln ausschließlich
vorhandene Inhalte. Sie erzeugen keine Checkliste, Empfehlung, Pflegegrad- oder
Leistungsberechnung, Immobilien- oder Finanzbewertung und keinen Maßnahmenplan.
Alle Fachgrenzen bleiben sichtbar. Die Services sind zustandslos und
deterministisch; sie persistieren nichts, nutzen weder Netzwerk noch LLM und
bilden weder Agentenkommunikation noch ein allgemeines Cross-Domain-Framework.
# Guardian Family Care Review UI v1

Das gezielte interne Prüfwerkzeug zeigt den bestehenden anonymisierten
Family-Care-Referenzfall ohne neue Fachlogik. Start im Repository:

```bash
python3 -m family_care_review_ui
```

Danach ist die Oberfläche ausschließlich lokal unter
`http://127.0.0.1:8765` erreichbar; `Ctrl-C` beendet sie. Codex übernimmt
Start, Prüfung und Bericht, der Nutzer dient nicht als Terminal-Transportweg.
Die Session speichert nur einen flüchtigen Schrittzeiger. Öffnen, Fortschreiben
und Reset verändern keine Repository-Datei. Es gibt keine externe Verbindung,
Persistenz, Freitextinterpretation, automatische Proposal-/Resolution-/
Revision-Erzeugung, Empfehlung oder Entscheidung.
