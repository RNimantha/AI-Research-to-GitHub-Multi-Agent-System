import logging
from typing import Any

logger = logging.getLogger(__name__)


class CostTracker:
    def __init__(self, max_cost_usd: float = 3.00) -> None:
        self.max_cost_usd = max_cost_usd
        self._total_cost = 0.0
        self._total_input_tokens = 0
        self._total_output_tokens = 0
        self._agent_costs: list[dict[str, Any]] = []

    def record(self, agent_name: str, usage: dict[str, Any]) -> None:
        cost = usage.get("estimated_cost_usd", 0.0)
        self._total_cost += cost
        self._total_input_tokens += usage.get("input_tokens", 0)
        self._total_output_tokens += usage.get("output_tokens", 0)
        self._agent_costs.append({"agent": agent_name, "cost_usd": cost, **usage})

        logger.info(
            f"[cost] {agent_name}: ${cost:.4f} | total: ${self._total_cost:.4f}"
        )

        if self._total_cost > self.max_cost_usd:
            raise RuntimeError(
                f"Run cost ${self._total_cost:.4f} exceeded limit ${self.max_cost_usd}. "
                "Halting to prevent runaway spend."
            )

    @property
    def total_cost(self) -> float:
        return self._total_cost

    @property
    def total_input_tokens(self) -> int:
        return self._total_input_tokens

    @property
    def total_output_tokens(self) -> int:
        return self._total_output_tokens

    def summary(self) -> dict[str, Any]:
        return {
            "total_cost_usd": round(self._total_cost, 6),
            "total_input_tokens": self._total_input_tokens,
            "total_output_tokens": self._total_output_tokens,
            "agent_breakdown": self._agent_costs,
        }
