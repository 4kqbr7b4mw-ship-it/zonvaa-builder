import governance


def test_operational_memory_public_api_is_complete():
    expected = (
        "OperationalMemoryArtifact",
        "OperationalMemoryArtifactBinding",
        "OperationalMemoryArtifactType",
        "OperationalMemoryOrigin",
        "OperationalMemoryPackage",
        "OperationalMemoryRecord",
        "OperationalMemorySnapshot",
        "OperationalMemoryValidationError",
        "OperationalMemoryValidator",
    )
    for name in expected:
        assert name in governance.__all__
        assert getattr(governance, name) is not None
