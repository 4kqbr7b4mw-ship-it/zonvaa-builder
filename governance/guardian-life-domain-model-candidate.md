# Guardian Life Domain Model

Dokument-ID: `GOV-ARCH-CANDIDATE-GUARDIAN-LIFE-DOMAIN-1`

Status:

- Registriert
- Nicht geplant
- Nicht implementiert
- Kein Implementierungsauftrag
- Keine Implementierungsfreigabe

Auslöser: Architekturdiskussion zur semantischen Ebene von ZONVAA

## Gegenstand

Der offene Architekturkandidat beschreibt ein mögliches späteres Modell
typisierter, jurisdiktionstreuer Lebensobjekte. Er ist keine
Architekturentscheidung, keine Governance-Regel, keine ADR, kein Vertrag und
keine Produkt-Roadmap-Zusage.

Erster registrierter Kernbereich: Vorsorgevollmacht.

## Dokumentierte Ausnahme zu ADR-0046 E6

Die Registrierung ist eine dokumentierte Ausnahme zu ADR-0046 E6. Der
Kandidat schützt eine grundlegende Verfassungsregel des Datenmodells, obwohl
die produktive B2-Runtime und die spätere Gesprächsschicht noch nicht
vollständig existieren.

Die Ausnahme gilt ausschließlich für die Registrierung dieses Kandidaten. Sie
autorisiert weder Planung noch Aktivierung, Architekturentscheidung oder
Implementierung. ADR-0046 und E6 bleiben unverändert.

## Verfassungskern des Kandidaten

### 1. Typisierte, jurisdiktionstreue Lebensobjekte

Lebensobjekte sind typisierte, jurisdiktionstreue Domänenobjekte. Jedes Objekt
besitzt mindestens:

- eine kanonische Typ-ID,
- ein Jurisdiktionskennzeichen,
- definierte Wirksamkeitsregeln,
- typisierte Relationen.

### 2. Sprache ist ausschließlich Darstellung

Lokalisierung verändert niemals Rechtsnatur, Wirksamkeitsbedingungen,
Semantik oder Identität eines Domänenobjekts.

### 3. Wachstum nur entlang realer Lebensbereiche

Das Domänenmodell wächst ausschließlich entlang realer Lebensbereiche und
validierter Journeys. Theoretische Universalmodelle und eine abstrakte
Vollontologie sind ausgeschlossen. Erweiterungen erfolgen ausschließlich
aufgrund realer Anwendungsfälle.

## Jurisdiktionsgrenze

Internationale Rechtsinstitute sind keine Synonyme. Sie sind eigenständige
typisierte Domänenobjekte. Verknüpfungen zwischen unterschiedlichen
Jurisdiktionen erfordern eigene typisierte Mapping-Objekte und eigene Evidenz.

Diese Registrierung definiert weder Rechtsinstitute noch Mappings oder
juristische Inhalte.

## Aktivierungsbedingungen

Der Architekturkandidat darf erst aktiviert werden, wenn alle folgenden
Voraussetzungen erfüllt sind:

- produktive B2-Runtime,
- stabile Conversation-Architektur,
- dokumentierter Aktivierungsbeschluss.

Vorher bleibt der Kandidat ausdrücklich ruhend.

## Macht- und Freigabegrenze

Aus diesem Kandidaten dürfen derzeit keine Runtime, APIs, Datenbankmodelle,
juristischen Inhalte, Gesprächsführungen oder Implementierungsaufträge
abgeleitet werden. Er erzeugt keine Verträge, Klassen, Provider,
Persistenzmodelle, Werkzeuge, Workflows oder Produktfunktion.
