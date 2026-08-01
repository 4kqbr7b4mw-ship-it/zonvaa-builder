"""Structural integration of already validated Guardian answer contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from guardian_understanding.answer_boundary import (
    AnswerBoundaryContract,
    AnswerOperatingMode,
    GuardianAnswerBoundaryValidator,
    answer_mode_protection_level,
)
from guardian_understanding.classification import (
    GuardianClassificationContract,
    GuardianClassificationValidator,
)
from guardian_understanding.source_chain import (
    GuardianSourceChainContract,
    GuardianSourceChainValidator,
)


@dataclass(frozen=True)
class GuardianAnswerFoundationIntegration:
    boundary_contract: AnswerBoundaryContract
    classification_contract: GuardianClassificationContract
    source_chain_contracts: Tuple[GuardianSourceChainContract, ...]
    require_complete_source_chain_set: bool

    def __post_init__(self) -> None:
        if not isinstance(self.boundary_contract, AnswerBoundaryContract):
            raise TypeError("boundary_contract must be an AnswerBoundaryContract")
        if not isinstance(
            self.classification_contract,
            GuardianClassificationContract,
        ):
            raise TypeError(
                "classification_contract must be a GuardianClassificationContract"
            )
        if not isinstance(self.source_chain_contracts, tuple) or not all(
            isinstance(item, GuardianSourceChainContract)
            for item in self.source_chain_contracts
        ):
            raise TypeError(
                "source_chain_contracts must contain GuardianSourceChainContract"
            )
        if not isinstance(self.require_complete_source_chain_set, bool):
            raise TypeError("require_complete_source_chain_set must be a bool")


class AnswerFoundationIntegrationError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


class GuardianAnswerFoundationIntegrationValidator:
    """Check supplied identities and protection without deriving any content."""

    def validate(
        self,
        integration: GuardianAnswerFoundationIntegration,
    ) -> GuardianAnswerFoundationIntegration:
        if not isinstance(integration, GuardianAnswerFoundationIntegration):
            raise TypeError(
                "integration must be a GuardianAnswerFoundationIntegration"
            )

        boundary = GuardianAnswerBoundaryValidator().validate(
            integration.boundary_contract
        )
        classification = GuardianClassificationValidator().validate(
            integration.classification_contract
        )
        source_chains = tuple(
            GuardianSourceChainValidator().validate(contract)
            for contract in integration.source_chain_contracts
        )

        classification_reference = boundary.classification_reference
        if (
            classification_reference is not None
            and classification_reference.classification_id
            != classification.classification_id
        ):
            _invalid(
                "CLASSIFICATION_REFERENCE_MISMATCH",
                "boundary classification reference does not match",
            )

        supplied_source_ids = tuple(
            contract.source_chain_id for contract in source_chains
        )
        if len(supplied_source_ids) != len(set(supplied_source_ids)):
            _invalid(
                "DUPLICATE_SOURCE_CHAIN_ID",
                "supplied source-chain IDs must be unique",
            )
        referenced_source_ids = tuple(
            reference.source_chain_id
            for reference in classification.source_chain_references
        )
        supplied = set(supplied_source_ids)
        referenced = set(referenced_source_ids)
        if not supplied <= referenced:
            _invalid(
                "UNREFERENCED_SOURCE_CHAIN",
                "supplied source chains must be referenced by classification",
            )
        if integration.require_complete_source_chain_set and supplied != referenced:
            _invalid(
                "INCOMPLETE_SOURCE_CHAIN_SET",
                "complete validation requires the exact referenced source-chain set",
            )

        if answer_mode_protection_level(
            boundary.effective_mode
        ) < answer_mode_protection_level(classification.effective_level):
            _invalid(
                "BOUNDARY_PROTECTION_TOO_LOW",
                "boundary mode must not be less protective than classification",
            )

        return integration


def _invalid(code: str, message: str) -> None:
    raise AnswerFoundationIntegrationError(code, message)
