# Vertrauensrats-Kenntnisnahme zu ADR-0058

Dokument-ID: `TRUST-ACK-ADR-0058-V1`

Status: Vorlage – Kenntnisnahme offen

Normstufe: C2-Verfahrensnachweis

## Bezug und Zweck

Diese Vorlage dokumentiert ausschließlich die institutionelle Kenntnisnahme
des Vertrauensrats zu
`knowledge/adr/ADR-0058-guardian-b2-architecture-v1.md`.

Sie betrifft Vetodomäne 2: Datenverwendung und externe Recherche. Die Vorlage
erteilt keine Zustimmung, Autorisierung oder Freigabe und ersetzt weder das
Prüf- und Vetoverfahren der Governance Charter noch eine gesonderte spätere
Architektur- oder Implementierungsentscheidung.

## Bestehendes bindendes Recht

- C1 Constitution: Nutzerhoheit, bewusste Autorisierung, persönliche
  Kontextisolation und Schutz vor stiller Garantieabschwächung.
- C2 Governance Charter: unabhängige Prüfung erheblicher Änderungen an
  Erhebung, Zweck, Zugriff, Weitergabe, Aufbewahrung und Löschung von
  Nutzerdaten.
- ADR-0030 und AAV: konkrete, zweck- und umfangsgebundene Autorisierung sowie
  getrennte unveränderliche Nachweise von Erteilung, Nutzung und Widerruf.
- ADR-0033 und UODL: User Ownership, Reference before Copy, Minimal Metadata,
  Explicit Consent, Privacy by Design und Provider Independence.
- ADR-0047: D1–D6, D3 und D3-UX sowie die Trennung von Modellschicht und
  deterministischem Kern.
- ADR-0048 bis ADR-0057: Authority-, Provider-, Invocation-, Runtime- und
  inhaltsblinde Betriebsgrenzen.

## Neue Architekturentscheidung

ADR-0058 definiert B2 als eigene Verfassungsstufe. B2 ist keine Erweiterung
der B1-Runtime. Vorgesehen sind eine eigene B2-Authority-Klasse, eigene Grants,
ein minimaler zweck-, zeit- und datenklassengebundener Datenkorridor,
vorgeschaltete Depersonalisierung sowie die vollständige Inhaltsblindheit des
Betriebsblocks.

D3 bleibt notwendig, ist aber nicht hinreichend. Eine B1-Autorisierung
autorisiert niemals B2.

## Ausdrücklich nicht autorisierte Bereiche

- B2 Runtime, Verträge, Provider, Invocation oder Capability,
- B2 Persistenz, Operational Memory, Metrics oder Notifications,
- B2 UI, Workflows oder Produktfunktion,
- ein Upgrade bestehender B1-Grants,
- personenbezogene Inhalte im Betriebsblock,
- Implementierungs-, Runtime- oder Produktfreigabe.

## Offene Risiken

- Im Repository ist keine kanonische, als `I4` bezeichnete Quellregel
  auffindbar; ihr Inhalt und ihre Herkunft dürfen nicht rekonstruiert werden.
- Datenklassen, Depersonalisierungsnachweis und technische Widerrufsfolgen sind
  noch nicht als B2-Verträge entschieden.
- Provider-, Credential-, Ausführungs- und Missbrauchsgrenzen für B2 sind noch
  nicht entschieden.
- Die Vertrauensrats-Kenntnisnahme selbst ist noch nicht erfolgt.

## Offene Folgeentscheidungen

- kanonische Klärung des I4-Verweises,
- institutionelle Freigabe nach erfolgter Kenntnisnahme,
- jeweils gesonderte Architekturentscheidungen für B2 Authority und Grants,
  Datenkorridor und Depersonalisierung, Invocation, Provider und Runtime,
- jeweils gesonderte begrenzte Implementierungsaufträge.

## Ergebnisfeld der Kenntnisnahme

- Ergebnis: `OFFEN`
- Kenntnis genommen durch: _nicht eingetragen_
- Rolle oder Mandatsreferenz: _nicht eingetragen_
- Datum und Zeitpunkt: _nicht eingetragen_
- Anmerkungen oder Auflagen: _nicht eingetragen_
- Veto oder Eskalationsreferenz: _nicht eingetragen_

Ein ausgefülltes Ergebnisfeld dokumentiert ausschließlich den institutionellen
Vorgang. Auch eine erfolgreiche Kenntnisnahme ist keine Runtime-Freigabe,
keine Implementierungsfreigabe und keine Produktfreigabe.
