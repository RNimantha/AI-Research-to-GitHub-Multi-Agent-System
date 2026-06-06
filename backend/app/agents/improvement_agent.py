import json
import logging
import time
from typing import Any

from backend.app.core.prompt_loader import load_prompt
from backend.app.integrations.llm_client import LLMClient

logger = logging.getLogger(__name__)


def run_improvement_agent(
    report_json: dict[str, Any],
    evaluation: dict[str, Any],
    generated_files: list[dict[str, str]],
    llm: LLMClient,
) -> dict[str, Any]:
    improvements = evaluation.get("improvements", [])
    flags = evaluation.get("flags", [])
    dimension_scores = evaluation.get("dimension_scores", {})

    if not improvements and not flags:
        logger.info("Improvement agent: nothing to improve")
        return {
            "improved_report_json": report_json,
            "improved_files": [],
            "changes_made": [],
            "usage": {},
        }

    system_prompt = load_prompt("improvement")

    weak_dimensions = [
        f"{k}: {v}/10"
        for k, v in dimension_scores.items()
        if isinstance(v, (int, float)) and v < 8
    ]

    user_content = json.dumps({
        "current_report": report_json,
        "eval_score": evaluation.get("overall_score"),
        "dimension_scores": dimension_scores,
        "weak_dimensions": weak_dimensions,
        "improvement_suggestions": improvements,
        "flags": flags,
        "current_files": [
            {"path": f.get("path", ""), "purpose": f.get("purpose", ""), "content": f.get("content", "")[:2000]}
            for f in generated_files[:5]
        ],
    }, default=str)

    start = time.time()
    result = llm.complete(
        system=system_prompt,
        user=f"Apply all improvement suggestions and return the improved report and files.\n\n{user_content}",
        max_tokens=8000,
        json_mode=True,
    )
    latency_ms = int((time.time() - start) * 1000)

    try:
        data = json.loads(result["content"])
    except Exception:
        logger.warning("Improvement agent: failed to parse LLM response, keeping original")
        return {
            "improved_report_json": report_json,
            "improved_files": [],
            "changes_made": ["Parse failed — original kept"],
            "usage": result.get("usage", {}),
        }

    improved_report = data.get("improved_report_json") or report_json
    improved_files = data.get("improved_files") or []
    changes_made = data.get("changes_made") or []

    # Merge improved files back — update matching paths, keep others
    if improved_files:
        file_map = {f["path"]: f for f in generated_files}
        for imp in improved_files:
            file_map[imp["path"]] = imp
        generated_files = list(file_map.values())

    usage = result.get("usage", {})
    usage["latency_ms"] = latency_ms

    logger.info(f"Improvement agent: {len(changes_made)} changes, "
                f"new estimate: {data.get('new_eval_estimate')}")

    return {
        "improved_report_json": improved_report,
        "improved_files": generated_files,
        "changes_made": changes_made,
        "new_eval_estimate": data.get("new_eval_estimate"),
        "usage": usage,
    }
