# ADR-0036 – Guardian Succession Architecture

## Status

Beschlossen

## Kontext und Problem

ZONVAA benötigt eine generische Grundlage für nutzerdefinierte,
ereignisgesteuerte Berechtigungsübergaben. Der Todesfall ist der erste
vorgesehene Anwendungsfall, darf aber weder eine globale Nachlassfreigabe noch
eine automatische Sonderlogik begründen. Spätere Auslöser können etwa
Geschäftsunfähigkeit, das Wirksamwerden einer Vorsorgevollmacht,
Unternehmensnachfolge, Stiftungsübergabe oder ein ausdrücklich
nutzerdefiniertes Ereignis sein.

ADR-0030 trennt Gespräch, Artefakt und autorisierte Handlung. ADR-0032 hält
Wissen personen-, quellen- und zeitgebunden. ADR-0033 verlangt
nutzerkontrollierte Originaldaten und Referenzen statt zentraler Kopien. Ohne
einen typisierten Default-Deny-Vertrag könnten Ereignismeldungen,
Beziehungen, Wahrscheinlichkeiten oder unvollständige Angaben
stillschweigend als Nutzerwille behandelt werden.

## Entscheidung

Guardian Succession wird als generische Capability für ereignisgesteuerte
Berechtigungsübergaben entwickelt. Der Tod eines Nutzers ist lediglich der
erste konkrete Anwendungsfall. Der Guardian trifft keine eigene
Freigabeentscheidung, sondern führt ausschließlich zuvor ausdrücklich
definierte, gültige und verifizierte Nutzeranordnungen aus.

Das neue Paket `guardian_succession` enthält unveränderliche, typisierte
Domänenmodelle und eine deterministische Release-Eligibility-Prüfung. Es
besitzt keine Persistenz, keine Runtime-Mutation und keine technische
Freigabeoperation.

## Architekturprinzipien

### Default Deny und Nutzeranordnung

Ohne vollständig erfüllte Bedingungen gilt `NO_RELEASE`. Ein Ereignis allein
erzeugt keine Freigabe. Fehlende oder widersprüchliche Angaben werden nicht
ergänzt, interpretiert oder priorisiert.

Eine `SuccessionDirective` trennt Anordnungs-ID, Owner, Ereignistyp,
Begünstigtenreferenz, konkrete `ResourceGrant`-Objekte, Freigabeumfang,
Verifikationsbedingungen, Status, Revision, Zeitpunkte, Widerruf und
Auditreferenzen. Der einzige Freigabeumfang
`EXPLICIT_RESOURCE_GRANTS` begrenzt die Anordnung konstruktiv auf ihre
einzelnen Grants; es gibt keine Operation „alle Daten freigeben“.

Jeder `ResourceGrant` bezeichnet genau eine logische Ressourcenreferenz,
einen neutralen Ressourcentyp, eine Zugriffsart und einen Begünstigten. Er
enthält die Ressource nicht. `DECRYPT` und `TRANSFER_CONTROL` sind lediglich
Vertragswerte; sie implementieren weder Kryptografie noch Schlüsselübergabe.

### Guardian ohne Entscheidungsgewalt

Der Guardian leitet weder Begünstigte noch Ressourcen oder Umfang aus
Beziehungen, Erinnerung, Wahrscheinlichkeit oder Ereignismeldung ab.
Eligibility ist eine strukturelle Vorprüfung und keine Autorisierung einer
technischen Aktion.

### Externe Verifikation

`VerificationStatus` unterscheidet `UNKNOWN`, `PENDING`, `VERIFIED` und
`REJECTED`. Das Modell konsumiert diesen Status, prüft aber keine
Sterbeurkunde, Identität, Behörde, notarielle Aussage oder andere Evidenz.
Evidenz bleibt eine logische Referenz und wird nicht eingebettet.

> Eine verifizierte Todesmeldung ist notwendig, aber nicht hinreichend für
> eine Freigabe.

> Ohne vorherige aktive, konkrete und nicht widerrufene Nutzeranordnung
> erfolgt keine Freigabe.

> Der Guardian besitzt keine Befugnis, Empfänger, Ressourcen oder
> Freigabeumfang selbst zu bestimmen.

## Domänenmodell

- `SuccessionEventType` umfasst neutral `DEATH`, `INCAPACITY`,
  `POWER_OF_ATTORNEY_EFFECTIVE`, `BUSINESS_SUCCESSION`,
  `FOUNDATION_TRANSFER` und `CUSTOM`. Die Werte definieren keine Fachlogik.
- `SuccessionEvent` trennt Ereignis-ID, Typ, betroffene Identität,
  Lebenszyklusstatus, Meldezeit, externen Verifikationsstatus und optionale
  Evidenzreferenzen.
- `BeneficiaryReference` referenziert ausdrücklich eine Identität oder Rolle.
  Beziehung oder Familienstatus erzeugen keine implizite Berechtigung.
- `ResourceGrant` ist objektbezogen. Mehrere Begünstigte werden durch
  getrennte Anordnungen und Grants getrennt gehalten.
- `ReleaseCondition` verlangt einen externen `VERIFIED`-Status.
- `SuccessionDirective` besitzt `DRAFT`, `ACTIVE`, `REVOKED`, `SUPERSEDED`
  oder `EXECUTED`, eine positive Revision und unveränderte Zeitbezüge.
- `SuccessionDirectiveHistory` bewahrt jede Revision als eigenes,
  unveränderliches Objekt. Revisionen sind lückenlos. `REVOKED` und
  `EXECUTED` sind terminal und können nicht reaktiviert werden.
- `ReleaseEligibility` enthält Entscheidung, boolesche Eligibility,
  typisierte Blocker, offene Bedingungen, Directive-/Event-ID und Prüfzeit.
  `authorized_actions` bleibt leer.
- `SuccessionAuditTrail` bildet eine append-only, chronologische und
  lückenlos nummerierte Folge von `SuccessionAuditEvent`-Objekten.

## Zustandsübergänge und Audit

Der Domänenkern führt keine Transition aus. Er macht
`DIRECTIVE_CREATED`, `DIRECTIVE_UPDATED`, `DIRECTIVE_REVOKED`,
`VERIFICATION_STARTED`, `VERIFICATION_STATUS_CHANGED`,
`RELEASE_ELIGIBILITY_EVALUATED`, `RELEASE_BLOCKED`,
`RELEASE_AUTHORIZED`, `RELEASE_STARTED`, `RELEASE_COMPLETED` und
`RELEASE_FAILED` als Audittypen modellierbar.

Ein Auditereignis enthält ausschließlich IDs, Typ, Reihenfolge,
zeitzonenbewussten Zeitpunkt, Akteursreferenz, sachlichen Grund und weitere
Referenzen. Der Grund ist ein begrenzter technischer Reason-Code statt freier
Dokumentinhalt. Originalnachweise oder Ressourceninhalte sind kein Feld.
Produktive Auditpersistenz ist nicht beschlossen.

## Eligibility

`evaluate_release_eligibility` liefert nur dann `ELIGIBLE`, wenn:

- eine `ACTIVE`-Anordnung vorliegt,
- das Ereignis offen und typgleich ist,
- Ereignis-Subject und Directive-Owner übereinstimmen,
- der externe Status `VERIFIED` ist,
- ein ausdrücklicher Begünstigter existiert,
- mindestens ein konkreter Grant existiert,
- jeder Grant genau diesen Begünstigten referenziert,
- keine Verifikationsbedingung offen ist,
- die Anordnung nicht widerrufen wurde.

Alle anderen Ergebnisse sind `NO_RELEASE` mit typisierten Blockern. Auch
`ELIGIBLE` überträgt keine Daten, startet keine Ausführung und erteilt keine
neue Autorisierung.

## Sicherheits- und Datenschutzgrenzen

- Originaldaten verbleiben gemäß ADR-0033 im nutzerkontrollierten Vault.
- Ressourcen und Evidenz werden ausschließlich logisch referenziert.
- Es gibt keine globale Entschlüsselung, Schlüsselweitergabe oder Komplettkopie.
- Eine Verifikation erzeugt keine globale Nachlassfreigabe.
- Widerrufene und ausgeführte Anordnungen sind terminal.
- Historie wird nicht still überschrieben.
- Auditdaten enthalten keine eingebetteten Originalnachweise.
- Rollen, Verwandtschaft oder Guardian-Wissen erzeugen keine Berechtigung.

## Missbrauchsrisiken

Falsche Ereignismeldungen, kompromittierte Verifikationsquellen,
Identitätstäuschung, unklare Rollen, veraltete Anordnungen,
Ressourcenverwechslung und unzulässige Schlüsselweitergabe bleiben reale
Risiken. Dieses Modell reduziert sie durch Default Deny, explizite Referenzen,
Status- und Revisionsschutz, löst sie aber nicht technisch oder rechtlich.

## Bewusst ausgeschlossene Funktionen

Nicht implementiert werden Datenfreigabe, Dateiübertragung, Kryptografie,
Schlüsselverwaltung, Wallet, Cloud, Benachrichtigung, Sterbeurkundenprüfung,
Register-, Behörden- oder Notarschnittstelle, Identitätsprüfung,
Begünstigten-Onboarding, UI, API, Datenbank, externe Persistenz,
Rechtsbewertung, testamentarische Auslegung, Erbenauswahl,
Pflichtteilsberechnung oder automatische Guardian-Entscheidung.

## Erweiterungspunkte

Eigene spätere Architekturentscheidungen benötigen konkrete
Todesfallverifikation, Identitätsprüfung der Begünstigten, kryptografische
Schlüsselübergabe, tatsächliche Ressourcenfreigabe, externe Persistenz,
Notar- und Behördenintegration, Recovery unterbrochener
Succession-Ausführungen sowie rechtliche und länderspezifische Regeln.
`CUSTOM` führt ohne konkrete aktive Anordnung und externe Verifikation
ebenfalls zu keiner Freigabe.

## Konsequenzen

- Der Todesfall bleibt Anwendungsfall statt Sonderarchitektur.
- Nutzerwille, Ereignis, externe Verifikation, Eligibility und technische
  Ausführung bleiben getrennt.
- Der Vertrag ist offline, deterministisch und Python-3.9-kompatibel.
- ADR-0030 bleibt Autorisierungsgrundlage, ADR-0032 bleibt Wissensgrenze und
  ADR-0033 bleibt Datenbesitz- und Referenzgrenze.
- RuntimeManager und KnowledgeManager werden nicht verändert, weil dieser
  Auftrag weder aktiven Runtime-Zustand noch Wissenspersistenz einführt.

## Teststrategie

Tests prüfen stabile Enums, Unveränderlichkeit, zeitzonenbewusste Zeitpunkte,
Default Deny für fehlende, unbestätigte, abgelehnte, widerrufene, typfremde
oder unvollständige Anordnungen, objektbezogene Grants,
Begünstigtenisolation, terminale Revisionen, append-only Auditordnung,
Referenzen statt Originalinhalten, deterministische Wiederholung und das
Ausbleiben technischer Ausführung.
