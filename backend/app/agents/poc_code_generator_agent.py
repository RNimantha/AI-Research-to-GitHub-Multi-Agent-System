import json
import logging
from typing import Any

from backend.app.core.prompt_loader import load_prompt
from backend.app.integrations.llm_client import LLMClient

logger = logging.getLogger(__name__)


def run_poc_code_generator_agent(
    topic: str,
    poc_plan: dict[str, Any],
    revision_issues: list[str] | None = None,
    llm: LLMClient | None = None,
) -> dict[str, Any]:
    """Generate all POC project files based on the plan."""
    llm = llm or LLMClient()

    logger.info(f"Code generator agent: generating code for '{topic}'")

    system = load_prompt("code_generator")

    revision_section = ""
    if revision_issues:
        revision_section = f"""
PREVIOUS REVIEW ISSUES TO FIX:
{chr(10).join(f'- {issue}' for issue in revision_issues)}

Address every issue above in this generation.
"""

    user = f"""Generate all files for this POC project:

TOPIC: {topic}

POC PLAN:
{json.dumps(poc_plan, indent=2)}

{revision_section}
Generate complete, working code for every file in the plan.
Return JSON with a "files" array where each element has "path", "purpose", and "content".
"""

    response = llm.complete_json(system=system, user=user, max_tokens=12000)
    files_data = response["parsed"]

    generated_files = files_data.get("files", [])
    logger.info(f"Code generator: generated {len(generated_files)} files")

    return {
        "generated_files": generated_files,
        "usage": {
            "model": response["model"],
            "input_tokens": response["input_tokens"],
            "output_tokens": response["output_tokens"],
            "estimated_cost_usd": response["estimated_cost_usd"],
            "latency_ms": response["latency_ms"],
        },
    }
