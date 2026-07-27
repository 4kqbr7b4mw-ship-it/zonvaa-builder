from builder.runtime import RuntimeManager


def test_runtime_boot():
    runtime = RuntimeManager().boot()

    assert runtime.artifact_contract_context is not None
    assert runtime.guardian_runtime_contract_context is not None
    assert runtime.guardian_runtime_snapshot is not None
    assert runtime.guardian_runtime_snapshot.active_subject_id is None
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


def test_runtime_exposes_project_state():
    runtime = RuntimeManager().boot()

    assert isinstance(runtime.project_state, dict)
    assert "python_version" in runtime.project_state
    assert "pytest_version" in runtime.project_state
    assert "git_branch" in runtime.project_state
    assert "git_commit" in runtime.project_state
    assert "git_clean" in runtime.project_state
