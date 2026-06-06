import json
import logging
from datetime import datetime
from typing import Any

from backend.app.core.prompt_loader import load_prompt
from backend.app.core.schemas import ResearchReport
from backend.app.integrations.llm_client import LLMClient

logger = logging.getLogger(__name__)


def _build_report_context(
    topic: str,
    research_context: dict[str, Any],
    technical_analysis: dict[str, Any],
    verified_sources: list[dict[str, Any]],
    poc_project: dict[str, Any] | None,
) -> str:
    return f"""TOPIC: {topic}

RESEARCH NOTES:
{json.dumps(research_context, indent=2)[:3000]}

TECHNICAL ANALYSIS:
{json.dumps(technical_analysis, indent=2)[:3000]}

VERIFIED SOURCES ({len(verified_sources)}):
{json.dumps(verified_sources[:12], indent=2)[:2000]}

POC PROJECT:
{json.dumps(poc_project, indent=2)[:2000] if poc_project else 'Not yet generated — use a placeholder POC structure'}
"""


def run_report_writer_agent(
    topic: str,
    research_context: dict[str, Any],
    technical_analysis: dict[str, Any],
    verified_sources: list[dict[str, Any]],
    poc_project: dict[str, Any] | None = None,
    revision_notes: str = "",
    llm: LLMClient | None = None,
) -> dict[str, Any]:
    """Generate the full ResearchReport from verified research context."""
    llm = llm or LLMClient()

    logger.info(f"Report writer agent: writing report for '{topic}'")

    context = _build_report_context(topic, research_context, technical_analysis, verified_sources, poc_project)
    system = load_prompt("report_writer")

    revision_section = ""
    if revision_notes:
        revision_section = f"\n\nREVISION NOTES FROM HUMAN REVIEWER:\n{revision_notes}\nAddress these issues in this revision."

    user = f"""Write a complete ResearchReport JSON for the following topic.
Fill every required field. Use only verified sources. Return valid JSON.

{context}{revision_section}

Current datetime: {datetime.utcnow().isoformat()}Z
"""

    response = llm.complete_json(system=system, user=user, max_tokens=12000)
    report_data = response["parsed"]

    # Inject current timestamp if missing
    if "created_at" not in report_data or not report_data["created_at"]:
        report_data["created_at"] = datetime.utcnow().isoformat() + "Z"

    # Validate against schema
    try:
        report = ResearchReport(**report_data)
        validated = report.model_dump()
    except Exception as e:
        logger.warning(f"Report schema validation warning: {e}")
        validated = report_data

    logger.info("Report writer agent: report generated")

    return {
        "report_json": validated,
        "report_raw": report_data,
        "usage": {
            "model": response["model"],
            "input_tokens": response["input_tokens"],
            "output_tokens": response["output_tokens"],
            "estimated_cost_usd": response["estimated_cost_usd"],
            "latency_ms": response["latency_ms"],
        },
    }
