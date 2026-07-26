import os

import pytest

from knowledge.manager import KnowledgeManager


def test_knowledge_manager_rejects_missing_core_structure(tmp_path):
    manager = KnowledgeManager()
    manager.root = tmp_path / "knowledge"
    manager.root.mkdir()

    with pytest.raises(FileNotFoundError, match="Missing knowledge folders"):
        manager.load()


def test_latest_context_prefers_newest_session_or_handover(
    tmp_path,
):
    manager = KnowledgeManager()
    manager.root = tmp_path / "knowledge"
    session_folder = manager.root / "sessions"
    handover_folder = manager.root / "handovers"
    session_folder.mkdir(parents=True)
    handover_folder.mkdir()
    session = session_folder / "session.md"
    handover = handover_folder / "handover.json"
    session.write_text("session", encoding="utf-8")
    handover.write_text("{}", encoding="utf-8")
    os.utime(session, (1, 1))
    os.utime(handover, (2, 2))

    assert manager.latest_context() == handover
