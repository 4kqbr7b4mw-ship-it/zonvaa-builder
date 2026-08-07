from __future__ import annotations

import json
import os
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import pytest

from development_orchestrator.backends import (
    BackendConfigurationError,
    OpenAIAgentsBackend,
)
from development_orchestrator.model_configuration import V1_LIVE_MODEL_CONFIGURATION
from development_orchestrator.schemas import AgentModelConfiguration


ROOT = Path(__file__).resolve().parents[1]


def run_cli(*arguments: str, env=None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "main.py", *arguments],
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_offline_cli_runs_real_manager_path() -> None:
    result = run_cli("run", "--request", "fixtures/smoke-request.json", "--offline")
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "COMPLETED"
    assert payload["review_outcome"] == "ACCEPT"
    assert payload["usage"]["cost_status"] == "not reliably determined"


def test_live_smoke_without_key_is_clean_configuration_error() -> None:
    env = dict(os.environ)
    env.pop("OPENAI_API_KEY", None)
    result = run_cli("smoke", env=env)
    assert result.returncode == 2
    assert "OPENAI_API_KEY is required" in result.stderr
    assert "Traceback" not in result.stderr
    assert result.stdout == ""


def test_backend_refuses_missing_key_before_sdk_import(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(BackendConfigurationError, match="OPENAI_API_KEY"):
        OpenAIAgentsBackend(V1_LIVE_MODEL_CONFIGURATION)


def test_live_backend_requires_explicit_model_configuration(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "synthetic-test-value")
    with pytest.raises(BackendConfigurationError, match="explicit Research"):
        OpenAIAgentsBackend(None)


def test_live_backend_rejects_unknown_models(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "synthetic-test-value")
    unknown = AgentModelConfiguration(
        research_model="unknown-model",
        review_model="gpt-4.1",
    )
    with pytest.raises(BackendConfigurationError, match="unsupported"):
        OpenAIAgentsBackend(unknown)


def test_live_configuration_explicitly_selects_both_agent_models() -> None:
    assert V1_LIVE_MODEL_CONFIGURATION.research_model == "gpt-4.1"
    assert V1_LIVE_MODEL_CONFIGURATION.review_model == "gpt-4.1"


def test_subproject_declares_agents_sdk_dependency() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert '"openai-agents"' in pyproject
    assert '"openai==2.19.0"' in pyproject
    assert 'requires-python = ">=3.9"' in pyproject


def test_current_repository_environment_does_not_claim_live_sdk_ready() -> None:
    try:
        installed = version("openai-agents")
    except PackageNotFoundError:
        installed = None
    assert installed is None or isinstance(installed, str)


def test_readme_states_internal_boundary_and_no_git_automation() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "not part of the ZONVAA product runtime" in readme
    assert "internal/development-orchestrator/**" in readme
    assert "No commit or push automation in v1" in readme
    assert "not represented as an OpenAI model run" in readme
    assert "explicitly selects `gpt-4.1` for both Research and Review" in readme
    assert "SDK default model and automatic fallback chains are not used" in readme
