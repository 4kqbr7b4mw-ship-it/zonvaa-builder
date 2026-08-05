# GOV-NO-FABRICATION Reference Consolidation v1

Dokument-ID: `GOV-NO-FABRICATION-REFERENCE-CONSOLIDATION-V1`

Bezugsentscheidung:
`GOV-NO-FABRICATION-REFERENCE-CONSOLIDATION-APPROVAL-V1`

Status:

- kanonische Referenzkonsolidierung
- keine Governance-Regel
- keine Verfassungsfamilie
- keine materielle Norm
- keine neue Taxonomie

## 1. Zweck und Nicht-Wirkung

Dieses Dokument ist ausschließlich eine Navigations- und
Zuständigkeitsübersicht für bereits vorhandene materielle Regeln. Es führt
keine neue Regel ein, ändert oder interpretiert keine bestehende Regel, erzeugt
keine Prioritäts- oder Vorrangregel und ersetzt keine vorhandene
Verfassungsfamilie.

Die nachfolgenden Kurzbeschreibungen benennen ausschließlich den bereits
dokumentierten Gegenstand der jeweiligen Regelinhaber. Für Bedeutung,
Geltungsbereich und Wirkung ist ausschließlich der referenzierte primäre
Regelinhaber zuständig. Unterstützende Artefakte erzeugen keine zusätzliche
materielle Zuständigkeit.

`GOV-NO-FABRICATION-1` bezeichnet in diesem Dokument ausschließlich die
Referenzkonsolidierung. Die Bezeichnung ist keine geltende Governance-Regel,
keine Verfassungsfamilie, keine materielle Norm und keine Taxonomie.

## 2. Vier registrierte Referenzbereiche

### 2.1 Erfundene Quellen

- **Neutrale Beschreibung:** Eine Quelle wird für eine Antwort als vorhanden,
  verfügbar oder tragend dargestellt, obwohl die Antwortarchitektur sie nicht
  als tatsächlich bereitgestellte Quellenreferenz führt.
- **Primärer materieller Regelinhaber:** ADR-0047, insbesondere W1 bis W4 und
  die Quellenkettenverfassung.
- **Unterstützende Regelinhaber:** ADR-0023, Foundation Values,
  `GuardianSourceChainContract`, Answer Boundary, Answer Foundation und
  Guardian Answer Reference Journey.
- **Betroffene Verfassungsfamilien:** Knowledge & Answer Layer, Understanding
  und die Antwortbetriebsarten B1 bis B3.
- **Vorhandene technische Durchsetzung:** immutable Quellenketten,
  Quellenreferenzen, Unsicherheitsstatus, Widerspruchsreferenzen,
  Vollständigkeitsprüfungen und kontrollierte Nicht-Bestätigung.
- **Bewusste technische Grenze:** Die Validatoren prüfen bereitgestellte Typen,
  Referenzen und interne Konsistenz. Sie führen keine externe Recherche oder
  allgemeine Wahrheitsprüfung durch und bestätigen nicht selbst die reale
  Existenz einer externen Quelle.
- **Kanonische Referenzen:**
  `knowledge/adr/ADR-0047-guardian-knowledge-answer-layer-v1.md`,
  `knowledge/adr/ADR-0023-guardian-conversation-principles.md`,
  `guardian_understanding/source_chain.py`,
  `guardian_understanding/answer_boundary.py`,
  `guardian_understanding/answer_foundation.py`,
  `guardian_understanding/answer_reference_journey.py`.
- **Nicht zuständig:** ADR-0064-Governance-Evidence bestätigt keine fachliche
  Quellenwahrheit; `GOV-NO-FABRICATION-1` prüft oder bewertet keine Quelle.

### 2.2 Erfundene Gefühle

- **Neutrale Beschreibung:** Gefühle, Motive oder mentale Zustände einer
  natürlichen Person werden als Tatsache behauptet, ohne dass die zuständige
  Gesprächsverfassung eine solche Behauptung zulässt.
- **Primärer materieller Regelinhaber:** ADR-0047, insbesondere die
  Empathieregeln, W7 und das ausdrückliche Nicht-Ziel „erfundene Gefühle“.
- **Unterstützender Regelinhaber:** ADR-0023 Guardian Conversation Principles.
- **Betroffene Verfassungsfamilien:** Knowledge & Answer Layer und
  Gesprächsverfassung.
- **Vorhandene technische Durchsetzung:** geschlossene Answer Boundaries,
  kontrollierte Nicht-Bestätigung sowie Dokumentations- und
  Gesprächsregressionstests.
- **Bewusste technische Grenze:** Es besteht kein Universalvalidator für
  beliebige Sprache und keine technische Ableitung psychologischer oder
  emotionaler Zustände. B2-Verträge modellieren natürliche Personen und deren
  mentale Zustände nicht als zulässige Beobachtungsgegenstände.
- **Kanonische Referenzen:**
  `knowledge/adr/ADR-0047-guardian-knowledge-answer-layer-v1.md`,
  `knowledge/adr/ADR-0023-guardian-conversation-principles.md`,
  `guardian_understanding/answer_boundary.py`.
- **Nicht zuständig:** `GOV-SYSTEM-BEHAVIOR-ONLY-1` begrenzt technische
  Betriebsnachweise, formuliert aber keine Gesprächs- oder Empathieregel;
  `GOV-NO-FABRICATION-1` beobachtet oder klassifiziert keine Person.

### 2.3 Erfundene Nachweise

- **Neutrale Beschreibung:** Evidence wird als vorhanden, tragend oder für
  einen Aussageumfang hinreichend dargestellt, obwohl die zuständige
  Evidence-Verfassung sie nicht als bereitgestellte Referenz ausweist.
- **Primärer materieller Regelinhaber:** ADR-0064 und ADR-0064-A1 für
  Governance Decision und Governance Incident Evidence.
- **Unterstützende Regelinhaber:** die jeweils lokalen Evidence- und
  Provenienzverträge aus ADR-0059 bis ADR-0065 sowie
  `GOV-INSTITUTIONAL-DECISION-SCOPE-1`.
- **Betroffene Verfassungsfamilien:** B2 Data Corridor, Authority, Provider
  Identity, Provider Authorization, Purpose/UODL, Governance und Capability
  Invocation.
- **Vorhandene technische Durchsetzung:** geschlossene Evidence-Arten,
  Missing-Evidence-Arten und -Status, begrenzte Aussageumfänge, getrennte
  Provenienz, immutable Zeittypen sowie deterministische zustandslose
  Validatoren.
- **Bewusste technische Grenze:** Die Validatoren prüfen typisierte
  Referenzen, zulässige Aussageumfänge und interne Konsistenz. Sie lesen keine
  externen Systeme und beweisen nicht allgemein den Wahrheitsgehalt eines
  referenzierten Artefakts. Provenienz ersetzt keine Evidence.
- **Kanonische Referenzen:**
  `knowledge/adr/ADR-0064-governance-decision-incident-evidence-constitution-v1.md`,
  `knowledge/adr/ADR-0064-A1-governance-decision-incident-closed-taxonomies-v1.md`,
  `governance/governance_decision_incident_evidence.py`,
  `governance/institutional-decision-scope-rule.md`.
- **Nicht zuständig:** ADR-0047-Quellenketten entscheiden keine Governance-
  Evidence; `GOV-NO-FABRICATION-1` erzeugt, schließt oder bestätigt keinen
  Nachweis.

### 2.4 Erfundene Rechenschaft

- **Neutrale Beschreibung:** Eine Rechenschaftserklärung würde Aussagen als
  aus Evidence ableitbar darstellen, ohne dass dafür ein aktivierter
  materieller Regel- und Vertragsrahmen besteht.
- **Primärer materieller Regelinhaber:** gegenwärtig keiner.
- **Dokumentarische Unterstützung:**
  `GOV-ARCH-CANDIDATE-GUARDIAN-ACCOUNTABILITY-1` beschreibt ausschließlich
  einen möglichen späteren Kandidatenumfang.
- **Betroffene Verfassungsfamilien:** gegenwärtig keine aktive
  Verfassungsfamilie; der Kandidat ist kein Vertrag und keine Produktfunktion.
- **Vorhandene technische Durchsetzung:** keine Accountability- oder
  Explanation-Verträge, keine Erklärungsklasse und kein Validator.
- **Bewusste technische Grenze:** Governance Evidence und Provenienz aus
  ADR-0064 dürfen nicht zu einer Accountability-Verfassung oder einem
  Universal-Evidence-Modell umgedeutet werden.
- **Kanonische Referenz:**
  `governance/guardian-accountability-explanation-candidate.md`.
- **Kandidatenstatus:** ruhender Kandidat, nicht aktiviert, nicht materiell
  geregelt und kein gegenwärtiger Regelinhaber.
- **Nicht zuständig:** ADR-0064 regelt Governance Evidence, nicht die lesbare
  Rechenschaftserklärung; `GOV-NO-FABRICATION-1` aktiviert oder regelt
  Accountability nicht.

## 3. Weitere referenzierte Fabrikationstypen

| Referenzbereich | Kurze neutrale Beschreibung | Primärer materieller Regelinhaber | Unterstützende Regelinhaber | Technische Durchsetzung | Bewusste technische Grenze |
|---|---|---|---|---|---|
| Institutionelle Entscheidung | Eine nicht dokumentierte Entscheidung wird als gefasst dargestellt. | ADR-0064/A1 | `GOV-INSTITUTIONAL-DECISION-SCOPE-1` | geschlossene Decision Classes, Rollen, Evidence und getrennte Zeiten | Record und Evidence erzeugen keine menschliche Entscheidung |
| Historische Zeit | Ein unbekannter historischer Zeitpunkt wird als bekannt dargestellt. | ADR-0064/A1 | lokale timezone-aware Zeitverträge | `UNBEKANNT`, bekannte Zeittypen und Zeitvalidatoren | keine Schätzung, Systemzeit oder rückwirkende Rekonstruktion |
| Rückwirkende Legitimierung | Spätere Evidence wird als Heilung eines früheren fehlenden Gates dargestellt. | ADR-0064/A1 | institutionelle Freigabedokumente | Missing-Evidence-Status und Incident-Erhaltung | spätere Evidence entfernt keinen Vorfall und simuliert keine frühere Entscheidung |
| Stillschweigende Freigabe | Nicht genannter Scope wird als freigegeben behandelt. | `GOV-INSTITUTIONAL-DECISION-SCOPE-1` | ADR-0064/A1 | getrennte `GRANTED_SCOPE`- und `EXCLUDED_SCOPE`-Einträge | fehlende Nennung bleibt Nichtfreigabe |
| Institutionelle Rolle | Eine freie oder unzulässige Rolle wird als entscheidungsbefugt dargestellt. | ADR-0064-A1 | ADR-0064 | geschlossene Rollen- und Decision-Class-Zulässigkeit | Rolle bleibt von natürlicher Person getrennt |
| Provider Identity | Eine freie, personenbezogene oder nicht registrierte Provider-Identität wird als gültig dargestellt. | ADR-0061 | ADR-0062 | geschlossene Provider Classes, Capability Descriptoren und Provenienz | Identity autorisiert oder aktiviert nichts |
| Authority und Authorization | Evidence, Provider Identity oder Provenienz wird als Authority oder Authorization behandelt. | ADR-0060 und ADR-0062 | ADR-0059, ADR-0061 und ADR-0063 | immutable Referenzketten, Evaluation und fail-closed Gründe | Evidence und Provenienz erzeugen keine neue Authority oder Authorization |
| Purpose und UODL | Freier, breiterer oder nicht vergleichbarer Scope wird als gebunden behandelt. | ADR-0063 | ADR-0059 und ADR-0060 | geschlossene Werte und vorhandene Halbordnung | keine freie Purpose- oder UODL-Semantik |
| Invocation-Ausführung | Eine positive Invocation-Prüfung wird als technische Ausführung dargestellt. | ADR-0065 | ADR-0060 bis ADR-0063 | geschlossene Decisions, Receipt und Resolution Snapshot | jeder Pfad bleibt nicht ausführend und endet kontrolliert |
| Runtime-Folgezustand | Nach dem Controlled Stop wird ein technischer Folgeschritt behauptet. | ADR-0066 | ADR-0065 | dokumentarische Negativ- und Regressionstests | kein Modul, Validator, Adapter, Bridge oder Runtime Readiness |
| Hypothese als Tatsache | Eine ausdrücklich offene Möglichkeit wird als bestätigter Fakt dargestellt. | Guardian Understanding Model | ADR-0047 | getrennte immutable Facts, Hypotheses und Unknowns sowie Regressionstests | keine allgemeine externe Wahrheitsprüfung |

Die Tabellenzeilen sind ausschließlich Referenzzuordnungen. Sie definieren
keinen Fabrikationstyp neu und verändern weder die materiellen Aussagen noch
den Geltungsbereich eines genannten Regelinhabers.

## 4. Unterstützende Referenzen ohne materielle Zuständigkeit

- `GOV-SYSTEM-BEHAVIOR-ONLY-1` begrenzt technische Betriebsnachweise auf
  Systemverhalten. Es ist keine allgemeine Quellen-, Evidence- oder
  Accountability-Regel.
- Foundation Mission, Vision und Values unterstützen Sichtbarkeit von Quellen,
  Annahmen und Unsicherheit. Sie ersetzen keine geschlossene Fach- oder
  Governance-Verfassung.
- Tests dokumentieren und prüfen bestehende Verträge. Sie erzeugen keine
  materielle Regel und keine institutionelle Entscheidung.
- Provenienz dokumentiert Herkunft. Sie bestätigt keine externe Wahrheit und
  ersetzt keine Evidence.

## 5. Zuständigkeits- und Doppelregelungsgrenze

Jeder referenzierte Regelinhaber bleibt ausschließlich in seinem vorhandenen
Geltungsbereich materiell zuständig. Dieses Dokument:

- ordnet keine Regel einer anderen unter,
- bestimmt keinen neuen Vorrang,
- vereinheitlicht keine unterschiedlichen Evidence-Begriffe,
- behandelt Hypothese, Unsicherheit oder kontrollierte Nicht-Bestätigung nicht
  als Fabrikation,
- behandelt Missing Evidence nicht als erfundene Evidence,
- erhebt lokale Validatoren nicht zu einem Universalvalidator und
- leitet aus technischer Abwesenheit keine neue materielle Norm ab.

## 6. Ausdrückliche Nicht-Ziele

Diese Referenzkonsolidierung erzeugt keine Runtime, Runtime Readiness,
Observation, externe Wahrheitsprüfung, psychologische oder emotionale
Zustandsableitung, personenbezogene Verarbeitung oder automatische
Folgeverfassung. Sie aktiviert weder Accountability & Explanation noch
ADR-0067 und verändert keine bestehende Architektur, Governance-Regel oder
Vertragssemantik.

## 7. Prüffrage Null

Kann diese Referenzkonsolidierung eine neue materielle Regel, Taxonomie,
Priorität, Entscheidung, Evidence, Authority, Authorization, Accountability,
Observation, Runtime oder technische Macht erzeugen?

Antwort: **Nein.** Sie verweist ausschließlich auf vorhandene Regelinhaber und
deren bereits dokumentierte Zuständigkeits- und Durchsetzungsgrenzen.
