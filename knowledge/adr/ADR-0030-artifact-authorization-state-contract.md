# ADR-0030 – Artifact Authorization State Contract

## Status

Beschlossen

## Kontext

MDR-0001 und Interaction 1.1 trennen Gespräch, Artefakt und autorisierte
Handlung. Sie schreiben Nutzerhoheit, personengebundene Kontextisolation,
explizite Freigaben, Neutralität in Mehrparteienkonflikten, Export und
Offboarding verbindlich vor. Ein ausführbarer, typisierter Vertrag für
Artefaktzustände, Autorisierungen, Übergangshistorien und deren Datenklassen
fehlt jedoch.

Der Architecture Workflow `workflow-81d7ba505f25f885` hat einen Gemini-Entwurf
zur nutzergerichteten Artefaktinteraktion und einen Kimi-Entwurf zum
Zustandsvertrag getrennt analysiert. Der Chief Architect hat beide mit
`ADOPT_WITH_CHANGES` bestätigt. Diese ADR dokumentiert ausschließlich diese
bestätigte Integration.

## Entscheidung

ZONVAA führt einen kleinen, unveränderlichen und versionierten
Artefakt-/Autorisierungszustandsvertrag ein. Er ist eine technische
Konkretisierung der bestehenden Conversation/Interaction-Grenze und keine
neue Architekturschicht.

Der kanonische Vertrag liegt unter `artifact_contract/contract.md`. Das Paket
`artifact_contract` enthält stabile Enums, unveränderliche Dataclasses und
einen strukturellen Loader. Es führt keine Zustandsänderung aus und speichert
keine Artefakte.

### Zustände und Hoheit

Artefaktzustände sind typisiert und behaupten keine rechtliche Wirksamkeit.
Jeder `ArtifactStateContract` referenziert genau einen verantwortlichen
Hoheitsträger. Weitere Personen werden ausschließlich als explizite
Beteiligte geführt. Beziehung, Familie, Betreuung, Vollmacht oder
Gesprächsteilnahme erzeugen keine Rolle.

Der bestehende `execution.DocumentArtifact` bleibt unverändert. Er bezeichnet
einen technischen Plan zur sicheren Erzeugung neuer Wissensdokumente und ist
kein fachliches Artefakt im Sinne dieser ADR.

### Autorisierung

`ArtifactAuthorization` enthält stabile ID, Beteiligtenreferenz,
Hoheitsträger, granulare Umfänge, Zweck, Status sowie zeitzonenbewusste
Erteilungs- und gegebenenfalls Widerrufszeitpunkte. Autorisierungen werden
nicht aus Strings, Gesprächen oder Beziehungen abgeleitet.

Ein Widerruf wird mit eigenem Zeitpunkt dokumentiert. Er wirkt im
Vertragsmodell unmittelbar, soweit keine dokumentierte rechtliche oder
technische Bindung referenziert ist. Der Vertrag bewertet solche Bindungen
nicht.

### Auditierbare Übergänge

Jeder Zustandswechsel ist ein unveränderlicher `ArtifactTransition` mit
stabiler ID, Artefaktbezug, Ausgangs- und Zielzustand, Typ, Akteur,
zeitzonenbewusstem Zeitpunkt, Begründung, Normstufe und expliziter
Irreversibilität.

Übergänge müssen eine chronologische, lückenlose Kette bilden. Ein
fallfremder Übergang, eine doppelte ID, ein unangekündigter Zustandswechsel
oder eine stille parallele Überschreibung ist ungültig. Neben dem
Hoheitsträger dürfen nur ausdrücklich aktive Beteiligte mit dem Umfang
`authorize_action` einen Übergang autorisieren.

Irreversibilität wird je Übergang dokumentiert. Weder Zustand noch
Dokumentart erzeugen sie automatisch.

### Historienklassen

Historien werden explizit als `immutable`, `retention_required`, `deletable`
oder `anonymizable` klassifiziert. Die Klassifikation legt keine konkrete
Frist oder technische Löschung fest. Damit werden pauschale Unlöschbarkeit
und stille Löschung gleichermaßen vermieden.

### C2 und C3

C2 regelt Prinzipien, Rollen, Vetos und Prüfpflichten. C3 regelt konkrete
Fristen, Gesten, Quoren, Risikoabstufungen und technische Verfahren.
Artefaktübergänge erhalten keinen C1-Rang.

### Runtime und Preflight

Runtime lädt genau einen `ArtifactContractContext` mit Quelle, Version,
SHA-256-Hash und vollständigen stabilen Typmengen. Mission Context 1.4 weist
diesen Vertrag zusätzlich zu Constitution, Governance, Institution und
Interaction nach. Fehlender oder veränderter Kontext bricht Preflight ab.
Operative Workflows erhalten daraus keine zusätzliche Vollmacht.

## Ausdrücklich abgelehnt oder zurückgestellt

Nicht übernommen werden:

- eine zwingende Drei-Sekunden-Geste,
- verpflichtende Biometrie-, SMS- oder Token-Verfahren,
- unbestätigte Kryptografie-, Signatur- oder Zero-Knowledge-Behauptungen,
- pauschale Rechtswirkungs-, Beweis- oder Haftungsgarantien,
- automatische externe Notfall-, Amts- oder Ereignismaßnahmen,
- absolute Unlöschbarkeit sämtlicher Historien,
- nicht vorhandene `GOV-*`-, `IL-*`- oder vergleichbare Referenzen.

Konkrete Fristen, Gesten, Quoren und technische Verfahren bleiben C3-Fragen.
Notfall- und automatische Ereignisübergänge benötigen eigene Entscheidungen.

## Folgen

- Artefaktzustand, Autorisierung und Übergangshistorie sind maschinenlesbar
  und voneinander getrennt.
- Nutzerhoheit und Beteiligung sind explizit statt implizit.
- Gespräch und Interaction bleiben frei von automatischer Handlungsmacht.
- Runtime kann Version und Integrität nachweisen, ohne Persistenz oder
  Ausführung einzuführen.
- UI, Cloud, Datenbank, Kryptografie, Dokumentanalyse, fachliche Workflows und
  rechtliche Wirkungsprüfung bleiben unverändert.
