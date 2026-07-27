# ZONVAA Guardian Runtime Knowledge Contract

Version: 1.0
Status: abgeleiteter technischer Vertrag
Normstufe: C2/C3

Normative Entscheidung:
`knowledge/adr/ADR-0032-guardian-runtime.md`

## Vertragsgrenze

Die Guardian Runtime ist der interne, personengebundene Wissenszustandsraum
unterhalb von Guardian, Conversation/Interaction und Institution. Sie
konkretisiert ADR-0009 und ersetzt weder KnowledgeManager noch RuntimeManager.
RuntimeManager bleibt technische Single Source of Truth; KnowledgeManager
bleibt einzige Knowledge-Schnittstelle.

Der Vertrag modelliert und validiert. Er speichert keine produktiven
Nutzerdaten, führt keine Löschung aus und trifft keine Entscheidung für den
Menschen.

## Wissen und Provenienz

Wissen bleibt als kleine, strukturierte `KnowledgeItem`-Einheit quellen-,
zeit-, personen- und versionsgebunden. `content_reference` referenziert einen
nutzergesteuerten Inhalt und enthält kein Originaldokument.

`VERIFIED_FACT`, `USER_STATEMENT`, `EXTERNAL_STATEMENT`, `OBSERVATION`,
`HYPOTHESIS`, `INTERPRETATION`, `PREFERENCE`, `DECISION`, `COMMITMENT`,
`MEMORY`, `PROCEDURAL_KNOWLEDGE` und `UNKNOWN` sind getrennte Typen. Sie
werden weder durch Wiederholung noch durch Confidence oder implizite
Transition ineinander umgewandelt.

Jede Einheit außer `UNKNOWN` benötigt maschinenlesbare Provenienz.
Verifikation und Confidence bleiben unabhängige Dimensionen.

## Zeit und Widerspruch

Ereignis- beziehungsweise Gültigkeitszeit, Beobachtungszeit und Speicherzeit
bleiben getrennt. Eine jüngere Speicherung beweist keine jüngere Information.

Widersprüche erhalten beide Wissenseinheiten, gegenseitige Referenzen,
Quellen und einen offenen `KnowledgeConflict`. Kein Konflikt wird automatisch
zugunsten einer Quelle aufgelöst. Entscheidungsrelevante Konflikte verlangen
Klärung.

## Guardian Memory

Guardian Memory referenziert ausschließlich minimale Knowledge Items als
episodische Erinnerung, semantisches Wissen, Nutzerpräferenz, bestätigte
Entscheidung, offene Verpflichtung, Beziehungs- und Vertrauenskontext oder
historischen Kontext. Vollständige Chatverläufe sind kein Memory-Modell.

Ein Knowledge Item gehört innerhalb eines Snapshots höchstens einem
Memory-Scope an. Memory erzeugt keine zusätzliche Wahrheit und keine
separate Persistenz.

## Retention und Forgetting

`KEEP_UNTIL_REVOKED`, `KEEP_FOR_ACTIVE_CONTEXT`, `KEEP_UNTIL_DATE`, `ARCHIVE`,
`ANONYMIZE`, `DELETE`, `LEGAL_HOLD` und `UNKNOWN` sind explizite
Retention-Klassen.

`KEEP_UNTIL_DATE` benötigt ein Datum. `LEGAL_HOLD` benötigt dokumentierte
Bindungsreferenzen. Historische Nachvollziehbarkeit macht nicht alle Daten
unlöschbar. Löschung oder Widerruf bleibt gesperrt, solange abhängige,
abgeleitete oder widersprüchliche Wissenseinheiten nicht neu bewertet wurden.
Der Planer löscht keine realen Daten.

Der Schutz von `heritage_memory` aus ADR-0009 bleibt unberührt. Eine spätere
Zuordnung von Guardian-Knowledge zu dieser Klasse darf nicht automatisch
gelöscht oder überschrieben werden.

## Personen- und Autorisierungsgrenze

Ein gebundener Snapshot gehört genau einer `active_guardian_id` und
`active_subject_id`. Alle enthaltenen Knowledge Items bleiben im selben
Owner- und Subject-Kontext. Ein ungebundener Builder-Snapshot ist zulässig,
aber vollständig leer.

Übergänge benötigen eine bereits aktive Autorisierungsreferenz. Die Guardian
Runtime erfindet keine Rechte. Mehrparteienfreigaben, Shared Safe und
institutionelle Handlungen bleiben am Artefakt- und Autorisierungsvertrag
gesperrt und werden in dieser Schicht nicht ausgeführt.

## Zustandsübergänge

Jede geplante Transition enthält vorherigen und neuen Zustand, typisierten
Auslöser, Autorisierungsreferenz, Zeitstempel, Begründung, Quellen und
Ergebnis. Zulässig sind:

- `statement_recorded`,
- `source_attached`,
- `verification_added`,
- `hypothesis_created`,
- `hypothesis_confirmed`,
- `hypothesis_rejected`,
- `interpretation_added`,
- `contradiction_detected`,
- `knowledge_superseded`,
- `retention_changed`,
- `knowledge_archived`,
- `knowledge_anonymized`,
- `knowledge_deleted`.

Transitionen dürfen ausschließlich die für ihren Typ vorgesehenen Felder
ändern. Knowledge Type, ID und Personengrenze bleiben unverändert.
`hypothesis_confirmed` bestätigt die Bewertung einer Hypothese, konvertiert
sie aber nicht automatisch in `VERIFIED_FACT`.

## Snapshot und Integrität

Der unveränderliche Snapshot enthält Zuordnung, Version, Memory-Scope,
Knowledge Items, Konflikte, offene Hypothesen, aktive
Autorisierungsreferenzen, Retention-Bindungen, Provenienzintegrität und
Transitionen. Sein SHA-256-Hash entsteht aus einer kanonischen
JSON-Darstellung ohne versteckte Annahmen.

Preflight weist Vertragsversion, Vertragshash, Enum-Sätze, Snapshot-Schema,
Personenzuordnung beziehungsweise leeren ungebundenen Zustand,
Snapshot-Hash, Konflikte, Hypothesen, Autorisierungsreferenzen, Retention und
Provenienz nach.

## Nicht implementiert

Nicht Bestandteil sind produktive Persistenz, Datenbank, Cloud,
Vektorsuche, semantische Volltextsuche, Dokumentanalyse, externe KI,
tatsächliche Löschung oder Anonymisierung, Datenmigration, UI,
Netzwerkzugriff, autonome Guardian-Persönlichkeit, verdeckte Profile,
Persuasion, Emotionserkennung als Fakt oder fachliche Bewertung.
