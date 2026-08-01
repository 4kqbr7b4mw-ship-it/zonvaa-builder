from dataclasses import FrozenInstanceError

import pytest

from guardian_understanding import (
    AnswerOperatingMode,
    ClassificationReference,
    SourceChainReference,
    ClassificationValidationError,
)
from guardian_understanding.tests.test_answer_boundary import (
    VALIDATOR as BOUNDARY_VALIDATOR,
    contract as boundary,
)
from guardian_understanding.tests.test_classification import (
    VALIDATOR as CLASSIFICATION_VALIDATOR,
    classification,
)


def test_classification_without_source_chain_reference_is_valid():
    value = classification(source_chain_references=())
    assert CLASSIFICATION_VALIDATOR.validate(value) is value


def test_classification_with_one_source_chain_reference_is_valid():
    reference = SourceChainReference("source-chain-1")
    value = classification(source_chain_references=(reference,))
    assert CLASSIFICATION_VALIDATOR.validate(value) is value
    assert value.source_chain_references == (reference,)


def test_classification_with_multiple_unique_source_chain_references_is_valid():
    references = (
        SourceChainReference("source-chain-1"),
        SourceChainReference("source-chain-2"),
    )
    value = classification(source_chain_references=references)
    assert CLASSIFICATION_VALIDATOR.validate(value) is value


def test_empty_source_chain_reference_is_rejected():
    with pytest.raises(ValueError, match="source_chain_id"):
        SourceChainReference("")


def test_duplicate_source_chain_references_are_rejected():
    reference = SourceChainReference("source-chain-1")
    value = classification(source_chain_references=(reference, reference))
    with pytest.raises(ClassificationValidationError) as error:
        CLASSIFICATION_VALIDATOR.validate(value)
    assert error.value.code == "DUPLICATE_SOURCE_CHAIN_REFERENCE"


def test_boundary_without_classification_reference_is_valid():
    value = boundary(AnswerOperatingMode.B1_GENERAL_ORIENTATION)
    assert value.classification_reference is None
    assert BOUNDARY_VALIDATOR.validate(value) is value


def test_boundary_with_one_classification_reference_is_valid():
    reference = ClassificationReference("classification-1")
    value = boundary(
        AnswerOperatingMode.B1_GENERAL_ORIENTATION,
        classification_reference=reference,
    )
    assert BOUNDARY_VALIDATOR.validate(value) is value
    assert value.classification_reference is reference


def test_empty_classification_reference_is_rejected():
    with pytest.raises(ValueError, match="classification_id"):
        ClassificationReference("")


def test_references_are_immutable_and_never_loaded_or_interpreted():
    source_reference = SourceChainReference("source-chain-not-loaded")
    classification_reference = ClassificationReference(
        "classification-not-loaded"
    )
    classification_value = classification(
        source_chain_references=(source_reference,)
    )
    boundary_value = boundary(
        AnswerOperatingMode.B1_GENERAL_ORIENTATION,
        classification_reference=classification_reference,
    )
    assert CLASSIFICATION_VALIDATOR.validate(classification_value) is classification_value
    assert BOUNDARY_VALIDATOR.validate(boundary_value) is boundary_value
    with pytest.raises(FrozenInstanceError):
        source_reference.source_chain_id = "changed"
    with pytest.raises(FrozenInstanceError):
        classification_reference.classification_id = "changed"
