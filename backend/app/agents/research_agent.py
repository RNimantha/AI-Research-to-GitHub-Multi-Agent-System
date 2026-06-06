import logging
from typing import Any

from backend.app.core.prompt_loader import load_prompt
from backend.app.integrations.llm_client import LLMClient
from backend.app.integrations.search_client import SearchClient

logger = logging.getLogger(__name__)


def _build_research_queries(topic: str) -> list[str]:
    return [
        f"{topic} overview explanation",
        f"{topic} how it works architecture",
        f"{topic} implementation tutorial code",
        f"{topic} use cases real world examples",
        f"{topic} limitations problems issues",
        f"{topic} comparison alternatives",
        f"{topic} recent developments 2025",
        f"{topic} research paper arxiv",
        f"{topic} GitHub repository open source",
        f"{topic} official documentation",
    ]


def run_research_agent(
    topic: str,
    max_sources: int = 12,
    llm: LLMClient | None = None,
    search: SearchClient | None = None,
) -> dict[str, Any]:
    """Perform deep research on a topic and return structured research context."""
    llm = llm or LLMClient()
    search = search or SearchClient()

    logger.info(f"Research agent: researching '{topic}'")

    queries = _build_research_queries(topic)
    raw_results = search.search_multiple(queries, max_results_each=6)
    raw_results = raw_results[:max_sources * 2]

    logger.info(f"Research agent: collected {len(raw_results)} search results")

    search_context = "\n\n---\n\n".join(
        f"Source {i+1}:\nTitle: {r['title']}\nURL: {r['url']}\n"
        f"Published: {r.get('published_date', 'unknown')}\n"
        f"Content: {r['content'][:800]}"
        for i, r in enumerate(raw_results[:30])
    )

    system = load_prompt("research")
    user = f"""Research the following AI topic deeply using the provided search results.

TOPIC: {topic}

SEARCH RESULTS:
{search_context}

Collect structured research notes covering all required areas. Include all source URLs found.
Return max {max_sources} sources, prioritizing the most authoritative and relevant ones.
"""

    response = llm.complete_json(system=system, user=user, max_tokens=8192)
    research_data = response["parsed"]

    logger.info(f"Research agent: completed research with {len(research_data.get('raw_sources', []))} sources")

    return {
        "research_context": research_data.get("research_notes", {}),
        "raw_sources": research_data.get("raw_sources", []),
        "usage": {
            "model": response["model"],
            "input_tokens": response["input_tokens"],
            "output_tokens": response["output_tokens"],
            "estimated_cost_usd": response["estimated_cost_usd"],
            "latency_ms": response["latency_ms"],
        },
    }
