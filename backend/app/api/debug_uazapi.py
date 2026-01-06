from fastapi import APIRouter, HTTPException
from app.services.uazapi_service import get_uazapi_service
import logging
import os

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/debug", tags=["debug"])

@router.get("/uazapi/config")
async def debug_uazapi_config():
    """
    Debug endpoint to check UazAPI configuration
    """
    return {
        "UAZAPI_BASE_URL": os.getenv("UAZAPI_BASE_URL", "NOT_SET"),
        "UAZAPI_INSTANCE": os.getenv("UAZAPI_INSTANCE", "NOT_SET"),
        "UAZAPI_TOKEN_SET": bool(os.getenv("UAZAPI_TOKEN")),
        "UAZAPI_TOKEN_LENGTH": len(os.getenv("UAZAPI_TOKEN", "")) if os.getenv("UAZAPI_TOKEN") else 0
    }

@router.post("/uazapi/test-send")
async def test_uazapi_send(phone: str, message: str = "Teste de envio"):
    """
    Test UazAPI message sending
    Example: POST /api/debug/uazapi/test-send?phone=5585999308484&message=Oi
    """
    try:
        logger.info(f"🧪 Testing UazAPI send to {phone}")
        
        # Get service
        uazapi = get_uazapi_service()
        
        # Log config
        logger.info(f"Base URL: {uazapi.base_url}")
        logger.info(f"Instance: {uazapi.instance_name}")
        logger.info(f"Token length: {len(uazapi.token)}")
        
        # Try to send
        result = uazapi.send_message(to=phone, text=message)
        
        return {
            "success": True,
            "result": result,
            "config": {
                "base_url": uazapi.base_url,
                "instance": uazapi.instance_name
            }
        }
    except Exception as e:
        logger.error(f"❌ Test send failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
