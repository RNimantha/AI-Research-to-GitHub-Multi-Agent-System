import time
from typing import Any

from backend.app.config import settings


class SearchClient:
    """Tavily API wrapper for web research."""

    def __init__(self) -> None:
        self._provider = settings.search_provider
        self._client = self._init_client()

    def _init_client(self) -> Any:
        if self._provider == "tavily":
            if not settings.tavily_api_key:
                raise ValueError("TAVILY_API_KEY is required when SEARCH_PROVIDER=tavily")
            from tavily import TavilyClient
            return TavilyClient(api_key=settings.tavily_api_key)
        raise ValueError(f"Unsupported search provider: {self._provider}")

    def search(self, query: str, max_results: int = 10) -> list[dict[str, Any]]:
        """Search the web and return structured results."""
        if self._provider == "tavily":
            return self._search_tavily(query, max_results)
        raise ValueError(f"Unsupported search provider: {self._provider}")

    def _search_tavily(self, query: str, max_results: int) -> list[dict[str, Any]]:
        response = self._client.search(
            query=query,
            max_results=max_results,
            search_depth="advanced",
            include_raw_content=False,
            include_images=False,
        )
        results = []
        for r in response.get("results", []):
            results.append({
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": r.get("content", ""),
                "score": r.get("score", 0.0),
                "published_date": r.get("published_date"),
                "accessed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            })
        return results

    def search_multiple(self, queries: list[str], max_results_each: int = 8) -> list[dict[str, Any]]:
        """Run multiple queries and deduplicate by URL."""
        seen_urls: set[str] = set()
        all_results: list[dict[str, Any]] = []
        for query in queries:
            results = self.search(query, max_results_each)
            for r in results:
                if r["url"] not in seen_urls:
                    seen_urls.add(r["url"])
                    all_results.append(r)
        return all_results
