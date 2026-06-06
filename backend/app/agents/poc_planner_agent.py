import json
import logging
from typing import Any

from backend.app.core.prompt_loader import load_prompt
from backend.app.integrations.llm_client import LLMClient

logger = logging.getLogger(__name__)


def run_poc_planner_agent(
    topic: str,
    technical_analysis: dict[str, Any],
    research_context: dict[str, Any],
    llm: LLMClient | None = None,
) -> dict[str, Any]:
    """Design a minimal, runnable POC project plan."""
    llm = llm or LLMClient()

    logger.info(f"POC planner agent: designing POC for '{topic}'")

    system = load_prompt("poc_planner")
    user = f"""Design a minimal, runnable proof-of-concept project that demonstrates: {topic}

TECHNICAL ANALYSIS:
{json.dumps(technical_analysis, indent=2)[:3000]}

RESEARCH CONTEXT (key points):
{json.dumps(research_context, indent=2)[:2000]}

Design the smallest project that meaningfully demonstrates the core concept.
Keep it under 400 lines of code total.
Include README, requirements.txt, .env.example, app/, and tests/.
"""

    response = llm.complete_json(system=system, user=user, max_tokens=4096)
    plan_data = response["parsed"]

    logger.info(f"POC planner: designed '{plan_data.get('project_name', 'unknown')}'")

    return {
        "poc_plan": plan_data,
        "usage": {
            "model": response["model"],
            "input_tokens": response["input_tokens"],
            "output_tokens": response["output_tokens"],
            "estimated_cost_usd": response["estimated_cost_usd"],
            "latency_ms": response["latency_ms"],
        },
    }
