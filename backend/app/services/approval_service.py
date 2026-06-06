from typing import Any

from backend.app.graph.checkpoints import checkpointer
from backend.app.graph.state import Trend2POCState


def record_approval(
    run_id: str,
    gate_name: str,
    action: str,
    user_id: str | None = None,
    notes: str = "",
) -> dict[str, Any]:
    from datetime import datetime
    approval = {
        "run_id": run_id,
        "gate_name": gate_name,
        "action": action,
        "user_id": user_id,
        "notes": notes,
        "created_at": datetime.utcnow().isoformat(),
    }
    return approval


def apply_topic_approval(state: Trend2POCState, approved: bool, topic_override: str | None = None) -> Trend2POCState:
    state.topic_approved = approved
    if topic_override:
        state.approved_topic = topic_override
    elif state.selected_topic:
        state.approved_topic = state.selected_topic.get("title", "")
    return state


def apply_report_approval(state: Trend2POCState, approved: bool, revision_notes: str = "") -> Trend2POCState:
    state.report_approved = approved
    state.report_revision_notes = revision_notes
    return state


def apply_github_approval(state: Trend2POCState, approved: bool) -> Trend2POCState:
    state.github_push_approved = approved
    return state
