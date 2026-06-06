#!/usr/bin/env python3
"""
Validate a generated project folder for syntax, structure, and security.

Usage:
    python scripts/validate_generated_project.py generated_projects/2026-06-06_mcp-agent-poc
"""
import ast
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.core.security import scan_content_for_secrets, validate_env_example


REQUIRED_FILES = ["README.md", "requirements.txt", ".env.example"]
OPTIONAL_REQUIRED = ["app/main.py", "tests/test_basic.py"]


def validate_folder(folder_path: str) -> bool:
    folder = Path(folder_path)
    if not folder.exists():
        print(f"ERROR: Folder not found: {folder}")
        return False

    all_ok = True
    files = list(folder.rglob("*"))
    file_names = {str(f.relative_to(folder)) for f in files if f.is_file()}

    print(f"\nValidating: {folder}\n")

    # Check required files
    for req in REQUIRED_FILES:
        if req in file_names:
            print(f"  [OK] {req}")
        else:
            print(f"  [MISSING] {req}")
            all_ok = False

    for req in OPTIONAL_REQUIRED:
        if req in file_names:
            print(f"  [OK] {req}")
        else:
            print(f"  [WARN] Optional file missing: {req}")

    # Python syntax check
    for py_file in folder.rglob("*.py"):
        rel = py_file.relative_to(folder)
        content = py_file.read_text(encoding="utf-8")
        try:
            ast.parse(content)
            print(f"  [SYNTAX OK] {rel}")
        except SyntaxError as e:
            print(f"  [SYNTAX ERROR] {rel}: {e}")
            all_ok = False

    # Secret scan
    for f in folder.rglob("*"):
        if f.is_file() and f.suffix in (".py", ".txt", ".md", ".json", ".yaml", ".yml", ".env"):
            rel = f.relative_to(folder)
            content = f.read_text(encoding="utf-8", errors="ignore")
            violations = scan_content_for_secrets(content, str(rel))
            for v in violations:
                print(f"  [SECRET VIOLATION] {v}")
                all_ok = False

    # .env.example check
    env_example = folder / ".env.example"
    if env_example.exists():
        violations = validate_env_example(env_example.read_text(encoding="utf-8"))
        for v in violations:
            print(f"  [ENV VIOLATION] {v}")
            all_ok = False

    print(f"\n{'PASS' if all_ok else 'FAIL'}: Validation {'succeeded' if all_ok else 'failed'}")
    return all_ok


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_generated_project.py <folder-path>")
        sys.exit(1)
    success = validate_folder(sys.argv[1])
    sys.exit(0 if success else 1)
