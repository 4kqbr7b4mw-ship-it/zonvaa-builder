from builder.runtime import RuntimeManager


def test_runtime_boot():
    runtime = RuntimeManager().boot()

    assert runtime.constitution is not None
    assert runtime.knowledge
    assert runtime.latest_session is not None
    assert runtime.latest_session_content != ""

from builder.runtime import get_runtime


def test_runtime_singleton():
    runtime1 = get_runtime()
    runtime2 = get_runtime()

    assert runtime1 is runtime2

from knowledge.manager import KnowledgeManager


def test_latest_session_empty(monkeypatch):
    monkeypatch.setattr(
        KnowledgeManager,
        "latest_session",
        lambda self: None,
    )

    runtime = RuntimeManager().boot()

    assert runtime.latest_session is None
    assert runtime.latest_session_content == ""
