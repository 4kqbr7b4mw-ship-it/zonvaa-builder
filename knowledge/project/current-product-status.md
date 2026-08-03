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
- Runtime Observation Governance v1
- Runtime Audit Architecture v1
- Operational Memory v1 (Speicherverträge ohne physische Persistenz)
- Physical Operational Persistence v1 (technologieneutraler Port ohne Adapter)
- Operational Metrics v1 (bereitgestellte technische Werte ohne Berechnung)
- Operational Notifications v1 (deklarative Nachweise ohne Zustellung)
- Guardian B2 Architecture v1 (reine Architekturentscheidung ohne Implementierung)
- C1 Governance Consolidation v1 (Dokumentation ohne I4-Neuerfindung)
- Institution Layer Completion v1 (Governance-Dokumentation ohne B2-Freigabe)
- Guardian B2 Data Corridor and Consent Boundary v1
- Guardian B2 Authority and Authorization v1

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
- Runtime Observation Governance v1 definiert versionierte,
  begründungspflichtige Observation Profiles und vollständig partitionierte
  Scopes ausschließlich für technische Systemereignisse. Nutzerverhalten,
  Profile, Inhalte, Interaktionsmuster und Nutzungsstatistiken bleiben
  ausdrücklich unbeobachtet. Validator und read-only Snapshot besitzen keine
  Nutzerbeobachtung und keine Observation Runtime, Analyse, Telemetrie,
  Evidence- oder Incident-Erzeugung, Persistenz oder Aktivierung.
- Runtime Audit Architecture v1 prüft bereitgestellte Observation-, Runtime-,
  Incident- und No-Incident-Nachweise ausschließlich innerhalb eines konkret
  gebundenen Observation Scopes. No-Incident Evidence führt Profile-Version,
  Scope, beobachtete und nicht beobachtete Ereignisse sowie durchgeführte und
  nicht durchgeführte Prüfungen. Fehlende Evidence bleibt eine sichtbare Lücke;
  nicht beobachtete Bereiche bleiben nicht beurteilbar. Audit prüft nur
  Systemverhalten und erzeugt keine Nutzerprofile, Persistenz, Metriken,
  Benachrichtigungen, Incident-Erkennung oder Runtime-Aktivierung.
- Die Gate-Bedingung aus ADR-0054 verlangte Runtime Audit Architecture v1 und
  einen ratifizierten, implementierten und validierten Operational-Memory-
  Block. Auch nach Erfüllung dieser Vorbedingungen autorisiert die Gate-Regel
  keine neue Runtime-Macht.
- Operational Memory v1 bildet ausschließlich bereits validierte,
  maschinengenerierte Observation-, Runtime-, Incident- und Audit-Nachweise als
  immutable Records und identitätstreue Artefaktbindungen ab. Der geschlossene
  Artefaktkatalog enthält keine Nutzerdaten, Gesprächsinhalte, Nutzerprofile,
  Nutzungsmuster oder personenbezogenen Artefakte. Duplikate werden durch
  Artefaktreferenz plus Version bestimmt. Validator und read-only Snapshot
  persistieren, verändern, ergänzen, löschen oder archivieren nichts.
- Physical Operational Persistence v1 definiert den einzigen
  technologieneutralen Port für `STORE`, `READ` und `EXISTS` sowie immutable
  physische Persistenz-, Backup- und Recovery-Nachweise. Der Validator bindet
  ausschließlich dieselben bereits validierten Operational-Memory-Objekte,
  Referenzen und Versionen. Er ruft keinen Port auf und führt weder Speicherung,
  Backup noch Recovery aus. Eine konkrete Datenbank-, Datei- oder Cloud-
  Anbindung existiert nicht.
- Löschung, Archivierung, Retention, Replikation und reale Backup-/Recovery-
  Ausführung bleiben offene, gesondert zu ratifizierende Architekturblöcke.
  AAV/UODL bleibt die getrennte spätere Hoheitsarchitektur für Nutzerdaten.
- Operational Metrics v1 bindet bereits bereitgestellte technische Werte an
  validierte Observation-, Audit-, Operational-Memory- und Physical-
  Persistence-Nachweise. Definitionen sind versioniert und führen nur den
  geschlossenen technischen Ereigniskatalog. Werte werden weder berechnet noch
  interpretiert; Nutzeridentitäten, Nutzungshäufigkeiten, Gesprächsthemen,
  Lebensbereiche und Profilbildung sind strukturell ausgeschlossen.
- Operational Notifications v1 dokumentiert bereits bereitgestellte
  betriebliche Benachrichtigungsentscheidungen auf Basis einer validierten
  Metrik oder eines beobachteten und physisch referenzierten Systemereignisses.
  Es gibt keine Endnutzeransprache, Textgenerierung, automatische Eskalation
  oder externe Zustellung.
- Der aus Operational Memory, Physical Operational Persistence, Operational
  Metrics und Operational Notifications bestehende Operational-Memory-Block
  ist auf Vertragsebene ratifiziert, implementiert und validiert. Dies gibt
  weder B2 noch B3 frei und erlaubt keine B2-/B3-Runtime oder Schreiboperation.
  Lediglich eine gesonderte Architekturentscheidung über eine mögliche
  B2-Stufe darf wieder aufgenommen werden.
- ADR-0058 definiert B2 als eigene Verfassungsstufe und nicht als Erweiterung
  der B1-Runtime. B2 benötigt eine eigene Authority-Klasse, eigene Grants,
  zweck-, zeit- und datenklassengebundene Datenhoheit sowie vorgeschaltete
  Minimierung und Depersonalisierung. D3 bleibt notwendig, ist aber nicht
  hinreichend; ein B1-Grant autorisiert niemals B2.
- Der bestehende Betriebsblock bleibt gegenüber B2-Inhalten blind:
  Observation und Audit prüfen nur Systemverhalten, Operational Memory und
  Physical Persistence speichern keine B2-Inhalte, Metrics und Notifications
  verarbeiten sie nicht. ADR-0058 implementiert weder Runtime noch Vertrag,
  Provider, API oder Produktfunktion.
- Die Gründer-Kenntnisnahme zu ADR-0058 ist am 02.08.2026 durch Michael Giese
  in konstituierender Funktion dokumentiert. Sie muss in der ersten
  ordentlichen Sitzung des künftig konstituierten Vertrauensrats bestätigt,
  geändert oder ersetzt werden.
- Die C1 Governance Consolidation ordnet C1, Institution, Authority und
  Runtime kanonisch ein und stellte die formale
  Vertrauensrats-Kenntnisnahmeunterlage für ADR-0058 bereit. Die Prüfung fand
  keine ursprüngliche I4-Quellnorm und keine mehrfachen ADR-Verweise darauf;
  deshalb wurde C1 nicht verändert und keine historische Regel rekonstruiert.
- Der B2-Readiness-Stand bestätigt den abgeschlossenen Betriebsblock und die
  abgeschlossene Verfassungsanalyse. Die historische I4-Frage ist als nicht
  belegbar geklärt; `GOV-SYSTEM-BEHAVIOR-ONLY-1` konsolidiert den bereits
  ratifizierten gemeinsamen Kern als neue C2-Referenz.
- Institution Layer Completion v1 dokumentiert Analyse, Referenz-Mapping,
  Gründer-Kenntnisnahme, institutionellen Freigabeablauf und eine nicht
  ausführende Future B2 Package Map.
- Die gesonderte institutionelle Freigabe
  `GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0059-V1` erlaubt ausschließlich Guardian
  B2 Data Corridor and Consent Boundary v1: ADR-0059, immutable Verträge,
  Consent Boundary, Data Classification, Depersonalization Boundary,
  deterministischen Validator, read-only Snapshot, Tests und Dokumentation.
- Alle weiteren B2-Pakete und jede B2-Runtime bleiben gesperrt.
- Guardian B2 Data Corridor and Consent Boundary v1 bindet D1–D6, D3, die
  kanonische AAV-Autorisierung und dieselbe UODL-Referenz in immutable
  Verträgen. Vollständige Negativregeln schließen Datenklassen, Quellen,
  Flüsse, Kombinationen, Restidentifikatoren, Zweckänderungen und jede
  Weitergabe an den Betriebsblock typisiert aus. Validator und read-only
  Snapshot bewegen, verarbeiten oder speichern keine Daten.
- ADR-0059 ist implementiert und validiert. Alle weiteren B2-Pakete sowie die
  B2-Runtime bleiben GESPERRT und benötigen eine eigene institutionelle
  Freigabe.
- ADR-0060 beschreibt Guardian B2 Authority and Authorization v1 als
  ratifizierte Architektur. Die Architektur trennt B2 strukturell von
  B1, definiert immutable Grants ohne Wirksamkeitszustand, die vollständige
  D3-/T4-/AAV-/UODL-Bindung, Purpose-Verengung, einen expliziten
  Auswertungszeitpunkt und rein punktuelle Evaluation Evidence. Der begrenzt
  freigegebene Vertragsscope ist als eigenständige immutable B2-Typfamilie,
  zustandslose Evaluation, positive Rekonstruktionsquittung und nicht
  personenbezogene Negative Governance Evidence implementiert. Grants besitzen
  keinen Wirksamkeitszustand; D3 ist notwendig, aber niemals hinreichend.
  Ratifizierung und begrenzte
  Implementierungsfreigabe sind getrennt dokumentiert durch
  `GOV-RATIFICATION-ADR-0060-V1` und
  `GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0060-V1`. Provider, Invocation, Runtime
  und jede technische Grant-Ausführung bleiben gesperrt.
- `GOV-INSTITUTIONAL-DECISION-SCOPE-1` verlangt künftig für jeden
  institutionellen Beschluss getrennte Abschnitte `Freigegeben` und
  `Ausdrücklich nicht freigegeben`.
- Guardian Accountability & Explanation Layer ist ausschließlich als offener,
  nicht geplanter und nicht implementierter Architekturkandidat registriert.
  Die Registrierung ist eine eng begrenzte Ausnahme zu ADR-0046 E6, weil der
  Kandidat bereits heute wirksame Verifizierbarkeitsgrenzen sichtbar hält; E6
  bleibt unverändert. Aktivierung verlangt produktive B2-Runtime, erste reale
  Rechenschaftspflichten und einen dokumentierten Aktivierungsbeschluss.
- `GOV-NO-FABRICATION-1` ist nur ein offener Konsolidierungspunkt und keine
  neue Governance-Regel. Aus beiden Registrierungen folgen weder Runtime, API,
  Erklärungsschicht noch Implementierungsfreigabe.
- Guardian Life Domain Model ist ausschließlich als offener, nicht geplanter
  und nicht implementierter Architekturkandidat registriert. Die Registrierung
  ist eine auf sie begrenzte Ausnahme zu ADR-0046 E6; ADR-0046 und E6 bleiben
  unverändert. Der Kandidat hält typisierte, jurisdiktionstreue Lebensobjekte,
  Sprache als reine Darstellung und Wachstum nur entlang realer Journeys fest.
  Die Vorsorgevollmacht ist der erste registrierte Kernbereich. Aktivierung
  verlangt produktive B2-Runtime, stabile Conversation-Architektur und einen
  dokumentierten Aktivierungsbeschluss; daraus folgen keine Runtime, API,
  Datenbank, juristischen Inhalte, Gesprächsführung oder Implementierungsfreigabe.
- ADR-0061 Guardian B2 Provider Identity v1 ist durch
  `GOV-RATIFICATION-ADR-0061-V1` ratifiziert und durch
  `GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0061-V1` ausschließlich im nicht
  ausführenden Provider-Identity-Scope implementierungsfreigegeben. Die
  Architektur begrenzt v1 auf fünf geschlossene,
  nicht personenbezogene Provider Classes, geschlossene Verantwortungs-Codes
  und Capability-Descriptoren sowie institutionelle Provenienzreferenzen mit
  explizitem Zeitpunkt. Sie übernimmt keine freie B1-Semantik, führt keine
  Schema-Versionierung ein und erzeugt weder Authorization, Invocation,
  Runtime, Schlüssel- oder Inhaltszugriff. Die Freigabe implementiert nichts;
  ein separater Codex-Auftrag bleibt erforderlich.
- Guardian B2 Provider Identity v1 ist implementiert. Die eigenständige
  immutable Typfamilie führt ausschließlich die fünf ratifizierten geschlossenen
  Provider Classes, geschlossene Responsibility Areas und Capability-
  Descriptoren sowie typisierte institutionelle Provenienz mit explizitem
  Erstellungszeitpunkt. Sie beschreibt keine natürliche Person und besitzt
  keine Autorisierungs-, Invocation- oder Runtime-Wirkung. B1-Konvertierung,
  Authority, Grants, Status, Schlüssel, Sessions, Caches, Tokens und
  personenbezogene Inhalte sind strukturell nicht modellierbar.

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

Als nächste B2-Aktivität ist ausschließlich ein separater Codex-Auftrag im
geschlossenen Scope von `GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0061-V1`
zulässig. Alle anderen B2-Pakete bleiben gesperrt.
B2-Runtime und alle späteren B2-Machtstufen bleiben gesperrt.
