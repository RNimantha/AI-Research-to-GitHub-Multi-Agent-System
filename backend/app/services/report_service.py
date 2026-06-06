import json
from pathlib import Path
from typing import Any

from backend.app.core.schemas import ResearchReport


def report_to_markdown(report: dict[str, Any]) -> str:
    r = report
    lines = [
        f"# {r.get('topic_name', 'Research Report')}",
        "",
        f"> {r.get('one_liner', '')}",
        "",
        f"**Tags:** {', '.join(r.get('tags', []))}",
        f"**Created:** {r.get('created_at', '')}",
        f"**Eval Score:** {r.get('eval_score', 'N/A')}",
        "",
        "## Executive Summary",
        "",
        r.get("executive_summary", ""),
        "",
        "## What It Is",
        "",
        r.get("what_it_is", ""),
        "",
        "## Why It Matters Now",
        "",
        r.get("why_it_matters_now", ""),
        "",
        "## Problem It Solves",
        "",
        r.get("problem_it_solves", ""),
        "",
        "## How It Works (Simple)",
        "",
        r.get("how_it_works_simple", ""),
        "",
        "## How It Works (Technical)",
        "",
        r.get("how_it_works_technical", ""),
        "",
        "## Architecture",
        "",
        r.get("architecture", ""),
        "",
        "## Ecosystem Placement",
        "",
        r.get("ecosystem_placement", ""),
        "",
        "## Real-World Implementations",
        "",
        r.get("real_world_implementations", ""),
        "",
        "## Use Cases",
        "",
    ]
    for uc in r.get("use_cases", []):
        lines.append(f"- {uc}")
    lines += [
        "",
        "## Limitations",
        "",
        r.get("limitations", ""),
        "",
        "## Alternatives",
        "",
    ]
    for alt in r.get("alternatives", []):
        lines.append(f"- {alt}")
    lines += [
        "",
        "## Future Outlook",
        "",
        r.get("future_outlook", ""),
        "",
        "## Sources",
        "",
    ]
    for source in r.get("sources", []):
        lines.append(f"- [{source.get('title', '')}]({source.get('url', '')}) — {source.get('summary', '')}")

    return "\n".join(lines)


def save_report_to_disk(report: dict[str, Any], output_dir: str = "generated_projects") -> Path:
    slug = report.get("topic_slug", "report")
    from datetime import datetime
    date = datetime.utcnow().strftime("%Y-%m-%d")
    folder = Path(output_dir) / f"{date}_{slug}"
    folder.mkdir(parents=True, exist_ok=True)

    (folder / "report.json").write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    (folder / "report.md").write_text(report_to_markdown(report), encoding="utf-8")

    return folder
