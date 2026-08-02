import governance


def test_physical_operational_persistence_public_api_is_complete():
    expected = (
        "PersistencePortOperation",
        "PersistencePortRequest",
        "PersistencePortResult",
        "PersistencePortResultStatus",
        "PhysicalBackupContract",
        "PhysicalBackupStatus",
        "PhysicalCompletenessStatus",
        "PhysicalOperationalPersistencePackage",
        "PhysicalOperationalPersistencePort",
        "PhysicalOperationalPersistenceSnapshot",
        "PhysicalOperationalPersistenceValidationError",
        "PhysicalOperationalPersistenceValidator",
        "PhysicalPersistenceRecord",
        "PhysicalPersistenceStatus",
        "PhysicalRecoveryContract",
        "PhysicalRecoveryStatus",
    )
    for name in expected:
        assert name in governance.__all__
        assert getattr(governance, name) is not None
