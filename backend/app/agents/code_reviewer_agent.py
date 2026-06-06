import ast
import logging
from typing import Any

from backend.app.core.prompt_loader import load_prompt
from backend.app.integrations.llm_client import LLMClient

logger = logging.getLogger(__name__)

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
]


def _check_python_syntax(content: str, path: str) -> list[str]:
    """Return list of syntax error strings for a Python file."""
    try:
        ast.parse(content)
        return []
    except SyntaxError as e:
        return [f"Syntax error in {path}: {e}"]


def _scan_secrets(content: str, path: str) -> list[str]:
    issues = []
    for pattern in SECRET_PATTERNS:
        if pattern in content:
            issues.append(f"Potential secret pattern '{pattern}' found in {path}")
    return issues


def _check_required_files(files: list[dict[str, str]]) -> list[str]:
    paths = {f["path"] for f in files}
    required = {"README.md", "requirements.txt", ".env.example", "app/main.py"}
    missing = required - paths
    return [f"Required file missing: {f}" for f in missing]


def run_code_reviewer_agent(
    generated_files: list[dict[str, str]],
    llm: LLMClient | None = None,
) -> dict[str, Any]:
    """Review generated POC code for syntax, security, and completeness."""
    llm = llm or LLMClient()

    logger.info(f"Code reviewer: reviewing {len(generated_files)} files")

    static_issues: list[str] = []

    # Static checks before LLM review
    static_issues.extend(_check_required_files(generated_files))

    for file_info in generated_files:
        path = file_info.get("path", "")
        content = file_info.get("content", "")

        # Secret scan
        static_issues.extend(_scan_secrets(content, path))

        # Python syntax check
        if path.endswith(".py"):
            static_issues.extend(_check_python_syntax(content, path))

    if static_issues:
        logger.warning(f"Code reviewer static checks found {len(static_issues)} issues")
        return {
            "status": "needs_revision",
            "issues": static_issues,
            "warnings": [],
            "usage": None,
        }

    # LLM review for semantic issues
    files_summary = "\n\n".join(
        f"=== {f['path']} ===\n{f['content'][:600]}"
        for f in generated_files
    )

    system = load_prompt("code_reviewer")
    user = f"""Review the following generated POC project files:

{files_summary[:8000]}

Check for: missing dependencies, README accuracy, missing error handling, security issues.
Return JSON with status ("approved" or "needs_revision"), issues list, and warnings list.
"""

    response = llm.complete_json(system=system, user=user, max_tokens=3000)
    review_data = response["parsed"]

    status = review_data.get("status", "needs_revision")
    issues = review_data.get("issues", [])
    warnings = review_data.get("warnings", [])

    logger.info(f"Code reviewer: status={status}, issues={len(issues)}, warnings={len(warnings)}")

    return {
        "status": status,
        "issues": issues,
        "warnings": warnings,
        "usage": {
            "model": response["model"],
            "input_tokens": response["input_tokens"],
            "output_tokens": response["output_tokens"],
            "estimated_cost_usd": response["estimated_cost_usd"],
            "latency_ms": response["latency_ms"],
        },
    }
