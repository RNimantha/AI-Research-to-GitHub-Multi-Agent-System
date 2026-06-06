import uuid
from typing import Any

from backend.app.graph.checkpoints import checkpointer
from backend.app.graph.state import RunStatus, Trend2POCState
from backend.app.graph.workflow import Trend2POCWorkflow


def create_run(topic: str | None = None, user_id: str | None = None) -> Trend2POCState:
    workflow = Trend2POCWorkflow()
    run_id = str(uuid.uuid4())
    state = workflow.run(input_topic=topic, user_id=user_id, run_id=run_id)
    checkpointer.save(run_id, state)
    return state


def get_run(run_id: str) -> Trend2POCState | None:
    return checkpointer.load(run_id)


def list_run_ids() -> list[str]:
    """Returns known run IDs from file-based checkpointer."""
    from pathlib import Path
    checkpoint_dir = Path(".checkpoints")
    if not checkpoint_dir.exists():
        return []
    return [p.stem for p in checkpoint_dir.glob("*.json")]
