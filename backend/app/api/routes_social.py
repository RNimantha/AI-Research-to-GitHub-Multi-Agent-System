from pathlib import Path
from typing import Any

from dotenv import set_key
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.app.api.deps import require_api_key
from backend.app.config import settings
from backend.app.graph.checkpoints import checkpointer
from backend.app.integrations.facebook_client import FacebookClient, format_report_post

router = APIRouter(tags=["social"])

ENV_FILE = Path(".env")


def _ensure_env() -> None:
    if not ENV_FILE.exists():
        ENV_FILE.write_text("")


class FacebookSettingsRequest(BaseModel):
    facebook_page_access_token: str = ""
    facebook_page_id: str = ""
    facebook_auto_post: bool = False


@router.get("/settings/facebook")
async def get_facebook_settings(_: str = Depends(require_api_key)) -> dict[str, Any]:
    tok = settings.facebook_page_access_token
    return {
        "facebook_page_access_token_set": bool(tok),
        "facebook_page_access_token_preview": f"{tok[:16]}…" if len(tok) > 16 else ("set" if tok else ""),
        "facebook_page_id": settings.facebook_page_id,
        "facebook_auto_post": settings.facebook_auto_post,
    }


@router.post("/settings/facebook")
async def save_facebook_settings(
    body: FacebookSettingsRequest,
    _: str = Depends(require_api_key),
) -> dict[str, Any]:
    _ensure_env()
    if body.facebook_page_access_token:
        set_key(str(ENV_FILE), "FACEBOOK_PAGE_ACCESS_TOKEN", body.facebook_page_access_token)
        settings.facebook_page_access_token = body.facebook_page_access_token
    if body.facebook_page_id:
        set_key(str(ENV_FILE), "FACEBOOK_PAGE_ID", body.facebook_page_id)
        settings.facebook_page_id = body.facebook_page_id
    set_key(str(ENV_FILE), "FACEBOOK_AUTO_POST", str(body.facebook_auto_post).lower())
    settings.facebook_auto_post = body.facebook_auto_post
    return {"saved": True, "facebook_page_access_token_set": bool(settings.facebook_page_access_token)}


@router.post("/settings/facebook/test")
async def test_facebook_connection(_: str = Depends(require_api_key)) -> dict[str, Any]:
    if not settings.facebook_page_access_token or not settings.facebook_page_id:
        return {"connected": False, "error": "FACEBOOK_PAGE_ACCESS_TOKEN or FACEBOOK_PAGE_ID not set"}
    client = FacebookClient()
    return client.test_connection()


@router.post("/runs/{run_id}/publish-facebook")
async def publish_run_to_facebook(
    run_id: str,
    _: str = Depends(require_api_key),
) -> dict[str, Any]:
    if not settings.facebook_page_access_token or not settings.facebook_page_id:
        raise HTTPException(
            status_code=400,
            detail="Facebook not configured. Set FACEBOOK_PAGE_ACCESS_TOKEN and FACEBOOK_PAGE_ID in Settings.",
        )

    state = checkpointer.load(run_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    if not state.github_push_approved:
        raise HTTPException(
            status_code=403,
            detail="GitHub push must be approved before publishing to Facebook.",
        )

    if not state.github_repo_url:
        raise HTTPException(
            status_code=400,
            detail="No GitHub URL on this run. Publish to GitHub first.",
        )

    report_json = state.report_json or {}
    topic_name = report_json.get("topic_name") or state.approved_topic or "AI Research Report"
    one_liner = report_json.get("one_liner") or report_json.get("executive_summary", "")[:200]
    tags = report_json.get("tags") or []

    message = format_report_post(
        topic_name=topic_name,
        one_liner=one_liner,
        eval_score=state.eval_score,
        tags=tags,
        github_url=state.github_repo_url,
    )

    client = FacebookClient()
    result = client.post_link(message=message, link=state.github_repo_url)

    state.agent_logs.append({
        "agent_name": "facebook_publisher",
        "status": "success",
        "output_json": result,
    })
    checkpointer.save(run_id, state)

    return {
        "published": True,
        "post_id": result.get("id"),
        "post_url": result.get("post_url"),
        "message_preview": message[:200],
    }
