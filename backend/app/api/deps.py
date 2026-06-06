from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

from backend.app.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def require_api_key(api_key: str | None = Security(api_key_header)) -> str:
    # When API_SECRET_KEY is unset, auth is disabled (dev mode)
    if not settings.api_secret_key:
        return ""
    if not api_key or api_key != settings.api_secret_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return api_key
