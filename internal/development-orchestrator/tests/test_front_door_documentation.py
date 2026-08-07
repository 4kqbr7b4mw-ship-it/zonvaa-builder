from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_readme_documents_the_local_front_door_and_hard_limits() -> None:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    for required in (
        "Single working front door",
        "submit_work",
        "approve_context",
        "local STDIO only",
        "browser-based ChatGPT integration cannot call this localhost process directly",
        "No commit or push automation in v1",
    ):
        assert required in text


def test_assessment_distinguishes_local_working_path_from_remote_gap() -> None:
    text = (
        ROOT / "docs" / "single-front-door-integration-assessment.md"
    ).read_text(encoding="utf-8")
    assert "**Selected:** a local, tool-only STDIO MCP adapter" in text
    assert "There is no shell" in text
    assert "Explicit approval is scoped to one run" in text
    assert "**Answer: NO.**" in text
    assert "A public anonymous" in text
    assert "service and a general shell capability are prohibited" in text
