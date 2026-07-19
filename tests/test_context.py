from brain.context_collector import ContextCollector
from brain.context_analyzer import ContextAnalyzer


def test_context_contains_latest_session():
    context = ContextCollector().collect()

    assert "latest_session" in context
    assert "path" in context["latest_session"]
    assert "content" in context["latest_session"]


def test_analyzer_keeps_latest_session():
    context = ContextCollector().collect()
    analysis = ContextAnalyzer().analyze(context)

    assert analysis["latest_session"] == context["latest_session"]
