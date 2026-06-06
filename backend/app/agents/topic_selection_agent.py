import logging
from typing import Any

from backend.app.core.prompt_loader import load_prompt
from backend.app.integrations.llm_client import LLMClient

logger = logging.getLogger(__name__)


def run_topic_selection_agent(
    topics: list[dict[str, Any]],
    llm: LLMClient | None = None,
) -> dict[str, Any]:
    """Select the best topic from discovered topics."""
    if not topics:
        raise ValueError("No topics provided to topic selection agent")

    llm = llm or LLMClient()

    topics_json = "\n".join(
        f"{i+1}. {t['title']} (novelty={t.get('novelty_score', 0)}, "
        f"poc={t.get('poc_feasibility_score', 0)}, value={t.get('business_value_score', 0)})\n"
        f"   Summary: {t.get('summary', '')}"
        for i, t in enumerate(topics)
    )

    system = load_prompt("topic_selection")
    user = f"""Select the best topic for a deep technical learning report and POC from these discovered topics:

{topics_json}

Consider novelty, practical usefulness, POC feasibility, source availability, and learning value.
"""

    response = llm.complete_json(system=system, user=user)
    selection_data = response["parsed"]

    logger.info(f"Topic selection agent: selected '{selection_data.get('selected_topic', {}).get('title', 'unknown')}'")

    return {
        "selected_topic": selection_data.get("selected_topic", {}),
        "ranked_topics": selection_data.get("ranked_topics", []),
        "usage": {
            "model": response["model"],
            "input_tokens": response["input_tokens"],
            "output_tokens": response["output_tokens"],
            "estimated_cost_usd": response["estimated_cost_usd"],
            "latency_ms": response["latency_ms"],
        },
    }
