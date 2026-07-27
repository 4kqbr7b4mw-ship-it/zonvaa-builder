# Handover: Build User-Owned Data Architecture

- Timestamp: `2026-07-27T07:56:59+00:00`
- Starting commit: `0efaafd07389451d18c2e95419d8507cccc90b85`
- Ending commit: `missing`
- Push status: `not_pushed`

## Changed files

- PLANS.md
- README.md
- builder/preflight.py
- builder/runtime.py
- knowledge/adr/ADR-0033-user-owned-data-architecture.md
- knowledge/handovers/2026-07-27_07-56-59-000000_Build-User-Owned-Data-Architecture.json
- knowledge/handovers/2026-07-27_07-56-59-000000_Build-User-Owned-Data-Architecture.md
- knowledge/manager.py
- tests/test_goal_application_service.py
- tests/test_goal_aware_orchestrator.py
- tests/test_goal_cli.py
- tests/test_power_of_attorney_workflow.py
- tests/test_preflight.py
- tests/test_runtime.py
- tests/test_user_owned_data.py
- user_owned_data/README.md
- user_owned_data/__init__.py
- user_owned_data/contract.md
- user_owned_data/loader.py
- user_owned_data/models.py

## Functional changes

- Introduced a provider-neutral user-owned reference boundary without storing or accessing original documents.
- Separated reference, read, copy, synchronization, export, metadata deletion and original deletion permissions.
- Required every storage reference to carry active owner-granted authorization bound to that exact reference.
- Kept local folders, NAS, private cloud, self-hosted servers, external connectors and unknown providers equal and offline-compatible.

## Technical changes

- Added immutable StorageReference, provider, scope, availability, checksum, capability, authorization and retention models.
- Reused ArtifactAuthorization and Guardian Runtime retention classes instead of creating parallel identity or lifecycle systems.
- Added a versioned static contract with deterministic SHA-256 integrity loading.
- Extended RuntimeManager, KnowledgeManager and Mission Context 1.6 without loading User Vault contents or locators.
- Added Preflight checks for contract presence, schema version and hash integrity with no personal reference data in output.

## Decisions

- ZONVAA remains an Intelligence Layer and never becomes the document platform.
- Original data remain user-owned and external to the Guardian Runtime.
- Reference construction and validation perform no file, cloud or network access.
- Copy and synchronization are never implicit; original deletion additionally requires provider capability evidence.
- Life-Decisions DocumentReference remains a domain model and is not converted into a general storage system.

## Relevant ADRs

- ADR-0019 Life Decisions Domain Model
- ADR-0030 Typed Artifact and Authorization State Contract
- ADR-0032 Guardian Runtime Knowledge Model
- ADR-0033 User-Owned Data Architecture

## Checks

- `python3 -m pytest -q tests/test_user_owned_data.py tests/test_preflight.py tests/test_runtime.py`: **passed** — 58 passed in 2.53s
- `python3 -m pytest -q`: **passed** — 552 passed in 17.08s
- `python3 -m builder.main doctor`: **passed** — ZONVAA Builder CLI funktioniert.
- `python3 -m builder.main preflight`: **passed** — MissionContext 1.6 ready with User-Owned Data contract 1.0 and no personal locator data.
- `git diff --check`: **passed** — No whitespace errors.

## Open risks

- No productive User Vault, provider adapter, capability verifier or storage executor exists.
- A syntactically valid locator cannot prove ownership, availability or the absence of sensitive meaning.
- Provider capability evidence is structural metadata and not proof that an external deletion was executed.
- Future adapters require separate security, privacy, failure, revocation and deletion-propagation decisions.

## Intentionally not implemented

- Central document storage, ZONVAA Cloud Drive, document hosting or file manager.
- File-system, NAS, cloud, connector or network access.
- Automatic copy, synchronization, replication, mirroring or backup.
- Encryption algorithms, document analysis, productive deletion, migration, UI or CLI.

## Recommended next step

Define a separately approved local adapter and execution boundary that proves owner consent, provider capability, revocation and deletion outcomes without weakening the reference-only contract.

## Git status

- User-Owned Data Architecture files are ready for the final local commit.
- Branch main; starting HEAD 0efaafd07389451d18c2e95419d8507cccc90b85.
