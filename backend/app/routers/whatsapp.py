from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.meta_service import get_meta_service_for_clinic

router = APIRouter()

class MessageRequest(BaseModel):
    phone: str
    message: str
    clinic_id: str = "00000000-0000-0000-0000-000000000001"  # Default clinic

@router.post("/send")
async def send_message(request: MessageRequest):
    """
    Send a WhatsApp message via Meta Cloud API.
    """
    try:
        meta_service = await get_meta_service_for_clinic(request.clinic_id)
        response = await meta_service.send_message(
            to=request.phone,
            text=request.message
        )
        return {"status": "success", "data": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_status():
    """
    Check the status of the WhatsApp integration.
    Note: Meta API doesn't have a direct status endpoint like UazAPI.
    This returns configuration status from database.
    """
    try:
        from app.core.database import get_supabase
        
        supabase = get_supabase()
        result = supabase.table('clinic_integrations') \
            .select('phone_number_id, waba_id, is_active') \
            .eq('type', 'whatsapp') \
            .eq('is_active', True) \
            .limit(1) \
            .execute()
        
        if result.data and len(result.data) > 0:
            return {
                "connected": True,
                "phone_number_id": result.data[0]['phone_number_id'],
                "waba_id": result.data[0]['waba_id']
            }
        
        return {"connected": False, "message": "WhatsApp não configurado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
