# P1 – Internationale Praktiken für Glossare und Terminologiesysteme

Status: **INFORMATIVE ANALYSE – KEINE ÜBERNAHME EINES MODELLS ODER EINER ONTOLOGIE**

## 1. Untersuchungsgrenze

Untersucht werden ausschließlich Begriffsstabilität, Identifier,
Mehrsprachigkeit, Versionierung und Referenzierung. Die genannten Systeme
werden nicht übernommen, kombiniert oder zur ZONVAA-Architektur erklärt.

## 2. Vergleich

| System | Beobachtete Praxis | Begrenzte Lehre für einen späteren ZONVAA-Entwurf |
| --- | --- | --- |
| W3C SKOS | bevorzugte, alternative und versteckte Labels sind getrennt; höchstens ein bevorzugtes Label je Sprachkennzeichen; Notes und Change Notes bleiben eigene Aussagen | Identifier, Benennung, Synonyme, Sprache und Änderungshistorie getrennt führen |
| IETF/RFC | Zitate und Referenzen müssen einander entsprechen; normative und informative Referenzen werden getrennt; interne Verweise verwenden stabile Abschnitte statt Seiten | auflösbare Referenzen und Aussageart explizit machen |
| OMG | das öffentliche Terms-and-Acronyms-Verzeichnis erklärt seine Definitionen nur so autoritativ wie die jeweils zitierte Quelle | ein Glossar darf die Autorität seiner Regelinhaber nicht übernehmen |
| ISO 704 | Terminologiearbeit trennt Objekte, Begriffe, Definitionen und Benennungen; veröffentlichte Editionen und Lebenszyklus sind sichtbar | Begriff, sprachliche Bezeichnung, Definition und Version nicht vermischen |
| Dublin Core | Terme besitzen eindeutige Identifikatoren, Definitionen, Labels und Release-Historien; ein „latest“-Verweis steht neben datierten Ständen | stabilen Identifier und präzise Release-Referenz parallel anbieten |
| Schema.org | Releases sind versioniert und archiviert; veröffentlichte Schemadaten eines Releases gelten als eingefroren, während Darstellung redaktionell gepflegt werden kann | semantischen Release von rein redaktioneller Darstellung trennen |
| Wikidata/Wikibase | stabile Entitäts-IDs sind von mehrsprachigen Labels, Beschreibungen und Aliasen getrennt; je Sprache gelten eigene Eindeutigkeitsgrenzen | sprachneutralen Identifier und sprachgebundene Benennungen getrennt halten |
| SNOMED CT | Konzepte, Beschreibungen und Referenzmengen besitzen eigene Identitäten; Language Reference Sets bestimmen bevorzugte und akzeptable Benennungen je Sprache/Dialekt; historische Assoziationen halten Ablösungen sichtbar | Lokalisierung und Deprecation als nachvollziehbare Beziehungen statt Überschreiben behandeln |
| ICD-11 | Inhalte sind multilingual veröffentlicht und klassifikationsbezogene Releases werden als konkrete Versionen bereitgestellt | Sprachfassung und veröffentlichter Klassifikationsstand müssen referenzierbar bleiben |
| HL7 FHIR Terminology | CodeSystem und ValueSet sind getrennt; kanonische URL, lokale Instanz-ID und Version haben verschiedene Rollen; Designations tragen Sprachangaben | Identität, Speicherort, Version, Auswahlkontext und sprachliche Anzeige nicht gleichsetzen |

## 3. Wiederkehrende Muster

1. **Persistente Identität:** Ein stabiler Identifier überlebt Änderungen an
   Labels und Ablageorten.
2. **Begriff vor Benennung:** Konzeptuelle Identität und sprachliche Form sind
   nicht dasselbe.
3. **Sprachmarkierung:** Mehrsprachige Werte tragen explizite Sprach- oder
   Dialektkennzeichen; Synonyme bleiben von bevorzugten Formen getrennt.
4. **Versionierte Veröffentlichung:** Ein aktueller Einstiegspunkt ersetzt
   nicht die präzise Referenz auf einen eingefrorenen Stand.
5. **Quellenautorität:** Eine Referenzübersicht ist nicht automatisch die
   materielle Quelle der referenzierten Definition.
6. **Historie statt Überschreiben:** Ablösung, Inaktivierung und Deprecation
   bleiben nachvollziehbar.

## 4. Bewusst nicht übernommen

- RDF, RDFS, OWL, SKOS oder eine andere Ontologie,
- globale URIs oder Web-Auflösungsdienste,
- medizinische Klassifikations- oder Terminologiesemantik,
- Value Sets, Reference Sets oder Concept Maps als ZONVAA-Vertrag,
- maschinelle Inferenz, Validierung oder Terminologiedienste,
- externe Wahrheitsprüfung,
- Prioritätsregeln zwischen ZONVAA-Regelinhabern.

Die internationalen Systeme zeigen redaktionelle und referenzielle
Gestaltungsmuster. Sie legitimieren keine neue ZONVAA-Architektur.

## 5. Primärquellen

- [W3C SKOS Reference](https://www.w3.org/TR/skos-reference/)
- [IETF RFC 7322 – RFC Style Guide](https://datatracker.ietf.org/doc/html/rfc7322)
- [OMG Terms and Acronyms](https://www.omg.org/gettingstarted/terms_and_acronyms.htm)
- [ISO 704:2022 – Terminology work](https://www.iso.org/standard/79077.html)
- [DCMI Metadata Terms](https://www.dublincore.org/specifications/dublin-core/dcmi-terms/)
- [Schema.org Releases](https://schema.org/docs/releases.html)
- [Wikibase Data Model](https://www.mediawiki.org/wiki/Wikibase/DataModel)
- [SNOMED CT Reference Set Guide](https://docs.snomed.org/snomed-ct-practical-guides/snomed-ct-reference-set-guide)
- [WHO ICD-11](https://www.who.int/news-room/fact-sheets/detail/icd-11)
- [HL7 FHIR CodeSystem](https://hl7.org/fhir/codesystem.html)

