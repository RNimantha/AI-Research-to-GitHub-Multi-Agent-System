"""Tests for GitHub client secret scanning (no PyGithub dependency required)."""
import pytest

from backend.app.integrations.github_client import SECRET_PATTERNS


def test_secret_patterns_list_not_empty():
    assert len(SECRET_PATTERNS) > 0


def test_secret_pattern_coverage():
    expected_patterns = ["sk-", "ghp_", "github_pat_", "BEGIN PRIVATE KEY", "AKIA"]
    for p in expected_patterns:
        assert p in SECRET_PATTERNS, f"Pattern '{p}' missing from SECRET_PATTERNS"


def _scan(content: str) -> list[str]:
    """Manual scan using SECRET_PATTERNS (no PyGithub needed)."""
    found = []
    for pattern in SECRET_PATTERNS:
        if pattern in content:
            found.append(f"Detected: '{pattern}'")
    return found


def test_scan_clean_content():
    assert _scan("api_key = os.getenv('API_KEY')") == []


def test_scan_finds_github_pat():
    violations = _scan("token = 'ghp_abc123xyz456def789'")
    assert len(violations) > 0


def test_scan_finds_openai_key():
    violations = _scan("key = 'sk-projabcdefghi'")
    assert len(violations) > 0


def test_scan_finds_private_key():
    violations = _scan("-----BEGIN PRIVATE KEY-----")
    assert len(violations) > 0


def test_scan_clean_env_reference():
    assert _scan("ANTHROPIC_API_KEY = os.environ['ANTHROPIC_API_KEY']") == []
