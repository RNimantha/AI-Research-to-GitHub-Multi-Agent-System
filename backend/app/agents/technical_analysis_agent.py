import json
import logging
from typing import Any

from backend.app.integrations.llm_client import LLMClient

logger = logging.getLogger(__name__)

TECHNICAL_ANALYSIS_SYSTEM = """You are a senior AI research engineer and software architect.

Your task is to perform a deep technical analysis of a topic based on verified research context.

Convert raw research into senior-engineer-level understanding. Explain:
1. What the technology does at a precise technical level
2. Why it matters in the current AI ecosystem
3. Where it fits relative to existing tools and paradigms
4. How data and computation flow through it
5. What components are required to build with it
6. How it compares to the main alternatives (trade-offs, not just features)
7. How an engineer would actually build and deploy it

Return a JSON object with keys:
- technical_summary: comprehensive technical analysis (string, 500-1000 words)
- component_breakdown: list of components with descriptions
- data_flow: step-by-step data flow explanation
- comparison_with_alternatives: dict mapping alternative name to trade-off summary
- implementation_guide: practical steps to build with this technology
- gotchas: list of non-obvious issues engineers encounter
"""


def run_technical_analysis_agent(
    topic: str,
    research_context: dict[str, Any],
    verified_sources: list[dict[str, Any]],
    llm: LLMClient | None = None,
) -> dict[str, Any]:
    """Convert raw research into senior-engineer-level technical analysis."""
    llm = llm or LLMClient()

    logger.info(f"Technical analysis agent: analyzing '{topic}'")

    context_json = json.dumps(research_context, indent=2)
    sources_summary = "\n".join(
        f"- [{s.get('title', 'Unknown')}]({s.get('url', '')}): {s.get('verification_notes', '')}"
        for s in verified_sources[:10]
    )

    user = f"""Perform deep technical analysis of: {topic}

VERIFIED RESEARCH CONTEXT:
{context_json[:5000]}

VERIFIED SOURCES:
{sources_summary}

Produce a comprehensive technical analysis that a senior AI engineer can use to write a detailed report.
"""

    response = llm.complete_json(system=TECHNICAL_ANALYSIS_SYSTEM, user=user, max_tokens=6144)
    analysis_data = response["parsed"]

    logger.info("Technical analysis agent: completed")

    return {
        "technical_analysis": analysis_data,
        "usage": {
            "model": response["model"],
            "input_tokens": response["input_tokens"],
            "output_tokens": response["output_tokens"],
            "estimated_cost_usd": response["estimated_cost_usd"],
            "latency_ms": response["latency_ms"],
        },
    }
