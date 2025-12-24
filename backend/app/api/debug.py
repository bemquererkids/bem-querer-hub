"""
Debug endpoint to check environment variables
"""
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(prefix="/debug", tags=["debug"])

@router.get("/env")
async def check_env():
    """Check if environment variables are loaded"""
    return {
        "UAZAPI_BASE_URL": settings.UAZAPI_BASE_URL,
        "UAZAPI_INSTANCE": settings.UAZAPI_INSTANCE,
        "UAZAPI_TOKEN_SET": bool(settings.UAZAPI_TOKEN and settings.UAZAPI_TOKEN != "placeholder_token"),
        "UAZAPI_TOKEN_LENGTH": len(settings.UAZAPI_TOKEN) if settings.UAZAPI_TOKEN else 0,
        "SUPABASE_URL": settings.SUPABASE_URL,
        "OPENAI_KEY_SET": bool(settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "sk-placeholder")
    }
