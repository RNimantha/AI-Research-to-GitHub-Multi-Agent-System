import json
import logging
from typing import Any

from backend.app.core.prompt_loader import load_prompt
from backend.app.integrations.llm_client import LLMClient

logger = logging.getLogger(__name__)

MAX_CRITIQUE_ROUNDS = 2


def _files_to_text(files: list[dict[str, Any]]) -> str:
    """Render generated files as readable text for the critique prompt."""
    parts = []
    for f in files:
        parts.append(f"### {f.get('path', 'unknown')}\n```\n{f.get('content', '')}\n```")
    return "\n\n".join(parts)


def _run_critique(
    files: list[dict[str, Any]],
    topic: str,
    llm: LLMClient,
) -> dict[str, Any]:
    """Ask the LLM to critique its own generated files. Returns parsed critique JSON."""
    system = load_prompt("code_critique")
    user = f"""Topic: {topic}

Generated files to review:

{_files_to_text(files)}
"""
    response = llm.complete_json(system=system, user=user, max_tokens=4000)
    return {"parsed": response["parsed"], "usage": response}


def _run_fix(
    files: list[dict[str, Any]],
    issues: list[dict[str, Any]],
    topic: str,
    poc_plan: dict[str, Any],
    llm: LLMClient,
) -> dict[str, Any]:
    """Ask the LLM to fix the errors found in the critique."""
    system = load_prompt("code_fix")

    issues_text = "\n".join(
        f"- [{i['severity'].upper()}] {i['file']} ({i.get('line_hint', '')}): "
        f"{i['description']} → Fix: {i['fix']}"
        for i in issues
    )

    user = f"""Topic: {topic}

POC Plan:
{json.dumps(poc_plan, indent=2)}

Errors found in your generated code:
{issues_text}

Original files:
{_files_to_text(files)}

Return the complete corrected file set as JSON.
"""
    response = llm.complete_json(system=system, user=user, max_tokens=12000)
    return {"parsed": response["parsed"], "usage": response}


def run_poc_code_generator_agent(
    topic: str,
    poc_plan: dict[str, Any],
    revision_issues: list[str] | None = None,
    llm: LLMClient | None = None,
) -> dict[str, Any]:
    """Generate POC files then self-critique and fix up to MAX_CRITIQUE_ROUNDS times."""
    llm = llm or LLMClient()

    logger.info(f"Code generator agent: generating code for '{topic}'")

    system = load_prompt("code_generator")

    revision_section = ""
    if revision_issues:
        revision_section = (
            "PREVIOUS REVIEW ISSUES TO FIX:\n"
            + "\n".join(f"- {issue}" for issue in revision_issues)
            + "\n\nAddress every issue above in this generation.\n"
        )

    user = f"""Generate all files for this POC project:

TOPIC: {topic}

POC PLAN:
{json.dumps(poc_plan, indent=2)}

{revision_section}
Generate complete, working code for every file in the plan.
Return JSON with a "files" array where each element has "path", "purpose", and "content".
"""

    # --- Initial generation ---
    gen_response = llm.complete_json(system=system, user=user, max_tokens=12000)
    files_data = gen_response["parsed"]
    generated_files: list[dict[str, Any]] = files_data.get("files", [])

    total_input_tokens = gen_response["input_tokens"]
    total_output_tokens = gen_response["output_tokens"]
    total_cost = gen_response["estimated_cost_usd"]
    total_latency = gen_response["latency_ms"]

    logger.info(f"Code generator: generated {len(generated_files)} files")

    # --- Self-critique loop ---
    critique_rounds = 0
    critique_log: list[dict[str, Any]] = []

    for round_num in range(1, MAX_CRITIQUE_ROUNDS + 1):
        logger.info(f"Code generator: self-critique round {round_num}")

        critique_result = _run_critique(generated_files, topic, llm)
        critique = critique_result["parsed"]
        cu = critique_result["usage"]

        total_input_tokens += cu["input_tokens"]
        total_output_tokens += cu["output_tokens"]
        total_cost += cu["estimated_cost_usd"]
        total_latency += cu["latency_ms"]

        error_issues = [i for i in critique.get("issues", []) if i.get("severity") == "error"]

        critique_log.append({
            "round": round_num,
            "has_issues": critique.get("has_issues", False),
            "error_count": len(error_issues),
            "assessment": critique.get("overall_assessment", ""),
        })

        if not critique.get("has_issues") or not error_issues:
            logger.info(f"Code generator: critique round {round_num} — no errors, done")
            break

        logger.info(f"Code generator: critique round {round_num} found {len(error_issues)} errors — fixing")

        fix_result = _run_fix(generated_files, error_issues, topic, poc_plan, llm)
        fix_data = fix_result["parsed"]
        fu = fix_result["usage"]

        total_input_tokens += fu["input_tokens"]
        total_output_tokens += fu["output_tokens"]
        total_cost += fu["estimated_cost_usd"]
        total_latency += fu["latency_ms"]

        fixed_files = fix_data.get("files", [])
        if fixed_files:
            generated_files = fixed_files
            logger.info(f"Code generator: applied fixes — now {len(generated_files)} files")

        critique_rounds += 1

    logger.info(
        f"Code generator: done — {len(generated_files)} files, "
        f"{critique_rounds} fix round(s), "
        f"${total_cost:.4f}"
    )

    return {
        "generated_files": generated_files,
        "critique_log": critique_log,
        "critique_rounds": critique_rounds,
        "usage": {
            "model": gen_response["model"],
            "input_tokens": total_input_tokens,
            "output_tokens": total_output_tokens,
            "estimated_cost_usd": total_cost,
            "latency_ms": total_latency,
        },
    }
