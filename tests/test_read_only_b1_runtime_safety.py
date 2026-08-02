import inspect

from governance import read_only_b1_runtime
from governance.read_only_b1_runtime import B1ReadOnlyRuntimeExecutor


def test_runtime_module_has_no_network_persistence_registry_or_provider_selection():
    source = inspect.getsource(read_only_b1_runtime)
    for forbidden in (
        "import requests",
        "import httpx",
        "import urllib",
        "import socket",
        "ProviderRegistry",
        "select_provider(",
        "fallback_provider(",
        "audit_log(",
        "persist(",
    ):
        assert forbidden not in source


def test_executor_exposes_no_retry_scheduling_or_answer_activation_api():
    executor = B1ReadOnlyRuntimeExecutor()
    for name in (
        "retry",
        "schedule",
        "select_provider",
        "activate_answer",
        "activate_tool",
        "start_workflow",
        "persist",
        "write_audit_log",
    ):
        assert not hasattr(executor, name)
