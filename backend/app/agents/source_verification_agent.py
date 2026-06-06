import json
import logging
from typing import Any

from backend.app.core.prompt_loader import load_prompt
from backend.app.integrations.llm_client import LLMClient

logger = logging.getLogger(__name__)


def run_source_verification_agent(
    topic: str,
    raw_sources: list[dict[str, Any]],
    research_context: dict[str, Any],
    llm: LLMClient | None = None,
) -> dict[str, Any]:
    """Verify source quality and return verified/rejected source lists."""
    llm = llm or LLMClient()

    logger.info(f"Source verification agent: verifying {len(raw_sources)} sources")

    sources_json = json.dumps(raw_sources, indent=2)
    context_json = json.dumps(research_context, indent=2)

    system = load_prompt("source_verification")
    user = f"""Verify the following sources collected for a technical report on: {topic}

RESEARCH CONTEXT SUMMARY:
{context_json[:2000]}

RAW SOURCES TO VERIFY:
{sources_json[:6000]}

Check each source for authority, recency, technical depth, and claim support.
Return verified sources (credibility_score >= 0.6) and rejected sources separately.
"""

    response = llm.complete_json(system=system, user=user, max_tokens=6144)
    verification_data = response["parsed"]

    verified = verification_data.get("verified_sources", [])
    rejected = verification_data.get("rejected_sources", [])
    confidence = verification_data.get("confidence_score", 0.0)

    logger.info(
        f"Source verification: {len(verified)} verified, {len(rejected)} rejected, "
        f"confidence={confidence:.2f}"
    )

    return {
        "verified_sources": verified,
        "rejected_sources": rejected,
        "unsupported_claims": verification_data.get("unsupported_claims", []),
        "confidence_score": confidence,
        "usage": {
            "model": response["model"],
            "input_tokens": response["input_tokens"],
            "output_tokens": response["output_tokens"],
            "estimated_cost_usd": response["estimated_cost_usd"],
            "latency_ms": response["latency_ms"],
        },
    }
