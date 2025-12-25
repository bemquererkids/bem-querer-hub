from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.core.database import get_supabase
from app.services.uazapi_service import get_uazapi_service, UazAPIService
from app.services.clinicorp_service import ClinicorpClient
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/integrations", tags=["integrations"])

# --- Schemas ---
class AvailabilityRequest(BaseModel):
    date: str # YYYY-MM-DD
    professional_id: Optional[str] = None

class AppointmentRequest(BaseModel):
    patient_name: str
    phone: str
    date: str
    time: str
    professional_id: str
    notes: Optional[str] = None

class ClinicorpConfig(BaseModel):
    client_id: str
    client_secret: str

# --- Dependency ---
def get_clinicorp_client():
    # In a real scenario, we would fetch credentials from the DB based on the current tenant/clinic_id
    # For now, we initialize in Mock Mode (no credentials = mock)
    return ClinicorpClient(clinic_id="demo_clinic", integration_config={})

# --- Endpoints ---

@router.post("/clinicorp/configure")
async def configure_clinicorp(config: ClinicorpConfig):
    """
    Validates and saves Clinicorp credentials.
    """
    try:
        # 1. Initialize Client with provided credentials
        client = ClinicorpClient(
            clinic_id="demo_clinic",
            integration_config={
                "client_id": config.client_id,
                "client_secret": config.client_secret
            }
        )
        
        # 2. Test Connection (checking professionals list is a good lightweight test)
        # If credentials are 'mock', the service handles it.
        try:
            await client.get_professionals()
        except Exception as e:
             if config.client_id == "mock":
                 pass # Allow mock to pass even if logic allows
             else:
                 raise HTTPException(status_code=400, detail=f"Falha na autenticação com Clinicorp: {str(e)}")

        # 3. Save to DB (TODO: Implement actual DB saving)
        # For prototype, we just return success
        
        return {
            "status": "connected",
            "message": "Conexão com Clinicorp estabelecida com sucesso!",
            "clinic_name": "Bem-Querer Matriz" # Mocked return
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/whatsapp/connect")
async def connect_whatsapp():
    """
    Triggers QR code generation for the WhatsApp instance.
    """
    try:
        logger.info("Attempting to connect WhatsApp...")
        logger.info(f"UAZAPI_BASE_URL: {settings.UAZAPI_BASE_URL}")
        logger.info(f"UAZAPI_INSTANCE: {settings.UAZAPI_INSTANCE}")
        
        # Validar configurações
        if not settings.UAZAPI_TOKEN or settings.UAZAPI_TOKEN == "placeholder_token":
            logger.error("UAZAPI_TOKEN not configured")
            raise HTTPException(
                status_code=500,
                detail="UAZAPI_TOKEN não configurado. Configure nas variáveis de ambiente da Vercel."
            )
        
        if not settings.UAZAPI_BASE_URL or settings.UAZAPI_BASE_URL == "https://free.uazapi.com":
            logger.error("UAZAPI_BASE_URL not configured properly")
            raise HTTPException(
                status_code=500,
                detail="UAZAPI_BASE_URL não configurado. Use: https://bemquerer.uazapi.com"
            )
        
        # Tentar conectar
        uazapi = get_uazapi_service()
        result = await uazapi.connect_instance(settings.UAZAPI_INSTANCE)
        
        logger.info(f"UazAPI connect response: {result}")
        
        # Extrair QR Code
        qrcode = None
        if isinstance(result, dict):
            qrcode = (
                result.get("qrcode") or 
                result.get("instance", {}).get("qrcode") or
                result.get("data", {}).get("qrcode")
            )
        
        if not qrcode:
            logger.error(f"QR Code not found in response: {result}")
            raise HTTPException(
                status_code=500,
                detail="QR Code não retornado pela UazAPI. Verifique se a instância está configurada corretamente."
            )
        
        return {
            "success": True,
            "qrcode": qrcode,
            "instance": settings.UAZAPI_INSTANCE
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to connect WhatsApp: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao conectar WhatsApp: {str(e)}"
        )

@router.get("/whatsapp/status")
async def get_whatsapp_status(
    uazapi: UazAPIService = Depends(get_uazapi_service)
):
    """
    Checks if WhatsApp is connected and triggers sync if newly connected.
    """
    try:
        instance_name = getattr(settings, "UAZAPI_INSTANCE", "bemquerer")
        status = await uazapi.get_instance_status(instance_name)
        
        # Auto-configure webhook on status check if connected
        is_connected = False
        if isinstance(status, dict):
            # Check various response structures
            is_connected = status.get("status", {}).get("connected") or status.get("connected")
            
            if is_connected:
                try:
                    public_url = getattr(settings, "PUBLIC_URL", "http://seu-dominio.com")
                    webhook_url = f"{public_url}/api/webhooks/whatsapp"
                    await uazapi.configure_webhook_sync(instance_name, webhook_url)
                    logger.info("Webhook sync triggered automatically")
                except:
                    pass
                
        return {
            **status,
            "config": {
                "token": getattr(settings, "UAZAPI_TOKEN", "Não configurado"),
                "instance": instance_name
            }
        }
    except Exception as e:
        status_code = getattr(e, "response", None).status_code if hasattr(e, "response") and hasattr(e.response, "status_code") else 500
        error_msg = str(e)
        if status_code == 401:
            error_msg = "Token inválido ou expirado na UazAPI (401). Verifique seu arquivo .env ou o painel UazAPI."
        
        logger.error(f"Status check failed: {error_msg}")
        return {
            "connected": False, 
            "error": error_msg,
            "status_code": status_code,
            "config": {
                "token": getattr(settings, "UAZAPI_TOKEN", "Não configurado"),
                "instance": getattr(settings, "UAZAPI_INSTANCE", "bemquerer")
            }
        }

@router.post("/clinicorp/availability")
async def check_availability(
    req: AvailabilityRequest,
    client: ClinicorpClient = Depends(get_clinicorp_client)
):
    """
    Proxy to check availability in Clinicorp.
    """
    try:
        slots = await client.check_availability(req.date, req.professional_id)
        return {"available_slots": slots}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clinicorp/appointment")
async def create_appointment(
    req: AppointmentRequest,
    client: ClinicorpClient = Depends(get_clinicorp_client)
):
    """
    Proxy to schedule an appointment in Clinicorp.
    1. Creates/Finds patient
    2. Schedules appointment
    """
    try:
        # 1. Create Patient (simplification: always create/update)
        patient_data = {
            "full_name": req.patient_name,
            "phone": req.phone
        }
        patient_id = await client.create_patient(patient_data)
        
        # 2. Schedule
        appt_data = {
            "patient_id": patient_id,
            "date": req.date,
            "time": req.time,
            "professional_id": req.professional_id,
            "notes": req.notes
        }
        appt_id = await client.create_appointment(appt_data)
        
        return {
            "status": "success", 
            "appointment_id": appt_id,
            "message": "Agendamento realizado com sucesso no Clinicorp (Mock)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))