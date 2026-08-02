# ADR-0048 – Guardian Authority Model v1

## Status

Accepted

## Kontext

Constitution, Governance Charter, Artifact Authorization und ADR-0047 trennen
Nutzerhoheit, Governance, operative Umsetzung, deterministischen Kern,
Guardian-Gespräch und professionelle Entscheidung. Bislang fehlt ein
gemeinsamer typisierter Nachweis, der diese Befugnisarten, Akteursklassen,
Verantwortungsgrenzen und Delegationsregeln beschreibt, ohne selbst eine
Befugnis zu erteilen.

## Entscheidung

ZONVAA führt das immutable `GuardianAuthorityModel` als rein beschreibenden,
deterministisch validierbaren Architekturvertrag ein. Das Modell führt
Authority-Typen, abstrakte Akteursklassen, Verantwortlichkeiten, zulässige und
verbotene Authority-Referenzen, nicht delegierbare, delegierbare und gemeinsam
auszuübende Befugnisse, Kontrollstufen, Widerrufbarkeit, verbotene
Befugniskombinationen, Provenienz und Reviewstatus.

Akteursklassen bezeichnen ausschließlich Rollenklassen. Sie benennen und
autorisieren keine Person, Organisation, Fachperson, Modellinstanz oder keinen
Provider. Ein im Modell als zulässig beschriebener Verantwortungsbereich ist
keine konkrete Zuweisung und keine Handlungsvollmacht.

## Vertragsstruktur

Eine `AuthorityDefinition` beschreibt genau eine Befugnisart, ihre
Verantwortung, ihre typisierten Fähigkeiten, ihre Ausübungsform,
Widerrufbarkeit, erforderliche Kontrollstufen und bei gemeinsamer Ausübung die
beteiligten Akteursklassen.

Eine `ActorResponsibilityBoundary` partitioniert für eine Akteursklasse jede
im Modell vorhandene Authority-Referenz ausdrücklich in zulässig oder verboten.
Sie ist eine Verantwortungsgrenze, keine Autorisierung.

Eine `AuthorityDelegationRule` beschreibt ausschließlich eine zulässige
Delegationsbeziehung zwischen abstrakten Akteursklassen. Sie delegiert keine
konkrete Befugnis. Nicht delegierbare und gemeinsam auszuübende Befugnisse
dürfen keine Delegationsregel besitzen. Widerrufbarkeit bleibt an der
Authority-Definition gebunden.

Eine `ProhibitedAuthorityCombination` verhindert, dass eine einzelne
Akteursklassengrenze zwei ausdrücklich unvereinbare Befugnisse zugleich als
zulässig führt.

## Validierung

Der Validator prüft ausschließlich Struktur und typisierte Konsistenz:

- globale Eindeutigkeit aller Vertragsidentitäten,
- vollständige und bekannte Authority-Referenzen,
- widerspruchsfreie Verantwortungsgrenzen,
- verbotene Befugniskombinationen,
- Delegation nur bei delegierbaren Befugnissen,
- Übereinstimmung der Widerrufbarkeit,
- erforderliche Grenzen und Mehrparteienkontrolle für gemeinsame Befugnisse,
- gemeinsame Provenienz und konsistenten Reviewstatus,
- ausschließlich die nicht ausführende Modellfähigkeit.

Bei Erfolg wird dasselbe unveränderte Modellobjekt zurückgegeben. Der Validator
ergänzt, delegiert, aktiviert oder widerruft keine Befugnis.

## Abgrenzung

### Provider-Autorisierung

Das Authority Model dokumentiert abstrakte Akteursklassen und Grenzen. Es prüft
weder Identität, Qualifikation, Vertrauen noch Berechtigung eines konkreten
Providers und erzeugt keine Provider-Autorisierung.

### Runtime

Das Modell besitzt keine Runtime, keinen Service-, Registry-, Repository- oder
Persistenz-Layer. Es startet keine Handlung und verändert keinen Zustand.

### LLM-Klassifikation

Das Modell interpretiert keine Nutzereingabe, klassifiziert keine Anfrage und
integriert kein LLM. Akteursklasse, Authority-Typ und sämtliche Referenzen
werden bereits typisiert bereitgestellt.

### Werkzeugaktivierung

Keine Authority-Definition und keine Delegationsregel aktiviert Werkzeug,
Domäne, Workflow, Routing, Recherche, Antworterzeugung, Resolution oder
Freigabe. Das Modell beschreibt Grenzen; es setzt sie nicht ausführend um.

## Verhältnis zu bestehenden Verträgen

Constitution und Governance Charter bleiben unverändert. Der
Artefakt-Autorisierungsvertrag bleibt allein für konkrete Artefaktzustände und
Autorisierungen zuständig. ADR-0047 und die Guardian-Answer-Verträge behalten
ihre Schichtentrennung und erhalten aus diesem Modell keine neue Macht.

## Nicht-Ziele

- keine konkrete Provider-, Personen- oder Rollenautorisierung,
- keine Runtime, Klassifikation oder natürliche Sprachverarbeitung,
- keine Antwortgenerierung, Recherche oder Quellenbeschaffung,
- keine Workflow-, Werkzeug-, Domänen- oder Routingaktivierung,
- keine Zustandsänderung, Resolution oder Freigabe,
- keine Persistenz,
- keine UI und keine rechtliche oder professionelle Wirkungsbehauptung.

## Konsequenzen

Die Authority-Architektur ist als unveränderlicher Vertrag reviewbar, ohne eine
zweite Autorisierungs- oder Ausführungsschicht zu schaffen. Konkrete
Zuweisungen, Providerzulassungen und Runtime-Durchsetzung benötigen jeweils
eigene begrenzte Architekturentscheidungen und Implementierungsaufträge.
