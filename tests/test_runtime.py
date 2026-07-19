from builder.runtime import RuntimeManager


def test_runtime_boot():
    runtime = RuntimeManager().boot()

    assert runtime.constitution is not None
    assert runtime.knowledge
    assert runtime.latest_session is not None
    assert runtime.latest_session_content != ""
