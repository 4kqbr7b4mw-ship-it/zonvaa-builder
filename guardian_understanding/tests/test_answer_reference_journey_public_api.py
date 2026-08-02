import guardian_understanding as public_api


def test_reference_journey_and_experience_public_api_is_complete():
    expected = (
        "AnswerFoundationReference",
        "AnswerReferenceJourneyCapability",
        "AnswerReferenceJourneyCompletionReason",
        "AnswerReferenceJourneyOrigin",
        "AnswerReferenceJourneyStatus",
        "AnswerReferenceJourneyStep",
        "AnswerReferenceJourneyStepResult",
        "AnswerReferenceJourneyStepType",
        "AnswerReferenceJourneyStopReason",
        "AnswerReferenceJourneyValidationError",
        "GuardianAnswerExperience",
        "GuardianAnswerExperienceAction",
        "GuardianAnswerExperienceProjector",
        "GuardianAnswerReferenceJourney",
        "GuardianAnswerReferenceJourneyContractValidator",
        "GuardianAnswerReferenceJourneyEnvelope",
        "GuardianAnswerReferenceJourneyValidator",
        "ProfessionalBoundaryReference",
        "answer_foundation_reference",
    )
    for name in expected:
        assert name in public_api.__all__
        assert getattr(public_api, name) is not None
