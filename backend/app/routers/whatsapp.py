
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.services.uazapi_service import UazAPIService, uazapi_service

router = APIRouter()

class MessageRequest(BaseModel):
    phone: str
    message: str

@router.post("/send")
async def send_message(request: MessageRequest):
    """
    Send a WhatsApp message via UazAPI.
    """
    try:
        response = uazapi_service.send_message(request.phone, request.message)
        return {"status": "success", "data": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_status():
    """
    Check the status of the WhatsApp instance.
    """
    try:
        status = uazapi_service.get_instance_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
