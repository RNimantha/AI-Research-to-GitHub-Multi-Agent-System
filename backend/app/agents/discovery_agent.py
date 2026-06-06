import logging
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from backend.app.core.prompt_loader import load_prompt
from backend.app.integrations.llm_client import LLMClient
from backend.app.integrations.search_client import SearchClient

logger = logging.getLogger(__name__)


DISCOVERY_QUERY_TEMPLATES = [
    "latest AI LLM breakthroughs {year}",
    "new agentic AI frameworks released {year}",
    "recent RAG retrieval augmented generation improvements {year}",
    "new multimodal AI models {year}",
    "LangChain LangGraph new releases {year}",
    "Anthropic Claude new features {year}",
    "AI fine-tuning techniques advances {year}",
    "new AI developer tools libraries {year}",
    "trending AI GitHub repositories {year}",
    "recent AI research papers with implementation {year}",
]


class DiscoverySource(BaseModel):
    title: str = Field(..., min_length=1)
    url: str = Field(..., min_length=1)
    source_type: str = "unknown"  # official_docs|paper|github|blog|tutorial|community|newsletter|supporting_source
    source_tier: int = Field(default=2, ge=1, le=3)  # 1=primary, 2=technical supporting, 3=community signal
    published_date: str | None = None
    why_relevant: str = ""


class DiscoveredTopic(BaseModel):
    title: str = Field(..., min_length=3)
    slug: str = Field(..., min_length=3)
    category: str = Field(..., min_length=3)
    summary: str = Field(..., min_length=20)
    why_now: str = Field(..., min_length=10)
    evidence_summary: str = Field(..., min_length=10)
    poc_idea: str = Field(..., min_length=10)
    required_tools: list[str] = Field(default_factory=list)
    estimated_complexity: str = "medium"

    sources: list[DiscoverySource] = Field(default_factory=list)

    novelty_score: int = Field(ge=0, le=10)
    practical_usefulness_score: int = Field(ge=0, le=10)
    poc_feasibility_score: int = Field(ge=0, le=10)
    technical_depth_score: int = Field(ge=0, le=10)
    source_quality_score: int = Field(ge=0, le=10)
    business_value_score: int = Field(ge=0, le=10)
    total_score: float = Field(ge=0, le=10)
    confidence_score: float = Field(ge=0, le=1)
    uncertainties: list[str] = Field(default_factory=list)


class DiscoveryResult(BaseModel):
    topics: list[DiscoveredTopic] = Field(default_factory=list)


def _build_discovery_queries(year: int | None = None) -> list[str]:
    year = year or datetime.now(UTC).year
    return [q.format(year=year) for q in DISCOVERY_QUERY_TEMPLATES]


def _normalize_result(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": result.get("title") or "Untitled",
        "url": result.get("url") or "",
        "content": result.get("content") or result.get("snippet") or "",
        "published_date": result.get("published_date"),
        "source_type": result.get("source_type") or "unknown",
    }


def _dedupe_results(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for r in results:
        url = r.get("url")
        if not url or url in seen:
            continue
        seen.add(url)
        out.append(r)
    return out


def _format_search_context(
    results: list[dict[str, Any]],
    max_results: int = 30,
    max_content_chars: int = 400,
) -> str:
    chunks: list[str] = []
    for i, r in enumerate(results[:max_results], start=1):
        chunks.append(
            f"Result {i}\n"
            f"Title: {r.get('title', 'Untitled')}\n"
            f"URL: {r.get('url', '')}\n"
            f"Published Date: {r.get('published_date') or 'unknown'}\n"
            f"Source Type: {r.get('source_type') or 'unknown'}\n"
            f"Content: {r.get('content', '')[:max_content_chars]}"
        )
    return "\n\n".join(chunks)


def _extract_usage(response: dict[str, Any]) -> dict[str, Any]:
    return {
        "model": response.get("model"),
        "input_tokens": response.get("input_tokens"),
        "output_tokens": response.get("output_tokens"),
        "estimated_cost_usd": response.get("estimated_cost_usd"),
        "latency_ms": response.get("latency_ms"),
    }


def run_discovery_agent(
    llm: LLMClient | None = None,
    search: SearchClient | None = None,
    max_topics: int = 5,
    max_results_each: int = 6,
    max_context_results: int = 30,
    recency_days: int = 90,
) -> dict[str, Any]:
    """Discover recent AI topics and score them for relevance."""
    llm = llm or LLMClient()
    search = search or SearchClient()
    max_topics = max(1, min(max_topics, 10))

    queries = _build_discovery_queries()
    logger.info("Discovery agent: searching for AI topics")

    try:
        raw_results = search.search_multiple(
            queries,
            max_results_each=max_results_each,
            recency_days=recency_days,
        )
    except TypeError:
        # SearchClient doesn't support recency_days yet — fall back
        raw_results = search.search_multiple(queries, max_results_each=max_results_each)
    except Exception as exc:
        logger.exception("Discovery agent: search failed")
        return {
            "discovered_topics": [],
            "raw_sources": [],
            "usage": None,
            "warnings": [],
            "error": f"Search failed: {exc}",
        }

    logger.info("Discovery agent: found %s raw results", len(raw_results))

    normalized = [_normalize_result(r) for r in raw_results]
    deduped = _dedupe_results(normalized)

    if not deduped:
        logger.warning("Discovery agent: no usable search results found")
        return {
            "discovered_topics": [],
            "raw_sources": [],
            "usage": None,
            "warnings": ["No usable search results found"],
            "error": None,
        }

    search_context = _format_search_context(deduped, max_results=max_context_results)

    system = load_prompt("discovery")
    user = f"""Based on the following recent search results, discover and rank the most interesting AI topics for a technical learning report and POC.

Return at most {max_topics} topics.

Prioritize:
1. Recency
2. Source quality
3. Technical depth
4. Practical usefulness
5. POC feasibility

SEARCH RESULTS:
{search_context}
"""

    try:
        response = llm.complete_json(system=system, user=user)
    except Exception as exc:
        logger.exception("Discovery agent: LLM call failed")
        return {
            "discovered_topics": [],
            "raw_sources": deduped,
            "usage": None,
            "warnings": [],
            "error": f"LLM call failed: {exc}",
        }

    try:
        validated = DiscoveryResult.model_validate(response.get("parsed", {}))
    except ValidationError as exc:
        logger.exception("Discovery agent: invalid LLM JSON output")
        return {
            "discovered_topics": [],
            "raw_sources": deduped,
            "usage": _extract_usage(response),
            "warnings": ["LLM returned invalid discovery JSON"],
            "error": str(exc),
        }

    topics = validated.topics[:max_topics]
    logger.info("Discovery agent: identified %s topics", len(topics))

    if not topics:
        return {
            "discovered_topics": [],
            "raw_sources": deduped,
            "usage": _extract_usage(response),
            "warnings": ["No topics identified by discovery agent"],
            "error": None,
        }

    return {
        "discovered_topics": [t.model_dump() for t in topics],
        "raw_sources": deduped,
        "usage": _extract_usage(response),
        "warnings": [],
        "error": None,
    }
