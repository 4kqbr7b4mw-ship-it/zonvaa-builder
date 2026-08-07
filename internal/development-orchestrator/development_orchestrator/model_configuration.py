"""Explicit, closed model selection for the v1 orchestrator."""

from __future__ import annotations

from typing import Optional

from .schemas import AgentModelConfiguration


V1_LIVE_MODEL = "gpt-4.1"
V1_SUPPORTED_LIVE_MODELS = frozenset({V1_LIVE_MODEL})
V1_LIVE_MODEL_CONFIGURATION = AgentModelConfiguration(
    research_model=V1_LIVE_MODEL,
    review_model=V1_LIVE_MODEL,
)
V1_OFFLINE_MODEL_CONFIGURATION = AgentModelConfiguration(
    research_model="offline-contract-v1",
    review_model="offline-contract-v1",
)


class ModelConfigurationError(RuntimeError):
    """Raised when an explicit live model selection is absent or unsupported."""


def require_supported_live_configuration(
    configuration: Optional[AgentModelConfiguration],
) -> AgentModelConfiguration:
    if configuration is None:
        raise ModelConfigurationError(
            "explicit Research and Review model configuration is required"
        )
    configured = {
        configuration.research_model,
        configuration.review_model,
    }
    unsupported = configured - V1_SUPPORTED_LIVE_MODELS
    if unsupported:
        raise ModelConfigurationError(
            "unsupported v1 live model configuration: {}".format(
                ", ".join(sorted(unsupported))
            )
        )
    return configuration
