import json
import logging
from typing import Any

from backend.app.core.prompt_loader import load_prompt
from backend.app.integrations.llm_client import LLMClient
from backend.app.integrations.search_client import SearchClient

logger = logging.getLogger(__name__)

SEARCH_TOOL = {
    "name": "search_web",
    "description": (
        "Search the web for information about a topic. "
        "Use specific, focused queries. Call multiple times to cover different angles: "
        "overview, technical details, use cases, limitations, recent developments, code examples."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "A focused search query (e.g. 'LangGraph multi-agent architecture 2025')",
            }
        },
        "required": ["query"],
    },
}

FINALIZE_TOOL = {
    "name": "finalize_research",
    "description": (
        "Call this when you have gathered enough information to write a complete research report. "
        "Pass all structured research notes and sources."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "research_notes": {
                "type": "object",
                "description": "Structured research notes covering all topic areas",
            },
            "raw_sources": {
                "type": "array",
                "description": "List of sources found",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "url": {"type": "string"},
                        "source_type": {"type": "string"},
                        "published_date": {"type": "string"},
                        "summary": {"type": "string"},
                        "credibility_score": {"type": "number"},
                    },
                },
            },
        },
        "required": ["research_notes", "raw_sources"],
    },
}


def run_research_agent(
    topic: str,
    max_sources: int = 12,
    llm: LLMClient | None = None,
    search: SearchClient | None = None,
) -> dict[str, Any]:
    """Research agent with LLM-driven tool-use search loop."""
    llm = llm or LLMClient()
    search = search or SearchClient()

    logger.info(f"Research agent: starting tool-use research for '{topic}'")

    finalized: dict[str, Any] = {}

    def tool_executor(name: str, args: dict[str, Any]) -> str:
        if name == "search_web":
            query = args.get("query", "")
            logger.info(f"Research agent: searching '{query}'")
            results = search.search(query, max_results=8)
            if not results:
                return "No results found."
            lines = []
            for r in results[:8]:
                lines.append(
                    f"Title: {r['title']}\n"
                    f"URL: {r['url']}\n"
                    f"Published: {r.get('published_date', 'unknown')}\n"
                    f"Content: {r['content'][:600]}\n"
                )
            return "\n---\n".join(lines)

        if name == "finalize_research":
            finalized["research_notes"] = args.get("research_notes", {})
            finalized["raw_sources"] = args.get("raw_sources", [])[:max_sources]
            logger.info(f"Research agent: finalized with {len(finalized['raw_sources'])} sources")
            return "Research finalized."

        return f"Unknown tool: {name}"

    system = load_prompt("research")
    user = f"""Research the following AI topic deeply.

TOPIC: {topic}

Use the search_web tool to find information. Search at least 6 times covering:
1. Overview and definition
2. How it works (technical)
3. Implementation and code examples
4. Real-world use cases
5. Limitations and problems
6. Recent developments (2024-2025)
7. Official docs, papers, or GitHub repos
8. Comparison with alternatives

When you have enough information, call finalize_research with structured notes and up to {max_sources} sources.
"""

    response = llm.complete_with_tools(
        system=system,
        user=user,
        tools=[SEARCH_TOOL, FINALIZE_TOOL],
        tool_executor=tool_executor,
        max_tool_calls=15,
        max_tokens=8192,
    )

    # Fallback: if finalize_research was never called, try parsing LLM text as JSON
    if not finalized:
        logger.warning("Research agent: finalize_research not called — attempting text parse")
        try:
            parsed = json.loads(response["content"])
            finalized["research_notes"] = parsed.get("research_notes", {})
            finalized["raw_sources"] = parsed.get("raw_sources", [])[:max_sources]
        except (json.JSONDecodeError, TypeError):
            finalized["research_notes"] = {"summary": response["content"]}
            finalized["raw_sources"] = []

    logger.info(
        f"Research agent: done — {len(finalized.get('raw_sources', []))} sources, "
        f"{response['tool_calls_made']} searches, "
        f"${response['estimated_cost_usd']:.4f}"
    )

    return {
        "research_context": finalized.get("research_notes", {}),
        "raw_sources": finalized.get("raw_sources", []),
        "usage": {
            "model": response["model"],
            "input_tokens": response["input_tokens"],
            "output_tokens": response["output_tokens"],
            "estimated_cost_usd": response["estimated_cost_usd"],
            "latency_ms": response["latency_ms"],
            "tool_calls_made": response["tool_calls_made"],
        },
    }
