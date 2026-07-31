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
