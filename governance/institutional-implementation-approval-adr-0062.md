# Institutionelle Implementierungsfreigabe – ADR-0062 Guardian B2 Provider Authorization v1

Dokument-ID: `GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0062-V1`

Status: `INSTITUTIONELLE IMPLEMENTIERUNGSFREIGABE – GÜLTIG`

Zeitpunkt der externen Beschlussfassung: 03.08.2026, 15:15 Uhr
Europe/Berlin (CEST, UTC+02:00)

Repository-Dokumentationszeitpunkt: 03.08.2026, 15:17:10 Uhr
Europe/Berlin (CEST, UTC+02:00)

Beschlusszeitpunkt und Repository-Dokumentationszeitpunkt sind ausdrücklich
getrennt. Der erste Zeitpunkt bezeichnet die außerhalb des Repositories
erfolgte menschliche Beschlussfassung; der zweite bezeichnet ausschließlich
deren spätere kanonische Dokumentation im Repository.

Entscheidungsrolle: Institutionsgründer in konstituierender Funktion bis zur
ersten ordentlichen Sitzung des Vertrauensrats.

## Grundlage

Grundlage ist der kanonische Ratifizierungsbeschluss zu ADR-0062, dokumentiert
durch `GOV-RATIFICATION-ADR-0062-V1`. Ratifizierung und institutionelle
Implementierungsfreigabe sind zwei getrennte menschliche Beschlüsse.

Diese Freigabe betrifft ausschließlich den in ADR-0062 abschließend
dokumentierten Architekturumfang. Provider Authorization erzeugt keine neue
Autorisierungssemantik, sondern spezialisiert ausschließlich die in ADR-0060
definierte B2-Autorisierungsverfassung auf unverändert referenzierte B2
Provider Identities aus ADR-0061. ADR-0058 bis ADR-0061 und ihre bestehenden
Freigaben werden weder erweitert noch verändert. Fehlende Nennungen gelten
nach `GOV-INSTITUTIONAL-DECISION-SCOPE-1` nicht als stillschweigende Freigabe.

## Freigegeben

Die spätere Implementierung ist ausschließlich freigegeben für:

- die in ADR-0062 abschließend dokumentierte und ratifizierte Architektur
  Guardian B2 Provider Authorization v1,
- eigenständige immutable B2-Provider-Authorization-Verträge,
- die ausschließliche Spezialisierung der ADR-0060-
  Autorisierungsverfassung auf unverändert referenzierte B2 Provider
  Identities aus ADR-0061,
- Bindung an die bestehenden D3-, T4-, AAV- und UODL-Verträge,
- D3 als aktuell wirksame, notwendige, aber niemals hinreichende Einwilligung,
- T4 ausschließlich als historische Quittierung der Grant-Erteilung,
- aktuelle Autorisierungs- und Widerrufsbindung ausschließlich über AAV,
- Wirksamkeitsableitung ausschließlich zu einem explizit übergebenen
  timezone-aware Auswertungszeitpunkt,
- deterministische, zustandslose Evaluation aus ausschließlich immutable
  typisierten Eingaben,
- Provider-Authorization-Evaluation-Evidence ohne Token-, Cache-, Permission-,
  Grant- oder Autorisierungswirkung,
- Negative Governance Evidence ausschließlich als deklarierter
  Beobachtungsumfang ohne Sperr-, Sanktions-, Profil- oder Entscheidungswirkung,
- nicht personenbezogene, vollständig rekonstruierbare und nicht
  selbstbestätigende Provenienz,
- ausschließlich die sechs in ADR-0062 dokumentierten UODL-Hooks:
  1. UODL Reference Identity,
  2. Grant Binding,
  3. AAV Binding,
  4. `REFERENCE_ONLY`,
  5. Temporal Effectiveness,
  6. User Ownership / Reference before Copy,
- die strukturellen Negativregeln aus ADR-0062,
- vollständige fokussierte Positiv- und Negativtests,
- erforderliche Exporte und minimale kanonische Dokumentationsanpassungen
  innerhalb dieses Pakets.

## Ausdrücklich nicht freigegeben

- Erweiterung oder Veränderung der Autorisierungssemantik aus ADR-0060,
- Veränderung oder Duplizierung der Provider-Identity-Verträge aus ADR-0061,
- Autorisierung natürlicher Personen oder personenbezogene Akteursbindung,
- personenbezogene Verarbeitung oder Speicherung personenbezogener Inhalte,
- B1→B2-Konvertierung oder Upgrade,
- Statusfelder wie `valid`, `active`, `revoked`, `expired`, `authorized`,
  `denied` oder `blocked`,
- interne Systemzeit oder interne Zustandsquellen,
- selbstständiges Lesen oder Abrufen von D3-, T4-, AAV-, UODL- oder
  Grant-Zuständen,
- Austauschbarkeit oder Zusammenlegung von D3 und T4,
- Ersetzung eines Nachweises durch einen anderen,
- eine zweite Grant-, Consent-, Authority-, Purpose-, Provider- oder
  Verbotsverfassung,
- Invocation oder Capability Invocation,
- Runtime oder technische Ausführung von Grants,
- Provider-Aufrufe oder Tools,
- Sessions, Caches oder Tokens,
- Schlüsselmaterial, Key Custody oder Inhaltszugriff,
- Observation oder Runtime Audit,
- Operational Memory, Metrics oder Notifications,
- externe Integrationen oder produktive Provider-Anbindungen,
- alle nicht ausdrücklich freigegebenen UODL-Operationen,
- Inhalts-, Speicher- oder Provider-Hooks,
- Architekturarbeit an nachgelagerten B2-Bausteinen,
- Implementierung von ADR-0062 in diesem Dokumentationsauftrag,
- Commit oder Push ohne jeweils gesonderte ausdrückliche Freigabe.

## Verfassungsinvarianten

- D3 ist notwendig, aber niemals hinreichend.
- T4 quittiert ausschließlich die historische Grant-Erteilung.
- Kein Nachweis ersetzt einen anderen.
- Provider Identity wird ausschließlich unverändert referenziert.
- Wirksamkeit wird nur zum explizit eingegebenen Auswertungszeitpunkt aus den
  vollständig bereitgestellten immutable Artefakten abgeleitet.
- Provider-Authorization-Evaluation-Evidence besitzt keine autorisierende oder
  fortwirkende Wirkung.
- Negative Governance Evidence ist ausschließlich deklarierter
  Beobachtungsumfang und besitzt keine Sperr-, Sanktions-, Profil- oder
  Entscheidungswirkung.
- Prüffrage Null aus ADR-0062 bleibt verbindlich und muss vor einer späteren
  Implementierungsanerkennung eindeutig mit `Nein` beantwortet werden.

## Wirkung und nächstes Gate

ADR-0062 ist ratifiziert und institutionell implementierungsfreigegeben, aber
weiterhin nicht implementiert. Diese Freigabe implementiert nichts, erzeugt
keine Autorisierung, Invocation, Runtime oder technische Macht und ist kein
Codex-Implementierungsauftrag.

Ein separater Implementierungsauftrag darf erst erteilt werden, nachdem der
Commit mit diesem Freigabedokument nachweisbar auf
`origin/builder-reset-v2` gepusht wurde. Der bei ADR-0061 dokumentierte
Prozessvorfall – Implementierungsbeginn vor kanonischem Freigabe-Push – darf
sich nicht wiederholen. Eine lokale Freigabe oder ein lokaler Freigabe-Commit
genügt nicht. Commit und Push bleiben jeweils eigene menschliche Entscheidungen.

## Provenienz

- Architektur: ADR-0062
- Ratifizierung: `GOV-RATIFICATION-ADR-0062-V1`
- Beschlussart: institutionelle Implementierungsfreigabe außerhalb des
  Repositories
- Externe Beschlusszeit: 03.08.2026, 15:15 Uhr Europe/Berlin (CEST,
  UTC+02:00)
- Repository-Dokumentationszeit: 03.08.2026, 15:17:10 Uhr Europe/Berlin
  (CEST, UTC+02:00)
- Repository-Ausgangsstand: `59e390931fa7d8579a0a342d061e78ca9754d990`
- Scope-Regel: `GOV-INSTITUTIONAL-DECISION-SCOPE-1`
