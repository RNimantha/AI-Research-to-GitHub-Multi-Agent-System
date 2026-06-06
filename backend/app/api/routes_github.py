from pathlib import Path
from typing import Any

from dotenv import set_key
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.app.api.deps import require_api_key
from backend.app.config import settings
from backend.app.graph.checkpoints import checkpointer
from backend.app.integrations.github_client import GitHubClient

router = APIRouter(tags=["github"])

ENV_FILE = Path(".env")


class GithubSettingsRequest(BaseModel):
    github_token: str = ""
    github_repo_owner: str = ""
    github_repo_name: str = ""
    github_default_branch: str = "main"


@router.get("/settings/github")
async def get_github_settings(_: str = Depends(require_api_key)) -> dict[str, Any]:
    token = settings.github_token
    return {
        "github_token_set": bool(token),
        "github_token_preview": f"{token[:12]}…" if len(token) > 12 else ("set" if token else ""),
        "github_repo_owner": settings.github_repo_owner,
        "github_repo_name": settings.github_repo_name,
        "github_default_branch": settings.github_default_branch,
    }


@router.post("/settings/github")
async def save_github_settings(
    body: GithubSettingsRequest,
    _: str = Depends(require_api_key),
) -> dict[str, Any]:
    if not ENV_FILE.exists():
        ENV_FILE.write_text("")

    if body.github_token:
        set_key(str(ENV_FILE), "GITHUB_TOKEN", body.github_token)
        settings.github_token = body.github_token
    if body.github_repo_owner:
        set_key(str(ENV_FILE), "GITHUB_REPO_OWNER", body.github_repo_owner)
        settings.github_repo_owner = body.github_repo_owner
    if body.github_repo_name:
        set_key(str(ENV_FILE), "GITHUB_REPO_NAME", body.github_repo_name)
        settings.github_repo_name = body.github_repo_name
    if body.github_default_branch:
        set_key(str(ENV_FILE), "GITHUB_DEFAULT_BRANCH", body.github_default_branch)
        settings.github_default_branch = body.github_default_branch

    return {"saved": True, "github_token_set": bool(settings.github_token)}


@router.post("/github/test-connection")
async def test_github_connection(_: str = Depends(require_api_key)) -> dict[str, Any]:
    if not settings.github_token:
        raise HTTPException(status_code=400, detail="GITHUB_TOKEN not configured")
    client = GitHubClient()
    return client.test_connection()


@router.post("/github/publish/{run_id}")
async def publish_run_to_github(
    run_id: str,
    _: str = Depends(require_api_key),
) -> dict[str, Any]:
    state = checkpointer.load(run_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    if not state.github_push_approved:
        raise HTTPException(
            status_code=403,
            detail="GitHub push not approved. Call /approve-github-push first.",
        )

    if not state.evaluation or not state.evaluation.get("passed"):
        raise HTTPException(
            status_code=400,
            detail="Run has not passed evaluation. Cannot publish.",
        )

    from backend.app.agents.github_publisher_agent import run_github_publisher_agent

    topic_slug = (state.report_json or {}).get("topic_slug", "unknown-topic")
    result = run_github_publisher_agent(
        topic_slug=topic_slug,
        generated_files=state.generated_files,
        eval_score=state.eval_score or 0.0,
        github_push_approved=state.github_push_approved,
        min_eval_score=settings.min_eval_score,
    )

    state.github_folder_path = result["github_folder_path"]
    state.github_repo_url = result["github_repo_url"]
    checkpointer.save(run_id, state)

    return result
