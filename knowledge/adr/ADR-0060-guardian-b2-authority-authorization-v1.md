# ADR-0060 – Guardian B2 Authority and Authorization v1

Status: RATIFIZIERT – IMPLEMENTIERUNG BEGRENZT FREIGEGEBEN – IMPLEMENTIERT UND VALIDIERT

Ratifizierungsdatum: 02.08.2026

Ratifizierungsnachweis: `GOV-RATIFICATION-ADR-0060-V1`

Implementierungsfreigabe: `GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0060-V1`

## Normativer Zeitstand und Evidenz

- **Ursprünglicher Entscheidungsinhalt:** ADR-0060 entschied ausschließlich
  die nicht ausführende Architektur; der Architekturakt selbst implementierte
  keinen Vertrag und erteilte keine Implementierungsfreigabe.
- **Historischer damaliger Governance-Zustand:** Nach Ratifizierung und
  Implementierungsfreigabe war der separate Implementierungsauftrag zunächst
  offen. Diese Vorstufe bleibt als damaliger Gate-Zustand sichtbar und wird
  nicht rückwirkend umgedeutet.
- **Gegenwärtiger normativer Status:** ADR-0060 ist ratifiziert, begrenzt
  implementierungsfreigegeben, implementiert und validiert. Runtime und
  technische Grant-Ausführung bleiben ausgeschlossen.
- **Implementierungs- und Validierungsevidenz:**
  `governance/b2_authorization.py` sowie die zugehörigen fokussierten
  Authorization- und Dokumentationstests; Implementierungs-Commit
  `ebc050d1ebb9e15f828f918b1d9cd2ff8c970b0f`.
- **Commit- und Push-Evidenz:** Der Implementierungs-Commit ist im aktuellen
  `origin/builder-reset-v2` enthalten. Diese heutige Repository-Evidenz
  ersetzt keinen historischen Beschluss- oder Pushzeitpunkt.

## 1. Kontext und Governance-Grenze

ADR-0058 verlangt für B2 eine eigenständige Verfassungsstufe. ADR-0059
definiert den vorgeschalteten Datenkorridor, autorisiert aber weder Authority
noch Grants. ADR-0060 entschied deshalb ursprünglich ausschließlich die
Architektur von B2 Authority, B2 Grants und deren zustandsloser Evaluation.
Der damalige Architekturakt implementierte keinen Vertrag, Validator,
Provider, Datenzugriff und keine Runtime. Der gegenwärtige Implementierungsstand
ist im Abschnitt „Normativer Zeitstand und Evidenz“ getrennt dokumentiert.

Diese ADR ist trotz Ratifizierung keine institutionelle Implementierungsfreigabe. Verbindliche
Sequenz:

1. ADR-0060 dokumentieren. Abgeschlossen.
2. Architektur validieren. Abgeschlossen.
3. ADR-0060 ausdrücklich menschlich ratifizieren. Abgeschlossen und durch
   `GOV-RATIFICATION-ADR-0060-V1` dokumentiert.
4. Eine gesonderte institutionelle Implementierungsfreigabe erstellen.
   Abgeschlossen durch `GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0060-V1`.
5. Diese Implementierungsfreigabe ausdrücklich menschlich bestätigen.
   Abgeschlossen durch den getrennten externen Beschluss.
6. Einen separaten, scopegebundenen Codex-Implementierungsauftrag erteilen.
   Zum damaligen Dokumentationszeitstand offen; inzwischen getrennt erteilt
   und durch den Implementierungs-Commit nachweisbar abgeschlossen.

Ratifizierung und Implementierungsfreigabe sind zwei eigenständige menschliche
Entscheidungen. Kein Schritt folgt stillschweigend aus dem vorherigen.

## 2. Eigenständige B2-Verfassungsstufe

B2 ist keine Erweiterung von B1. B2 besitzt eigene Authority-Klassen und
eigene Grants. Eine B1 Authority ist niemals eine B2 Authority. Ein B1 Grant
darf nicht erweitert, konvertiert, migriert oder hochgestuft werden. B1
Authorization darf nicht semantisch um personenbezogene Verarbeitung ergänzt
werden.

Gemeinsame technische Basistypen sind nur zulässig, wenn sie reine
Identitäts-, Versions-, Zeit- oder Provenienzkonventionen tragen und keinerlei
gemeinsame Autorisierungssemantik erzeugen. B1-Authority-, B1-Grant- oder
B1-Invocation-Typen dürfen weder vererbt noch als Union-Alternative in einem
B2-Vertrag zugelassen werden.

## 3. B2 Authority Model

Eine B2 Authority ist ein immutable verfassungsmäßiger Befugnisnachweis. Die
spätere technische Form muss mindestens geschlossen typisieren:

- eine eigene B2 Authority ID,
- eine B2 Authority Class,
- einen institutionellen Scope,
- die verfassungsmäßige Grundlage einschließlich ADR-0058 und dieser ADR.

Zulässige Authority-Klassen müssen institutionelle oder verfassungsmäßige
Befugnisse bezeichnen. Freie Akteursangaben sind unzulässig. Das Objekt darf
keine natürliche Person, keinen Provider, keine Runtime, keinen
personenbezogenen Inhalt, keine operative Ausführungsinformation und keinen
gespeicherten Aktiv-, Gültigkeits-, Ablauf- oder Widerrufszustand referenzieren.

Eine B2 Authority beweist ausschließlich, dass eine institutionell definierte
Befugnisklasse innerhalb eines geschlossenen Scopes verfassungsmäßig vorgesehen
ist. Sie beweist keine konkrete Einwilligung, keinen Grant, keine aktuelle
Wirksamkeit, keine Provider-Autorisierung und keine Berechtigung zur
personenbezogenen Verarbeitung.

## 4. B2 Grant Model

Ein B2 Grant ist ein eigenes immutable verfassungsmäßiges Bindungsobjekt. Er
ist kein B1 Grant, Autorisierungszustand, Runtime-Objekt, Provider-Auftrag,
Token, Cache oder Session. Er muss zwingend typisierte, nicht leere Referenzen
enthalten auf:

- genau eine B2 Authority,
- genau eine D3-Einwilligung,
- genau eine T4-Erteilungsquittung,
- genau eine AAV-Autorisierung,
- genau eine UODL-Referenz,
- genau einen erlaubten Purpose Scope.

Der Grant speichert ausdrücklich kein `valid`, `active`, `revoked`, `expired`,
`authorized` oder vergleichbares Wirksamkeitsfeld, kein früheres
Evaluation-Ergebnis, keinen Provider, keine Runtime und keine
personenbezogenen Inhalte. Diese Felder und semantisch gleichwertige Varianten
sind im späteren geschlossenen Vertrag nicht repräsentierbar.

Widerruf oder Änderung einer referenzierten D3-Einwilligung mutiert den Grant
nicht. Grant-Wirksamkeit ist ausschließlich eine für einen expliziten
Auswertungszeitpunkt abgeleitete Eigenschaft.

## 5. D3-, T4-, AAV- und UODL-Bindung

D3 ist notwendig, aber niemals hinreichend. Eine vorhandene oder zum
Auswertungszeitpunkt wirksame D3-Einwilligung darf allein nie zu einer
positiven Evaluation führen. Zusätzlich müssen dieselbe B2 Authority, die
zugehörige T4-Erteilungsquittung, AAV, UODL, der Purpose Scope und sämtliche
gegenseitigen Referenzbindungen konsistent und zum expliziten Zeitpunkt
wirksam sein.

T4 belegt die konkrete Erteilung des Grants, nicht dessen fortdauernde
Wirksamkeit. AAV trägt die aktuelle konkrete Autorisierungs- und
Widerrufsbindung. UODL trägt Nutzerhoheit und die konkrete Referenzbindung,
nicht eine Verarbeitungsvollmacht. Kein Nachweis ersetzt einen anderen.
Fehlende, nicht vergleichbare oder widersprüchliche Bindungen führen fail
closed zu einer negativen Evaluation. Es gibt keine automatische Heilung.

## 6. Purpose-Scope-Regeln

Der Purpose Scope eines B2 Grants muss gleich oder nach einer geschlossenen,
typisierten Teilmengenordnung enger sein als der Purpose Scope der
referenzierten D3-Einwilligung.

- **Gleichheit:** zulässig, wenn beide typisierten Scopes identisch sind.
- **Verengung:** zulässig, wenn jede Grant-Dimension vollständig innerhalb der
  entsprechenden D3-Dimension liegt.
- **Erweiterung:** unzulässig; eine zusätzliche Datenklasse, Nutzung, Operation,
  ein zusätzlicher Vorgang oder ein weiterer Zweck macht den Grant ungültig.
- **Nicht vergleichbar oder inkonsistent:** negative Evaluation; keine
  Interpretation, Normalisierung oder permissive Voreinstellung.

Freitext ist keine Scope-Ordnung. Ein breiterer Grant Scope darf im späteren
Vertrag strukturell nicht konstruierbar sein; ein bloßer nachgelagerter
Warnhinweis genügt nicht.

## 7. Expliziter typisierter Auswertungszeitpunkt

Der Auswertungszeitpunkt ist zwingender timezone-aware, typisierter Eingang
jeder Authorization Evaluation. Die Evaluation ruft kein `now()` auf, liest
keine Wanduhr, globale Uhr, Systemzeit oder Runtime-Zeitquelle und besitzt
keinen impliziten Zeitpunkt. Identische Eingaben einschließlich Zeitpunkt
erzeugen identische Ergebnisse.

Der Auswertungszeitpunkt ist Bestandteil jeder positiven und negativen
Evaluation Evidence und macht zeitabhängige D3-, AAV- und UODL-Prüfungen
rekonstruierbar. Rückwirkende Evaluationen mit nachträglich ausgewählten oder
rekonstruierten Eingaben sind unzulässig.

## 8. Zustandslose B2 Authorization Evaluation

Die Evaluation beantwortet ausschließlich:

> Ist die durch diesen B2 Grant beschriebene Befugnis zu dem explizit
> angegebenen Auswertungszeitpunkt wirksam?

Sie ist deterministisch, zustandslos, rein funktional und vollständig aus
ihren typisierten Eingaben rekonstruierbar. Sie hat keine Runtime-, Provider-,
Persistenz-, Session-, Cache- oder globale Zustandsabhängigkeit. Sie verändert
keine Authority, keinen Grant, keine D3-Einwilligung, T4-Quittung, AAV oder
UODL-Referenz.

Eine positive Evaluation verlangt alle folgenden positiven Teilprüfungen:

1. B2 Authority gehört zur eigenständigen B2-Typfamilie und passt zum Grant.
2. D3 ist zum Eingabezeitpunkt wirksam und vollständig gebunden.
3. T4 quittiert genau diesen Grant und seine Erteilung.
4. AAV ist zum Eingabezeitpunkt wirksam und bindet denselben Grant, Zweck und
   Vorgang.
5. UODL bindet dieselbe AAV und die erlaubte Referenzoperation.
6. Grant Purpose Scope ist gleich oder enger als D3.
7. sämtliche IDs, Versionen und Referenzen sind konsistent.

Jede andere Konstellation ist negativ. Weder positive noch negative Ergebnisse
werden als zukünftige Wahrheit persistiert oder zwischengespeichert.

## 9. Evaluation Evidence

Ein immutable, typisiertes Evaluation-Evidence-Objekt quittiert genau eine
Evaluation. Es ist kein Cache, Token, Grant oder fortwirkender
Autorisierungszustand. Seine geschlossene Struktur muss mindestens enthalten:

- Evaluation-Evidence-ID,
- nicht personenbezogene Referenzen auf Grant und B2 Authority,
- nicht personenbezogene Referenz- oder Proof-Nachweise zu D3, T4, AAV und
  UODL,
- geprüften typisierten Purpose Scope,
- expliziten Auswertungszeitpunkt,
- typisiertes positives oder negatives Ergebnis,
- geschlossene typisierte Entscheidungsgründe,
- Evaluationsvertragsversion.

Vollständige personenbezogene Eingabeobjekte dürfen nicht eingebettet werden.
Zulässig sind ausschließlich nicht personenbezogene IDs, versionsgebundene
Hashes, Proofs oder geschlossene Referenzen. Freitextgründe sind unzulässig.
`repr`, Fehler und Debugdarstellungen dürfen keine personenbezogenen Inhalte
offenlegen.

Positive Evidence beweist nur, dass die Evaluation unter den angegebenen
Eingaben zu genau diesem Zeitpunkt positiv ausfiel. Sie beweist keine
fortdauernde Wirksamkeit, verlängert keinen Grant und ersetzt keine spätere
Evaluation.

## 10. Governance Evidence bei negativer Evaluation

Eine negative Evaluation erzeugt keinen negativen Autorisierungszustand und
keine personenbezogene Sperre. Sie ist dennoch durch dieselbe Evaluation
Evidence als nicht personenbezogene Verweigerungsquittung rekonstruierbar.
Diese darf enthalten:

- Evidence-ID und nicht personenbezogene Grant-Referenz,
- expliziten Auswertungszeitpunkt,
- negatives Ergebnis,
- geschlossene typisierte Ablehnungsgründe,
- nicht personenbezogene Bindungs- und Konsistenznachweise,
- Evaluationsvertragsversion.

Sie darf keine personenbezogenen Inhalte, Rohdaten der D3-Einwilligung,
personenbezogene AAV-/UODL-Inhalte, Provider- oder Runtime-Daten, freie
Fehlertexte, automatische Sanktionen, Sperrlisten oder personenbezogene
Risiko-, Verdachts- oder Rüttelprofile enthalten.

Governance Evidence ist Nachweis einer verweigerten Evaluation, nicht Teil der
Authorization und nicht Teil einer B2 Runtime. Eine spätere Speicherung dieser
nicht personenbezogenen Governance Evidence benötigt eine eigene, noch nicht
erteilte Architektur- und Implementierungsfreigabe.

## 11. Strukturelle Unmöglichkeit unerlaubter Zustände

Die zentrale Invariante lautet: Ein unerlaubter personenbezogener Zustand darf
strukturell nicht modellierbar sein. Daraus folgen geschlossene Typen und
Konstruktorinvarianten; ein optionales Feld plus Validatorwarnung genügt nicht.

| Unerlaubter Zustand | Struktureller Ausschluss |
|---|---|
| Grant ohne B2 Authority, D3, T4, AAV oder UODL | sämtliche Referenzen sind zwingende, nicht optionale, eigenständig typisierte Felder |
| breiterer oder nicht vergleichbarer Purpose Scope | Grant-Konstruktion verlangt nachgewiesene Gleichheit oder typisierte Verengung; sonst kein gültiger Grant |
| eigener Aktiv-, Gültigkeits-, Widerrufs- oder Ablaufzustand | geschlossener Grant-Typ besitzt kein entsprechendes Feld |
| Provider-, Runtime- oder personenbezogener Inhalt im Grant | diese Typfamilien sind nicht Teil des Grant-Schemas |
| positive Evaluation ohne aktuelle D3-Wirksamkeit oder allein durch D3 | geschlossene vollständige Prüfkette ist konjunktiv; jede fehlende Teilprüfung ist negativ |
| inkonsistente T4-, AAV- oder UODL-Bindung | exakte gegenseitige Referenz- und Objektidentität ist zwingend |
| Evaluation ohne expliziten Zeitpunkt oder mit Wanduhr | Zeitpunkt ist Pflichtinput; Evaluation besitzt keine Zeitquelle |
| fortwirkender Authorization State | Evaluation gibt nur punktuelle Evidence zurück; kein Repository, Cache, Token oder Session gehört zum Modell |
| Evidence als wiederverwendbares Token | Evidence-Typ besitzt keine Capability, Operation oder Aktivierungssemantik |
| personenbezogene Evidence oder Reasons | nur geschlossene nicht personenbezogene Referenzen, Proofs und Reason-Enums |
| B1→B2-Upgrade oder B1 Authority in B2 | getrennte Typfamilien ohne Konvertierung, Vererbung oder gemeinsame Autorisierungsunion |
| automatische Sanktion oder Personenprofil aus negativer Evidence | Evidence besitzt keine Akteur-, Sanktions-, Profil- oder Ausführungsfelder |

Ermöglicht ein späterer Entwurf dennoch einen dieser Zustände, ist dies ein
Architekturblocker. Eine schwächere Validatorlösung darf ihn nicht ersetzen.

## 12. Negative Authority and Grant Rules

Verboten sind:

- natürliche Personen, Provider oder Runtime-Komponenten als B2 Authority,
- implizite oder geerbte B1 Authority,
- erweiterte, konvertierte oder hochgestufte B1 Grants,
- unvollständig gebundene B2 Grants,
- Grants mit eigenem Wirksamkeitszustand,
- Scope-Ausweitung und permissive Defaults,
- rückwirkende Evaluation oder Evaluation ohne expliziten Zeitpunkt,
- versteckte Wanduhr oder veränderlicher globaler Zustand,
- Evaluation Evidence als fortwirkende Autorisierung,
- negative Evidence als automatische Sperre oder Sanktion,
- personenbezogene Inhalte in Authority, Grant, Reason, Fehler oder Evidence,
- Freitextgründe, die personenbezogene Daten aufnehmen könnten.

Diese Negativregeln müssen später als eigener geschlossener Vertragsbestandteil
oder durch strukturell gleich starke Typgrenzen umgesetzt werden, nicht bloß
als Kommentare.

## 13. Weiterhin gesperrte Bereiche

Nicht freigegeben sind B2 Provider, Provider Identity, Provider Authorization,
Capability Invocation, Runtime, technische Ausführung auf Grundlage eines
B2 Grants, personenbezogene Verarbeitung oder Speicherung, Sessions, Caches,
Observation, Runtime Audit, Operational Memory, Metrics, Notifications,
produktive externe Anbindungen, UI, Workflows und Werkzeuge.

Der ursprüngliche ADR-0060-Architekturakt implementierte dafür keine Verträge
und formulierte keine Implementierungsfreigabe. Nach der dokumentierten menschlichen Ratifizierung
ist das gesonderte, menschlich bestätigte Freigabedokument
`GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0060-V1` mit erneut ausdrücklich
begrenztem Scope maßgeblich. Es ersetzt keinen separaten Codex-Auftrag.

## 14. Auswirkungen und Nicht-Ziele

ADR-0047 bis ADR-0059, AAV, UODL und
`GOV-SYSTEM-BEHAVIOR-ONLY-1` bleiben unverändert. Insbesondere wird
`GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0059-V1` weder erweitert noch ersetzt.

Nicht Gegenstand des ursprünglichen Architekturentscheids waren Klassen,
Enums, APIs, Validatoren, Provider, Runtime, Persistenz, Datenverarbeitung,
Produktfunktion, Freigabe, Ratifizierung oder Ausführung. Die Ratifizierung
bestätigte nur diese Architektur; die später getrennt erteilte und
dokumentierte Implementierungsfreigabe blieb erforderlich.
