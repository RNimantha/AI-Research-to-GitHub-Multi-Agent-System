from typing import Any

from backend.app.config import settings


SECRET_PATTERNS = [
    "sk-",
    "github_pat_",
    "ghp_",
    "gho_",
    "ghu_",
    "ghs_",
    "ghr_",
    "BEGIN PRIVATE KEY",
    "BEGIN RSA PRIVATE KEY",
    "AKIA",
    "AWS_SECRET_ACCESS_KEY",
]


class GitHubClient:
    def __init__(self) -> None:
        if not settings.github_token:
            raise ValueError("GITHUB_TOKEN is required for GitHub operations")
        from github import Github  # lazy import — PyGithub installed separately
        self.client = Github(settings.github_token)
        self.repo = self.client.get_repo(
            f"{settings.github_repo_owner}/{settings.github_repo_name}"
        )

    def scan_for_secrets(self, content: str) -> list[str]:
        """Return list of detected secret patterns in content."""
        found = []
        for pattern in SECRET_PATTERNS:
            if pattern in content:
                found.append(f"Detected secret pattern: '{pattern}'")
        return found

    def create_or_update_file(self, path: str, content: str, message: str) -> str:
        """Create or update a file in the repository. Returns the file URL."""
        from github import GithubException

        violations = self.scan_for_secrets(content)
        if violations:
            raise ValueError(f"Secret scan failed before push: {violations}")

        try:
            existing = self.repo.get_contents(path, ref=settings.github_default_branch)
            if isinstance(existing, list):
                raise ValueError(f"Path {path} is a directory")
            result = self.repo.update_file(
                path=path,
                message=message,
                content=content,
                sha=existing.sha,  # type: ignore[union-attr]
                branch=settings.github_default_branch,
            )
        except GithubException as exc:
            if exc.status == 404:
                result = self.repo.create_file(
                    path=path,
                    message=message,
                    content=content,
                    branch=settings.github_default_branch,
                )
            else:
                raise

        return result["content"].html_url

    def publish_folder(
        self,
        folder_path: str,
        files: list[dict[str, str]],
        commit_prefix: str = "feat(trend2poc)",
        approved: bool = False,
    ) -> dict[str, Any]:
        """
        Publish a set of files under folder_path in the GitHub repo.

        approved must be True — this is the HITL gate enforcement.
        """
        if not approved:
            raise PermissionError(
                "GitHub publish requires explicit human approval. Set approved=True after HITL gate."
            )

        published_urls = []
        for file_info in files:
            path = f"{folder_path}/{file_info['path']}"
            content = file_info["content"]
            url = self.create_or_update_file(
                path=path,
                content=content,
                message=f"{commit_prefix}: add {file_info['path']}",
            )
            published_urls.append({"path": path, "url": url})

        repo_url = (
            f"https://github.com/{settings.github_repo_owner}/{settings.github_repo_name}"
            f"/tree/{settings.github_default_branch}/{folder_path}"
        )
        return {"folder_url": repo_url, "files": published_urls}

    def test_connection(self) -> dict[str, Any]:
        """Verify GitHub token, repo access, and write permission."""
        import base64
        from github import GithubException
        import httpx

        repo = self.repo

        # Check token scopes via direct HTTP call
        try:
            r = httpx.get(
                "https://api.github.com/user",
                headers={"Authorization": f"token {settings.github_token}"},
                timeout=10,
            )
            scopes = r.headers.get("X-OAuth-Scopes", "none returned")
            token_type = "fine-grained" if not scopes or scopes == "none returned" else "classic"
        except Exception as exc:
            scopes = f"error: {exc}"
            token_type = "unknown"

        # Try a write test: create then delete a sentinel file
        write_ok = False
        write_error = ""
        test_path = ".trend2poc-write-test"
        try:
            test_content = base64.b64encode(b"write test").decode()
            try:
                existing = repo.get_contents(test_path)
                repo.delete_file(test_path, "chore: remove write test", existing.sha)
            except GithubException:
                pass
            result = repo.create_file(test_path, "chore: write test", "write test",
                                      branch=settings.github_default_branch)
            repo.delete_file(test_path, "chore: remove write test",
                             result["content"].sha, branch=settings.github_default_branch)
            write_ok = True
        except GithubException as exc:
            write_error = str(exc)

        return {
            "connected": True,
            "repo": repo.full_name,
            "default_branch": repo.default_branch,
            "private": repo.private,
            "token_type": token_type,
            "token_scopes": scopes,
            "token_prefix": settings.github_token[:10] + "…" if settings.github_token else "empty",
            "write_access": write_ok,
            "write_error": write_error or None,
        }
