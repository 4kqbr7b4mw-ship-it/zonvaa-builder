# ADR-0064-A1 – Governance Decision and Incident Closed Taxonomies v1

Status: **RATIFIZIERT – INSTITUTIONELL IMPLEMENTIERUNGSFREIGEGEBEN – NICHT IMPLEMENTIERT**

Ratifizierungsnachweis: `GOV-RATIFICATION-ADR-0064-A1-V1`

Implementierungsfreigabe: `GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0064-A1-V1`

Die Ratifizierung und die davon getrennte Implementierungsfreigabe bestätigen
ausschließlich diese geschlossenen Taxonomien. Die Freigabe implementiert
nichts, wendet den gesicherten Stash nicht an und nimmt die ADR-0064-
Implementierung in ihrem Dokumentationsauftrag nicht wieder auf.

## 1. Bezug zu ADR-0064

Diese Ergänzung schließt ausschließlich die in ADR-0064 vorausgesetzten, dort
aber nicht mit Werten festgelegten Typmengen. ADR-0064 bleibt der ratifizierte
Haupt-ADR. ADR-0064-A1 ersetzt ihn nicht, ändert keine Historie und erzeugt
weder Ratifizierung noch Implementierungsfreigabe oder Implementierung.

## 2. Anlass und Implementierungsblocker

Der Implementierungsversuch zu ADR-0064 konnte die elf ratifizierten
Incident-Klassen und `UNBEKANNT` unmittelbar abbilden. Vollständige Decision
Records und Incident Evidence erfordern weitere geschlossene Typmengen. Ihre
Werte waren nicht ratifiziert; eine technische Festlegung hätte neue
Governance-Semantik erfunden. Der partielle Arbeitsstand ist deshalb
reversibel in einem benannten Stash gesichert und nicht kanonische
Implementierung.

## 3. Kanonische Grundlagen

- ADR-0064 und `GOV-RATIFICATION-ADR-0064-V1`;
- `GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0064-V1`;
- `GOV-INSTITUTIONAL-DECISION-SCOPE-1`;
- die 18 Schritte des B2-Verfassungsreviews;
- tatsächlich dokumentierte Ratifikations-, Freigabe-, Commit- und
  Push-Entscheidungen;
- der dokumentierte ADR-0061-Prozessvorfall;
- die Trennung zu ADR-0052, Observation, Audit und Operational Memory.

## 4. Regel für geschlossene Typmengen

Jeder v1-Wert besitzt eine benennbare Grundlage. Erweiterungen erfordern einen
neuen institutionellen Architekturakt. Freie Codes, dynamische Registrierung,
Fallbackwerte und `OTHER` sind unzulässig. Darstellungstext ist niemals Code,
Evidence, Scope oder Entscheidung.

## 5. Governance Decision Classes

Die kleinste belegte Menge lautet:

| Code | Bedeutung und zulässiger Ort | Zwingende Evidence und Scope | Quelle | Unzulässige Verwendung |
|---|---|---|---|---|
| `ARCHITECTURE_RATIFICATION` | dokumentiert eine menschliche Ratifizierung eines bezeichneten ADR | Ratifizierungsartefakt; Architektur-Scope und Ausschlüsse | Ratifikationen ADR-0060–0064 | keine Implementierungsfreigabe |
| `INSTITUTIONAL_IMPLEMENTATION_APPROVAL` | dokumentiert die getrennte institutionelle Implementierungsfreigabe | Freigabeartefakt; freigegebener und ausgeschlossener Scope | Freigaben ADR-0059–0064 | keine Ratifizierung, Ausführung oder Commit-Freigabe |
| `COMMIT_APPROVAL` | dokumentiert die ausdrückliche Freigabe genau eines reviewten Commit-Scope | Commit-Auftrag und Validierungsevidence; exakter Dateiscope | AGENTS.md und belegte Commit-Aufträge | erstellt oder autorisiert keinen Push |
| `PUSH_APPROVAL` | dokumentiert die ausdrückliche Freigabe benannter Commits für ein Remote-Ziel | Push-Auftrag, Commit-Referenzen und Remote-Bezug | AGENTS.md und belegte Push-Aufträge | erzeugt keinen Commit und keine fachliche Freigabe |

Eine Kenntnisnahme, gutachterliche Bewertung oder Implementierungsbeauftragung
ist in v1 keine Decision Class. Sie bleibt Prozess- beziehungsweise
Auftragsevidence und wird nicht zur institutionellen Entscheidung umgedeutet.

## 6. Institutionelle Entscheidungsrollen

| Code | Funktion | Zulässige Decision Classes | Unzulässig | Quelle |
|---|---|---|---|---|
| `INSTITUTION_FOUNDER` | konstituierende institutionelle Entscheidungsrolle | `ARCHITECTURE_RATIFICATION`, `INSTITUTIONAL_IMPLEMENTATION_APPROVAL` | keine persönliche Identität, keine automatische Stellvertretung | dokumentierte Ratifizierungen und Freigaben ADR-0060–0064 |
| `CHIEF_ARCHITECT` | begrenzt Architektur- und Repository-Aufträge | `COMMIT_APPROVAL`, `PUSH_APPROVAL` | keine institutionelle Ratifizierung oder Implementierungsfreigabe | AGENTS.md und institutioneller Freigabeablauf |
| `REVIEWER` | reine Gutachter- und Bewertungsrolle | keine Decision Class | keine Ratifikations-, Freigabe-, Commit- oder Pushwirkung | Schritt 1 des institutionellen Freigabeablaufs |

Rollen sind geschlossene institutionelle Rollen, niemals Namen, Konten,
E-Mail-Adressen oder Personenobjekte. Delegation oder Stellvertretung wird
nicht angenommen.

## 7. Governance-Schritte

Die kanonische Sequenz enthält exakt 18 unterscheidungsrelevante Schritte:

| Nr. | Code | Bedeutung | Quelle und Negativabgrenzung |
|---:|---|---|---|
| 1 | `ARCHITECTURE` | fachliche Architekturarbeit | Review-Sequenz; keine Entscheidung |
| 2 | `ADR_DOCUMENTATION` | ADR-Dokumentation | kein Ratifikationsnachweis |
| 3 | `ARCHITECTURE_VALIDATION` | Architekturprüfung | keine Ratifizierung |
| 4 | `HUMAN_RATIFICATION` | externer menschlicher Beschluss | nicht dessen Repository-Dokumentation |
| 5 | `RATIFICATION_DOCUMENTATION` | Dokumentation des Beschlusses | trifft ihn nicht selbst |
| 6 | `RATIFICATION_COMMIT` | Commit der Dokumentation | keine Push- oder Freigabewirkung |
| 7 | `RATIFICATION_PUSH` | Push des Ratifikationscommits | beweist keine externe Beschlusszeit |
| 8 | `INSTITUTIONAL_IMPLEMENTATION_APPROVAL` | externer Freigabebeschluss | keine Implementierung |
| 9 | `IMPLEMENTATION_APPROVAL_DOCUMENTATION` | Dokumentation der Freigabe | erteilt sie nicht selbst |
| 10 | `IMPLEMENTATION_APPROVAL_COMMIT` | Freigabe-Commit | keine Pushwirkung |
| 11 | `IMPLEMENTATION_APPROVAL_PUSH` | Push des Freigabe-Commits | kein Implementierungsauftrag |
| 12 | `SEPARATE_IMPLEMENTATION_ORDER` | separater begrenzter Auftrag | keine Scope-Erweiterung |
| 13 | `IMPLEMENTATION` | lokale Umsetzung | keine Commit-Freigabe |
| 14 | `TESTS_AND_REVIEW` | Validierung und Review | keine fachliche Entscheidung |
| 15 | `COMMIT_APPROVAL` | ausdrückliche Commit-Freigabe | kein Commit und kein Push |
| 16 | `IMPLEMENTATION_COMMIT` | Commit des reviewten Scope | keine Push-Freigabe |
| 17 | `PUSH_APPROVAL` | ausdrückliche Push-Freigabe | kein Push |
| 18 | `IMPLEMENTATION_PUSH` | Push benannter Commits | keine neue Machtfreigabe |

`git add`, einzelne Testkommandos oder andere technische Unteroperationen sind
keine Governance-Schritte.

## 8. Scope-Verfassung

Gewählt wird Variante D: geschlossener Scope-Typ plus kanonische Artefakt- und
Abschnittsreferenz.

Geschlossene Scope-Typen:

- `GRANTED_SCOPE`: ausschließlich explizit freigegebener Abschnitt;
- `EXCLUDED_SCOPE`: ausdrücklich nicht freigegebener Abschnitt.

Ein Scope-Eintrag enthält eine typisierte kanonische Artefaktreferenz und eine
maschinenlesbare Abschnittsreferenz. Freigegebene und ausgeschlossene Mengen
sind disjunkt. Fehlende Nennung ist Nichtfreigabe, aber kein künstlicher
`DEFAULT_DENIED`-Datensatz.

Bewertung der Varianten:

- A wird verworfen: globale Fachcodeliste wäre eine zweite Scope-Verfassung.
- B wird verworfen: freie Strings sind weder beweisbar noch geschlossen.
- C wird verworfen: eine bloße Referenz unterscheidet Freigabe und Ausschluss
  nicht strukturell.
- D wird bevorzugt: geschlossene Polarität, eine Wahrheit im referenzierten
  Artefakt, maschinelle Prüfbarkeit und Erweiterung nur durch neue kanonische
  Artefakte.
- E ist nicht erforderlich; keine weitere Semantik wird eingeführt.

## 9. Governance-Abweichungscodes

ADR-0064 trennt Incident Class und beobachtete Abweichung. Dafür genügt eine
geschlossene Abweichungsrelation; sie bildet keine zweite Incident-Verfassung:

| Code | Semantik/Verwendungsort | Quelle | Negativabgrenzung |
|---|---|---|---|
| `STEP_OCCURRED_BEFORE_REQUIRED_PREDECESSOR` | tatsächlicher Schritt lag vor seinem Gate | Incident-Klassen 1–5 und 18-Schritt-Folge | kein Schuldurteil |
| `REQUIRED_APPROVAL_ABSENT` | erforderlicher Beschlussnachweis fehlt am Gate | Incident-Klassen 1–2, 4–5 | behauptet nicht, dass nie entschieden wurde |
| `REQUIRED_EVIDENCE_ABSENT` | bezeichnete Evidence fehlt | `GOVERNANCE_EVIDENCE_MISSING` | ersetzt Evidence nicht |
| `APPROVED_SCOPE_EXCEEDED` | beobachteter Scope liegt außerhalb der Referenz | `SCOPE_EXCEEDED` | keine Sanktion |
| `DOCUMENTED_STATUS_CONTRADICTS_EVIDENCE` | Statusdarstellung widerspricht Evidence | `STATUS_MISREPRESENTED` | keine Motivannahme |
| `WORK_STATE_RETROACTIVELY_REINTERPRETED` | früherer Stand wurde rückwirkend umgedeutet | gleichnamige Incident Class | keine Legitimierung |
| `DECISION_TIME_EVIDENCE_ABSENT` | Beschlusszeit ist unbelegt | `DECISION_TIME_NOT_DOCUMENTED` | keine Zeitschätzung |
| `DECISION_AND_DOCUMENTATION_TIME_CONFLATED` | Zeitarten wurden nicht getrennt | gleichnamige Incident Class | kein Ersatzzeitpunkt |

Incident Class, Governance-Schritt, Abweichungsrelation und Evidence müssen
konsistent sein; keine Komponente darf aus den anderen automatisch erfunden
werden.

## 10. Vorhandene Evidence-Arten

| Code | Kann bestätigen | Kann nicht bestätigen | Grundlage |
|---|---|---|---|
| `ADR_ARTIFACT` | dokumentierten Architekturinhalt | menschliche Ratifizierung | ADR-Konvention |
| `ARCHITECTURE_VALIDATION_ARTIFACT` | ausgeführte dokumentierte Architekturprüfung | institutionellen Beschluss | Review-Sequenz |
| `RATIFICATION_RECORD` | dokumentierten externen Ratifikationsbeschluss im belegten Scope | Implementierungsfreigabe | Ratifikationsdokumente |
| `IMPLEMENTATION_APPROVAL_RECORD` | dokumentierte institutionelle Freigabe | Implementierung, Commit oder Push | Freigabedokumente |
| `COMMIT_REFERENCE` | Commit-Identität und Git-Inhalt | menschliche Entscheidung oder damaligen Push | Git-Evidenzregel ADR-0064 |
| `PUSH_EVIDENCE` | belegten Transport benannter Commits zum Ziel | fachliche Entscheidung | dokumentierte Push-Prüfungen |
| `TEST_VALIDATION_ARTIFACT` | bezeichnetes Testergebnis | Ratifizierung oder Scope-Freigabe | Test-/Review-Schritt |
| `HANDOVER_ARTIFACT` | dokumentierten Übergabestand | institutionellen Beschluss | ADR-0059-Befund |
| `REPOSITORY_STATUS_EVIDENCE` | Zustand zum Erfassungszeitpunkt | historischen Push- oder Beschlusszeitpunkt | ADR-0064 Zeitregel |
| `GOVERNANCE_DECISION_RECORD` | bereits evidenzgebunden dokumentierten Beschlussumfang | neue oder automatische Entscheidung | ADR-0064 Decision Record |

Provenienz ist keine Evidence-Art und ersetzt keine dieser Referenzen.

## 11. Missing-Evidence-Arten und Status

Geschlossene Arten:

| Code | Nicht bestätigbare Aussage | Betroffener Schritt/Quelle | Negativabgrenzung |
|---|---|---|---|
| `RATIFICATION_EVIDENCE_MISSING` | Ratifizierung ist nicht bestätigt | Schritte 4–7; ADR-0059-Befund | keine Behauptung der Nichtexistenz |
| `IMPLEMENTATION_APPROVAL_EVIDENCE_MISSING` | Freigabe ist nicht bestätigt | Schritte 8–11 | keine automatische Sperre |
| `COMMIT_APPROVAL_EVIDENCE_MISSING` | Commit-Freigabe ist nicht bestätigt | Schritt 15 | Commit ersetzt sie nicht |
| `PUSH_APPROVAL_EVIDENCE_MISSING` | Push-Freigabe ist nicht bestätigt | Schritt 17 | Push ersetzt sie nicht |
| `DECISION_TIME_EVIDENCE_MISSING` | Beschlusszeit ist unbekannt | Schritte 4 oder 8 | keine Git-Zeitableitung |
| `DECISION_ROLE_EVIDENCE_MISSING` | institutionelle Rolle ist unbekannt | Schritte 4 oder 8 | kein Personenraten |
| `SCOPE_DOCUMENTATION_MISSING` | Umfang ist nicht bestätigt | Decision Record | fehlende Nennung bleibt Nichtfreigabe |
| `PUSH_TIME_NOT_RECONSTRUCTABLE` | damaliger Pushzeitpunkt ist unbekannt | Schritte 7 oder 11 oder 18 | heutige Synchronisation ersetzt ihn nicht |
| `DECISION_DOCUMENTATION_TIME_SEPARATION_MISSING` | Zeittrennung ist nicht bestätigt | Decision Record | Dokumentationszeit ersetzt keine Beschlusszeit |

Geschlossene Status:

- `OPEN`: Evidence fehlt weiterhin;
- `CLOSED_BY_REFERENCED_EVIDENCE`: die zuvor fehlende Evidence ist nun
  referenziert, ohne den früheren Prozess rückwirkend zu legitimieren;
- `HISTORICALLY_NOT_RECONSTRUCTABLE`: die historische Lücke bleibt dauerhaft
  als nicht rekonstruierbar dokumentiert.

## 12. Auswirkungscodes

| Code | Aussage | Quelle/Ort | Unzulässige Deutung |
|---|---|---|---|
| `GOVERNANCE_TRACEABILITY_LIMITED` | Nachvollziehbarkeit ist evidence-begrenzt | ADR-0059-Befund | kein technischer Schaden |
| `GATE_SEQUENCE_BREACHED` | belegte Reihenfolge wich ab | ADR-0061-Vorfall | keine Schuldzuweisung |
| `SCOPE_CONFORMITY_UNCONFIRMED` | Scope-Konformität ist nicht bestätigt | Scope-Incident | kein Beweis der Überschreitung |
| `FORMAL_STATUS_UNCONFIRMED` | formaler Status ist evidence-seitig offen | Status-Incident | keine automatische Statusänderung |
| `NO_TECHNICAL_ERROR_EVIDENCED` | im Beobachtungsumfang ist kein Codefehler belegt | ADR-0061-Vorfall | keine Qualitätsgarantie |
| `NO_RUNTIME_IMPACT_EVIDENCED` | keine Runtime-Auswirkung ist belegt | ADR-0064-Abgrenzung | kein Runtime-Audit |
| `NO_PERSONAL_DATA_IMPACT_EVIDENCED` | keine personenbezogene Auswirkung ist belegt | Negative Rules | keine Personenbeobachtung |

Es gibt keine Schweregrade, Risikoscores oder Sanktionsvorschläge.

## 13. Korrekturfolgeschritte

| Code | Beschreibung | Quelle | Keine Wirkung |
|---|---|---|---|
| `DOCUMENT_MISSING_EVIDENCE` | fehlenden Nachweis sichtbar dokumentieren | ADR-0059-Befund | erzeugt ihn nicht |
| `PUSH_APPROVAL_COMMIT` | Freigabe-Commit nach Freigabe pushen | ADR-0061-Korrektur | keine Rückwirkung |
| `REISSUE_IMPLEMENTATION_ORDER` | Auftrag nach kanonischem Push neu erteilen | ADR-0061-Korrektur | erkennt Altstand nicht automatisch an |
| `REVALIDATE_WORK_STATE_AGAINST_SCOPE` | vorhandenen Stand erneut prüfen | ADR-0061-Korrektur | keine automatische Anerkennung |
| `ADD_MISSING_NEGATIVE_TESTS` | belegte Testlücke schließen | Review-Prozess | keine Architekturänderung |
| `CORRECT_STATUS_DOCUMENTATION` | falsche Darstellung berichtigen | Status-Incident | keine fachliche Freigabe |
| `DOCUMENT_GOVERNANCE_INCIDENT` | belegten Vorfall dokumentieren | ADR-0064 | keine Sanktion |
| `REQUEST_INSTITUTIONAL_DECISION` | offene Entscheidung anfordern | offenes Gate | beantwortet sie nicht |

Jeder Schritt führt zusätzlich den Ausführungsstand `DOCUMENTED_AS_COMPLETED`
oder `DOCUMENTED_AS_OPEN`. Dieser Stand beschreibt nur die Korrekturfolge und
führt keine Aktion aus.

## 14. Dokumentationsstände

- `FULLY_DOCUMENTED`: alle für den Aussageumfang erforderlichen Referenzen
  sind vorhanden;
- `INCOMPLETELY_DOCUMENTED`: Pflichtdokumentation ist unvollständig;
- `OPEN_EVIDENCE_GAP`: mindestens eine Evidence-Lücke ist offen;
- `HISTORICALLY_NOT_FULLY_RECONSTRUCTABLE`: historische Pflichtangaben bleiben
  unbekannt;
- `CORRECTION_SEQUENCE_DOCUMENTED`: Korrekturfolge ist dokumentiert;
- `INSTITUTIONAL_DECISION_OPEN`: eine ausdrücklich bezeichnete Entscheidung
  steht aus.

Diese Werte beschreiben Dokumentation, niemals Wirksamkeit, Autorisierung,
Sperre, Sanktion oder Freigabe.

## 15. Beobachtungs- und Aussageumfänge

- `DECISION_DOCUMENTED`;
- `SCOPE_DOCUMENTED`;
- `REPOSITORY_STATE_DOCUMENTED`;
- `SEQUENCE_DEVIATION_DOCUMENTED`;
- `EVIDENCE_GAP_DOCUMENTED`;
- `CORRECTION_SEQUENCE_DOCUMENTED`;
- `HISTORICAL_TIME_UNKNOWN_DOCUMENTED`;
- `NO_TECHNICAL_IMPACT_EVIDENCED`.

Jeder Wert ist auf ausdrücklich referenzierte Artefakte begrenzt. Er ist keine
Entscheidung, Autorisierung oder Aussage über Personen und erweitert Evidence
nicht.

## 16. Provenienz-Artefaktklassen und Kontexte

Geschlossene Artefaktklassen:

- `ADR`;
- `RATIFICATION_RECORD`;
- `IMPLEMENTATION_APPROVAL_RECORD`;
- `COMMIT`;
- `PUSH_EVIDENCE`;
- `TEST_ARTIFACT`;
- `HANDOVER`;
- `GOVERNANCE_DECISION_RECORD`;
- `GOVERNANCE_INCIDENT_EVIDENCE`.

Geschlossene Dokumentationskontexte:

- `ARCHITECTURE`;
- `RATIFICATION`;
- `IMPLEMENTATION_APPROVAL`;
- `IMPLEMENTATION`;
- `VALIDATION`;
- `COMMIT`;
- `PUSH`;
- `GOVERNANCE_REVIEW`;
- `INCIDENT_DOCUMENTATION`.

Die Werte stammen aus den vorhandenen kanonischen Artefakt- und
Prozessfamilien. Personen, Geräte, Konten und Organisationseinheiten sind
keine Provenienzobjekte. Provenienz bestätigt nur Herkunft, nicht Wahrheit,
Entscheidung oder Scope.

## 17. Offene Entscheidungsfragen

Gewählt wird eine geschlossene Fragenklasse plus maschinenlesbare kanonische
Referenz und optionale begrenzte nicht autoritative Darstellung.

Geschlossene Fragenklassen:

- `ARCHITECTURE_DECISION_REQUIRED`;
- `RATIFICATION_REQUIRED`;
- `IMPLEMENTATION_APPROVAL_REQUIRED`;
- `EVIDENCE_CONFIRMATION_REQUIRED`;
- `CORRECTION_SEQUENCE_DECISION_REQUIRED`.

Die Darstellung darf die Frage lesbar machen, besitzt aber keine Scope-,
Evidence- oder Entscheidungssemantik und darf keine personenbezogenen Inhalte
führen. Vollständig freie Fragen werden verworfen; nur eine Klasse ohne
Referenz wäre nicht rekonstruierbar.

## 18. Beziehungen zwischen den Typmengen

- Decision Class und institutionelle Rolle müssen der Rollenmatrix entsprechen.
- Jeder Decision Record enthält disjunkte `GRANTED_SCOPE`- und
  `EXCLUDED_SCOPE`-Mengen.
- Incident Class, Governance-Schritt und Abweichungsrelation müssen ein
  zulässiges, evidence-belegtes Tripel bilden.
- Evidence-Art begrenzt den Aussageumfang.
- Missing Evidence bleibt von vorhandener Evidence getrennt.
- `CLOSED_BY_REFERENCED_EVIDENCE` verlangt eine vorhandene Evidence-Referenz,
  verändert aber Incident und Historie nicht.
- Auswirkung, Korrekturfolge und Dokumentationsstand sind rein beschreibend.
- Provenienz darf keine fehlende Evidence ersetzen.
- Eine offene Frage bleibt von Decision Records getrennt.

## 19. Strukturelle Invarianten

Jede Typmenge ist geschlossen und jeder Wert hat eine benannte Grundlage.
Unbekannte historische Tatsachen bleiben unbekannt. Rollen sind
institutionell und nicht personenbezogen. Decision Record und Incident
Evidence, vorhandene und fehlende Evidence sowie freigegebener und
ausgeschlossener Scope bleiben getrennt. Kein Dokumentationswert besitzt
Autorisierungs-, Sperr- oder Sanktionswirkung. Korrekturschritte führen nichts
aus; offene Fragen beantworten sich nicht selbst. Es gibt keine automatische
Record- oder Incident-Erzeugung, Runtime, Observation oder personenbezogene
Verarbeitung.

## 20. Negative Rules

Unzulässig sind freie Codes, `OTHER`, implizite Defaults, natürliche Personen,
Namen, Konten, Profile, Bewertungen, Sanktionen, Sperren, Widerruf,
Autorisierung, automatische Entscheidung, Ratifizierung, Freigabe,
Scope-Erweiterung, rückwirkende Legitimierung, Zeitrekonstruktion aus Git,
Evidence-Ersatz durch Provenienz, automatische Klassifikation oder Erzeugung,
Observation, Überwachung, Runtime Audit, Operational Memory, Metrics,
Notifications, Capability Invocation, Runtime und technische Ausführung.

## 21. Auswirkungen auf den gesicherten partiellen Stand

Voraussichtlich kompatibel, aber nicht automatisch übernehmbar, sind die elf
unveränderten Incident-Klassen, `UNBEKANNT`, die ID-Primitiven, nicht
personenbezogene Evidence-Referenzen, explizite timezone-aware Zeitwerte und
die leeren kanonischen Verwahrorte. Sämtliche Primitive müssen nach einer
Ratifizierung erneut gegen ADR-0064 und ADR-0064-A1 geprüft werden.

Danach wären Decision Record, Incident Evidence, Missing Evidence,
Governance-Provenienz sowie vollständige zustandslose Validatoren technisch
entscheidbar. Der Stash ist keine kanonische Implementierung. Nichts daraus
darf vor Ratifizierung, Implementierungsfreigabe und neuem Auftrag angewendet
werden. Eine spätere bloße Wiederanwendung wäre keine
Implementierungsgenehmigung und ersetzt die vollständige Neuprüfung nicht.

## 22. Wiederaufnahmebedingungen

Die menschliche Ratifizierung ist durch
`GOV-RATIFICATION-ADR-0064-A1-V1` getrennt dokumentiert. Vor einer technischen
Wiederaufnahme bleiben erforderlich:

1. Commit und Push der Ratifizierungsdokumentation;
2. gesonderte institutionelle Implementierungsfreigabe;
3. Dokumentation, Commit und Push dieser Freigabe;
4. separater Implementierungsauftrag;
5. vollständige Prüfung des gesicherten Stands gegen beide ADRs.

## 23. Prüffrage Null

Kann diese Architektur eine nicht gefasste Entscheidung als gefasst behandeln,
Evidence ersetzen, unbekannte Zeit als bekannt behandeln, Scope stillschweigend
erweitern, Gutachten zur institutionellen Entscheidung machen, Personen
modellieren oder sanktionieren, rückwirkend legitimieren oder automatische
Entscheidung, Observation, Invocation, Runtime oder personenbezogene Zustände
erzeugen?

Antwort: **Nein.** Alle Typmengen sind geschlossen, referenzgebunden,
nicht personenbezogen und ohne ausführende Wirkung.

## 24. Ratifikationsanforderungen

Die Ratifizierung muss alle Tabellen und geschlossenen Mengen ausdrücklich als
abschließend bestätigen. Änderungen, Ergänzungen oder Auslassungen erfordern
eine neue Architekturprüfung. Die Ratifizierung darf ADR-0059 nicht bestätigen
und keinen Stash anerkennen. Diese Anforderungen werden durch
`GOV-RATIFICATION-ADR-0064-A1-V1` erfüllt; daraus folgt keine
Implementierungsfreigabe.

## 25. Implementierungsfreigabeanforderungen

Eine spätere Freigabe muss den implementierbaren Vertragsscope und sämtliche
Ausschlüsse getrennt nennen. Sie darf weder Stash-Anwendung noch Migration,
historische Records, automatische Erzeugung, Observation oder Runtime
stillschweigend freigeben.

## 26. Testanforderungen

Erforderlich sind eigene Positiv- und Negativtests für jede Typmenge,
Rollenmatrix, 18-Schritt-Sequenz, Scope-Disjunktheit, Evidence-Grenzen,
Missing-Evidence-Status, Zeittrennung, Beziehungen, Immutability und sämtliche
Negative Rules. Public API und Verwahrorte bleiben getrennt zu prüfen.

## 27. Ausdrücklich nicht freigegeben

Nicht freigegeben sind Ratifizierung, Implementierungsfreigabe,
Implementierung, Stash-Anwendung, Migration, historische Decision oder
Incident Records, ADR-0059-Bestätigung, neue Incident-Klassen, freie Semantik,
natürliche Personen, Sanktion, Sperre, automatische Entscheidungen,
Observation, Audit, Operational Memory, Capability Invocation, Runtime,
ADR-0065, Commit und Push.
