from pathlib import Path
from typing import Any

from dotenv import set_key
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.app.api.deps import require_api_key
from backend.app.config import settings

router = APIRouter(tags=["settings"])

ENV_FILE = Path(".env")


def _ensure_env() -> None:
    if not ENV_FILE.exists():
        ENV_FILE.write_text("")


class SupabaseSettingsRequest(BaseModel):
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""


@router.get("/settings/supabase")
async def get_supabase_settings(_: str = Depends(require_api_key)) -> dict[str, Any]:
    srk = settings.supabase_service_role_key
    anon = settings.supabase_anon_key
    return {
        "supabase_url": settings.supabase_url,
        "supabase_url_set": bool(settings.supabase_url),
        "supabase_anon_key_set": bool(anon),
        "supabase_anon_key_preview": f"{anon[:16]}…" if len(anon) > 16 else ("set" if anon else ""),
        "supabase_service_role_key_set": bool(srk),
        "supabase_service_role_key_preview": f"{srk[:16]}…" if len(srk) > 16 else ("set" if srk else ""),
    }


@router.post("/settings/supabase")
async def save_supabase_settings(
    body: SupabaseSettingsRequest,
    _: str = Depends(require_api_key),
) -> dict[str, Any]:
    _ensure_env()

    if body.supabase_url:
        set_key(str(ENV_FILE), "SUPABASE_URL", body.supabase_url)
        settings.supabase_url = body.supabase_url
    if body.supabase_anon_key:
        set_key(str(ENV_FILE), "SUPABASE_ANON_KEY", body.supabase_anon_key)
        settings.supabase_anon_key = body.supabase_anon_key
    if body.supabase_service_role_key:
        set_key(str(ENV_FILE), "SUPABASE_SERVICE_ROLE_KEY", body.supabase_service_role_key)
        settings.supabase_service_role_key = body.supabase_service_role_key

    return {
        "saved": True,
        "supabase_url_set": bool(settings.supabase_url),
        "supabase_service_role_key_set": bool(settings.supabase_service_role_key),
    }


@router.post("/settings/supabase/test")
async def test_supabase_connection(_: str = Depends(require_api_key)) -> dict[str, Any]:
    if not settings.supabase_url or not settings.supabase_service_role_key:
        return {"connected": False, "error": "SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set"}
    try:
        from backend.app.integrations.supabase_client import SupabaseClient
        db = SupabaseClient()
        # Simple read to verify credentials
        db._client.table("research_runs").select("id").limit(1).execute()
        return {"connected": True, "url": settings.supabase_url}
    except Exception as exc:
        return {"connected": False, "error": str(exc)}
