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

## Datenprinzip

Nutzer bestimmen den Speicherort ihrer Originaldateien. Originale verbleiben möglichst lokal, auf einem NAS oder im persönlichen Cloudspeicher. ZONVAA ist eine Intelligenz- und Entscheidungsschicht und kein zentraler Besitzer der Originale. Nur ausdrücklich freigegebene Inhalte dürfen verarbeitet werden. Sensible Inhalte müssen vor externer Verarbeitung löschbar oder schwärzbar sein. Originale, extrahierte Fakten, Interpretationen und Entscheidungen werden getrennt behandelt. Freigaben und Löschungen bleiben nachvollziehbar; eine stillschweigende Wiederverwendung findet nicht statt.

## Qualitätsprinzipien

- Quellen und Bearbeitungsstand sind nachvollziehbar.
- Fehlende Angaben werden nicht erfunden.
- Unsicherheit wird nicht als bestätigte Tatsache dargestellt.
- Fachliche Prüfung besitzt einen sichtbaren Status.
- Zugriffe und Freigaben folgen dem Prinzip der minimalen Berechtigung.
- Aktualisierungsbedarf wird erkennbar und erinnerbar.
