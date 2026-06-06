import json
import logging
from typing import Any

from backend.app.core.prompt_loader import load_prompt
from backend.app.integrations.llm_client import LLMClient
from backend.app.integrations.search_client import SearchClient

logger = logging.getLogger(__name__)

DISCOVERY_QUERIES = [
    "latest AI LLM breakthroughs 2025",
    "new agentic AI frameworks released 2025",
    "recent RAG retrieval augmented generation improvements",
    "new multimodal AI models 2025",
    "LangChain LangGraph new releases 2025",
    "Anthropic Claude new features 2025",
    "AI fine-tuning techniques advances 2025",
    "new AI developer tools libraries 2025",
    "trending AI GitHub repositories 2025",
    "recent AI research papers implementation",
]


def run_discovery_agent(
    llm: LLMClient | None = None,
    search: SearchClient | None = None,
    max_topics: int = 5,
) -> dict[str, Any]:
    """Discover recent AI topics and score them for relevance."""
    llm = llm or LLMClient()
    search = search or SearchClient()

    logger.info("Discovery agent: searching for AI topics")

    raw_results = search.search_multiple(DISCOVERY_QUERIES, max_results_each=6)
    logger.info(f"Discovery agent: found {len(raw_results)} raw results")

    search_context = "\n\n".join(
        f"Title: {r['title']}\nURL: {r['url']}\nContent: {r['content'][:500]}"
        for r in raw_results[:40]
    )

    system = load_prompt("discovery")
    user = f"""Based on the following recent search results, discover and rank the most interesting AI topics for a technical learning report and POC.

Return at most {max_topics} topics, prioritizing novelty and POC feasibility.

SEARCH RESULTS:
{search_context}
"""

    response = llm.complete_json(system=system, user=user)
    topics_data = response["parsed"]

    logger.info(f"Discovery agent: identified {len(topics_data.get('topics', []))} topics")

    return {
        "discovered_topics": topics_data.get("topics", []),
        "usage": {
            "model": response["model"],
            "input_tokens": response["input_tokens"],
            "output_tokens": response["output_tokens"],
            "estimated_cost_usd": response["estimated_cost_usd"],
            "latency_ms": response["latency_ms"],
        },
    }
