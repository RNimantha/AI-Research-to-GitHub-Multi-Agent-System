import logging
from datetime import datetime
from typing import Any

from backend.app.config import settings
from backend.app.integrations.github_client import GitHubClient

logger = logging.getLogger(__name__)


def _build_folder_path(topic_slug: str) -> str:
    date_prefix = datetime.utcnow().strftime("%Y-%m-%d")
    slug = topic_slug[:50] if len(topic_slug) > 50 else topic_slug
    return f"reports/{date_prefix}_{slug}"


def run_github_publisher_agent(
    topic_slug: str,
    generated_files: list[dict[str, str]],
    eval_score: float,
    github_push_approved: bool,
    min_eval_score: float | None = None,
) -> dict[str, Any]:
    """
    Publish approved research artifacts to GitHub.

    github_push_approved must be True — enforces HITL gate.
    eval_score must be >= min_eval_score — enforces quality gate.
    """
    min_score = min_eval_score or settings.min_eval_score

    if not github_push_approved:
        raise PermissionError(
            "GitHub publish blocked: github_push_approved is False. "
            "Human approval at HITL Gate 4 is required."
        )

    if eval_score < min_score:
        raise ValueError(
            f"GitHub publish blocked: eval_score {eval_score:.1f} < min {min_score}. "
            "Report must pass evaluation before publishing."
        )

    logger.info(f"GitHub publisher: publishing '{topic_slug}' (score={eval_score:.1f})")

    client = GitHubClient()
    folder_path = _build_folder_path(topic_slug)

    result = client.publish_folder(
        folder_path=folder_path,
        files=generated_files,
        commit_prefix="feat(trend2poc)",
        approved=github_push_approved,
    )

    logger.info(f"GitHub publisher: published to {result['folder_url']}")

    return {
        "github_folder_path": folder_path,
        "github_repo_url": result["folder_url"],
        "published_files": result["files"],
    }
