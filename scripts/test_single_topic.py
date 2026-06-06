#!/usr/bin/env python3
"""
CLI script: research one topic end-to-end and generate a report.

Usage:
    python scripts/test_single_topic.py --topic "MCP for AI Agents"
    python scripts/test_single_topic.py --topic "LangGraph multi-agent workflows"
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.agents.evaluator_agent import run_evaluator_agent
from backend.app.agents.poc_code_generator_agent import run_poc_code_generator_agent
from backend.app.agents.poc_planner_agent import run_poc_planner_agent
from backend.app.agents.report_writer_agent import run_report_writer_agent
from backend.app.agents.research_agent import run_research_agent
from backend.app.agents.source_verification_agent import run_source_verification_agent
from backend.app.agents.technical_analysis_agent import run_technical_analysis_agent
from backend.app.config import settings
from backend.app.services.report_service import save_report_to_disk


def run_pipeline(topic: str, output_dir: str = "generated_projects") -> None:
    print(f"\n{'='*60}")
    print(f"TREND2POC — Single Topic Pipeline")
    print(f"Topic: {topic}")
    print(f"{'='*60}\n")

    # Step 1: Research
    print("[1/7] Researching topic...")
    research = run_research_agent(topic=topic, max_sources=settings.max_sources_per_topic)
    raw_sources = research["raw_sources"]
    research_context = research["research_context"]
    print(f"      Found {len(raw_sources)} raw sources")

    # Step 2: Source verification
    print("[2/7] Verifying sources...")
    verification = run_source_verification_agent(
        topic=topic,
        raw_sources=raw_sources,
        research_context=research_context,
    )
    verified_sources = verification["verified_sources"]
    confidence = verification["confidence_score"]
    print(f"      Verified: {len(verified_sources)} sources, confidence={confidence:.2f}")

    if confidence < settings.source_confidence_threshold:
        print(f"      WARNING: Source confidence {confidence:.2f} below threshold {settings.source_confidence_threshold}")
        print("      Consider running with a more specific topic.")

    # Step 3: Technical analysis
    print("[3/7] Running technical analysis...")
    analysis = run_technical_analysis_agent(
        topic=topic,
        research_context=research_context,
        verified_sources=verified_sources,
    )
    technical_analysis = analysis["technical_analysis"]
    print("      Technical analysis complete")

    # Step 4: Write report
    print("[4/7] Writing research report...")
    report_result = run_report_writer_agent(
        topic=topic,
        research_context=research_context,
        technical_analysis=technical_analysis,
        verified_sources=verified_sources,
    )
    report_json = report_result["report_json"]
    print(f"      Report generated: {report_json.get('topic_slug', 'unknown')}")

    # Step 5: Plan POC
    print("[5/7] Planning POC project...")
    poc_plan_result = run_poc_planner_agent(
        topic=topic,
        technical_analysis=technical_analysis,
        research_context=research_context,
    )
    poc_plan = poc_plan_result["poc_plan"]
    print(f"      POC plan: {poc_plan.get('project_name', 'unknown')}")

    # Step 6: Generate code
    print("[6/7] Generating POC code...")
    code_result = run_poc_code_generator_agent(topic=topic, poc_plan=poc_plan)
    generated_files = code_result["generated_files"]
    print(f"      Generated {len(generated_files)} files")

    # Inject POC into report
    report_json["poc"] = {
        "project_name": poc_plan.get("project_name", "poc"),
        "goal": poc_plan.get("goal", ""),
        "dependencies": poc_plan.get("dependencies", []),
        "files": [{"path": f["path"], "purpose": f["purpose"], "content": f["content"]} for f in generated_files],
        "run_instructions": poc_plan.get("run_instructions", ""),
        "limitations": poc_plan.get("limitations", []),
    }

    # Step 7: Evaluate
    print("[7/7] Evaluating report and POC...")
    eval_result = run_evaluator_agent(
        report_json=report_json,
        generated_files=generated_files,
        min_eval_score=settings.min_eval_score,
    )
    evaluation = eval_result["evaluation"]
    score = eval_result["eval_score"]
    passed = evaluation["passed"]

    print(f"\n{'='*60}")
    print(f"EVALUATION RESULTS")
    print(f"{'='*60}")
    print(f"Overall score:  {score:.1f}/10")
    print(f"Passed:         {'YES' if passed else 'NO'}")
    for dim, dim_score in evaluation.get("dimension_scores", {}).items():
        print(f"  {dim:<30} {dim_score:.1f}")
    if evaluation.get("flags"):
        print("\nFlags:")
        for flag in evaluation["flags"]:
            print(f"  - {flag}")
    if evaluation.get("improvements"):
        print("\nSuggested improvements:")
        for improvement in evaluation["improvements"]:
            print(f"  - {improvement}")

    # Save to disk
    report_json["eval_score"] = score
    report_json["eval_flags"] = evaluation.get("flags", [])

    output_path = save_report_to_disk(report_json, output_dir=output_dir)

    # Save generated files
    for file_info in generated_files:
        file_path = output_path / file_info["path"]
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(file_info["content"], encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"Output saved to: {output_path}")
    print(f"{'='*60}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run ARAS pipeline for a single topic")
    parser.add_argument("--topic", required=True, help="AI topic to research")
    parser.add_argument("--output-dir", default="generated_projects", help="Output directory")
    args = parser.parse_args()

    run_pipeline(topic=args.topic, output_dir=args.output_dir)


if __name__ == "__main__":
    main()
