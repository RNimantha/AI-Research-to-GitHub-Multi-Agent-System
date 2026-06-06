"""Tests for security scanning utilities."""
import pytest

from backend.app.core.security import (
    scan_content_for_secrets,
    scan_files_for_secrets,
    validate_env_example,
)


def test_detects_openai_key():
    content = "api_key = 'sk-proj-abc123xyz456def789ghi012'"
    violations = scan_content_for_secrets(content, "config.py")
    assert len(violations) > 0


def test_detects_github_pat():
    content = "token = 'ghp_abcdefghijklmnopqrstuvwxyz123456'"
    violations = scan_content_for_secrets(content)
    assert len(violations) > 0


def test_clean_content_passes():
    content = "api_key = os.environ['ANTHROPIC_API_KEY']"
    violations = scan_content_for_secrets(content)
    assert len(violations) == 0


def test_scan_files_for_secrets():
    files = [
        {"path": "app/config.py", "content": "key = os.getenv('API_KEY')"},
        {"path": "app/main.py", "content": "print('hello')"},
    ]
    violations = scan_files_for_secrets(files)
    assert len(violations) == 0


def test_scan_files_finds_secret():
    files = [
        {"path": "app/config.py", "content": "key = 'ghp_abcdefghijklmnopqrstuvwxyz1234'"},
    ]
    violations = scan_files_for_secrets(files)
    assert len(violations) > 0


def test_validate_env_example_clean():
    content = "ANTHROPIC_API_KEY=\nGITHUB_TOKEN=\nSUPABASE_URL="
    violations = validate_env_example(content)
    assert len(violations) == 0


def test_validate_env_example_with_real_value():
    content = "ANTHROPIC_API_KEY=sk-this-looks-real-but-isnt-12345678"
    violations = validate_env_example(content)
    assert len(violations) > 0


def test_detects_private_key():
    content = "-----BEGIN RSA PRIVATE KEY-----\nMIIEpA..."
    violations = scan_content_for_secrets(content)
    assert len(violations) > 0
