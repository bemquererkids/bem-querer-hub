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
from datetime import datetime
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
class ClinicorpConfig(BaseModel):
    client_id: str
    client_secret: str

class OpenAIConfig(BaseModel):
    api_key: str

class GeminiConfig(BaseModel):
    api_key: str

# --- Dependency ---
# --- Persistence Helper (Supabase) ---
CLINIC_ID_DEFAULT = "00000000-0000-0000-0000-000000000001" # Bem-Querer Matriz (Hardcoded for MVP)

def db_save_config(integration_type: str, config: dict):
    """Save config to Supabase"""
    try:
        supabase = get_supabase()
        
        data = {
            "clinica_id": CLINIC_ID_DEFAULT,
            "type": integration_type,
            "config": config,
            "is_active": True,
            "updated_at": str(datetime.now())
        }
        
        # Upsert (requires unique constraint on clinica_id + type)
        supabase.table("clinic_integrations").upsert(data, on_conflict="clinica_id, type").execute()
    except Exception as e:
        logger.error(f"Failed to save to Supabase: {e}")
        # Could fallback to Env Vars or File if needed
        pass

def db_load_config(integration_type: str) -> dict:
    """Load config from Supabase"""
    try:
        supabase = get_supabase()
        res = supabase.table("clinic_integrations") \
            .select("config") \
            .eq("clinica_id", CLINIC_ID_DEFAULT) \
            .eq("type", integration_type) \
            .execute()
            
        if res.data and len(res.data) > 0:
            return res.data[0]["config"]
    except Exception as e:
        logger.error(f"Failed to load from Supabase: {e}")
    
    return {}

# --- Dependency ---
def get_clinicorp_client():
    # 1. Try DB
    db_config = db_load_config("clinicorp")
    client_id = db_config.get("client_id")
    client_secret = db_config.get("client_secret")

    # 2. Fallback to Env Vars (Vercel)
    if not client_id:
        client_id = os.getenv("CLINICORP_CLIENT_ID")
        client_secret = os.getenv("CLINICORP_CLIENT_SECRET")

    # 3. Fallback to Mock
    if not client_id:
        client_id = "mock"
        client_secret = "mock"

    return ClinicorpClient(
        clinic_id="bemquerer", 
        integration_config={
            "client_id": client_id,
            "client_secret": client_secret
        }
    )

# --- Endpoints ---

@router.post("/clinicorp/connect")
async def connect_clinicorp(config_in: ClinicorpConfig):
    # Changed from configure_clinicorp to standard naming
    try:
        # 1. Verify credentials by initing client
        client = ClinicorpClient(
            clinic_id="demo_clinic",
            integration_config={
                "client_id": config_in.client_id,
                "client_secret": config_in.client_secret
            }
        )
        
        if config_in.client_id != "mock":
             try:
                 await client.get_professionals()
             except Exception as e:
                 raise HTTPException(status_code=400, detail=f"Falha de autenticação: {str(e)}")

        # 2. Save to DB
        db_save_config("clinicorp", {
            "client_id": config_in.client_id,
            "client_secret": config_in.client_secret
        })
        
        return {
            "status": "connected",
            "message": "Conectado com sucesso!"
        }
    except HTTPException: raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clinicorp/status")
async def clinicorp_status():
    # Check DB
    config = db_load_config("clinicorp")
    if config.get("client_id"):
        return {"connected": True, "source": "database"}
    
    # Check Env
    if os.getenv("CLINICORP_CLIENT_ID"):
        return {"connected": True, "source": "environment"}
        
    return {"connected": False}

@router.post("/openai/connect")
async def connect_openai(config: OpenAIConfig):
    try:
        if not config.api_key.startswith("sk-"):
             raise HTTPException(status_code=400, detail="Chave OpenAI inválida")
             
        db_save_config("openai", {"api_key": config.api_key})
        return {"status": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/openai/status")
async def openai_status():
    # Check DB
    config = db_load_config("openai")
    if config.get("api_key"):
        return {"connected": True}
        
    # Check Env
    if os.getenv("OPENAI_API_KEY"):
        return {"connected": True}
        
    return {"connected": False}


@router.post("/gemini/connect")
async def connect_gemini(config: GeminiConfig):
    try:
        # Simple validation
        if not config.api_key:
             raise HTTPException(status_code=400, detail="Chave Gemini inválida")
             
        db_save_config("gemini", {"api_key": config.api_key})
        return {"status": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/gemini/status")
async def gemini_status():
    # Check DB
    config = db_load_config("gemini")
    if config.get("api_key"):
        return {"connected": True}
        
    # Check Env
    if os.getenv("GEMINI_API_KEY"):
        return {"connected": True}
        
    return {"connected": False}



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
            
        # 3. Save to DB for persistence
        db_save_config("whatsapp", {
            "instance": settings.UAZAPI_INSTANCE,
            "token": settings.UAZAPI_TOKEN, # Note: Saving token might be sensitive, but required for persistence if not in env
            "connected_at": str(datetime.now())
        })
        
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
    try:
        # Try to get instance from DB first, then Env
        db_config = db_load_config("whatsapp")
        instance_name = db_config.get("instance") or getattr(settings, "UAZAPI_INSTANCE", "bemquerer")
        
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
            "start_time": req.time,
            # Simple assumption: 1h duration
            "end_time": req.time, 
            "professional_id": req.professional_id,
            "observation": req.notes
        }
        appt_id = await client.create_appointment(appt_data)
        
        return {
            "status": "success", 
            "appointment_id": appt_id,
            "message": "Agendamento realizado com sucesso no Clinicorp"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))