# I4 Canonical Source Analysis

Dokument-ID: `GOV-ANALYSIS-I4-2026-08-02`

Status: abgeschlossen – keine historische I4-Quellnorm gefunden

Diese Analyse ist keine Verfassungsänderung, keine institutionelle
Kenntnisnahme und keine Implementierungsfreigabe.

## Suchumfang

Untersucht wurden `AGENTS.md`, sämtliche ADRs ADR-0002 bis ADR-0058,
MDR-0001, Constitution, Institution, Governance Charter, AAV, UODL,
Interaction, Guardian Runtime, Guardian Understanding sowie Observation-,
Audit-, Operational-Memory-, Physical-Persistence-, Metrics-, Notifications-
und B2-Dokumente.

Gesucht wurde nach `I4` und Schreibvarianten sowie nach Regeln zu
Nutzerprofilbildung, Nutzerverhalten, Nutzungsstatistik, Nutzersegmenten,
Gesprächsinhalten, Themen, Lebensbereichen und nutzerbezogener Aggregation.

## Direkte und indirekte Regelquellen

Eine direkte historische oder kanonische Norm mit der Bezeichnung `I4` wurde
nicht gefunden. Vor ADR-0058 referenziert keine ADR eine solche Norm.
ADR-0058 dokumentierte ausschließlich das Fehlen der Quelle.

Der sachliche Kern existiert dagegen verteilt und ratifiziert:

- C1 `Keine Umgehung der Nutzerhoheit` und `Keine Aufweichung von Guardian-
  oder Institution-Garantien`,
- Institution: Nutzerhoheit, Schutz, Würde und Vertrauensmodell,
- C2-Schutzdomäne Daten,
- ADR-0047 D6: keine stille Datenanreicherung, Profile oder Aggregate,
- ADR-0053: Observation ausschließlich von Systemverhalten,
- ADR-0054: Audit ohne Nutzerprofile, Nutzungsmuster oder Themenanalyse,
- ADR-0055: Operational Memory ohne Nutzerdaten, Profile oder Nutzungsthemen,
- ADR-0056: Physical Persistence ausschließlich für Operational Memory,
- ADR-0057: Metrics und Notifications ohne Nutzeridentität, Segmente, Themen,
  Lebensbereiche oder Häufigkeiten pro Nutzer,
- ADR-0058: der B2-Betriebsblock bleibt gegenüber B2-Inhalten blind.

AAV und UODL schützen Autorisierung, Zweckbindung, minimale Metadaten,
Referenz-vor-Kopie und Nutzerhoheit. Sie enthalten keine historische
I4-Bezeichnung und werden nicht zu einer Profiling-Regel umgedeutet.

## Vollständige Referenzkette

```text
C1 Nutzerhoheit und Garantieerhalt
→ Institution Nutzerhoheit, Schutz und Würde
→ C2 Schutzdomäne Daten
→ ADR-0047 D6 und ADR-0053 Systemverhaltensgrenze
→ ADR-0054 bis ADR-0057 inhaltsblinder Betriebsblock
→ ADR-0058 B2-Inhaltsblindheit
```

## Tatsächlicher Regelstatus

Der gemeinsame Kern ist materiell bindend, aber bislang über mehrere
kontextspezifische Entscheidungen verteilt. `I4` ist weder eine gültige ID
noch eine wiederherstellbare historische Norm. Eine Behauptung, I4 habe schon
immer existiert, wäre falsch.

Unmittelbar vorausgesetzt wird der gemeinsame Kern durch ADR-0053 bis
ADR-0058 sowie die Governance-Dokumente zu Audit, Operational Memory,
Persistence, Metrics, Notifications und B2 Readiness.

## Drift- und Mehrfachwahrheitsrisiken

- Abweichende Aufzählungen könnten einzelne Nutzeranalyseformen auslassen.
- Eine technische Betriebsregel könnte fälschlich als C1-Regel bezeichnet
  werden.
- Die Bezeichnung `I4` könnte eine nicht vorhandene historische Autorität
  vortäuschen.
- Eine neue C1-Regel neben strengeren ADR-Grenzen könnte unklar machen,
  welche Detailregel gilt.

## Variantenvergleich

### Variante A – neue C1-Verfassungsregel

Vorteil wäre ein sehr hoher, einheitlicher Rang. Sie wäre jedoch eine echte
neue Verfassungsentscheidung mit Mehrschlüssel-Verfahren nach ADR-0027 und
nicht die Wiederherstellung von I4. Die detaillierte Aufzählung technischer
Auswertungsverbote würde außerdem C2/C3-Inhalte in C1 versteinern.

Auswirkung: Constitution, Governance-Loader, C1-Tests und sämtliche abhängigen
Referenzen müssten nach einer realen Verfassungsentscheidung geändert werden.
Dieser menschliche Mehrschlüsselbeschluss liegt nicht vor.

### Variante B – kanonische Referenz unterhalb C1

Der bereits ratifizierte gemeinsame Kern wird als C2-Architekturreferenz
zusammengeführt. C1 bleibt unverändert; strengere ADR-Regeln bleiben
unverändert und verweisen zusätzlich auf die gemeinsame Mindestgrenze.

Auswirkung: keine Verfassungsänderung, keine neue Runtime-Macht und keine
Abschwächung. Die Referenz kann bei späteren Änderungen kontrolliert gegen C1,
Institution und die strengeren ADRs geprüft werden.

## Entscheidung und Empfehlung

Variante B wird gewählt. Die kanonische Referenz lautet
`governance/system-behavior-only-rule.md`. Sie ist eine neue
Konsolidierungsentscheidung, keine historische I4-Regel. Sie ersetzt keine
strengere Einzelnorm und bildet keine zweite fachliche Wahrheitsquelle; sie
ist ausschließlich der gemeinsame Mindestverweis.

Eine C1-Hebung ist derzeit nicht eindeutig gerechtfertigt und ohne das
verfassungsrechtliche Mehrschlüssel-Verfahren unzulässig. Sollte später eine
C1-Hebung vorgeschlagen werden, benötigt sie eine neue ausdrückliche
GOV-40-/Verfassungsentscheidung.
