#!/usr/bin/env python3
"""
Standalone evaluation runner for testing evaluator agent.
Loads a report from disk and re-evaluates it.

Usage:
    python evals/eval_runner.py generated_projects/2026-06-06_mcp-agent-poc/report.json
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.agents.evaluator_agent import run_evaluator_agent
from backend.app.config import settings


def run_eval(report_path: str) -> None:
    path = Path(report_path)
    if not path.exists():
        print(f"ERROR: {report_path} not found")
        sys.exit(1)

    report_json = json.loads(path.read_text(encoding="utf-8"))
    folder = path.parent

    generated_files = []
    for f in folder.rglob("*"):
        if f.is_file() and f != path:
            rel = str(f.relative_to(folder))
            generated_files.append({
                "path": rel,
                "purpose": "",
                "content": f.read_text(encoding="utf-8", errors="ignore"),
            })

    result = run_evaluator_agent(
        report_json=report_json,
        generated_files=generated_files,
        min_eval_score=settings.min_eval_score,
    )

    evaluation = result["evaluation"]
    print(f"\nEVALUATION RESULTS")
    print(f"{'='*40}")
    print(f"Overall score: {result['eval_score']:.1f}/10")
    print(f"Passed:        {'YES' if evaluation['passed'] else 'NO'}")
    print()
    for dim, score in evaluation.get("dimension_scores", {}).items():
        print(f"  {dim:<35} {score:.1f}")
    if evaluation.get("flags"):
        print("\nFlags:")
        for flag in evaluation["flags"]:
            print(f"  - {flag}")
    if evaluation.get("improvements"):
        print("\nImprovements:")
        for imp in evaluation["improvements"]:
            print(f"  - {imp}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python evals/eval_runner.py <path-to-report.json>")
        sys.exit(1)
    run_eval(sys.argv[1])
