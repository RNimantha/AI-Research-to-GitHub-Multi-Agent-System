from backend.app.config import settings
from backend.app.graph.state import Trend2POCState

MAX_CODE_REVISIONS = 3


def route_after_discovery(state: Trend2POCState) -> str:
    """After discovery: always wait for human topic approval."""
    return "await_topic_approval"


def route_after_topic_approval(state: Trend2POCState) -> str:
    if not state.topic_approved:
        return "end_awaiting_topic"
    return "research"


def route_after_source_verification(state: Trend2POCState) -> str:
    score = state.source_confidence_score or 0.0
    if score < settings.source_confidence_threshold:
        return "research"  # Re-research with lower confidence
    return "technical_analysis"


def route_after_report_approval(state: Trend2POCState) -> str:
    if not state.report_approved:
        return "end_awaiting_report"
    return "poc_planner"


def route_after_code_review(state: Trend2POCState) -> str:
    review = state.code_review or {}
    if review.get("status") == "approved":
        return "evaluator"
    if state.code_revision_count >= MAX_CODE_REVISIONS:
        return "evaluator"  # Proceed despite issues after max retries
    return "code_generator"


def route_after_evaluation(state: Trend2POCState) -> str:
    evaluation = state.evaluation or {}
    if not evaluation.get("passed", False):
        return "end_eval_failed"
    return "await_github_approval"


def route_after_github_approval(state: Trend2POCState) -> str:
    if not state.github_push_approved:
        return "end_awaiting_github"
    return "github_publisher"
