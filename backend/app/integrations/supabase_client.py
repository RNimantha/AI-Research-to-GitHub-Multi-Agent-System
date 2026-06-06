from typing import Any

from backend.app.config import settings


class SupabaseClient:
    """Supabase client wrapper using service role key for backend operations."""

    def __init__(self) -> None:
        if not settings.supabase_url or not settings.supabase_service_role_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required")
        from supabase import create_client
        self._client = create_client(settings.supabase_url, settings.supabase_service_role_key)

    # --- Research Runs ---

    def create_run(self, run_data: dict[str, Any]) -> dict[str, Any]:
        result = self._client.table("research_runs").insert(run_data).execute()
        return result.data[0]

    def upsert_run(self, run_data: dict[str, Any]) -> dict[str, Any]:
        result = self._client.table("research_runs").upsert(run_data, on_conflict="id").execute()
        return result.data[0] if result.data else run_data

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        result = (
            self._client.table("research_runs")
            .select("*")
            .eq("id", run_id)
            .single()
            .execute()
        )
        return result.data

    def update_run(self, run_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        result = (
            self._client.table("research_runs")
            .update(updates)
            .eq("id", run_id)
            .execute()
        )
        return result.data[0]

    def list_runs(self, user_id: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        query = self._client.table("research_runs").select("*").limit(limit).order("created_at", desc=True)
        if user_id:
            query = query.eq("user_id", user_id)
        return query.execute().data

    # --- Reports ---

    def save_report(self, report_data: dict[str, Any]) -> dict[str, Any]:
        result = self._client.table("reports").insert(report_data).execute()
        return result.data[0]

    def upsert_report(self, run_id: str, report_data: dict[str, Any]) -> dict[str, Any]:
        existing = (
            self._client.table("reports").select("id").eq("run_id", run_id).execute()
        )
        if existing.data:
            report_id = existing.data[0]["id"]
            result = self._client.table("reports").update(report_data).eq("id", report_id).execute()
        else:
            result = self._client.table("reports").insert(report_data).execute()
        return result.data[0] if result.data else report_data

    def get_report(self, topic_slug: str) -> dict[str, Any] | None:
        result = (
            self._client.table("reports")
            .select("*")
            .eq("topic_slug", topic_slug)
            .single()
            .execute()
        )
        return result.data

    def list_reports(self, user_id: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        query = self._client.table("reports").select("*").limit(limit).order("created_at", desc=True)
        if user_id:
            query = query.eq("user_id", user_id)
        return query.execute().data

    # --- Sources ---

    def save_sources(self, sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
        result = self._client.table("sources").insert(sources).execute()
        return result.data

    # --- Generated Files ---

    def save_generated_files(self, files: list[dict[str, Any]]) -> list[dict[str, Any]]:
        result = self._client.table("generated_files").insert(files).execute()
        return result.data

    # --- Approvals ---

    def record_approval(self, approval_data: dict[str, Any]) -> dict[str, Any]:
        result = self._client.table("approvals").insert(approval_data).execute()
        return result.data[0]

    def get_approvals(self, run_id: str) -> list[dict[str, Any]]:
        result = (
            self._client.table("approvals")
            .select("*")
            .eq("run_id", run_id)
            .execute()
        )
        return result.data

    # --- Agent Logs ---

    def save_agent_log(self, log_data: dict[str, Any]) -> dict[str, Any]:
        result = self._client.table("agent_logs").insert(log_data).execute()
        return result.data[0]

    def save_agent_logs_batch(self, logs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        result = self._client.table("agent_logs").insert(logs).execute()
        return result.data

    def get_agent_logs(self, run_id: str) -> list[dict[str, Any]]:
        result = (
            self._client.table("agent_logs")
            .select("*")
            .eq("run_id", run_id)
            .order("created_at")
            .execute()
        )
        return result.data
