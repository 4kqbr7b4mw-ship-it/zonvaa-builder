# ADR-0058 – Guardian B2 Architecture v1

## Status

RATIFIZIERT – 02.08.2026

Reine Architekturentscheidung. Keine Implementierungsfreigabe. Vor jeder
Implementierung sind die Kenntnisnahme des Vertrauensrats und die Auflösung
des in Abschnitt 2 dokumentierten fehlenden kanonischen I4-Verweises
erforderlich.

## 1. Kontext

B1 gibt allgemeine Orientierung auf Grundlage nicht personenbezogener oder
vor einer Ausführung ausdrücklich entpersonalisierter Eingaben. B2 strukturiert
hingegen persönliche Vorbereitung und kann dafür zweckgebunden ausgewählten
persönlichen Kontext benötigen. Damit ändern sich Datenhoheit,
Autorisierungsbedarf, Widerrufsfolgen und die zulässige Betriebsgrenze
kategorial.

B2 ist deshalb keine Erweiterung, Konfiguration oder höhere Ausbaustufe der
B1-Runtime. Eine B1-Fähigkeit darf weder technisch noch rechtlich zu B2
hochgestuft werden. Personenbezogene und besonders schutzbedürftige Daten
begründen eine neue Verfassungsstufe, weil ihre Nutzung nicht allein durch
Antwortmodus, Providerfähigkeit oder allgemeine Einwilligung legitimiert wird.

Diese ADR entscheidet ausschließlich die Architekturgrenzen. Sie implementiert
keine B2-Runtime, keinen Vertrag, keinen Provider und keine Produktfunktion.

## 2. Bestehendes Recht

Die folgende Zuordnung referenziert bestehende Regeln, ohne sie neu zu
formulieren oder zu ersetzen. AAV bezeichnet ADR-0030 und den kanonischen
Artefakt-/Autorisierungszustandsvertrag; UODL bezeichnet ADR-0033 und den
kanonischen User-Owned-Data-Vertrag.

| Themengebiet | Bindende Entscheidung | Bindende AAV-/UODL-Regel | Unverändert übernommene Regel |
|---|---|---|---|
| Answer Boundary | ADR-0047 und Guardian Answer Boundary Contracts v1 | Gespräch erzeugt keine Autorisierung | B2 bleibt ausschließlich Schutz- und Auditmetadatum und aktiviert nichts. |
| Authority Model | ADR-0048 | Authority ersetzt keine konkrete Autorisierung | Abstrakte Befugnis ist weder Grant noch Ausführungsmacht. |
| Provider Authorization | ADR-0049 | Autorisierung bleibt aktiv, zweck- und umfangsgebunden | Herkunft oder Provider-Typ autorisiert weder Provider noch Capability. |
| Invocation Boundary | ADR-0050 | Jede kontrollierte Operation benötigt gesonderte Autorisierung | Die bestehende Invocation Boundary ist B1-begrenzt und autorisiert kein B2. |
| Runtime | ADR-0051 | Referenzzugriff und Datenoperationen bleiben getrennt autorisiert | Die einzige reale Provider-Runtime ist read-only B1; B2 besitzt keine Runtime. |
| Observation Governance | ADR-0053 | Minimale Metadaten und Kontextisolation bleiben bindend | Observation sieht ausschließlich Systemverhalten und niemals Nutzerinhalte. |
| Incident | ADR-0052 | Nachweise erzeugen keine neue Datenvollmacht | Incident Evidence dokumentiert bereitgestellte Systemereignisse und erkennt keine B2-Inhalte. |
| Audit | ADR-0054 | Audit darf Nutzerhoheit nicht umgehen | Audit prüft Systemnachweise, nicht personenbezogene Inhalte oder Nutzerverhalten. |
| Operational Memory | ADR-0055 | UODL bleibt separate Hoheitsarchitektur für Nutzerdaten | Operational Memory nimmt keine B2-Inhalte, Gesprächsinhalte oder personenbezogenen Artefakte auf. |
| Physical Operational Persistence | ADR-0056 | Referenz ist keine Erlaubnis zur Kopie oder Speicherung | Physische Betriebspersistenz speichert keine B2-Inhalte. |
| Operational Metrics | ADR-0057 | Nutzerbezogene Metadaten bleiben außerhalb des Betriebsblocks | Metriken verarbeiten nur Systemverhalten, keine Nutzeridentitäten, Themen oder Lebensbereiche. |
| Operational Notifications | ADR-0057 | Weitergabe benötigt eigene ausdrückliche Autorisierung | Notifications verarbeiten keine B2-Inhalte und sprechen keine Endnutzer an. |
| D1–D6 | ADR-0047 § 6 | UODL: Reference before Copy, Minimal Metadata, Explicit Consent, Privacy by Design | Entpersonalisierung ist Normalfall; Kontext und externe Recherche bleiben getrennt; Minimalität und Verbot stiller Anreicherung gelten fort. |
| D3 | ADR-0047 § 6 | AAV: aktive, konkrete, zweckgebundene und widerrufbare Autorisierung | Einwilligung ist vorgangs- und datenklassenspezifisch, dokumentiert, widerrufbar und minimal. |
| D3-UX | ADR-0047 § 6 | Nutzerhoheit und bewusste Autorisierung dürfen nicht umgangen werden | Keine Vorauswahl, Bevorzugung, Dauerfreigabe oder Blockade der entpersonalisierten Alternative. |
| I4 | Kein kanonischer, als `I4` bezeichneter Normtext im Repository auffindbar | Keine belastbare Zuordnung ohne kanonische Quelle | Keine Regel wird rekonstruiert. Vor B2-Implementierung muss die zuständige kanonische Quelle benannt und ihre unveränderte Bindung dokumentiert werden. |

Der fehlende I4-Verweis wird nicht durch eine Annahme, Nummerierung eines
anderen Dokuments oder eine neue Regel dieser ADR ersetzt.

## 3. Neue Architekturentscheidungen

### 3.1 Datenhoheit

**Bisher unbeantwortete Frage:** Welche persönlichen Daten darf eine künftige
B2-Verarbeitung innerhalb eines konkreten Vorbereitungszwecks erhalten?

**Warum das bestehende Recht nicht genügt:** AAV und UODL definieren Hoheit,
Referenzen und Operationen, aber noch keinen geschlossenen B2-Datenkorridor.

**Neue Regel:** B2 darf nur eine ausdrücklich autorisierte, zweck- und
vorgangsgebundene minimale Auswahl aus bestätigten Angaben, freigegebenen
Dokumentfragmenten und für die Vorbereitung erforderlichen Kontextmerkmalen
erhalten. Autorisierung muss Datenklasse, Zweck, Vorgang und zeitliche Grenze
einzeln ausweisen. Rohgespräche, vollständige Understanding States,
Hypothesen, Beziehungsartefakte, nicht erforderliche Dokumentinhalte,
Zugangsdaten, Geheimnisse sowie Daten anderer Personen ohne eigene
Autorisierungsgrundlage sind unzulässig. Widerruf folgt ausschließlich AAV.

### 3.2 Depersonalisierung

**Bisher unbeantwortete Frage:** Welche Schutzverarbeitung muss vor einer
künftigen B2-Verarbeitung stattfinden?

**Warum das bestehende Recht nicht genügt:** D1–D6 begrenzen Recherche, legen
aber noch keinen B2-spezifischen Eingangskorridor fest.

**Neue Regel:** Vor B2 werden direkte Identifikatoren und nicht erforderliche
indirekte Identifikatoren entfernt. Dazu gehören mindestens Name, Anschrift,
Kontakt-, Konto-, Versicherungs- und amtliche Kennungen sowie stabile
personen- oder fallübergreifende Schlüssel. Die verbleibende Eingabe wird auf
den autorisierten Zweck minimiert. Rohgespräche, vollständige Dokumente,
vollständige Understanding States, Hypothesen, T2-Beziehungsartefakte,
Zugangsdaten und nicht autorisierte Drittpersonendaten dürfen B2 niemals
erreichen. D3 kann eine ausdrücklich benannte minimale Ausnahme für einen
konkreten Vorgang tragen, hebt diese Verbote aber nicht pauschal auf.

### 3.3 B2-Autorisierung

**Bisher unbeantwortete Frage:** Kann eine bestehende B1-Autorisierung auf B2
erweitert werden?

**Warum das bestehende Recht nicht genügt:** B1-Grants wurden für
nicht personenbezogene oder entpersonalisierte read-only Orientierung
entworfen.

**Neue Regel:** B2 besitzt eine eigene Authority-Klasse und ausschließlich
eigene B2 Authorization Grants. Ein B1-Grant kann weder erweitert, migriert
noch als B2-Grant interpretiert werden. D3 ist notwendige, aber nicht
hinreichende Voraussetzung: Zusätzlich sind eine passende B2-Authority,
separater B2-Grant, Datenklassen-, Zweck-, Zeit-, Provider-, Capability- und
Kontrollbindung erforderlich. B1-Autorisierung autorisiert niemals B2.

### 3.4 Betriebsblock

**Bisher unbeantwortete Frage:** Dürfen bestehende Betriebsnachweise
personenbezogene B2-Inhalte verarbeiten?

**Warum das bestehende Recht nicht genügt:** Der Betriebsblock ist
systemverhaltensbezogen; seine Anwendung auf eine künftige B2-Stufe musste
ausdrücklich festgelegt werden.

**Neue Regel:** Observation bleibt gegenüber B2-Inhalten blind. Audit bewertet
keine personenbezogenen Inhalte. Operational Memory und Physical Operational
Persistence speichern keine B2-Inhalte. Operational Metrics und Operational
Notifications verarbeiten keine B2-Inhalte. Zulässig bleiben ausschließlich
nicht personenbezogene, in den bestehenden geschlossenen Katalogen erlaubte
Systemnachweise. Diese ADR erweitert keinen dieser Kataloge.

### 3.5 Widerruf

**Bisher unbeantwortete Frage:** Welche B2-spezifische Folge hat ein Widerruf?

**Warum das bestehende Recht nicht genügt:** Die B2-Grenze muss die vorhandene
AAV-Trennung zwischen aktueller Autorisierung und historischem Nachweis
ausdrücklich übernehmen.

**Neue Regel:** Ein Widerruf beendet die aktuelle B2-Zugänglichkeit;
personenbezogene Inhalte werden für künftige B2-Verarbeitung unzugänglich.
Unveränderliche Governance-Nachweise über Erteilung, Nutzung und Widerruf
bleiben erhalten. Die geltenden AAV-Regeln werden unverändert übernommen.
Diese ADR erfindet weder Löschung noch neue Widerrufslogik.

### 3.6 Vetodomäne und Freigabe

**Bisher unbeantwortete Frage:** Welche unabhängige Governance-Beteiligung ist
vor einer B2-Implementierung zwingend?

**Warum das bestehende Recht nicht genügt:** B2 verarbeitet potentiell
personenbezogene Daten und berührt damit eine eigene Macht- und
Vertrauensebene.

**Neue Regel:** B2 berührt Vetodomäne 2 zwingend. Vor jedem begrenzten
Implementierungsauftrag ist die Vertrauensrats-Kenntnisnahme zu dokumentieren.
Ohne diese Architekturfreigabe, die Auflösung des I4-Verweises und einen
gesonderten begrenzten Auftrag ist jede B2-Implementierung unzulässig.

## 4. Vererbungsregeln

| Architekturregel | Kennzeichnung | Verbindliche Folge |
|---|---|---|
| Authority | VERSCHÄRFT | Bestehendes Modell gilt; B2 benötigt eine eigene Authority-Klasse. |
| Provider Authorization | VERSCHÄRFT | Bestehende Prüfkette gilt; B2 benötigt einen separaten Grant. |
| D3 | GEERBT | Einwilligungs-, Minimalitäts- und Widerrufsregeln gelten unverändert. |
| Observation | GEERBT | Nur Systemverhalten; B2-Inhalte bleiben unsichtbar. |
| Audit | GEERBT | Nur Systemnachweise; keine Prüfung personenbezogener Inhalte. |
| Runtime | UNZULÄSSIG | ADR-0051 bleibt B1-only; diese ADR autorisiert keine B2-Runtime. |
| Operational Memory | GEERBT | Keine B2-Inhalte oder personenbezogenen Artefakte. |
| Metrics | GEERBT | Keine B2-Inhalte, Nutzerstatistiken oder Themenauswertung. |
| Notifications | GEERBT | Keine B2-Inhalte oder Endnutzeransprache. |
| B2 Grant | NEU | Eigener, zweck-, zeit-, datenklassen-, Provider- und Capability-gebundener Grant erforderlich. |
| B1→B2 Upgrade | UNZULÄSSIG | Kein Grant, Modus, Provider oder Invocation-Pfad darf hochgestuft werden. |

## 5. Auswirkungen

ADR-0046 bis ADR-0057, ADR-0030, ADR-0033 und MDR-0001 bleiben unverändert.
ADR-0058 ergänzt sie ausschließlich um die neue B2-Verfassungsgrenze. Sie
ändert keine vorhandenen Verträge, Enums, Validatoren oder Public APIs.

Spätere, jeweils gesondert zu entscheidende und freizugebende Pakete hängen
von ADR-0058 ab: B2 Authority und Authorization, B2 Data Envelope und
Depersonalisierung, B2 Invocation Boundary, B2 Provider-Grenze, B2 Runtime
sowie deren begrenzte Betriebsnachweise. Ihre Reihenfolge und Umsetzung sind
nicht Gegenstand dieser ADR.

Der fehlende kanonische I4-Verweis bleibt eine offene Architekturfrage und
blockiert jede Implementierung. Vertrauensrats-Kenntnisnahme bleibt ebenfalls
eine Voraussetzung und ist durch dieses Dokument nicht bereits erfolgt.

## 6. Nicht-Ziele

Nicht behandelt oder freigegeben werden:

- B2 Runtime,
- B2 Verträge,
- B2 Provider,
- B2 Persistenz,
- B2 Metrics,
- B2 Notifications,
- B2 UI,
- B2 Workflows,
- B2 Implementierung.

Diese ADR führt keine Klasse, API, Runtime, Persistenz, Capability,
Autorisierung oder Produktfunktion ein.
