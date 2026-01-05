from fastapi import APIRouter, Request
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/webhooks", tags=["debug"])

@router.post("/uazapi/debug")
async def debug_uazapi_webhook(request: Request):
    """Debug endpoint to see raw UAZAPI payload"""
    try:
        payload = await request.json()
        logger.info(f"🔍 DEBUG UAZAPI Payload: {payload}")
        print(f"🔍 DEBUG UAZAPI Payload: {payload}")
        return {"status": "received", "payload": payload}
    except Exception as e:
        logger.error(f"Debug error: {e}")
        return {"status": "error", "error": str(e)}
