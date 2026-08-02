# ADR-0049 – Guardian Provider Authorization Package v1

## Status

Accepted

## Zweck

Das Guardian Provider Authorization Package bindet abstrakte Befugnisse aus
ADR-0048 kontrolliert an bereits bereitgestellte konkrete Provider-Identitäten.
Es dokumentiert Identität, Zuordnung, Entscheidungsevidenz und explizite
Lifecycle-Nachweise, ohne eine Capability auszuführen oder eine Runtime zu
starten.

## Provider-Identitätsmodell

Eine immutable `ProviderIdentity` führt Provider-ID und -Typ, eine rechtliche
oder technische Identitätsreferenz, die bereits zugeordnete abstrakte
Akteursklasse, Verantwortungsbereich, unterstützte Authority-Typen,
Herkunftsnachweis, Identitätsprüf- und Reviewstatus, Gültigkeitszeitraum,
Unsicherheit, Provenienz und eine optionale deklarative Vorgängerreferenz.

Provider-Typ und Identitätsprüfstatus sind beschreibende Nachweise. Sie
autorisieren nichts, bewerten kein Vertrauen und bestätigen weder rechtliche
Identität noch Qualifikation.

## Verhältnis zu ADR-0048

Authority-Typen, Akteursklassen, Capabilities, Verantwortungsgrenzen,
Delegationsregeln, gemeinsame Akteursklassen, Kontrollstufen, Widerrufbarkeit,
Provenienz und Reviewstatus werden ausschließlich aus ADR-0048 wiederverwendet.
Es entsteht keine zweite Authority-, Capability- oder Kontrollhierarchie.

Der Provider passt nur, wenn seine bereitgestellte Akteursklasse in der
vorhandenen `ActorResponsibilityBoundary` die Authority zulässt. Eine
delegierbare Zuordnung benötigt zusätzlich die vorhandene passende
`AuthorityDelegationRule`. Nicht delegierbare und gemeinsam auszuübende
Befugnisse werden nicht über eine Delegationsregel umgedeutet.

## Autorisierungsnachweis

Ein immutable `ProviderAuthorizationGrant` dokumentiert Provider-, Authority-
und Verantwortungsgrenzenreferenz, vollständig erlaubte und verbotene
Capabilities, Status, Gültigkeit, Kontrollen, gemeinsame Akteursklassen,
Delegierbarkeit, Widerrufbarkeit, erteilende Authority- oder
Delegationsregelreferenz, Review, Unsicherheit, Provenienz und optionalen
Vorgänger.

Unterstützte Statuswerte sind `PROPOSED`, `AUTHORIZED`, `REJECTED`,
`SUSPENDED`, `REVOKED` und `EXPIRED`. Ausschließlich ein ausdrücklich
bereitgestellter Status `AUTHORIZED` beschreibt eine gültige Autorisierung.
Der Status löst keine Capability aus und wird nicht aus Datum oder Kontext
berechnet.

## Entscheidungsevidenz

`AuthorizationDecisionEvidence` dokumentiert eine bereits getroffene
Entscheidung mit Grund, geprüften Authority-Regeln und Grenzen, festgestellten
Konflikten, erforderlichen Kontrollen, typisierten entscheidenden
Akteursreferenzen, Zeitpunkt, Review und Provenienz. Die Evidenz trifft keine
Entscheidung und ergänzt keine Akteursklasse.

Gemeinsam auszuübende Befugnisse verlangen, dass die bereits bereitgestellte
Entscheidungsevidenz sämtliche in ADR-0048 geforderten Akteursklassen enthält.

## Widerruf, Aussetzung, Ablauf und Wiederherstellung

Widerruf, Aussetzung, Ablauf und Wiederherstellung besitzen getrennte immutable
Nachweise. Jeder Nachweis führt Authorization, Grund, wirksamen Zeitpunkt,
entscheidende Authority-Referenz, Kontrollstufen, Vorgänger- und Zielstatus,
Review und Provenienz.

- Widerruf und Ablauf beenden die Gültigkeit.
- Aussetzung verhindert einen gültigen `AUTHORIZED`-Status.
- Wiederherstellung ist nur nach dokumentierter Aussetzung, zeitlich danach und
  innerhalb des unveränderten Gültigkeitszeitraums zulässig.
- Es gibt keine rückwirkende Wiederherstellung, automatische Verlängerung,
  Reautorisierung oder Ersatzproviderauswahl.
- Ein abgelaufenes Datum berechnet keinen Status. `EXPIRED` benötigt einen
  ausdrücklich bereitgestellten Ablaufnachweis.

## Kontroll-, Konflikt- und Gültigkeitsregeln

Der Paketvalidator verwendet zuerst unverändert den Authority-Validator aus
ADR-0048. Danach prüft er eindeutige IDs, bekannte Referenzen, vollständige
Capability-Grenzen, Akteurs- und Verantwortungsgrenzen, Delegationsregel,
Kontrollstufen, gemeinsame Akteursklassen, Widerrufbarkeit, Provider- und
Grant-Gültigkeit, Status-/Entscheidungskonsistenz, Lifecycle-Nachweise,
Provenienz und Reviewstatus.

Zeitlich überlappende gültige Zuordnungen derselben Authority an denselben
Provider sowie in ADR-0048 verbotene Kombinationen werden abgelehnt. Konflikte
werden weder priorisiert noch automatisch gelöst.

## Resolution Snapshot

Der immutable `ProviderAuthorizationResolutionSnapshot` ist eine read-only
Darstellung bereits bereitgestellter Zustände. Er erhält die Originalobjekte
für Provider und Autorisierungen und zeigt getrennt gültige, ausgesetzte,
widerrufene und abgelaufene Nachweise sowie Capabilities, Kontrollstufen,
Verantwortungsgrenze, Review, Unsicherheit und Provenienz.

Der Snapshot erteilt, verändert, verlängert oder aktiviert nichts. Seine
Kategorien stammen ausschließlich aus den ausdrücklich bereitgestellten
Statuswerten; es gibt keine zeitabhängige Statusberechnung.

## Abgrenzung zur Runtime

Das Paket besitzt keine Runtime, keinen Provider-Aufruf, keine Capability-
Aktivierung, kein Routing, keine Workflow- oder Werkzeugaktivierung und keinen
Zustandsautomaten. Validierung gibt dieselben unveränderten Vertragsobjekte
zurück.

## Abgrenzung zu IAM und RBAC

Das Paket ist keine allgemeine IAM-, RBAC- oder Policy-Engine. Es verwaltet
keine Accounts, Rollenbindungen, Credentials, Secrets, Tokens, Sessions oder
Zugriffsprüfungen. Es implementiert ausschließlich den begrenzten
Guardian-Provider-Nachweis gegen ADR-0048.

## Abgrenzung zu Auswahl und Vertrauensbewertung

Provider werden vollständig typisiert bereitgestellt. Das Paket erkennt,
bewertet, priorisiert oder wählt keinen Provider und prüft keine fachliche,
rechtliche oder technische Vertrauenswürdigkeit außerhalb der bereitgestellten
Nachweise.

## Nicht-Ziele

- keine Runtime oder Ausführung autorisierter Capabilities,
- keine natürliche Sprach- oder LLM-Klassifikation,
- keine Antwortgenerierung oder Prompting,
- keine Recherche, Quellenbeschaffung oder Quellenbewertung,
- keine Provider-Erkennung, -Auswahl oder Vertrauensbewertung,
- keine automatische Autorisierung, Verlängerung oder Reautorisierung,
- keine automatische Konfliktlösung oder Statusberechnung,
- keine Werkzeug-, Workflow-, Domänen- oder Routingaktivierung,
- keine Triage, Kontaktaufnahme oder fachliche Entscheidung,
- keine Persistenz, UI, Netzwerk-, Secret-, Credential- oder Token-Verwaltung,
- keine allgemeine IAM-, RBAC-, Policy- oder Runtime-Architektur.

## Konsequenzen

Provider-Autorisierungen sind als immutable Nachweis vollständig reviewbar,
ohne daraus Ausführungsmacht abzuleiten. Eine spätere Runtime-Durchsetzung,
Providerintegration oder Credential-Verwaltung benötigt jeweils eine eigene
Architekturentscheidung und einen gesonderten begrenzten Auftrag.
