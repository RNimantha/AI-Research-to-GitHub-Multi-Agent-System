"""
State persistence for Trend2POC runs.

Three storage backends:
  - FileCheckpointer   — disk JSON files (default, local dev)
  - RedisCheckpointer  — Redis (short-term, fast, TTL-based)
  - SupabaseCheckpointer — Supabase research_runs.state_json (long-term)
  - DualCheckpointer   — writes to both Redis + Supabase; reads Redis first

Factory:
  get_checkpointer()   — picks the right backend from config automatically
"""
import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from backend.app.graph.state import Trend2POCState

logger = logging.getLogger(__name__)

_REDIS_KEY_PREFIX = "trend2poc:state:"


# ---------------------------------------------------------------------------
# File (default — always works, no deps)
# ---------------------------------------------------------------------------

class FileCheckpointer:
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

    def list_run_ids(self) -> list[str]:
        return [
            p.stem for p in sorted(
                self._dir.glob("*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
        ]


# ---------------------------------------------------------------------------
# In-memory (tests only)
# ---------------------------------------------------------------------------

class InMemoryCheckpointer:
    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}

    def save(self, run_id: str, state: Trend2POCState) -> None:
        self._store[run_id] = state.model_dump()

    def load(self, run_id: str) -> Trend2POCState | None:
        data = self._store.get(run_id)
        return Trend2POCState(**data) if data else None

    def delete(self, run_id: str) -> None:
        self._store.pop(run_id, None)

    def list_run_ids(self) -> list[str]:
        return list(self._store.keys())


# ---------------------------------------------------------------------------
# Redis (short-term — fast read/write, TTL-based expiry)
# ---------------------------------------------------------------------------

class RedisCheckpointer:
    """
    Stores full state JSON in Redis under trend2poc:state:{run_id}.
    State expires after ttl_seconds (default 24h). Used for hot active runs.
    """

    def __init__(self, redis_url: str, ttl_seconds: int = 86400) -> None:
        import redis as redis_lib
        self._client = redis_lib.from_url(redis_url, decode_responses=True)
        self._ttl = ttl_seconds

    def _key(self, run_id: str) -> str:
        return f"{_REDIS_KEY_PREFIX}{run_id}"

    def save(self, run_id: str, state: Trend2POCState) -> None:
        self._client.setex(
            self._key(run_id),
            self._ttl,
            json.dumps(state.model_dump(), default=str),
        )

    def load(self, run_id: str) -> Trend2POCState | None:
        raw = self._client.get(self._key(run_id))
        if raw is None:
            return None
        return Trend2POCState(**json.loads(raw))

    def delete(self, run_id: str) -> None:
        self._client.delete(self._key(run_id))

    def refresh_ttl(self, run_id: str) -> None:
        """Reset TTL on an active run so it doesn't expire mid-pipeline."""
        self._client.expire(self._key(run_id), self._ttl)

    def list_run_ids(self) -> list[str]:
        prefix = _REDIS_KEY_PREFIX
        return [k[len(prefix):] for k in self._client.keys(f"{prefix}*")]


# ---------------------------------------------------------------------------
# Supabase (long-term — full state + individual columns for queries)
# ---------------------------------------------------------------------------

_RUN_COLUMNS = {
    "status": lambda s: s.status.value if hasattr(s.status, "value") else s.status,
    "input_topic": lambda s: s.input_topic,
    "approved_topic": lambda s: s.approved_topic,
    "eval_score": lambda s: s.eval_score,
    "github_url": lambda s: s.github_repo_url,
    "github_folder": lambda s: s.github_folder_path,
    "error_log": lambda s: s.errors,
    "updated_at": lambda _: datetime.now(UTC).isoformat(),
}


class SupabaseCheckpointer:
    """
    Persists full state JSON to research_runs.state_json.
    Also maps key fields to their own columns so queries (list runs, filter by status) stay fast.

    Requires state_json JSONB column on research_runs — see docs/database.md.
    """

    def __init__(self) -> None:
        from backend.app.integrations.supabase_client import SupabaseClient
        self._db = SupabaseClient()

    def save(self, run_id: str, state: Trend2POCState) -> None:
        payload: dict[str, Any] = {
            "id": run_id,
            "state_json": state.model_dump(mode="json"),
        }
        for col, extractor in _RUN_COLUMNS.items():
            try:
                payload[col] = extractor(state)
            except Exception:
                pass

        # Mark completed_at when run finishes
        if state.status in ("complete", "failed"):
            payload["completed_at"] = datetime.now(UTC).isoformat()

        try:
            self._db.upsert_run(payload)
        except Exception as exc:
            logger.error("SupabaseCheckpointer.save failed for run %s: %s", run_id, exc)
            raise

    def load(self, run_id: str) -> Trend2POCState | None:
        try:
            row = self._db.get_run(run_id)
        except Exception as exc:
            logger.error("SupabaseCheckpointer.load failed for run %s: %s", run_id, exc)
            return None

        if not row:
            return None

        # Prefer full state_json if present; fall back to column-level reconstruction
        state_data = row.get("state_json")
        if state_data:
            return Trend2POCState(**state_data)

        # Minimal reconstruction from individual columns (older rows without state_json)
        return Trend2POCState(
            run_id=run_id,
            status=row.get("status", "pending"),
            input_topic=row.get("input_topic"),
            approved_topic=row.get("approved_topic"),
            eval_score=row.get("eval_score"),
            github_repo_url=row.get("github_url"),
            github_folder_path=row.get("github_folder"),
            errors=row.get("error_log") or [],
        )

    def delete(self, run_id: str) -> None:
        try:
            self._db._client.table("research_runs").delete().eq("id", run_id).execute()
        except Exception as exc:
            logger.error("SupabaseCheckpointer.delete failed for run %s: %s", run_id, exc)

    def list_run_ids(self) -> list[str]:
        try:
            rows = self._db._client.table("research_runs").select("id").order("created_at", desc=True).execute()
            return [r["id"] for r in (rows.data or [])]
        except Exception as exc:
            logger.error("SupabaseCheckpointer.list_run_ids failed: %s", exc)
            return []


# ---------------------------------------------------------------------------
# Dual (Redis hot cache + Supabase persistent store)
# ---------------------------------------------------------------------------

class DualCheckpointer:
    """
    Write path:  save to Redis (fast, short-lived) AND Supabase (durable, long-lived).
    Read path:   try Redis first; on miss, load from Supabase and warm Redis.
    Delete path: remove from both.

    If Redis is unavailable, falls back to Supabase-only silently.
    If Supabase is unavailable, Redis still works (but state won't survive TTL expiry).
    """

    def __init__(self, redis: RedisCheckpointer, supabase: SupabaseCheckpointer) -> None:
        self._redis = redis
        self._supabase = supabase

    def save(self, run_id: str, state: Trend2POCState) -> None:
        # Always persist to Supabase first — it's the source of truth
        self._supabase.save(run_id, state)

        # Write to Redis for fast subsequent reads
        try:
            self._redis.save(run_id, state)
        except Exception as exc:
            logger.warning("DualCheckpointer: Redis write failed for %s (Supabase OK): %s", run_id, exc)

    def load(self, run_id: str) -> Trend2POCState | None:
        # Fast path: Redis
        try:
            state = self._redis.load(run_id)
            if state is not None:
                return state
        except Exception as exc:
            logger.warning("DualCheckpointer: Redis read failed for %s, falling back to Supabase: %s", run_id, exc)

        # Slow path: Supabase
        state = self._supabase.load(run_id)
        if state is not None:
            # Warm the Redis cache for future reads
            try:
                self._redis.save(run_id, state)
            except Exception:
                pass

        return state

    def delete(self, run_id: str) -> None:
        try:
            self._redis.delete(run_id)
        except Exception as exc:
            logger.warning("DualCheckpointer: Redis delete failed for %s: %s", run_id, exc)
        self._supabase.delete(run_id)

    def list_run_ids(self) -> list[str]:
        # Supabase is the source of truth for listing — has ordering and all historical runs
        return self._supabase.list_run_ids()


# ---------------------------------------------------------------------------
# Factory — picks backend automatically from config
# ---------------------------------------------------------------------------

def get_checkpointer() -> Any:
    """
    Returns the best available checkpointer based on environment config.

    Priority:
      Redis + Supabase both configured → DualCheckpointer
      Supabase only                    → SupabaseCheckpointer
      Redis only                       → RedisCheckpointer
      Neither                          → FileCheckpointer (local dev default)
    """
    from backend.app.config import settings

    has_redis = bool(settings.redis_url)
    has_supabase = bool(settings.supabase_url and settings.supabase_service_role_key)

    if has_redis and has_supabase:
        logger.info("Checkpointer: DualCheckpointer (Redis + Supabase)")
        return DualCheckpointer(
            redis=RedisCheckpointer(settings.redis_url, settings.redis_state_ttl_seconds),
            supabase=SupabaseCheckpointer(),
        )

    if has_supabase:
        logger.info("Checkpointer: SupabaseCheckpointer")
        return SupabaseCheckpointer()

    if has_redis:
        logger.info("Checkpointer: RedisCheckpointer")
        return RedisCheckpointer(settings.redis_url, settings.redis_state_ttl_seconds)

    logger.info("Checkpointer: FileCheckpointer (.checkpoints/)")
    return FileCheckpointer()


# Module-level instance — used by all routes and workflow nodes
checkpointer = get_checkpointer()
