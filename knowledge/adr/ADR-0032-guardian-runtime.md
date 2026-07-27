# ADR-0032 – Guardian Runtime Knowledge Model

## Status

Beschlossen

## Kontext

ADR-0004 bestimmt RuntimeManager als technische Single Source of Truth.
ADR-0009 klassifiziert Memory nach Lebensdauer, Schutz und Verlässlichkeit.
MDR-0001 fordert personengebundene Guardian-Instanzen, minimale strukturierte
Erinnerung, nutzerkontrollierte Originale, Portabilität, Löschung und
nachvollziehbare Freigaben. Institution, Governance und der Artefaktvertrag
begrenzen Rechte und Mehrparteienübergänge.

Es fehlt ein gemeinsamer technischer Vertrag, der Wissen innerhalb einer
Guardian-Instanz nach Typ, Person, Zeit, Herkunft, Unsicherheit, Gültigkeit,
Retention, Widerspruch und Transition trennt. Ohne ihn könnten
Nutzeraussagen, Hypothesen oder Interpretationen still zu globaler Wahrheit
werden.

## Entscheidung

ZONVAA führt die Guardian Runtime als personengebundenen internen
Wissenszustandsraum ein.

> Der Guardian besitzt keine untypisierte globale Wahrheit.

Der kanonische technische Vertrag liegt unter
`guardian_runtime/contract.md`. Das Paket `guardian_runtime` enthält stabile
Enums, unveränderliche Modelle, einen strukturellen Loader und einen
deterministischen Transition Planner. Es ist keine neue Persistenz und kein
sichtbarer Workflow.

### Wissen, Provenienz und Zeit

`KnowledgeItem` trennt `VERIFIED_FACT`, `USER_STATEMENT`,
`EXTERNAL_STATEMENT`, `OBSERVATION`, `HYPOTHESIS`, `INTERPRETATION`,
`PREFERENCE`, `DECISION`, `COMMITMENT`, `MEMORY`,
`PROCEDURAL_KNOWLEDGE` und `UNKNOWN`.

Knowledge Types werden nicht aus Strings normalisiert und nicht implizit
konvertiert. Nutzeraussagen bleiben Nutzeraussagen. Die Bestätigung einer
Hypothese ändert ihren prüfbaren Status, macht sie aber nicht automatisch zum
Fakt.

Jede Wissenseinheit außer `UNKNOWN` besitzt maschinenlesbare Provenienz mit
Quelle, Owner, Quellzeit, Extraktions- und Verifikationsmethode,
Transformationshistorie und optionalem Quellhash. Confidence und Verification
sind getrennt. `VERIFIED_FACT` erfordert eine Quelle und eine ausdrückliche
Verifikation.

Ereigniszeit, Speicherzeit, Beobachtungszeit und Gültigkeitszeit bleiben
getrennt. Eine neuere Speicherung beweist keine aktuellere Information.

### Widerspruch und Interpretation

Widersprüchliche Einheiten bleiben erhalten. Ein typisierter
`KnowledgeConflict` referenziert beide Einheiten und verlangt Klärung.
Interpretationen referenzieren ihre Grundlagen und überschreiben sie nicht.
Entscheidungsrelevante offene Konflikte sind im Snapshot sichtbar.

### Guardian Memory

`GuardianMemory` referenziert minimale Knowledge Items getrennt als:

- episodische Erinnerung,
- semantisches Wissen,
- Nutzerpräferenz,
- bestätigte Entscheidung,
- offene Verpflichtung,
- Beziehungs- und Vertrauenskontext,
- historischen Kontext.

Vollständige Chatverläufe sind kein Memory-Modell. ADR-0009 bleibt die
übergeordnete Klassifikation einschließlich des besonderen Schutzes von
`heritage_memory`.

### Retention, Vergessen und Löschen

Retention ist typisiert als `KEEP_UNTIL_REVOKED`,
`KEEP_FOR_ACTIVE_CONTEXT`, `KEEP_UNTIL_DATE`, `ARCHIVE`, `ANONYMIZE`,
`DELETE`, `LEGAL_HOLD` oder `UNKNOWN`.

Zeitgebundene und rechtlich gebundene Aufbewahrung benötigt explizite
Metadaten. Historie begründet keine pauschale Unlöschbarkeit. Bevor eine
Quelle gelöscht oder auf Löschung gesetzt werden kann, müssen davon
abgeleitete, widersprüchliche oder anderweitig referenzierende Einheiten
geklärt werden. Der Planner plant nur; er löscht oder anonymisiert keine
realen Daten.

Nutzerhoheit umfasst Widerruf, Vergessen, Löschung und Export innerhalb
dokumentierter Bindungen. Originaldokumente verbleiben außerhalb der
zentralen Guardian Runtime und werden ausschließlich referenziert.

### Personengrenze und Autorisierung

Ein gebundener `GuardianRuntimeSnapshot` gehört genau einer Guardian- und
Subject-ID. Knowledge Items eines anderen Personenraums werden abgelehnt.
Ein ungebundener Builder-Snapshot ist zulässig, enthält aber keinerlei
Personenwissen, Memory, Autorisierung oder Transition.

Jede Transition benötigt eine bereits aktive Autorisierungsreferenz. Die
Guardian Runtime erzeugt keine Autorisierung. Gemeinsame Sichtbarkeit und
Mehrparteienübergänge bleiben am bestehenden Artefakt- und
Autorisierungsvertrag gesperrt. Es gibt keine globale Familienwahrheit und
keine Ableitung aus nicht freigegebenen Kontexten.

### Übergänge und Determinismus

Jede Transition enthält vorherigen und neuen Zustand, typisierten Übergang,
Auslöser, Autorisierungsreferenz, Zeitpunkt, Begründung, Quellen und Ergebnis.
Sie darf nur die für den Transitionstyp zugelassenen Felder ändern.

Der Planner prüft Snapshot-Version, Personenbindung, Autorisierung,
Transition-Matrix und abhängiges Wissen. Er gibt einen neuen Snapshot mit
kanonischem Hash zurück und mutiert keinen Eingangszustand. Gleicher Zustand
und gleiche Eingabe erzeugen denselben Plan.

### Runtime und Preflight

RuntimeManager lädt genau einen versionierten
`GuardianRuntimeContractContext`. Den leeren ungebundenen Snapshot erhält er
über KnowledgeManager; KnowledgeManager bleibt einzige Knowledge-Schnittstelle.

Mission Context 1.5 weist Vertragsversion und -hash, stabile Typmengen,
Snapshot-Schema, Guardian-/Subject-Zuordnung, Snapshot-Version, Memory-Scope,
Konflikte, offene Hypothesen, Autorisierungsreferenzen,
Retention-Bindungen, Provenienzintegrität und Runtime-Hash nach.

Preflight bricht bei fehlendem oder verändertem Vertrag, Hashabweichung,
unvollständiger Personenzuordnung, veralteter Gültigkeit, fälliger Retention,
fehlender Provenienz oder unzulässiger Typtransition ab.

## MDR-Abgrenzung

MDR-0001 bleibt alleinige verbindliche Detailquelle für Guardian Conversation
und Continuity. Diese Entscheidung konsolidiert keine konkurrierenden
Master-Entwürfe, sondern konkretisiert deren technische Runtime-Grenzen.
Deshalb entsteht kein zweiter MDR.

## CLI-Abgrenzung

Es wird kein Guardian-Runtime-CLI eingeführt. Ohne freigegebene produktive
Persistenz würde ein JSON-CLI lediglich ein zweites Lade- und
Serialisierungssystem schaffen. Modelle, Loader, Planner, Runtime und
Preflight bilden die vollständige prüfbare Grenze dieses Arbeitspakets.

## Folgen

- Wissen bleibt quellen-, zeit- und personenbezogen.
- Fakten, Aussagen, Hypothesen und Interpretationen sind maschinenlesbar
  getrennt.
- Widersprüche und Retention-Bindungen bleiben sichtbar.
- Die Runtime berät und prüft; sie entscheidet nicht über den Menschen.
- Produktive Persistenz kann später nur hinter diesem Vertrag entstehen.

## Nicht-Ziele

Nicht eingeführt werden Datenbank, Cloud, Netzwerkzugriff, Vektordatenbank,
semantische Suche, Dokumentanalyse, externe KI, reale Löschung,
Anonymisierung oder Migration, UI, autonome Persönlichkeit, verdeckte
Profile, Persuasion, Emotionserkennung als Fakt, fachliche Bewertung oder
zentrale Speicherung von Originaldokumenten.
