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
