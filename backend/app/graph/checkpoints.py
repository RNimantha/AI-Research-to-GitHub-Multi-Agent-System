"""
LangGraph checkpoint support.

For MVP, state is held in memory. Production uses Supabase-backed persistence.
"""
import json
from pathlib import Path
from typing import Any

from backend.app.graph.state import Trend2POCState


class InMemoryCheckpointer:
    """Simple in-memory checkpoint store for development."""

    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}

    def save(self, run_id: str, state: Trend2POCState) -> None:
        self._store[run_id] = state.model_dump()

    def load(self, run_id: str) -> Trend2POCState | None:
        data = self._store.get(run_id)
        if data is None:
            return None
        return Trend2POCState(**data)

    def delete(self, run_id: str) -> None:
        self._store.pop(run_id, None)


class FileCheckpointer:
    """File-based checkpoint store for single-machine persistence."""

    def __init__(self, checkpoint_dir: str = ".checkpoints") -> None:
        self._dir = Path(checkpoint_dir)
        self._dir.mkdir(exist_ok=True)

    def _path(self, run_id: str) -> Path:
        return self._dir / f"{run_id}.json"

    def save(self, run_id: str, state: Trend2POCState) -> None:
        self._path(run_id).write_text(
            json.dumps(state.model_dump(), indent=2, default=str),
            encoding="utf-8",
        )

    def load(self, run_id: str) -> Trend2POCState | None:
        path = self._path(run_id)
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return Trend2POCState(**data)

    def delete(self, run_id: str) -> None:
        path = self._path(run_id)
        if path.exists():
            path.unlink()


# Default checkpointer for the session
checkpointer = FileCheckpointer()
