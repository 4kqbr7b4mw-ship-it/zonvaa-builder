import governance


def test_b2_data_corridor_public_api_is_exposed():
    expected = (
        "B2DataCorridor",
        "B2ConsentBoundary",
        "B2DataClassification",
        "B2DepersonalizationBoundary",
        "B2NegativeCorridorRules",
        "B2DataCorridorPackage",
        "B2DataCorridorSnapshot",
        "B2DataCorridorValidator",
        "B2DataCorridorValidationError",
    )
    for name in expected:
        assert hasattr(governance, name)
        assert name in governance.__all__
