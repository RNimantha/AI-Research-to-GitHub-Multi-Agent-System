"""
Sync Trend2POCState to Supabase after each checkpoint save.
Silently skips if Supabase is not configured.
Uses in-process counters to avoid re-inserting already-synced logs/sources/files.
"""
import logging
from datetime import datetime, timezone
from typing import Any

from backend.app.graph.state import Trend2POCState

logger = logging.getLogger(__name__)

# Per-run sync counters: run_id -> {"logs": N, "sources": N, "files": N, "report_synced": bool}
_counters: dict[str, dict[str, Any]] = {}


def sync_state_to_supabase(state: Trend2POCState) -> None:
    from backend.app.config import settings

    if not settings.supabase_url or not settings.supabase_service_role_key:
        return

    try:
        from backend.app.integrations.supabase_client import SupabaseClient

        db = SupabaseClient()
        _sync_run(db, state)
        _sync_report(db, state)
        _sync_sources(db, state)
        _sync_logs(db, state)
        _sync_files(db, state)
    except Exception as exc:
        logger.warning(f"Supabase sync skipped for {state.run_id}: {exc}")


def _counters_for(run_id: str) -> dict[str, Any]:
    if run_id not in _counters:
        _counters[run_id] = {"logs": 0, "sources": 0, "files": 0, "report_synced": False}
    return _counters[run_id]


def _sync_run(db: Any, state: Trend2POCState) -> None:
    total_input = sum(u.get("input_tokens", 0) for u in state.model_usage if isinstance(u, dict))
    total_output = sum(u.get("output_tokens", 0) for u in state.model_usage if isinstance(u, dict))
    total_cost = sum(u.get("estimated_cost_usd", 0.0) for u in state.model_usage if isinstance(u, dict))

    run_data: dict[str, Any] = {
        "id": state.run_id,
        "status": state.status.value if hasattr(state.status, "value") else state.status,
        "input_topic": state.input_topic,
        "selected_topic": state.selected_topic,
        "approved_topic": state.approved_topic,
        "eval_score": state.eval_score,
        "github_url": state.github_repo_url,
        "github_folder": state.github_folder_path,
        "input_tokens": total_input,
        "output_tokens": total_output,
        "estimated_cost_usd": total_cost,
        "error_log": state.errors,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    if state.user_id:
        run_data["user_id"] = state.user_id

    db.upsert_run(run_data)


def _sync_report(db: Any, state: Trend2POCState) -> None:
    if not state.report_json:
        return

    c = _counters_for(state.run_id)

    report_data: dict[str, Any] = {
        "run_id": state.run_id,
        "topic_slug": state.report_json.get("topic_slug", ""),
        "topic_name": state.report_json.get("topic_name", ""),
        "one_liner": state.report_json.get("one_liner", ""),
        "tags": state.report_json.get("tags", []),
        "report_json": state.report_json,
        "report_markdown": state.report_markdown,
        "eval_score": state.eval_score,
        "eval_flags": state.eval_flags,
        "github_url": state.github_repo_url,
        "github_folder": state.github_folder_path,
        "status": "published" if state.github_repo_url else ("approved" if state.report_approved else "draft"),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    if state.user_id:
        report_data["user_id"] = state.user_id

    db.upsert_report(run_id=state.run_id, report_data=report_data)
    c["report_synced"] = True


def _sync_sources(db: Any, state: Trend2POCState) -> None:
    c = _counters_for(state.run_id)
    sources = state.verified_sources
    already = c["sources"]
    new_sources = sources[already:]
    if not new_sources:
        return

    rows = []
    for s in new_sources:
        if not isinstance(s, dict):
            continue
        rows.append({
            "run_id": state.run_id,
            "title": s.get("title", ""),
            "url": str(s.get("url", "")),
            "source_type": s.get("source_type", ""),
            "published_date": s.get("published_date"),
            "summary": s.get("summary", ""),
            "credibility_score": s.get("credibility_score"),
            "status": "verified",
        })

    if rows:
        db.save_sources(rows)
        c["sources"] += len(rows)


def _sync_logs(db: Any, state: Trend2POCState) -> None:
    c = _counters_for(state.run_id)
    logs = state.agent_logs
    already = c["logs"]
    new_logs = logs[already:]
    if not new_logs:
        return

    rows = []
    for log in new_logs:
        if not isinstance(log, dict):
            continue
        rows.append({
            "run_id": state.run_id,
            "agent_name": log.get("agent_name", ""),
            "status": log.get("status", "success"),
            "model_name": log.get("model_name"),
            "input_tokens": log.get("input_tokens", 0),
            "output_tokens": log.get("output_tokens", 0),
            "estimated_cost_usd": log.get("estimated_cost_usd", 0.0),
            "latency_ms": log.get("latency_ms"),
            "created_at": log.get("created_at", datetime.now(timezone.utc).isoformat()),
        })

    if rows:
        db.save_agent_logs_batch(rows)
        c["logs"] += len(rows)


def _sync_files(db: Any, state: Trend2POCState) -> None:
    c = _counters_for(state.run_id)
    files = state.generated_files
    already = c["files"]
    new_files = files[already:]
    if not new_files:
        return

    rows = []
    for f in new_files:
        if not isinstance(f, dict):
            continue
        path = f.get("path", "")
        ext = path.rsplit(".", 1)[-1] if "." in path else ""
        rows.append({
            "run_id": state.run_id,
            "file_path": path,
            "file_type": ext,
            "purpose": f.get("purpose", ""),
            "file_content": f.get("content", ""),
        })

    if rows:
        db.save_generated_files(rows)
        c["files"] += len(rows)
