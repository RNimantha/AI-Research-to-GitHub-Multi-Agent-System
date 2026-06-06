from typing import Any

from backend.app.core.security import scan_files_for_secrets
from backend.app.integrations.github_client import GitHubClient


def validate_pre_publish(
    generated_files: list[dict[str, str]],
    eval_score: float,
    min_eval_score: float,
    github_push_approved: bool,
) -> list[str]:
    """Run all pre-publish checks. Return list of blocking issues."""
    issues = []

    if not github_push_approved:
        issues.append("Human approval not granted")

    if eval_score < min_eval_score:
        issues.append(f"Eval score {eval_score:.1f} < min {min_eval_score}")

    if len(generated_files) == 0:
        issues.append("No generated files to publish")

    required_filenames = {"README.md", "requirements.txt", ".env.example"}
    file_paths = {f.get("path", "") for f in generated_files}
    missing = required_filenames - file_paths
    if missing:
        issues.append(f"Required files missing: {missing}")

    secret_violations = scan_files_for_secrets(generated_files)
    issues.extend(secret_violations)

    return issues


def publish_to_github(
    topic_slug: str,
    generated_files: list[dict[str, str]],
    eval_score: float,
    min_eval_score: float,
    github_push_approved: bool,
) -> dict[str, Any]:
    issues = validate_pre_publish(generated_files, eval_score, min_eval_score, github_push_approved)
    if issues:
        raise ValueError(f"Pre-publish validation failed: {issues}")

    client = GitHubClient()
    from datetime import datetime
    folder_path = f"reports/{datetime.utcnow().strftime('%Y-%m-%d')}_{topic_slug}"

    return client.publish_folder(
        folder_path=folder_path,
        files=generated_files,
        approved=github_push_approved,
    )
