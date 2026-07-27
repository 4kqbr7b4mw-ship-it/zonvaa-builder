# ADR-0033 – User-Owned Data Architecture

## Status

Beschlossen

## Kontext

Constitution, Institution, MDR-0001, ADR-0018, ADR-0019, ADR-0030 und ADR-0032
verlangen Nutzerhoheit, Portabilität, explizite Autorisierung,
Personenkontext-Isolation und Referenzen statt zentraler Originalkopien.

Life Decisions besitzt bereits eine fachliche `DocumentReference`. Guardian
Runtime besitzt `KnowledgeItem.content_reference`. Es fehlt jedoch ein
domänenübergreifender, providerneutraler Vertrag, der festlegt, was eine
Referenz nachweist und welche Speicherhandlungen sie ausdrücklich nicht
erlaubt. Ohne diese Grenze könnten Referenzen schleichend zu zentralem
Dokumentenhosting, automatischer Synchronisation oder impliziter
Löschvollmacht werden.

## Entscheidung

ZONVAA führt den User-Owned Data Layer als eigenständige Referenz- und
Schutzgrenze ein.

> ZONVAA ist eine Intelligence Layer.
>
> Nicht die Dokumentenplattform.
>
> Der Nutzer besitzt die Daten.
>
> ZONVAA besitzt Wissen über freigegebene Daten.

Der kanonische technische Vertrag liegt unter
`user_owned_data/contract.md`. Das Paket `user_owned_data` enthält stabile
Enums, unveränderliche Modelle und einen deterministischen Contract Loader. Es
enthält keinen Speicheradapter.

### Eigentum und Speicherwahl

Originaldaten gehören dem Nutzer. Nur der Nutzer bestimmt Speicherort,
Zugriff, Export und Löschung. Lokaler Ordner, NAS, private Cloud,
selbstbetriebener Server, externer Connector und unbekannter Speicher werden
gleichrangig modelliert. Es gibt keinen bevorzugten Anbieter.

Verbindliche Prinzipien sind Local First, User Ownership, User Controlled
Storage, Reference before Copy, Minimal Metadata, No Central Document Storage,
Explicit Consent, Privacy by Design, Delete by Design und Provider
Independence.

### Typisierte Referenz

`StorageReference` enthält:

- `reference_id`,
- `owner`,
- `storage_provider`,
- `storage_scope`,
- `locator`,
- optionale `checksum`-Integritätsmetadaten,
- `version`,
- `created_at`,
- optionales `last_verified`,
- eine an die Referenz gebundene `authorization`,
- optionale, separat nachgewiesene Provider-`capability`,
- `retention`,
- `availability`.

Der Locator ist eine logische, begrenzte, einzeilige Referenz. Das Modell
verbietet bekannte eingebettete Inhaltsformen, kann aber nicht die Semantik
jedes Strings beweisen. Konstruktion oder Serialisierung einer Referenz führt
keinen Datei-, Cloud- oder Netzwerkzugriff aus.

Checksums sind optionale, typisierte Metadaten. Dieser Layer berechnet oder
bestätigt sie nicht durch Zugriff auf das Original.

### Autorisierung und Operationen

Der Layer verwendet `ArtifactAuthorization` aus ADR-0030 und führt kein
zweites Identitäts- oder Rechtesystem ein. `ReferenceAuthorization` bindet
diese bestehende, aktive und zweckgebundene Autorisierung zusätzlich an genau
eine Referenz und explizite Operationen. Jede `StorageReference` benötigt
mindestens eine Freigabe für `REFERENCE`:

- Referenzieren,
- Lesen,
- Kopieren,
- Synchronisieren,
- Exportieren,
- Löschen eigener Metadaten,
- Löschen des Originals.

Keine Operation impliziert eine andere. Kontrollierte Operationen benötigen
`authorize_action`; Lesen benötigt `read`. Die Autorisierung muss vom Owner
für den Owner erteilt sein. Geteilte Scopes sind ohne explizite Autorisierung
unzulässig.

### Kopien und Synchronisation

Originale verbleiben grundsätzlich im User Vault. Kopie, Synchronisation,
Replikation und Cloud-Spiegelung geschehen niemals automatisch. Die Modelle
können eine ausdrückliche Erlaubnis nachweisen, führen aber keine dieser
Handlungen aus.

### Löschung und Retention

ZONVAA darf ohne gesonderte Erlaubnis ausschließlich eigene Metadaten löschen.
Original-Löschung verlangt Eigentümerbindung, bestätigte Verfügbarkeit eines
nicht unbekannten Providers, separat referenzierte Fähigkeitsevidenz und eine
ausdrückliche `DELETE_ORIGINAL`-Autorisierung. Die Evidenz ist kein technischer
Vollzugnachweis; ob ein externer Speicher die Löschung tatsächlich erlaubt und
ausgeführt hat, bleibt eine spätere Adapter- und Prüfverantwortung.

Retention nutzt die stabilen Guardian-Runtime-Klassen. Zeitbindungen und
Legal Holds benötigen explizite Metadaten. Historische Nachvollziehbarkeit
begründet keine pauschale Unlöschbarkeit.

### Runtime, KnowledgeManager und Preflight

RuntimeManager lädt genau einen statischen `UserOwnedDataContractContext`. Er
lädt keine Referenzen und keine User-Vault-Inhalte.

KnowledgeManager bleibt einzige Wissensschnittstelle. Er validiert
`StorageReference`-Objekte ohne Locator-Zugriff und ohne Persistenz.

Mission Context weist nur Vertragspfad, Version, Hash und stabile Typmengen
nach. Persönliche Locator, Checksums oder Autorisierungsinhalte gelangen nicht
in den Preflight. Preflight bricht bei fehlendem Vertrag, nicht unterstützter
Version oder Hashabweichung ab.

Die Guardian Runtime bleibt offline bootfähig. Ihr `content_reference` ist
eine logische Referenz-ID; vollständige Originale, Bild-, Video- oder
PDF-Sammlungen sind nicht Teil ihres Zustands.

## Verhältnis zu bestehenden Entscheidungen

- C1 und MDR-0001 behalten unverändert Vorrang.
- ADR-0019 bleibt das Life-Decisions-Fachmodell; seine `DocumentReference`
  wird nicht ersetzt oder erweitert.
- ADR-0030 bleibt die einzige Autorisierungsgrundlage.
- ADR-0032 bleibt der personengebundene Wissenszustandsvertrag.
- Diese ADR ergänzt diese Grenzen um ein providerneutrales Referenzmodell und
  erzeugt weder Knowledge Store noch Dokumentenplattform.

## Folgen

- Providerwechsel und Offboarding bleiben architektonisch möglich.
- Runtime und Knowledge können auf stabile Referenzen zeigen, ohne Originale
  zu besitzen.
- Fehlende Verfügbarkeit bleibt sichtbar und wird nicht als Datenverlust oder
  Löschung interpretiert.
- Produktive Speicheradapter müssen später getrennt genehmigt und gegen diese
  Grenze geprüft werden.

## Nicht-Ziele

Nicht eingeführt werden ZONVAA Cloud Drive, User-Vault-Implementierung,
Dateimanager, Dokumentenhosting, zentrale Originalspeicherung, Provider-API,
Dateisystemzugriff, Netzwerkzugriff, Synchronisation, Replikation, Backup,
Verschlüsselung, tatsächliche Original-Löschung, Dokumentanalyse, UI oder
Migration.
