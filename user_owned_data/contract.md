# ZONVAA User-Owned Data Contract

Version: 1.0
Status: abgeleiteter technischer Vertrag
Normstufe: C2/C3

Normative Entscheidung:
`knowledge/adr/ADR-0033-user-owned-data-architecture.md`

## Architekturgrenze

ZONVAA ist eine Intelligence Layer.

Nicht die Dokumentenplattform.

Der Nutzer besitzt die Daten.

ZONVAA besitzt Wissen über freigegebene Daten.

Der User-Owned Data Layer ist kein Speicherprodukt. Er beschreibt ausschließlich
providerneutrale Referenzen, Eigentums-, Autorisierungs-, Verfügbarkeits- und
Retention-Grenzen. Er liest, kopiert, synchronisiert oder löscht keine Datei.

## Eigentum und Kontrolle

Originaldaten gehören dem Nutzer. Der Nutzer bestimmt Speicherort, Zugriff,
Export und Löschung. ZONVAA darf weder Eigentum noch Verfügungsgewalt aus einer
Referenz, einem Gespräch oder einer technischen Erreichbarkeit ableiten.

Local First, User Ownership, User Controlled Storage, Reference before Copy,
Minimal Metadata, No Central Document Storage, Explicit Consent, Privacy by
Design, Delete by Design und Provider Independence sind verbindlich.

## Referenzmodell

`StorageReference` ist unveränderlich, versioniert und enthält ausschließlich:

- Referenz-ID und Owner,
- abstrahierten Provider und Scope,
- logischen Locator,
- optionale Integritätsmetadaten,
- Erstellungs- und letzten Prüfzeitpunkt,
- explizite, an die Referenz gebundene Autorisierung,
- optionale, separat nachgewiesene Provider-Fähigkeiten,
- Retention und Verfügbarkeit.

Der Locator ist eine begrenzte einzeilige logische Referenz. Er enthält keine
Originaldaten und führt keinen Zugriff aus. Checksum-Metadaten werden nur
validiert; ZONVAA liest keine Datei, um sie in diesem Layer zu berechnen.

## Provider-Neutralität

`LOCAL_FOLDER`, `NAS`, `PRIVATE_CLOUD`, `SELF_HOSTED_SERVER`,
`EXTERNAL_CONNECTOR` und `UNKNOWN` werden gleichrangig modelliert. Der Vertrag
bevorzugt keinen Anbieter und kennt keine anbieterspezifische API.

Remote Provider sind optional. Ein lokaler oder derzeit unbekannter Speicher
bleibt ein gültiger Referenzkontext.

## Autorisierung

Autorisierung stammt aus dem bestehenden Artefakt- und
Autorisierungszustandsvertrag. `ReferenceAuthorization` begrenzt eine aktive
`ArtifactAuthorization` zusätzlich auf genau eine Referenz und konkrete
Storage-Operationen. Jede `StorageReference` benötigt eine solche Freigabe
mindestens für `REFERENCE`.

Referenzieren, Lesen, Kopieren, Synchronisieren, Exportieren, Löschen eigener
Metadaten und Löschen des Originals sind getrennte Operationen. Keine Operation
ist aus einer anderen impliziert. Gemeinsame Scopes benötigen eine ausdrückliche
aktive Autorisierung. Ein Gespräch erzeugt keine Speicherberechtigung.

## Synchronisation und Kopien

Es gibt keine automatische Synchronisation, Replikation, Cloud-Spiegelung oder
Kopie. `COPY` und `SYNCHRONIZE` dürfen nur nach einer aktiven, zweckgebundenen
Autorisierung geplant werden. Dieser Vertrag führt sie nicht aus.

## Löschung und Retention

ZONVAA löscht ohne gesonderte Original-Löschautorisierung ausschließlich eigene
Metadaten. Eine Original-Löschung setzt nachweisbares Nutzereigentum, einen
erreichbaren Speicher, eine separate Fähigkeitsevidenz des Providers sowie eine
ausdrückliche Autorisierung für `DELETE_ORIGINAL` voraus.

Retention verwendet die Guardian-Runtime-Klassen. Zeit- und
Aufbewahrungsbindungen bleiben explizit. Historie macht Originaldaten nicht
pauschal unlöschbar; eine Referenz beweist aber auch nicht, dass eine externe
Originaldatei tatsächlich gelöscht wurde.

## Offlinefähigkeit

Vertragsladen, Modellvalidierung und Guardian Runtime funktionieren ohne
Internet. Cloud- oder Connector-Zugriffe sind optionale spätere Adapter und
keine Voraussetzung für Boot oder Preflight.

## Runtime- und Knowledge-Grenze

RuntimeManager lädt nur diesen statischen Vertrag, keine User-Vault-Inhalte.
KnowledgeManager bleibt einzige Wissensschnittstelle und validiert typisierte
Referenzen ohne Zugriff auf den Locator.

Guardian Runtime speichert typisierte Wissenseinheiten, Provenienz,
Referenz-IDs, Zustände, Autorisierungen und minimale Metadaten. Sie speichert
keine vollständigen Originaldokumente, Bildarchive, Videosammlungen oder
PDF-Sammlungen. `KnowledgeItem.content_reference` bezeichnet eine logische
Referenz und keine eingebettete Kopie.

## Nicht implementiert

Nicht Bestandteil sind User Vault, Dateimanager, Cloud Drive,
Dokumentenhosting, Provider-Adapter, Dateisystemzugriff, Netzwerkzugriff,
Synchronisation, Replikation, Backup, Verschlüsselung, Original-Löschung,
Migration, Dokumentanalyse, UI oder zentrale Dokumentenpersistenz.
