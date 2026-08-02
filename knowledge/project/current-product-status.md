# ZONVAA V2 Product Status

Dieses Dokument ist die kanonische Quelle für den aktuellen fachlichen
Produktstand. Ein fachlich abgeschlossener Produktauftrag muss diesen Stand als
Teil derselben Änderung aktualisieren. Commit-Hashes werden nicht dauerhaft
eingetragen, weil der Status-Commit sie unmittelbar veralten ließe; die
read-only Chat-Übergabe ermittelt sie zur Laufzeit.

## Aktives Repository

- Produktlinie: ZONVAA V2
- Erwarteter Branch: `builder-reset-v2`
- ZONVAA V1: ausschließlich Archiv

## Abgeschlossene Produktbausteine

- Guardian Understanding Core v1
- Guardian Understanding Model v2
- Guardian Understanding Proposal Layer v1
- Guardian Clarification Resolution v1
- Guardian Life Decision Conversation v1: Vorsorgevollmacht
- Guardian Life Decision Conversation v2: Mehrzügige Vorsorgevollmacht-Gesprächsführung
- Guardian Life Decision Journey v1: Vorsorgevollmacht
- Power-of-Attorney Professional Review Preparation
- Guardian Life Decision Experience v1: Vorsorgevollmacht
- Guardian Life Decision v1: Patientenverfügung
- Guardian Cross-Domain Life Situation v1: Pflegefall in der Familie
- Family Care Cross-Domain Scenario Validation v1
- Family Care End-to-End Reference Journey v1
- Guardian Family Care Review UI v1 (lokales internes Prüfwerkzeug)
- Guardian Answer Boundary Contracts v1
- Guardian Source Chain Contracts v1
- Guardian Classification Contract v1
- Guardian Answer Foundation Integration v1
- Guardian Controlled Orientation Package v1
- Guardian Personal Preparation Package v1
- Guardian Professional Decision Boundary Package v1
- End-to-End Guardian Answer Reference Journey v1
- Guardian Authority Model v1
- Guardian Provider Authorization Package v1
- Guardian Capability Invocation Boundary v1
- Read-only B1 Provider Runtime v1
- Runtime Incident Evidence v1

## Aktueller fachlicher Stand

- Die vier Guardian-Understanding-Bausteine, die vorbereitende und mehrzügige
  Vorsorgevollmacht-Gesprächsführung, die kontrollierte Journey, ihre
  Professional-Review-Vorbereitung und die UI-neutrale Experience sind
  abgeschlossen.
- Die zustandslose Patientenverfügungs-Preparation, Conversation, Journey,
  Professional-Review-Vorbereitung und UI-neutrale Experience sind abgeschlossen.
- Die erste Cross-Domain-Lebenslage strukturiert den Pflegefall in der Familie
  über einen gemeinsamen Understanding State, explizite fachlich getrennte
  Contributions und Abhängigkeiten, eine kontrollierte Guardian-Frage, Journey,
  Professional-Review-Vorbereitung und UI-neutrale Experience. Für den Nutzer
  bleibt ausschließlich ein Guardian sichtbar.
- Zwölf anonymisierte, vollständig typisierte Family-Care-Szenarien sowie
  Robustheits- und Negativfälle validieren den bestehenden Vertrag. Vier dabei
  gefundene Vertragslücken wurden minimal geschlossen; die Scenario Validation
  ergänzt weder Service noch Workflow oder Laufzeitlogik.
- Ein anonymisierter End-to-End-Referenzfall validiert sechs chronologische
  kontrollierte Gesprächszüge mit vollständiger Quellenkette. Drei ausdrücklich
  ausgewählte Proposals führen über bestehende Revisionen zu neuem State;
  ungeklärte Vertretungs-, Wohn- und Kostenpunkte bleiben als `KEEP_OPEN`
  sichtbar. Journey, explizit gebundenes Professional Review und UI-neutrale
  Experience sind konsistent, ohne automatische Semantik oder Aktivierung.
- Eine kleine lokale Review UI macht denselben typisierten Referenzfall
  schrittweise prüfbar. Sie ist weder Nutzer-App noch Produktionsfrontend und
  hält ausschließlich einen flüchtigen UI-Schrittzeiger im Arbeitsspeicher.
- Die Guardian Answer Boundary Contracts bilden B1, B2 und B3 ausschließlich
  als unveränderliches Sicherheits- und Auditmetadatum ab. Ihr deterministischer
  Validator erlaubt nur Schutzeskalation, erzwingt die B3-Nicht-Bestätigung und
  besitzt keinerlei Klassifizierungs-, Aktivierungs-, Routing- oder
  Zustandsänderungsbefugnis.
- Die Guardian Source Chain Contracts bilden die zwölf Pflichtfelder aus
  ADR-0047 § 7 als unveränderliche, typisierte T4-Struktur ab. Widersprüche
  bleiben deklarativ; der Validator bewertet, recherchiert, ersetzt oder
  priorisiert keine Quelle und besitzt weder B1-/B2-/B3-Laufzeitkopplung noch
  Persistenz- oder Ausführungsmacht.
- Der Guardian Classification Contract dokumentiert bereits bereitgestellte
  B1-/B2-/B3-Zuordnungen als unveränderlichen Nachweis. Kandidaten und
  Mindestschutz werden ausschließlich über die kanonische Boundary-Schutzordnung
  geprüft; Herkunft bedeutet keine Autorisierung. Der Baustein klassifiziert
  und aktiviert nichts und besitzt keine Runtime oder Ausführungsmacht.
- Die Guardian Answer Foundation Integration verbindet Boundary,
  Classification und Source Chain ausschließlich über immutable IDs und einen
  strukturellen Validator. Schutzvergleiche verwenden nur die kanonische
  Boundary-Ordnung; es entstehen keine Rückreferenz, Runtime, Aktivierung,
  Interpretation, Normalisierung oder Zustandsänderung.
- Das Guardian Controlled Orientation Package dokumentiert bereits
  bereitgestellte allgemeine B1-Orientierung als unveränderlichen Nachweis.
  Nur exakt B1 klassifizierte und begrenzte Inhalte mit mindestens einer
  vollständig und konsistent referenzierten Source Chain sind zulässig.
  Text, Quellen und fachliche Prüfung werden weder erzeugt noch semantisch
  bewertet; Herkunft und Prüfstatus bleiben rein deklarativ, ohne Runtime oder
  Ausführungsmacht.
- Das Guardian Personal Preparation Package dokumentiert bereits
  bereitgestellte persönliche B2-Vorbereitung mit bekannten Tatsachen, offenen
  Fragen, Optionen, Unsicherheiten und professionellen Prüfthemen. Es verlangt
  exakt B2/B2 und eine vollständige Source-Chain-Bindung; eine bestehende B1-
  Orientierung kann optional nur referenziert werden. Inhalte, Optionen und
  Risiken werden nicht erzeugt, interpretiert, priorisiert oder entschieden;
  Provider und Fachprüfstatus bleiben ohne Autorisierungs- oder
  Ausführungsmacht.
- Das Guardian Professional Decision Boundary Package dokumentiert eine bereits
  bereitgestellte B3-Reaktion mit fünf getrennten Bestandteilen: sachliche
  Anerkennung, klare Nicht-Bestätigung, professionelle Grenze, sichere
  Orientierung oder Vorbereitung und bei deklarierter akuter Gefahr ein
  bereitgestellter Soforthilfehinweis. Es verlangt exakt B3/B3, eine typisiert
  verlangte professionelle Einzelfallentscheidung und die vollständige
  Source-Chain-Bindung. Optionale B1-/B2-Nachweise werden nur referenziert;
  Texte, Dringlichkeit, Entscheidungen und Maßnahmen werden weder erzeugt noch
  interpretiert oder ausgeführt.
- Die End-to-End Guardian Answer Reference Journey verbindet die bestehenden
  Classification-, Boundary-, Source-Chain-, Foundation-, B1-, B2- und B3-
  Nachweise als immutable, deterministisch validierte Referenzreise. Zulässige
  vollständige und partielle Schutzpfade behalten ihre ursprünglichen Objekte,
  Quellen und Inhalte; die UI-neutrale Experience projiziert sie ohne
  Generierung, Interpretation, Priorisierung, Aktivierung oder Zustandsänderung.
- Das Guardian Authority Model beschreibt Authority-Typen, abstrakte
  Akteursklassen, Verantwortungsgrenzen, Delegierbarkeit, gemeinsame Ausübung,
  Widerrufbarkeit, Kontrollstufen, verbotene Kombinationen, Provenienz und
  Reviewstatus als immutable Architekturvertrag. Es autorisiert weder konkrete
  Provider noch Personen, besitzt keine Runtime und führt keine Befugnis aus.
- Das Guardian Provider Authorization Package bindet vorhandene Authority-
  Definitionen kontrolliert an bereits bereitgestellte Provider-Identitäten.
  Grants, Entscheidungsevidenz, Widerruf, Aussetzung, Ablauf, Wiederherstellung
  und Resolution Snapshots bleiben immutable und rein nachweisend; das Paket
  wählt keinen Provider, aktiviert keine Capability und besitzt keine Runtime.
- Die Guardian Capability Invocation Boundary dokumentiert ausschließlich
  bereitgestellte B1-Invocation-Requests, kontrollierte Entscheidungen und den
  vollständigen Authority-/Provider-/Authorization-/Lifecycle-Prüfpfad. Sie
  erzeugt immutable Receipts und read-only Snapshots ohne Persistenz,
  Provider-Ausführung, Capability-Aktivierung oder Runtime.
- Die Read-only B1 Provider Runtime führt erstmals genau einen bereits
  benannten und autorisierten Provider-Adapter aus, jedoch ausschließlich nach
  vollständig validiertem `ACCEPTED`-Invocation-Pfad, exakt für B1 und
  `READ_ONLY` sowie nur mit nicht personenbezogener oder ausdrücklich
  entpersonalisierter Datenbindung. Input, Kontext, Source Chains, Output,
  Ergebnis, Evidence und Receipt bleiben typisiert und immutable. Fehler,
  Timeout und ungültige Ausgaben degradieren fail-closed ohne Providerwahl,
  Fallback, Retry oder automatische Guardian-Antwort. Es gibt keine B2- oder
  B3-Runtime. Da kein kanonisch autorisierter externer Provider mit sicherer
  Credential-Grenze vorliegt, wurde keine externe Anbindung improvisiert; die
  Ausführungsgrenze ist mit einem kontrollierten Testadapter validiert.
- Runtime Incident Evidence v1 bindet bereits eingetretene oder ausdrücklich
  ausgebliebene Runtime-Ereignisse an die unveränderten Execution-, Result-,
  Evidence- und Receipt-Objekte der Read-only B1 Runtime. Typisierte Incident-
  und No-Incident-Nachweise sowie ein read-only Snapshot bleiben immutable und
  rein dokumentierend. No-Incident ist weder Qualitätsurteil noch Garantie;
  es gibt keine automatische Incident-Erkennung, Fehlerbehebung, Retry-Logik,
  Persistenz, Metrik, Benachrichtigung oder Aktivierung.
- Der nächste Produktbaustein ist noch nicht bestimmt.

## Bewusste Produktgrenzen

- Keine automatische Semantik
- Keine Intent Engine
- Kein Routing
- Keine Decision Engine
- Keine automatische Fähigkeitsaktivierung
- Keine automatische Workflow-Aktivierung
- Kein persistentes Guardian Memory
- Keine LLM-Integration
- Keine Confidence-Scores

## Nächster noch nicht begonnener Schritt

Noch nicht bestimmt. Der Handover wählt keinen Produktbaustein automatisch aus.
