"""Conservative step, iteration, usage, and reported-cost accounting."""

from __future__ import annotations

from dataclasses import dataclass

from .schemas import UsageRecord


class BudgetExceeded(RuntimeError):
    pass


@dataclass
class CostUsageGuard:
    max_iterations: int
    max_steps: int
    max_cost: float | None = None
    steps: int = 0
    iterations: int = 0
    requests: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    reported_cost: float | None = None

    def start_step(self) -> None:
        if self.steps >= self.max_steps:
            raise BudgetExceeded("maximum run steps reached")
        self.steps += 1

    def start_iteration(self) -> None:
        if self.iterations >= self.max_iterations:
            raise BudgetExceeded("maximum review iterations reached")
        self.iterations += 1

    def add_usage(self, usage: UsageRecord) -> None:
        self.requests += usage.requests
        self.input_tokens += usage.input_tokens
        self.output_tokens += usage.output_tokens
        self.total_tokens += usage.total_tokens
        if usage.reported_cost is not None:
            self.reported_cost = (self.reported_cost or 0.0) + usage.reported_cost
            if self.max_cost is not None and self.reported_cost > self.max_cost:
                raise BudgetExceeded("reported cost budget exceeded")

    def snapshot(self) -> UsageRecord:
        return UsageRecord(
            requests=self.requests,
            input_tokens=self.input_tokens,
            output_tokens=self.output_tokens,
            total_tokens=self.total_tokens,
            reported_cost=self.reported_cost,
            cost_status=(
                "reported by provider; no local price inference"
                if self.reported_cost is not None
                else "not reliably determined"
            ),
        )
