from __future__ import annotations

import pytest

from development_orchestrator.boundary import BoundaryGuard, BoundaryViolation
from development_orchestrator.context_loader import ProjectContextLoader
from development_orchestrator.cost_guard import BudgetExceeded, CostUsageGuard
from development_orchestrator.schemas import UsageRecord


def test_context_loader_selects_only_explicit_paths(isolated_repository) -> None:
    repository, tool_root = isolated_repository
    loader = ProjectContextLoader(BoundaryGuard(repository, tool_root))
    bundle = loader.load("research evidence", ["README.md", "docs/research.md"])
    assert bundle.selected_paths == ["docs/research.md", "README.md"]
    assert bundle.total_characters == sum(len(item.content) for item in bundle.documents)


def test_context_loader_deduplicates_and_limits_content(isolated_repository) -> None:
    repository, tool_root = isolated_repository
    loader = ProjectContextLoader(
        BoundaryGuard(repository, tool_root), max_files=1, max_file_characters=5
    )
    bundle = loader.load("readme", ["README.md", "README.md", "docs/research.md"])
    assert len(bundle.documents) == 1
    assert len(bundle.documents[0].content) == 5
    assert bundle.documents[0].truncated is True


def test_context_loader_blocks_external_path(isolated_repository, tmp_path) -> None:
    repository, tool_root = isolated_repository
    outside = tmp_path / "outside.md"
    outside.write_text("outside", encoding="utf-8")
    with pytest.raises(BoundaryViolation):
        ProjectContextLoader(BoundaryGuard(repository, tool_root)).load(
            "outside", [str(outside)]
        )


def test_cost_guard_records_usage_without_inventing_cost() -> None:
    guard = CostUsageGuard(max_iterations=2, max_steps=4)
    guard.add_usage(UsageRecord(requests=1, input_tokens=10, output_tokens=3, total_tokens=13))
    snapshot = guard.snapshot()
    assert snapshot.total_tokens == 13
    assert snapshot.reported_cost is None
    assert snapshot.cost_status == "not reliably determined"


def test_cost_guard_stops_on_reported_budget_excess() -> None:
    guard = CostUsageGuard(max_iterations=2, max_steps=4, max_cost=0.5)
    with pytest.raises(BudgetExceeded, match="cost budget"):
        guard.add_usage(UsageRecord(reported_cost=0.6))


def test_cost_guard_stops_on_steps_and_iterations() -> None:
    guard = CostUsageGuard(max_iterations=1, max_steps=1)
    guard.start_iteration()
    guard.start_step()
    with pytest.raises(BudgetExceeded, match="iterations"):
        guard.start_iteration()
    with pytest.raises(BudgetExceeded, match="steps"):
        guard.start_step()
