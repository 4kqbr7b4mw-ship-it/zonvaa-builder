# ADR-0062 – Guardian B2 Provider Authorization v1

Status: RATIFIZIERT – IMPLEMENTIERUNG BEGRENZT FREIGEGEBEN

Ratifizierungsnachweis: `GOV-RATIFICATION-ADR-0062-V1`

Implementierungsfreigabe: `GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0062-V1`

## 1. Kontext und Entscheidungsgrenze

ADR-0060 definiert die eigenständige B2-Authority-, Grant- und zustandslose
Authorization-Evaluation. ADR-0061 definiert eine rein beschreibende,
nicht personenbezogene B2 Provider Identity ohne Autorisierungs- oder
Ausführungswirkung. Offen ist ausschließlich, wie eine solche unveränderte
Identity in eine konkrete, zeitpunktbezogene Anwendung der bereits
ratifizierten ADR-0060-Autorisierungsverfassung einbezogen werden darf.

ADR-0062 entscheidet deshalb ausschließlich die Architektur von Guardian B2
Provider Authorization v1. Provider Authorization ist Anwendung von ADR-0060
und keine neue Autorisierungsverfassung. Sie erzeugt keine Authority, keinen
Grant, keine Einwilligung, keine Provider Identity und keine technische
Ausführung.

Diese ADR ist durch den eigenständigen menschlichen Beschluss
`GOV-RATIFICATION-ADR-0062-V1` ratifiziert. Die davon getrennte institutionelle
Implementierungsfreigabe `GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0062-V1` ist
ausschließlich für den geschlossenen nicht ausführenden ADR-0062-Scope gültig.
Beide Beschlüsse bleiben nach `GOV-INSTITUTIONAL-DECISION-SCOPE-1` getrennt.
Die ratifizierte Architektur ist im institutionell freigegebenen,
nicht ausführenden Scope implementiert. Die Implementierung erzeugt weder
Invocation, Runtime noch technische Ausführung.

## 2. Vererbtes bindendes Recht

- ADR-0058 hält B2 kategorial von B1 getrennt.
- ADR-0059 bindet Datenklassen, D3, AAV und UODL an den unveränderlichen
  B2-Datenkorridor.
- ADR-0060 bleibt die einzige B2-Autorisierungsverfassung. D3 ist notwendig,
  aber niemals hinreichend; T4, AAV, UODL, Purpose Scope und der explizite
  Auswertungszeitpunkt sind eigenständige, konjunktive Nachweise.
- ADR-0061 stellt ausschließlich eine nicht personenbezogene, institutionelle
  oder fachliche Provider Identity bereit. Identity beweist keine
  Autorisierung, Eignung, Vertrauenswürdigkeit oder Ausführbarkeit.
- ADR-0033 bleibt die kanonische UODL-Referenz- und Nutzerhoheitsgrenze.
- `GOV-SYSTEM-BEHAVIOR-ONLY-1` bleibt unverändert bindend.

Keine dieser Regeln wird neu formuliert, ersetzt oder erweitert.

## 3. Provider-Authorization-Vertrag

Ein späterer immutable Provider-Authorization-Vertrag darf ausschließlich
folgende typisierte Referenzen und Werte enthalten:

- eine eigenständige B2 Provider Authorization ID,
- genau eine Referenz auf eine unveränderte `B2ProviderIdentity`,
- genau eine Referenz auf einen unveränderten B2 Grant aus ADR-0060,
- nicht personenbezogene Referenzen auf B2 Authority, D3, T4, AAV und UODL,
- den durch den Grant geschlossenen Purpose Scope,
- einen zwingend explizit übergebenen timezone-aware Auswertungszeitpunkt,
- eine Referenz auf die konkrete ADR-0060 Evaluation Evidence,
- ein geschlossen typisiertes punktuelles Ergebnis,
- eigene nicht personenbezogene Provider-Authorization-Provenienz,
- die verwendete kanonische Evaluationsvertragsversion.

Die Provider Identity wird ausschließlich referenziert. Sie wird weder inline
kopiert noch ergänzt, autorisiert, mutiert oder mit einem Status versehen. Der
Vertrag darf nur eine `B2ProviderIdentity` aus der eigenständigen ADR-0061-
Typfamilie referenzieren. B1-Identitäten, natürliche Personen,
Personenaccounts, Namen und Kontaktdaten sind strukturell ausgeschlossen.

Provider Authorization ist eine Rekonstruktionsaussage über die Anwendung
eines wirksamen ADR-0060-Grants auf genau eine institutionelle oder fachliche
Provider Identity zu genau einem Zeitpunkt. Sie ist kein Token, keine Session,
kein Cache, kein Provider-Auftrag und keine fortwirkende Berechtigung.

## 4. Verhältnis von D3 und T4

D3 und T4 haben getrennte, nicht austauschbare Rollen:

- D3 trägt die aktuelle, zweck- und datenklassengebundene Einwilligung. D3 ist
  notwendig, aber niemals hinreichend.
- T4 ist die unveränderliche Erteilungsquittung für genau den referenzierten
  Grant, seine B2 Authority, seine D3-Referenz und seinen Purpose Scope.
- T4 beweist die historische Grant-Erteilung, aber weder aktuelle
  D3-Wirksamkeit noch fortdauernde Grant- oder Provider-Autorisierung.
- Eine aktuelle D3-Einwilligung ersetzt T4 nicht. Eine T4-Quittung ersetzt
  weder aktuelle D3-Wirksamkeit noch AAV, UODL oder Purpose-Kompatibilität.
- Änderung oder Widerruf von D3 mutiert weder T4, Grant, Provider Identity noch
  frühere Evidence. Eine spätere Evaluation fällt mit den dann bereitgestellten
  aktuellen Eingaben nicht positiv aus.

Eine Provider Authorization darf nur positiv sein, wenn die vollständige
ADR-0060-Evaluation zum expliziten Zeitpunkt positiv ist und ihre T4-Bindung
genau denselben Grant referenziert. Es gibt keine automatische Heilung,
Substitution oder permissive Voreinstellung.

## 5. Einzeln berührte UODL-Hooks

ADR-0062 verwendet ausschließlich die bereits kanonischen UODL-Hooks und
benennt sie einzeln:

1. **UODL Reference Identity:** die typisierte UODL-Referenz muss exakt der im
   B2 Grant gebundenen Referenz entsprechen.
2. **Grant Binding:** die UODL-Bindung muss exakt denselben B2 Grant
   referenzieren.
3. **AAV Binding:** die UODL-Bindung muss exakt dieselbe aktuelle AAV-Bindung
   referenzieren; UODL erzeugt keine zweite Autorisierung.
4. **Reference Operation:** ausschließlich die bestehende geschlossene
   B2-Operation `REFERENCE_ONLY` ist zulässig. Sie autorisiert weder `READ`,
   `COPY`, `SYNCHRONIZE`, `EXPORT`, `DELETE_METADATA` noch `DELETE_ORIGINAL`.
5. **Temporal Effectiveness:** `effective_from`, optionales `effective_until`
   und optionales `revoked_at` werden als bereitgestellter immutable Snapshot
   gegen den expliziten Auswertungszeitpunkt geprüft.
6. **User Ownership / Reference before Copy:** die Referenz bleibt eine
   Nutzerhoheits- und Referenzgrenze. Sie ist keine Verarbeitungsvollmacht,
   kein Inhaltszugriff und kein Speicherauftrag.

`StorageReference`-Locator, Owner, Storage Provider, Storage Scope,
Availability, Retention, Checksum, Provider Capability sowie andere
UODL-Operationen werden von ADR-0062 weder gelesen noch übernommen. Würde ein
späterer Anwendungsfall einen solchen Hook benötigen, verlangte dies einen
neuen Architekturakt; ADR-0062 darf ihn nicht stillschweigend ergänzen.

## 6. Zustandslose Provider-Authorization-Evaluation

Die Evaluation beantwortet ausschließlich:

> Ist die durch den referenzierten B2 Grant beschriebene Befugnis für die
> referenzierte B2 Provider Identity zu dem explizit angegebenen
> Auswertungszeitpunkt wirksam?

Sie wendet die ADR-0060-Evaluation unverändert an. Sie liest keinen aktuellen
Zustand selbst, greift auf kein Repository oder Service zu und verwendet keine
globale Uhr oder Systemzeit. D3-, T4-, AAV-, UODL-, Grant-, Identity- und
Zeitinformationen werden vollständig als typisierte immutable Eingaben oder
Snapshots bereitgestellt.

Eine positive Evaluation verlangt konjunktiv:

1. eine unveränderte eigenständige B2 Provider Identity aus ADR-0061,
2. eine positive, vollständig rekonstruierbare ADR-0060-Evaluation desselben
   Grants zum identischen expliziten Auswertungszeitpunkt,
3. exakte D3-, T4-, AAV-, UODL-, Authority-, Grant- und Purpose-Referenzen,
4. die ausschließlich zulässige UODL-Operation `REFERENCE_ONLY`,
5. konsistente Evaluationsvertragsversion und Provider-Authorization-
   Provenienz.

Jede fehlende, inkonsistente oder nicht vergleichbare Bindung ist negativ.
Wirksamkeit ist kein gespeicherter Zustand. Der Vertrag besitzt keine Felder
wie `active`, `valid`, `revoked`, `expired`, `authorized`, `blocked` oder
vergleichbare Statusbehauptungen. Identische Eingaben erzeugen identische
Ergebnisse.

## 7. Negative Governance Evidence als Beobachtungsumfang

Bestehende ADR-0060 Negative Governance Evidence darf ausschließlich als
deklarierter Beobachtungsumfang einer konkreten Evaluation referenziert
werden. Sie dokumentiert, welche bereits bereitgestellten negativen
Evaluationsnachweise bei der Rekonstruktion sichtbar waren.

Sie ist ausdrücklich kein Entscheidungsinput für Grant-Wirksamkeit und darf:

- keine Provider Authorization automatisch verweigern oder blockieren,
- keine Sperrliste, Sanktion, Risikobewertung oder Profilbildung erzeugen,
- kein früheres negatives Ergebnis als zukünftige Wahrheit übernehmen,
- keine personenbezogenen Inhalte oder freien Ablehnungsgründe zuführen,
- keine erneute ADR-0060-Evaluation ersetzen.

Die aktuelle Provider-Authorization-Entscheidung folgt ausschließlich den
aktuellen typisierten Eingaben und dem expliziten Auswertungszeitpunkt. Ein
vorhandener negativer Nachweis kann sichtbar bleiben, verändert das Ergebnis
aber nicht. Fehlt die Evidenz, darf daraus weder Zulässigkeit noch Unzulässigkeit
abgeleitet werden.

## 8. Provider-Authorization-Provenienz

Provider Authorization besitzt eine eigene immutable, vollständig
rekonstruierbare und nicht personenbezogene Provenienz. Sie muss mindestens
typisierte Referenzen auf institutionelle Source ID, Governance-Decision-ID,
ADR-0060-Evaluation-Evidence-ID, ADR-0061-Provider-Identity-ID, Grant-ID und
den expliziten Auswertungszeitpunkt enthalten.

Provenienz ist kein Ausstellerbeweis, keine Selbstbestätigung, kein
Vertrauensurteil und keine Autorisierung. Unzulässig sind natürliche Personen,
Namen, Kontaktdaten, Freitext, implizite Vertrauensannahmen, versteckte
Systemzeit und selbst erzeugte Bestätigungen. Eine Provider Identity darf ihre
eigene Autorisierung oder Provenienz niemals bestätigen.

## 9. Strukturelle Invarianten

Ein späterer Vertrag muss strukturell ausschließen:

- Provider Authorization ohne B2 Provider Identity oder mit B1 Identity,
- natürliche Personen oder personenbezogene Akteursbindungen,
- inline kopierte oder mutierte Provider Identity,
- Provider Authorization ohne vollständige ADR-0060-Evaluation,
- positive Entscheidung allein aufgrund von Identity, D3 oder T4,
- fehlende oder widersprüchliche D3-, T4-, AAV- oder UODL-Bindung,
- andere UODL-Operationen als `REFERENCE_ONLY`,
- Evaluation ohne expliziten typisierten Auswertungszeitpunkt,
- gespeicherten Aktiv-, Gültigkeits-, Widerrufs- oder Sperrstatus,
- Negative Governance Evidence mit automatischer Sperr- oder Sanktionswirkung,
- selbstbestätigende oder personenbezogene Provenienz,
- Invocation, Runtime, technische Ausführung, Schlüssel- oder Inhaltszugriff,
- Observation, Audit, Operational Memory, Metrics oder Notifications.

Ein nachgelagerter Warnhinweis genügt nicht. Kann ein Implementierungsentwurf
einen dieser Zustände ausdrücken, ist dies ein Architekturblocker.

## 10. Negative Provider Authorization Rules

Provider Authorization darf insbesondere nicht:

- eine natürliche Person oder eine B1 Provider Identity autorisieren,
- Provider Identity inline definieren, erweitern oder mutieren,
- eine neue Authority-, Grant- oder Einwilligungssemantik einführen,
- D3, T4, AAV oder UODL gegenseitig ersetzen,
- einen aktuellen Zustand, Zeitpunkt oder eine Version selbst ermitteln,
- Negative Governance Evidence als Blockade oder künftige Wahrheit verwenden,
- einen Provider auswählen, priorisieren, aktivieren oder ausführen,
- Capability Invocation, Runtime, Session, Cache oder Token vorbereiten,
- Daten lesen, bewegen, verarbeiten, speichern oder weitergeben,
- Keys, Credentials, Secrets oder Inhaltszugriff referenzieren,
- Betriebsnachweise erzeugen, beobachten, auditieren oder persistieren.

## 11. Referenzszenarien

Spätere Tests verwenden ausschließlich synthetische nicht personenbezogene
IDs und geschlossene Typen. Mindestens zu prüfen sind:

1. gültige punktuelle Provider Authorization für eine institutionelle B2
   Provider Identity mit vollständiger positiver ADR-0060-Evaluation,
2. Ablehnung einer B1 Identity oder natürlichen Person,
3. Ablehnung fehlender oder mutierter Provider-Identity-Referenz,
4. D3 ist wirksam, T4 fehlt: negative Evaluation,
5. T4 ist vorhanden, D3 ist unwirksam: negative Evaluation,
6. D3 und T4 sind vorhanden, AAV oder UODL ist inkonsistent: negativ,
7. andere UODL-Operation als `REFERENCE_ONLY`: negativ,
8. identische Eingaben und identischer Zeitpunkt ergeben dasselbe Ergebnis,
9. Evaluation ohne expliziten Zeitpunkt ist strukturell ausgeschlossen,
10. frühere Negative Governance Evidence bleibt sichtbar, blockiert aber eine
    aktuelle vollständig positive Evaluation nicht,
11. keine Statusfelder, Invocation, Runtime oder technische Ausführung,
12. nicht personenbezogene, nicht selbstbestätigende Provenienz.

## 12. Weiterhin gesperrt

Nicht Gegenstand und nicht freigegeben bleiben:

- B2 Capability Invocation,
- B2 Runtime und jede technische Ausführung,
- Provider-Auswahl, Aktivierung oder externe Provider-Anbindung,
- personenbezogene Verarbeitung oder Speicherung,
- Key Custody, Schlüsselverwaltung, Credentials und Inhaltszugriff,
- Sessions, Caches und Tokens,
- Observation und Runtime Audit,
- Operational Memory, Metrics und Notifications,
- UI, Workflow- oder Werkzeugaktivierung.

## 13. Governance-Sequenz und Nicht-Ziele

ADR-0062 dokumentiert ausschließlich eine ratifizierte und begrenzt
implementierungsfreigegebene Architektur. Sie implementiert keine Klasse,
Enum, Value Object, API oder Produktfunktion. Die bestehende
Implementierungsfreigabe für ADR-0061 wird nicht erweitert.

Jede spätere Arbeit verlangt getrennt:

1. Validierung dieses Architekturvorschlags – abgeschlossen,
2. ausdrückliche menschliche Ratifizierung von ADR-0062 – abgeschlossen,
3. gesonderte institutionelle Implementierungsfreigabe – abgeschlossen,
4. ausdrückliche menschliche Bestätigung dieser Freigabe – abgeschlossen,
5. nachweisbarer Push des Freigabe-Commits auf `origin/builder-reset-v2` – abgeschlossen,
6. separaten Codex-Implementierungsauftrag nach diesem Push – abgeschlossen.

Keine Stufe impliziert die nächste.

## 14. Prüffrage Null

Die Architektur referenziert nur bereits bereitgestellte immutable
Identitäts-, Grant-, Binding- und Evidence-Artefakte. Sie besitzt weder
Datenzugriff noch Invocation-, Runtime- oder Ausführungssemantik und kann keine
natürliche Person autorisieren.

> Kann durch die dokumentierte Architektur eine Provider Authorization bereits
> personenbezogene Verarbeitung, Runtime-Ausführung oder unerlaubte
> Machtausübung ermöglichen?

Antwort: Nein.
