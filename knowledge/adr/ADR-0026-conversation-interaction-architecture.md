# ADR-0026 – Conversation & Interaction Architecture

## Status

Beschlossen

## Kontext

ADR-0023 definiert S-V-N-P als Reihenfolge sichtbarer Interaktion.
ADR-0024 legt fest, dass der Nutzer immer mit dem personengebundenen Guardian
spricht und Workflows interne Werkzeuge bleiben. ADR-0025 führt die
Institution als nicht-operative Garantieebene ein.

Damit sind Haltung und langfristige Garantien geklärt. Es fehlt jedoch ein
verbindlicher Vertrag für die Grenze zwischen freiem Gespräch, strukturierten
Artefakten und autorisierten Handlungen. Ohne diese Ebene könnten
Gesprächskontext, Board-Zustand, Mehrparteienfreigaben oder institutionelle
Aktionen stillschweigend vermischt werden.

Primärquelle dieser Entscheidung ist der vom Produktarchitekten bereitgestellte
Gemini-Entwurf „Conversation- und Interaction-Architektur“. Seine normativen
Grenzen werden übernommen; konkrete UX-, Sicherheits-, Rechts- und
Implementierungsvorschläge bleiben ausdrücklich offen.

## Entscheidung

ZONVAA führt Conversation/Interaction als eigenständige Architekturebene ein:

Guardian → Conversation/Interaction → Institution → Runtime

Der kanonische Vertrag liegt unter `interaction/interaction.md`. Ein kleiner,
unveränderlicher `InteractionContext` enthält Quelle, Version, SHA-256-Hash
und stabile Prinzipientypen. Der Loader prüft UTF-8, Version und strukturelle
Vollständigkeit, interpretiert aber keine Gesprächsinhalte.

### Conversation Engine und Institution Board

Die Conversation Engine bezeichnet den nutzergerichteten freien
Gesprächsraum. Sie konkretisiert Guardian First, ohne eine neue Persona,
Emotionserkennung oder Workflow-Steuerung einzuführen.

Das Institution Board bezeichnet die getrennte strukturierte Handlungsebene
für Artefakte, Status, offene Angaben, Fristen, Prüfungen und Freigaben. Es ist
nicht der Institution Layer. Es spricht nicht als Guardian und führt keine
Aktion ohne Autorisierung aus.

Diese Begriffe definieren Architekturverantwortungen. ADR-0026 implementiert
weder Conversation Engine noch Board oder UI.

### Dual-Space und Übergang

Gesprächsraum und Institution Board bleiben getrennt. Ein Wechsel ist
bewusst, sichtbar und abbrechbar. Gesprächskontext startet keinen Workflow,
öffnet kein Board und erzeugt keine Vollmacht. Ablehnung oder Abbruch bleibt
ohne institutionelle Nebenwirkung.

### Artefakte und Autorisierung

Artefakte sind klar begrenzte Übergangsobjekte. Sie halten bestätigte
Aussagen, Zusammenfassungen, offene Fragen, Unsicherheiten, externe
Bestätigungen und konkrete Autorisierungen unterscheidbar.

Die Artefakt-Insel bezeichnet ihre isolierte, prüfbare Darstellung im Board.
Zwischen Artefakt und Aktion liegt der Autorisierungs-Graben: Jede
institutionelle oder externe Aktion benötigt eine separate, nachvollziehbare
Freigabe. Die konkrete Stärke dieser Freigabe wird später risikobasiert
entschieden.

### Personen und gemeinsame Räume

Eine Guardian-Instanz gehört genau einer Person. Persönliche Kontexte werden
nicht zwischen Personen übertragen oder zur verdeckten Empfehlung für andere
genutzt.

Die Multi-Party Graph Engine ist der künftige Verantwortungsrahmen für
dokumentierte Beziehungen und Berechtigungen, keine implementierte Engine.
Ein Shared Safe ist ein begrenzter gemeinsamer Entscheidungsraum, der nur
aktiv freigegebene Informationen und Artefakte enthält.

Bei Konflikten strukturiert ZONVAA Positionen und hält fehlenden Konsens
sichtbar. Es entscheidet nicht zugunsten einer Partei. Sicherheits- und
Schutzgrenzen werden durch Neutralität nicht abgeschwächt.

### Inaktivität, Offboarding und Unverfügbarkeit

Nicht-Nutzung ist kein Fehler und kann Erfolg bedeuten. Emotionales
Re-Engagement, Schuldgefühle und künstliche Dringlichkeit sind unzulässig.
Sachliche Erinnerungen benötigen Nutzerauftrag oder bestätigte Frist und
bleiben kontrollierbar.

Offboarding muss ohne emotionalen oder technischen Lock-in möglich sein.
Erzeugte Daten und Artefakte müssen in dokumentierten offenen oder allgemein
lesbaren Formaten nutzbar bleiben. Konkrete Löschung respektiert bestehende
Memory-Schutzklassen, insbesondere `heritage_memory`, und benötigt spätere
Rechts- und Datenschutzentscheidungen.

Die Unverfügbarkeits-Klausel verhindert, dass Gespräch oder Guardian-Nutzung
als automatische Überwachungs-, Handlungs- oder Eskalationspflicht
missverstanden werden. Kritische Pläne dürfen nicht allein vom aktiven
Guardian oder proprietären Zugang abhängen.

### Systemgrenzen

Der Guardian übernimmt keine moralischen Letztentscheidungen und keine
Verantwortung für irreversible Folgen. Er darf ordnen, Fragen vorbereiten,
dokumentierte Wünsche sichtbar machen und an geeignete Menschen oder
Fachstellen übergeben.

Notfälle dürfen normale Gesprächsprinzipien übersteuern. Automatische externe
Eskalation ist nicht freigegeben und benötigt eine eigene Architektur-,
Risiko-, Rechts-, Datenschutz- und Missbrauchsentscheidung.

## Verhältnis zu bestehenden Entscheidungen

- ADR-0023 und ADR-0024 bleiben vollständig gültig und bestimmen Haltung und
  sichtbare Guardian-Beziehung.
- ADR-0025 bleibt für Institution-Garantien gültig. ADR-0026 ersetzt
  ausschließlich dessen kürzere Schichtenfolge
  `Guardian → Institution → Runtime` durch die erweiterte Folge.
- Institution Board und Institution Layer sind ausdrücklich verschiedene
  Verantwortungen.
- RuntimeManager bleibt Single Source of Truth und KnowledgeManager bleibt
  einzige Knowledge-Schnittstelle.
- Goal-, Decision-, Execution- und Life-Decisions-Workflows erhalten keine
  zusätzlichen Rechte und dürfen die neue Ebene nicht umgehen.

## Runtime und Preflight

Runtime lädt genau einen unveränderlichen Interaction-Kontext zusätzlich zu
Identity und Institution. Identity bleibt zuerst, Institution wird weiterhin
vor operativem Kontext geladen. Interaction wird anschließend vor
Constitution, Knowledge, Project State und Engines nachgewiesen.

Mission Context Schema 1.2 enthält Status, Quelle, Version, Content-Hash und
Prinzipientypen. Fehlender oder veränderter Interaction-Vertrag bricht den
Preflight ab. Der abgeleitete WorkflowContext erhält weiterhin weder
Interaction- noch Institution-Inhalte.

## Zurückgestellte Details

Keine verbindlichen Architekturvorgaben sind:

- feste Verzögerungen, Zeichenzahlen, Prozentwerte oder Gesprächsrunden,
- starre Wort-, Verb- oder Promptfilter,
- konkrete Farben, Layouts, Gesten oder biometrische Verfahren,
- konkrete Kryptografie, Signaturen oder Zero-Knowledge-Verfahren,
- PDF/A oder andere konkrete Dokumentformate,
- automatische rechtsverbindliche Klauseln oder behauptete Haftungsfreiheit,
- konkrete Autorisierungs-, Export-, Lösch-, Notfall- oder
  Verfügbarkeitsmechanismen.

Diese Punkte benötigen bei Bedarf eigene UX-, Sicherheits-, Rechts-,
Datenschutz- oder Implementierungsentscheidungen.

## Konsequenzen

- Gespräch und institutionelle Handlung haben eine explizite, prüfbare
  Grenze.
- Persönliche und gemeinsam freigegebene Kontexte dürfen nicht implizit
  vermischt werden.
- Artefakte übertragen Struktur, aber keine Vollmacht.
- Institution-Garantien werden nicht dupliziert, sondern durch
  Interaction-Grenzen konkretisiert.
- Spätere technische Durchsetzung benötigt eigene, begrenzte Entscheidungen.
