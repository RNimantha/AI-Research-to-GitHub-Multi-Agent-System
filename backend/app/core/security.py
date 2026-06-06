import re

SECRET_PATTERNS = [
    r"sk-[A-Za-z0-9\-]{10,}",          # OpenAI / Anthropic keys (sk-proj-... or sk-...)
    r"github_pat_[A-Za-z0-9_]{10,}",
    r"ghp_[A-Za-z0-9]{10,}",
    r"gho_[A-Za-z0-9]{10,}",
    r"ghu_[A-Za-z0-9]{10,}",
    r"ghs_[A-Za-z0-9]{10,}",
    r"ghr_[A-Za-z0-9]{10,}",
    r"-----BEGIN (RSA |EC )?PRIVATE KEY-----",
    r"AKIA[0-9A-Z]{16}",
    r"eyJ[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+",  # JWT
]

COMPILED_PATTERNS = [re.compile(p) for p in SECRET_PATTERNS]


def scan_content_for_secrets(content: str, filename: str = "") -> list[str]:
    """Return list of violation descriptions found in content."""
    violations = []
    for pattern in COMPILED_PATTERNS:
        if pattern.search(content):
            violations.append(
                f"Potential secret matching pattern '{pattern.pattern}' in {filename or 'content'}"
            )
    return violations


def scan_files_for_secrets(files: list[dict[str, str]]) -> list[str]:
    """Scan a list of file dicts ({path, content}) for secrets."""
    all_violations = []
    for file_info in files:
        path = file_info.get("path", "")
        content = file_info.get("content", "")
        violations = scan_content_for_secrets(content, path)
        all_violations.extend(violations)
    return all_violations


def validate_env_example(content: str) -> list[str]:
    """
    Validate that .env.example has no real values assigned.
    Returns list of violations.
    """
    violations = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            value = value.strip()
            if value and not value.startswith("your-") and len(value) > 8:
                violations.append(
                    f".env.example key '{key.strip()}' appears to have a real value assigned"
                )
    return violations
