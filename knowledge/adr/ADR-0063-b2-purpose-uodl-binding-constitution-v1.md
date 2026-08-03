# ADR-0063 – B2 Purpose and UODL Binding Constitution v1

Status: **RATIFIZIERT – NICHT IMPLEMENTIERUNGSFREIGEGEBEN – NICHT IMPLEMENTIERT**

Ratifizierungsnachweis: `GOV-RATIFICATION-ADR-0063-V1`

Die Ratifizierung bestätigt ausschließlich diese Architektur. Sie ist keine
institutionelle Implementierungsfreigabe und implementiert weder Purpose-
Bindung noch UODL-Mapping oder Migration.

## 1. Kontext

ADR-0059 beschreibt den B2 Data Corridor mit `purpose`, `purpose_binding` und
`StorageOperation.REFERENCE`. ADR-0060 definiert mit `B2PurposeScope` die
geschlossene fachliche Purpose-Verfassung und mit
`B2UODLOperation.REFERENCE_ONLY` die Autorisierungsbindung. ADR-0062 übernimmt
diese UODL-Bindung für Provider Authorization. Das Review
`GOV-B2-CONSTITUTIONAL-REVIEW-0059-0062-V1` hat zwei nicht auflösbare
Übersetzungsfragen dokumentiert.

## 2. Problemstellung

Freie Corridor-Purpose-Werte dürfen keine konkurrierende fachliche Wahrheit
neben `B2PurposeScope` bilden. Ebenso darf Namensähnlichkeit zwischen
`REFERENCE` und `REFERENCE_ONLY` keine Gleichheit oder Konvertierung beweisen.
Ohne ausdrückliche Bindung bleibt die End-to-End-Kette fail closed.

## 3. Kanonische Grundlagen

- ADR-0059: Corridor, Consent Boundary und `StorageOperation.REFERENCE`;
- ADR-0060: `B2PurposeScope`, Purpose-Halbordnung und
  `B2UODLOperation.REFERENCE_ONLY`;
- ADR-0062: ausschließlich die sechs ratifizierten UODL-Hooks;
- AAV und UODL: Nutzerhoheit, Widerruf und Reference before Copy;
- `GOV-SYSTEM-BEHAVIOR-ONLY-1` und
  `GOV-INSTITUTIONAL-DECISION-SCOPE-1`.

Diese ADR ergänzt die Bindungsarchitektur. Sie ändert keine bestehende ADR.

## 4. Begriffsdefinitionen

- **Kanonischer Purpose:** ein `B2PurposeScope` nach ADR-0060.
- **Corridor-Purpose-Darstellung:** bestehender syntaktischer Wert aus
  ADR-0059; ohne Bindungsnachweis nicht fachlich autoritativ.
- **Purpose-Bindungsnachweis:** spätere immutable Evidenz einer expliziten
  Bindung an genau einen kanonischen Scope.
- **Corridor-Operation:** `StorageOperation.REFERENCE` auf ADR-0059-Ebene.
- **B2-UODL-Operation:** `B2UODLOperation.REFERENCE_ONLY` auf
  Autorisierungsbindungsebene.
- **UODL-Mapping:** spätere immutable Evidenz eines zulässigen typisierten
  Ebenenpaares, keine Konvertierung.

## 5. Architekturentscheidung

Es gibt genau eine fachlich autoritative Purpose-Verfassung für B2:
`B2PurposeScope` aus ADR-0060. Corridor-Purpose und Purpose Binding aus
ADR-0059 sind keine zweite fachliche Wahrheit. Die beiden UODL-Operationen
bleiben getrennte Typen auf getrennten Ebenen und dürfen ausschließlich über
ein geschlossenes Mapping verbunden werden.

## 6. Purpose-Verfassung

Bestehende freie oder historische Purpose-Darstellungen sind nicht
autoritativ. Sie werden weder interpretiert noch automatisch zugeordnet oder
implizit konvertiert. Es entsteht keine zweite Purpose-Liste. Evidence,
Provenienz oder Validatorannahmen ersetzen keine fehlende Purpose-Bindung.

## 7. Purpose-Bindungsnachweis

Ein später implementierbarer immutable Vertrag muss ausschließlich typisiert
enthalten:

- Bindungs-ID;
- Corridor-Referenz;
- kanonischen `B2PurposeScope`;
- Ausgangs-Purpose-Referenz;
- geschlossene Bindungsregel;
- typisierte Vergleichsrelation;
- Evidenzreferenzen;
- nicht personenbezogene Provenienz;
- explizit bereitgestellten timezone-aware Erstellungszeitpunkt;
- typisierten Beobachtungsumfang.

Er ist Rekonstruktionsnachweis, keine Autorisierung und kein Statusobjekt.

## 8. Purpose-Halbordnung

Eine Bewegung ist ausschließlich zu einem identischen oder nachweisbar
engeren `B2PurposeScope` zulässig. Erweiterung ist unzulässig. Fehlende,
inkonsistente oder nicht vergleichbare Scopes führen fail closed zu keiner
positiven Bindung. Es gibt keine permissiven Defaults und keine automatische
Heilung.

## 9. UODL-Ebenentrennung

`StorageOperation.REFERENCE` beschreibt die Corridor-Ebene.
`B2UODLOperation.REFERENCE_ONLY` beschreibt die B2-Autorisierungsbindung.
Beide bleiben unterschiedliche geschlossene Typen. Enum-Wert, String und Name
sind weder identisch noch austauschbar.

## 10. UODL-Mapping

Das einzige vorgeschlagene zulässige Paar lautet:

- Corridor-Operation: `StorageOperation.REFERENCE`;
- B2-UODL-Operation: `B2UODLOperation.REFERENCE_ONLY`.

Ein später implementierbarer immutable Vertrag muss ausschließlich typisiert
enthalten:

- Mapping-ID;
- Corridor-Operation;
- B2-UODL-Operation;
- Ebenenbezug;
- geschlossene zulässige Paarregel;
- Evidenzreferenzen;
- nicht personenbezogene Provenienz;
- explizit bereitgestellten timezone-aware Erstellungszeitpunkt;
- typisierten Beobachtungsumfang.

Kein anderes Paar ist zulässig. Fehlendes oder abweichendes Mapping führt fail
closed. Es gibt keine String-Konvertierung, Alias- oder
Namensähnlichkeitslogik und keine automatische Operationserweiterung.

## 11. Evidenz- und Provenienzgrenzen

Evidenz und Provenienz bleiben nicht personenbezogen, typisiert,
referenzgebunden und nicht selbstbestätigend. Sie belegen nur den angegebenen
Beobachtungsumfang. Sie ersetzen weder Purpose-Bindung noch UODL-Mapping und
besitzen keine Autorisierungs-, Inhalts-, Speicher- oder Ausführungswirkung.

## 12. Strukturelle Invarianten

- `B2PurposeScope` bleibt die einzige fachliche Purpose-Verfassung.
- Ein breiterer, fehlender oder nicht vergleichbarer Scope ist nicht positiv
  bindbar.
- Die UODL-Ebenen bleiben typisiert getrennt.
- Nur das eine geschlossene Paar ist abbildbar.
- Beide Nachweise sind immutable und benötigen explizite Zeitpunkte.
- Kein Nachweis enthält personenbezogene Inhalte oder operative Macht.

## 13. Negative Rules

Nicht zulässig sind freie Purpose-Texte als Autorität, Textinterpretation,
implizite Purpose-Konvertierung, Scope-Erweiterung, interne Zeit- oder
Zustandsquellen, Statusfelder wie `valid`, `active`, `approved` oder
`authorized`, String-Mapping, Alias- oder Namensähnlichkeitslogik, zusätzliche
UODL-Operationen, Inhaltsreferenzen mit Zugriffssemantik, Lesen, Kopieren,
Schreiben, Speichern, Provider-Funktionen, Callbacks, Runtime-Handles,
Schlüsselmaterial, Token, Cache, Permission, Session, Autorisierung,
Invocation, Runtime und personenbezogene Inhalte.

## 14. Prüffrage Null

Kann durch diese Architektur ein freier oder breiterer Purpose autoritativ,
eine nicht vergleichbare Bindung akzeptiert, eine UODL-Operation implizit
konvertiert, eine zusätzliche Operation zugelassen oder Inhaltszugriff,
personenbezogene Verarbeitung, Autorisierung, Invocation oder Runtime-Macht
erzeugt werden?

Antwort: **Nein.** Alle Übergänge sind geschlossen typisiert, explizit und
fail closed; diese ADR besitzt keine Ausführungswirkung.

## 15. Ausdrücklich nicht freigegebene Bereiche

Nicht freigegeben sind Implementierung, Migration, Änderung produktiver
Verträge oder Validatoren, Ratifizierung, institutionelle
Implementierungsfreigabe, personenbezogene Verarbeitung oder Speicherung,
Inhaltszugriff, neue UODL-Operationen, Provider-Aufruf, Capability Invocation,
Runtime, Tools, Sessions, Caches, Tokens, Schlüsselverwaltung, Observation,
Audit, Operational Memory, Metrics, Notifications und externe Integration.

## 16. Auswirkungen auf ADR-0059 bis ADR-0062

ADR-0059 bis ADR-0062 bleiben unverändert. Bei späterer Ratifizierung würde
ADR-0063 ausschließlich ihre offene Purpose- und UODL-Bindungsgrenze
ergänzen. Sie erweitert weder Corridor, Authority, Grant, Provider Identity
noch Provider Authorization.

## 17. Migrationsfragen

Bestehende ADR-0059-Werte dürfen nicht automatisch migriert, interpretiert
oder umgedeutet werden. Eine Migration erfordert einen ausdrücklichen
institutionellen Beschluss, geschlossene Migrationsregeln, fail-closed für
unbekannte Werte, keine Textinterpretation oder Ähnlichkeitszuordnung, eine
eigene Implementierungsfreigabe, eigene Tests und nachvollziehbare
Migrations-Evidence.

## 18. Offene institutionelle Entscheidungen

Offen sind die menschliche Ratifizierung dieses ADR sowie – davon getrennt –
eine mögliche institutionelle Implementierungsfreigabe. Eine Migration wäre
ein weiterer gesonderter Beschluss. Keine dieser Entscheidungen wird hier
gefällt.

## 19. Implementierungsgrenze

Diese ADR implementiert keinen Vertrag, Validator, Mapper, Adapter oder
Migrationspfad. Ein späterer Codex-Auftrag darf erst nach Ratifizierung,
gesonderter Implementierungsfreigabe und deren kanonischem Push erfolgen.

## 20. Ratifikationsanforderungen

Ratifizierung muss Purpose-Alleinquelle, Halbordnung, fail-closed Verhalten,
UODL-Ebenentrennung, das einzige Paar, Migrationstrennung und sämtliche
Negativregeln ausdrücklich bestätigen. Sie ist keine Implementierungsfreigabe.

## 21. Implementierungsfreigabeanforderungen

Eine spätere Freigabe muss `Freigegeben` und `Ausdrücklich nicht freigegeben`
nach `GOV-INSTITUTIONAL-DECISION-SCOPE-1` getrennt enthalten. Purpose-Bindung,
UODL-Mapping und Migration dürfen nicht stillschweigend gemeinsam freigegeben
werden.

## 22. Test- und Evidenzanforderungen

Erforderlich sind positive und negative Tests für Gleichheit, Verengung,
Erweiterung, Nichtvergleichbarkeit, fehlende Bindung, exakt ein UODL-Paar,
fremde Operationen, String- und Aliasversuche, naive Zeit, interne Zeit- und
Zustandsquellen, Statusfelder sowie jede Inhalts-, Autorisierungs-, Invocation-
und Runtime-Wirkung. Objektidentität und Determinismus sind nachzuweisen.

## 23. Konsequenzen

Die End-to-End-Verfassung erhält eine beweisbare Bindungsstelle ohne zweite
Purpose- oder UODL-Wahrheit. Bis zur Ratifizierung bleiben beide Review-Blocker
offen und alle produktiven Verträge unverändert.

## 24. Risiken

Eine spätere Migration kann historische freie Werte nicht ohne zusätzliche
institutionelle Entscheidung einordnen. Dies ist beabsichtigtes fail closed,
nicht eine Einladung zu heuristischer Zuordnung. Lokale Wiederholungen dieser
Regeln dürfen nicht zu Parallelverfassungen werden.
