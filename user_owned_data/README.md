# User-Owned Data Architecture

Dieses Paket definiert ZONVAAs providerneutrale Grenze zu nutzerkontrollierten
Originaldaten. Es ist weder Store noch Dateisystemadapter.

## Komponenten

- `contract.md`: versionierter Architekturvertrag,
- `models.py`: unveränderliche Referenz-, Provider-, Autorisierungs-,
  Retention-, Integritäts- und Verfügbarkeitsmodelle,
- `loader.py`: deterministischer Loader mit SHA-256-Integritätsnachweis.

`StorageReference` enthält einen logischen Locator, aber weder Dokumentinhalt
noch eine Zugriffsfunktion. `ReferenceAuthorization` verwendet die bestehende
`ArtifactAuthorization` und begrenzt sie zusätzlich auf konkrete
Storage-Operationen.

RuntimeManager lädt ausschließlich den statischen Vertrag. KnowledgeManager
validiert Referenzobjekte, ohne den User Vault zu öffnen. Produktive Adapter,
Speicherzugriffe, Kopien, Synchronisation und Löschung sind Nicht-Ziele.
