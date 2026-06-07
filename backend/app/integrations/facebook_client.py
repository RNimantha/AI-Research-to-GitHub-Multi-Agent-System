import logging
from typing import Any

import httpx

from backend.app.config import settings

logger = logging.getLogger(__name__)

GRAPH_BASE = "https://graph.facebook.com/v19.0"


class FacebookClient:
    def __init__(self, page_access_token: str | None = None, page_id: str | None = None) -> None:
        self.page_access_token = page_access_token or settings.facebook_page_access_token
        self.page_id = page_id or settings.facebook_page_id
        if not self.page_access_token:
            raise ValueError("FACEBOOK_PAGE_ACCESS_TOKEN is required for Facebook operations")
        if not self.page_id:
            raise ValueError("FACEBOOK_PAGE_ID is required for Facebook operations")

    def _post(self, endpoint: str, data: dict[str, Any]) -> dict[str, Any]:
        data["access_token"] = self.page_access_token
        r = httpx.post(f"{GRAPH_BASE}/{endpoint}", data=data, timeout=15)
        payload = r.json()
        if "error" in payload:
            raise RuntimeError(f"Facebook API error: {payload['error'].get('message', payload['error'])}")
        r.raise_for_status()
        return payload

    def _get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        p = {"access_token": self.page_access_token, **(params or {})}
        r = httpx.get(f"{GRAPH_BASE}/{endpoint}", params=p, timeout=10)
        payload = r.json()
        if "error" in payload:
            raise RuntimeError(f"Facebook API error: {payload['error'].get('message', payload['error'])}")
        r.raise_for_status()
        return payload

    def post_link(self, message: str, link: str) -> dict[str, Any]:
        """Post a message with a link to the Page feed. Returns {id, post_url}."""
        result = self._post(f"{self.page_id}/feed", {"message": message, "link": link})
        post_id = result.get("id", "")
        return {
            "id": post_id,
            "post_url": f"https://www.facebook.com/{post_id.replace('_', '/posts/')}" if post_id else "",
        }

    def post_text(self, message: str) -> dict[str, Any]:
        """Post a text-only update to the Page feed."""
        result = self._post(f"{self.page_id}/feed", {"message": message})
        post_id = result.get("id", "")
        return {
            "id": post_id,
            "post_url": f"https://www.facebook.com/{post_id.replace('_', '/posts/')}" if post_id else "",
        }

    def test_connection(self) -> dict[str, Any]:
        """Verify page access token and return page info."""
        try:
            page = self._get(self.page_id, {"fields": "id,name,category,fan_count"})
            return {
                "connected": True,
                "page_id": page.get("id"),
                "page_name": page.get("name"),
                "category": page.get("category"),
                "fans": page.get("fan_count"),
                "token_prefix": self.page_access_token[:16] + "…",
            }
        except Exception as exc:
            return {"connected": False, "error": str(exc)}


def format_report_post(
    topic_name: str,
    one_liner: str,
    eval_score: float | None,
    tags: list[str],
    github_url: str,
) -> str:
    """Build a Facebook post body for a published research report."""
    lines: list[str] = [
        f"New Research Report: {topic_name}",
        "",
        one_liner,
        "",
    ]
    if eval_score is not None:
        lines.append(f"Eval Score: {eval_score:.1f}/10")
    if tags:
        lines.append("Tags: " + ", ".join(f"#{t.replace(' ', '')}" for t in tags[:6]))
    lines += ["", f"Read the full report and runnable POC: {github_url}"]
    return "\n".join(lines)
