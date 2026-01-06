from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/test", tags=["test"])

@router.get("/logs")
async def test_logs():
    """Test if logs are working"""
    logger.debug("🔵 DEBUG log test")
    logger.info("🟢 INFO log test")
    logger.warning("🟡 WARNING log test")
    logger.error("🔴 ERROR log test")
    
    return {
        "message": "Logs sent! Check Railway logs for colored emoji logs.",
        "levels": ["DEBUG", "INFO", "WARNING", "ERROR"]
    }
