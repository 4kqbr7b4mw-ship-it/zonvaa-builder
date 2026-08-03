# ADR-0061 – Guardian B2 Provider Identity v1

Status: VORGESCHLAGEN – NICHT RATIFIZIERT

## 1. Kontext und Entscheidungsgrenze

ADR-0058 trennt B2 kategorial von B1. ADR-0059 begrenzt den Datenkorridor;
ADR-0060 begrenzt B2 Authority, Grants und deren zustandslose Evaluation.
Keines dieser Dokumente definiert, wie eine spätere B2-Architektur eine
nicht personenbezogene Provider-Identität beschreiben dürfte.

ADR-0061 entscheidet deshalb ausschließlich die Architektur eines immutable,
nicht autorisierenden B2 Provider Identity Model. Sie implementiert keinen
Vertrag, ratifiziert keine Architektur und erteilt keine institutionelle
Implementierungsfreigabe. Institutionelle Beschlüsse bleiben durch
`GOV-INSTITUTIONAL-DECISION-SCOPE-1` begrenzt.

## 2. Verhältnis zum B1 Provider Identity Model

Das B1-Modell aus ADR-0049 besitzt `ProviderType` und `ProviderIdentity`, ist
aber Teil eines gemeinsamen Provider-Authorization-Pakets und führt unter
anderem freie Verantwortungsbeschreibungen, Authority-Typen, Prüfstatus und
zeitliche Gültigkeit. Diese Semantik wird nicht nach B2 übernommen.

B2 erhält eine eigenständige Typfamilie. B1 Provider Identity darf weder
konvertiert, erweitert, vererbt noch als Union-Alternative zugelassen werden.
Es gibt keinen B1→B2-Upgradepfad. Gemeinsam nutzbar bleiben ausschließlich
allgemeine technische Konventionen für immutable Value Objects, geschlossene
Enums, nicht personenbezogene Referenz-IDs, explizite timezone-aware
Zeitpunkte und optionale Vorgängerreferenzen. Daraus entsteht keine gemeinsame
Identitäts-, Vertrauens- oder Autorisierungssemantik.

## 3. B2 Provider Identity Contract

Ein späterer geschlossener B2-Vertrag muss mindestens enthalten:

- eine eigenständige typisierte B2 Provider Identity ID,
- genau eine geschlossene B2 Provider Class,
- mindestens einen geschlossenen Responsibility Code,
- mindestens einen geschlossenen Capability Descriptor,
- eine nicht personenbezogene institutionelle Source ID,
- eine Governance-Decision-ID,
- eine Vertrags- oder Registrierungsgrundlage als typisierte Reference ID,
- einen explizit übergebenen timezone-aware Erstellungszeitpunkt,
- optional eine rein deklarative B2-Vorgängerreferenz.

Der Vertrag enthält keine natürliche Person, keinen Account, keine
Kontaktangabe, keinen freien fachlichen Text, keine Authority, keinen Grant,
keinen Status und keine operative Information. Seine Identität beschreibt nur
eine institutionelle, fachliche oder technische Leistungseinheit. Sie beweist
weder Existenz, Qualifikation, Vertrauen, Autorisierung noch Ausführbarkeit.

## 4. Geschlossene Provider Classes v1

Die folgende Menge ist für v1 vollständig und abschließend:

- `INSTITUTIONAL_SERVICE_UNIT`
- `PROFESSIONAL_ROLE_UNIT`
- `MODEL_SERVICE_UNIT`
- `RESEARCH_SERVICE_UNIT`
- `TECHNICAL_TOOL_SERVICE_UNIT`

`PROFESSIONAL_ROLE_UNIT` bezeichnet ausschließlich eine typisierte
institutionelle oder fachliche Rollenstelle beziehungsweise Leistungseinheit.
Sie bezeichnet niemals eine konkrete natürliche Person. Namen, Personenkonten,
Kontaktdaten und personenbezogene Akteursbindungen sind strukturell
ausgeschlossen.

`MODEL_SERVICE_UNIT` bezeichnet ausschließlich eine institutionelle fachliche
Modellierungs- oder Unterstützungseinheit. Die Klasse bezeichnet weder ein
ML-Modell noch ein Datenmodell, einen Modellprozess, Tool-Aufruf oder eine
Runtime-Identität und besitzt keinerlei technische Modell- oder
Ausführungssemantik.

`TECHNICAL_TOOL_SERVICE_UNIT` bezeichnet ausschließlich eine typisierte
institutionelle technische Leistungseinheit. Die Klasse ist kein Tool-Aufruf,
keine Invocation und keine Runtime-Identität und verleiht keinerlei
Ausführungsmacht.

Keine Klasse darf frei oder dynamisch ergänzt werden. Jede Erweiterung dieser
Menge benötigt einen neuen institutionellen Architekturakt.

## 5. Typisiertes Verantwortungsbereichsmodell

Verantwortungsbereiche werden ausschließlich durch die folgende geschlossene
Menge nicht personenbezogener Codes beschrieben:

- `GENERAL_ORIENTATION_SUPPORT`
- `PERSONAL_PREPARATION_SUPPORT`
- `PROFESSIONAL_REVIEW_PREPARATION_SUPPORT`
- `SOURCE_REFERENCE_SUPPORT`

Die Codes beschreiben nur den institutionell registrierten
Verantwortungsbereich der Identität. Sie autorisieren keine Verarbeitung und
bezeichnen keinen Zugriff. Freitext, lokalisierte Bezeichnungen und freie
fachliche Beispiele sind keine gespeicherte Semantik.

Das Repository besitzt derzeit keinen ratifizierten kanonischen
Life-Domain-Typ oder jurisdiktionstreuen Domain-Identifier. Der registrierte
Kandidat Guardian Life Domain Model ist ausdrücklich ruhend. ADR-0061 nimmt
ihn nicht vorweg und führt deshalb keine Domänen- oder Jurisdiktionsreferenz in
den v1-Vertrag ein. Sprache bleibt Darstellung, niemals Datenmodell.

## 6. Geschlossenes Capability-Descriptor-Modell

Capabilities sind für v1 ausschließlich beschreibende, geschlossene
Descriptoren:

- `GENERAL_ORIENTATION_SERVICE_DESCRIPTOR`
- `PERSONAL_PREPARATION_SERVICE_DESCRIPTOR`
- `PROFESSIONAL_REVIEW_PREPARATION_DESCRIPTOR`
- `SOURCE_REFERENCE_SERVICE_DESCRIPTOR`

Ein Descriptor dokumentiert ausschließlich eine institutionell bereitgestellte
Funktionsbeschreibung. Er ist kein Token, Grant, Permission, ausführbarer
Funktionsverweis oder Boolean-Permission. Er enthält und erzeugt keine
Autorisierung, Berechtigung, Aktivierung, Invocation, Runtime, Schlüssel- oder
Inhaltszugriff und keinen operativen Status.

Freie Capability-Texte und beliebige Strings mit fachlicher Bedeutung sind
unzulässig. Änderungen der Descriptor-Menge benötigen einen neuen
institutionellen Architekturakt.

## 7. Nicht personenbezogenes Provenienzmodell

Die Provenienz ist ein eigenes immutable Value Object und darf ausschließlich
enthalten:

- eine typisierte institutionelle Source ID,
- eine Governance-Decision-ID,
- eine typisierte Vertrags- oder Registrierungsgrundlage,
- eine nicht personenbezogene Reference ID,
- den explizit übergebenen timezone-aware Erstellungszeitpunkt.

Es gibt keinen Aussteller als natürliche Person, keinen freien
Provenienztext, Namen, Kontaktdaten, selbst bestätigte Identität, versteckte
Systemzeit oder implizite Vertrauensannahme. Der Zeitpunkt ist reiner Input;
kein Konstruktor oder Validator darf `now()` oder eine globale Uhr lesen.

## 8. Versionierung

Das vergleichbare B1-`ProviderIdentity` besitzt keine kanonische
`schema_version`; es verwendet nur eine optionale deklarative
Vorgängerreferenz. Andere Repository-Verträge nutzen Versionen jeweils lokal
für ihren eigenen Vertragszweck. Daraus folgt keine allgemeine, auf B2
Provider Identity übertragbare Schema-Versionierung.

ADR-0061 führt deshalb kein `schema_version`-, Vertragsversions- oder
Modellversionsfeld ein. `v1` bezeichnet ausschließlich diese
Architekturentscheidung. Eine optionale Vorgängerreferenz folgt dem bereits
vorhandenen Identitätsmuster, erzeugt aber weder Migration noch Konvertierung.

## 9. Strukturelle Invarianten

Ein späterer Vertrag muss durch geschlossene Typen ausschließen:

- freie, unbekannte oder dynamische Provider Classes,
- natürliche Personen, Personenkonten oder Kontaktdaten,
- freien Verantwortungs-, Capability- oder Provenienztext,
- Provider Class oder Identity aus der B1-Typfamilie,
- B1→B2-Konvertierung, Upgrade, Migration oder Vererbung,
- Authority-, Grant-, Authorization- oder Permission-Felder,
- Aktiv-, Gültigkeits-, Widerrufs-, Vertrauens- oder Qualifikationsstatus,
- Invocation-, Runtime-, Session-, Cache- oder Token-Felder,
- Schlüssel-, Credential-, Secret- oder Inhaltszugriff,
- personenbezogene Inhalte oder Akteursbindungen,
- implizite Zeit, selbst bestätigte Identität oder automatische Erkennung,
- freie oder stillschweigende Erweiterung geschlossener Mengen.

Ein nachgelagerter Warnhinweis genügt nicht. Lässt ein Implementierungsentwurf
einen dieser Zustände zu, ist dies ein Architekturblocker.

## 10. Negative Provider Identity Rules

Eine B2 Provider Identity darf insbesondere nicht:

- eine konkrete natürliche Person repräsentieren,
- einen Provider autorisieren, auswählen, priorisieren oder aktivieren,
- fachliche Qualifikation, Vertrauen oder Eignung bestätigen,
- einen B2 Grant tragen oder dessen Wirksamkeit beeinflussen,
- Capability Invocation oder Runtime vorbereiten oder auslösen,
- Schlüssel, Credentials, Secrets, Tokens oder Sessions referenzieren,
- Inhaltszugriff oder personenbezogene Verarbeitung beschreiben,
- freie Capability-, Verantwortungs- oder Provenienztexte führen,
- sich selbst bestätigen oder einen aktuellen Zustand selbst ermitteln,
- als B1 Provider Identity verwendet oder aus ihr erzeugt werden.

## 11. Referenzszenarien

Spätere Tests dürfen ausschließlich synthetische, nicht personenbezogene Werte
verwenden. Zulässige Szenarien sind beispielsweise:

1. `b2-provider-identity:institutional-unit-01` mit
   `INSTITUTIONAL_SERVICE_UNIT`, `GENERAL_ORIENTATION_SUPPORT` und
   `GENERAL_ORIENTATION_SERVICE_DESCRIPTOR`.
2. `b2-provider-identity:professional-role-unit-01` mit
   `PROFESSIONAL_ROLE_UNIT`, `PROFESSIONAL_REVIEW_PREPARATION_SUPPORT` und
   `PROFESSIONAL_REVIEW_PREPARATION_DESCRIPTOR`.
3. Ablehnung einer unbekannten Provider Class.
4. Ablehnung einer natürlichen Person oder Personenkontaktreferenz.
5. Ablehnung freien Verantwortungs-, Capability- oder Provenienztexts.
6. Ablehnung jedes Authority-, Authorization-, Invocation-, Runtime-,
   Schlüssel- oder Inhaltszugriffsfelds.
7. Ablehnung einer B1 Identity oder B1→B2-Konvertierung.
8. Nachweis, dass der explizite Erstellungszeitpunkt unverändert übernommen
   und keine Systemzeit gelesen wird.

Die Szenarien speichern keine Namen, Kontakte oder fachlichen Freitexte.

## 12. Weiterhin gesperrt

Nicht Gegenstand und nicht freigegeben bleiben:

- B2 Provider Authorization,
- B2 Capability Invocation,
- B2 Runtime und technische Grant-Ausführung,
- personenbezogene Akteursbindung, Verarbeitung oder Speicherung,
- Key Custody, Schlüsselverwaltung, Credentials und Secrets,
- Inhaltszugriff,
- Sessions, Caches und Tokens,
- Observation und Runtime Audit,
- Operational Memory, Metrics und Notifications,
- externe oder produktive Integrationen.

## 13. Governance-Sequenz und Nicht-Ziele

ADR-0061 ist vorgeschlagen und nicht ratifiziert. Sie ist keine
institutionelle Implementierungsfreigabe. Eine spätere Implementierung
verlangt getrennt:

1. Architekturvalidierung,
2. ausdrückliche menschliche Ratifizierung,
3. gesonderte institutionelle Implementierungsfreigabe mit den Abschnitten
   `Freigegeben` und `Ausdrücklich nicht freigegeben`,
4. ausdrückliche menschliche Bestätigung dieser Freigabe,
5. separaten Codex-Implementierungsauftrag.

Diese ADR implementiert keine Klasse, Enum, Value Object, API, Runtime,
Provider Authorization, Invocation, Verarbeitung oder Speicherung und ändert
weder ADR-0060 noch bestehende Implementierungsfreigaben.

## 14. Abschlussprüfung

Die dokumentierte Architektur erlaubt ausschließlich eine nicht
personenbezogene, beschreibende Identität mit geschlossenen Klassen, Codes,
Descriptoren und Provenienzreferenzen. Sie enthält keine Autorisierungs-,
Personen- oder Ausführungssemantik.

Damit lautet die strukturelle Prüffrage:

> Kann durch die dokumentierte Architektur eine B2 Provider Identity bereits
> Autorisierung, personenbezogene Bindung oder ausführbare Macht enthalten?

Antwort: Nein.
