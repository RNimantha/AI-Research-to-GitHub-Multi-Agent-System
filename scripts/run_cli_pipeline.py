#!/usr/bin/env python3
"""
Full CLI pipeline with HITL gates at every checkpoint.
Supports discovery mode (no topic) or direct topic mode.

Usage:
    python scripts/run_cli_pipeline.py
    python scripts/run_cli_pipeline.py --topic "Structured outputs in LLMs"
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.graph.workflow import Trend2POCWorkflow
from backend.app.graph.state import RunStatus
from backend.app.services.report_service import save_report_to_disk


def prompt_yes_no(prompt: str) -> bool:
    while True:
        answer = input(f"{prompt} [y/n]: ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("Please enter 'y' or 'n'")


def main() -> None:
    parser = argparse.ArgumentParser(description="ARAS CLI Pipeline with HITL gates")
    parser.add_argument("--topic", help="AI topic to research (skips discovery)")
    parser.add_argument("--output-dir", default="generated_projects")
    args = parser.parse_args()

    workflow = Trend2POCWorkflow()

    print("\n=== ARAS — AI Research Automation System ===\n")

    # Phase 1: Run until topic approval
    state = workflow.run(input_topic=args.topic)

    if state.status == RunStatus.FAILED:
        print(f"Pipeline failed: {state.errors}")
        sys.exit(1)

    # HITL Gate 1: Topic Approval
    if not args.topic:
        print("\n--- HITL GATE 1: TOPIC APPROVAL ---")
        if state.selected_topic:
            t = state.selected_topic
            print(f"Selected topic: {t.get('title', 'Unknown')}")
            print(f"Reason: {t.get('reason', '')}")
            print(f"Difficulty: {t.get('difficulty', '')}")
            print(f"Expected POC: {t.get('expected_poc', '')}")

        if prompt_yes_no("Approve this topic?"):
            state.topic_approved = True
            state.approved_topic = (state.selected_topic or {}).get("title", "")
        else:
            custom = input("Enter a custom topic (or leave blank to exit): ").strip()
            if not custom:
                print("Exiting.")
                sys.exit(0)
            state.topic_approved = True
            state.approved_topic = custom

        # Resume research
        from backend.app.graph.workflow import (
            node_research, node_verify_sources, node_technical_analysis, node_write_report
        )
        from backend.app.config import settings

        print("\n[Researching...]")
        state = node_research(state, workflow.llm, workflow.search)
        state = node_verify_sources(state, workflow.llm)
        if (state.source_confidence_score or 0) < settings.source_confidence_threshold:
            print(f"Low source confidence ({state.source_confidence_score:.2f}). Re-searching...")
            state = node_research(state, workflow.llm, workflow.search)
            state = node_verify_sources(state, workflow.llm)
        print("[Analyzing...]")
        state = node_technical_analysis(state, workflow.llm)
        print("[Writing report...]")
        state = node_write_report(state, workflow.llm)

    # HITL Gate 2: Report Approval
    print("\n--- HITL GATE 2: REPORT REVIEW ---")
    report = state.report_json or {}
    print(f"Topic: {report.get('topic_name', 'Unknown')}")
    print(f"Summary: {report.get('executive_summary', '')[:300]}...")
    print(f"Sources: {len(state.verified_sources)}")

    if prompt_yes_no("Approve this report?"):
        state.report_approved = True
        state.report_revision_notes = ""
    else:
        notes = input("Revision notes (what should be improved): ").strip()
        state.report_revision_notes = notes
        state.report_approved = False
        print("Report not approved. Revise and re-run.")
        sys.exit(0)

    # Resume: POC + evaluation
    print("\n[Planning POC...]")
    state = workflow.resume_after_report_approval(state)

    if state.status == RunStatus.FAILED:
        print(f"Pipeline failed: {state.errors}")
        sys.exit(1)

    # HITL Gate 3: POC Review
    print("\n--- HITL GATE 3: POC REVIEW ---")
    code_review = state.code_review or {}
    print(f"Code review status: {code_review.get('status', 'unknown')}")
    if code_review.get("issues"):
        print("Issues:")
        for issue in code_review["issues"]:
            print(f"  - {issue}")
    if code_review.get("warnings"):
        print("Warnings:")
        for w in code_review["warnings"]:
            print(f"  - {w}")

    eval_result = state.evaluation or {}
    print(f"\nEvaluation score: {state.eval_score:.1f}/10")
    print(f"Passed: {'YES' if eval_result.get('passed') else 'NO'}")

    if not eval_result.get("passed"):
        print("Evaluation did not pass. Cannot proceed to GitHub.")
        sys.exit(1)

    if prompt_yes_no("Approve POC for publishing?"):
        state.poc_approved = True
    else:
        print("POC not approved.")
        sys.exit(0)

    # HITL Gate 4: GitHub Push
    print("\n--- HITL GATE 4: GITHUB PUBLISH APPROVAL ---")
    topic_slug = report.get("topic_slug", "unknown")
    print(f"This will publish '{topic_slug}' to GitHub.")

    if prompt_yes_no("Approve GitHub publish?"):
        state.github_push_approved = True
        print("\n[Publishing to GitHub...]")
        state = workflow.resume_after_github_approval(state)
        print(f"\nPublished! GitHub URL: {state.github_repo_url}")
    else:
        print("GitHub publish held. Run saved locally.")

    # Save to disk regardless
    if state.report_json:
        output_path = save_report_to_disk(state.report_json, output_dir=args.output_dir)
        for file_info in state.generated_files:
            fp = output_path / file_info.get("path", "unknown.txt")
            fp.parent.mkdir(parents=True, exist_ok=True)
            fp.write_text(file_info.get("content", ""), encoding="utf-8")
        print(f"\nLocal output: {output_path}")


if __name__ == "__main__":
    main()
