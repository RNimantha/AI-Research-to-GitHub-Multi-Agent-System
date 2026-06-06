import json
import logging
from typing import Any

from backend.app.core.prompt_loader import load_prompt
from backend.app.integrations.llm_client import LLMClient

logger = logging.getLogger(__name__)

DIMENSION_WEIGHTS: dict[str, float] = {
    "research_completeness": 0.20,
    "technical_accuracy": 0.25,
    "source_quality": 0.15,
    "report_clarity": 0.10,
    "poc_usefulness": 0.10,
    "poc_runnability": 0.10,
    "security": 0.10,
}


def _compute_weighted_score(dimension_scores: dict[str, float]) -> float:
    total = 0.0
    weight_sum = 0.0
    for dim, weight in DIMENSION_WEIGHTS.items():
        score = dimension_scores.get(dim, 0.0)
        total += score * weight
        weight_sum += weight
    return round(total / weight_sum if weight_sum > 0 else 0.0, 2)


def run_evaluator_agent(
    report_json: dict[str, Any],
    generated_files: list[dict[str, str]],
    min_eval_score: float = 7.0,
    llm: LLMClient | None = None,
) -> dict[str, Any]:
    """Score the report and POC using the evaluation rubric."""
    llm = llm or LLMClient()

    logger.info("Evaluator agent: scoring report and POC")

    report_summary = json.dumps(report_json, indent=2)[:4000]
    files_summary = "\n\n".join(
        f"=== {f['path']} ===\n{f['content'][:400]}"
        for f in generated_files[:8]
    )

    system = load_prompt("evaluator")
    user = f"""Evaluate the following research report and POC project.

RESEARCH REPORT (truncated):
{report_summary}

GENERATED FILES (truncated):
{files_summary[:3000]}

Score each dimension from 0 to 10.
Compute overall_score as the weighted average.
Set passed=true if overall_score >= {min_eval_score}.
Return JSON only.
"""

    response = llm.complete_json(system=system, user=user, max_tokens=3000)
    eval_data = response["parsed"]

    dimension_scores = eval_data.get("dimension_scores", {})
    computed_score = _compute_weighted_score(dimension_scores)

    overall_score = eval_data.get("overall_score", computed_score)
    passed = overall_score >= min_eval_score

    # Security score below 5 is an automatic fail per CLAUDE.md
    security_score = dimension_scores.get("security", 10.0)
    if security_score < 5.0:
        passed = False
        eval_data.setdefault("flags", []).append("SECURITY_FAIL: security score below 5.0")

    logger.info(f"Evaluator: score={overall_score:.1f}, passed={passed}")

    return {
        "evaluation": {
            "overall_score": overall_score,
            "dimension_scores": dimension_scores,
            "passed": passed,
            "flags": eval_data.get("flags", []),
            "improvements": eval_data.get("improvements", []),
        },
        "eval_score": overall_score,
        "usage": {
            "model": response["model"],
            "input_tokens": response["input_tokens"],
            "output_tokens": response["output_tokens"],
            "estimated_cost_usd": response["estimated_cost_usd"],
            "latency_ms": response["latency_ms"],
        },
    }
