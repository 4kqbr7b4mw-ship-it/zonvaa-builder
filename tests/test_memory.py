from datetime import datetime, timezone

import pytest

from knowledge.manager import KnowledgeManager
from knowledge.memory import Confidence, MemoryRecord, MemoryType


def memory_metadata(**overrides):
    metadata = {
        "memory_type": "project_memory",
        "source": "tests/test_memory.py",
        "created_at": datetime(2026, 7, 21, tzinfo=timezone.utc),
        "confidence": "confirmed",
        "retention_policy": "retain for project lifetime",
        "protected": False,
        "verified": True,
    }
    metadata.update(overrides)
    return metadata


@pytest.mark.parametrize("memory_type", list(MemoryType))
def test_all_memory_types_are_accepted(memory_type):
    record = MemoryRecord(**memory_metadata(memory_type=memory_type))

    assert record.memory_type is memory_type


def test_unknown_memory_type_is_rejected():
    with pytest.raises(ValueError, match="Unknown memory type"):
        MemoryRecord(**memory_metadata(memory_type="temporary_memory"))


def test_heritage_memory_is_always_protected():
    record = MemoryRecord(
        **memory_metadata(memory_type="heritage_memory", protected=False)
    )

    assert record.protected is True


@pytest.mark.parametrize("confidence", [Confidence.UNCERTAIN, Confidence.PROBABLE])
def test_unconfirmed_memory_cannot_be_verified(confidence):
    with pytest.raises(ValueError, match="Only confirmed memory"):
        MemoryRecord(**memory_metadata(confidence=confidence, verified=True))


def test_knowledge_manager_validates_memory_classification():
    record = KnowledgeManager().classify_memory(
        **memory_metadata(memory_type="archive_memory")
    )

    assert record.memory_type is MemoryType.ARCHIVE
    assert record.verified is True
