from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.core.database import get_supabase
from app.services.meta_service import get_meta_service_for_clinic, MetaWhatsAppService
from app.services.clinicorp_service import ClinicorpClient
from app.core.config import settings
import logging
import os
import uuid

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
    try:
        logger.info(f"Attempting to connect Clinicorp with client_id: {config_in.client_id}")
        
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
                 logger.info("Clinicorp authentication successful")
             except Exception as e:
                 logger.error(f"Clinicorp auth failed: {str(e)}")
                 raise HTTPException(status_code=400, detail=f"Falha de autenticação: {str(e)}")

        # 2. Save to DB
        try:
            db_save_config("clinicorp", {
                "client_id": config_in.client_id,
                "client_secret": config_in.client_secret
            })
            logger.info("Clinicorp config saved to DB")
        except Exception as e:
            logger.error(f"Failed to save to DB: {str(e)}")
            # Continue even if DB save fails
        
        return {
            "status": "connected",
            "message": "Conectado com sucesso!"
        }
    except HTTPException: 
        raise
    except Exception as e:
        logger.error(f"Unexpected error in connect_clinicorp: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

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




class MetaWhatsAppConfig(BaseModel):
    phone_number_id: str
    waba_id: str
    access_token: str

class UazAPIConfig(BaseModel):
    instance_name: str
    token: str
    base_url: Optional[str] = None


@router.post("/whatsapp/connect")
async def connect_whatsapp(config: MetaWhatsAppConfig):
    """
    Configure Meta WhatsApp Business Cloud API credentials
    
    Body:
        phone_number_id: Meta Phone Number ID
        waba_id: WhatsApp Business Account ID
        access_token: Permanent access token from System User
    
    Returns:
        webhook_url: URL to configure in Meta Developer Console
        verify_token: Token to use for webhook verification
    """
    try:
        logger.info(f"Configuring Meta WhatsApp for phone_number_id: {config.phone_number_id}")
        
        # Validate credentials format
        if not config.phone_number_id or not config.phone_number_id.isdigit():
            raise HTTPException(
                status_code=400,
                detail="Phone Number ID inválido. Deve ser numérico."
            )
        
        if not config.waba_id or not config.waba_id.isdigit():
            raise HTTPException(
                status_code=400,
                detail="WABA ID inválido. Deve ser numérico."
            )
        
        if not config.access_token or not config.access_token.startswith("EAA"):
            raise HTTPException(
                status_code=400,
                detail="Access Token inválido. Deve começar com 'EAA'."
            )
        
        # Generate verify token
        verify_token = str(uuid.uuid4())
        
        # Save to database
        supabase = get_supabase()
        
        data = {
            "clinica_id": CLINIC_ID_DEFAULT,
            "type": "whatsapp",
            "phone_number_id": config.phone_number_id,
            "waba_id": config.waba_id,
            "access_token": config.access_token,
            "verify_token": verify_token,
            "is_active": True,
            "updated_at": str(datetime.now())
        }
        
        # Upsert (update if exists, insert if not)
        supabase.table("clinic_integrations").upsert(
            data,
            on_conflict="clinica_id,type"
        ).execute()
        
        logger.info("✅ Meta WhatsApp credentials saved successfully")
        
        # Generate webhook URL
        public_url = os.getenv("PUBLIC_URL", "https://seu-dominio.vercel.app")
        webhook_url = f"{public_url}/api/webhooks/whatsapp"
        
        return {
            "success": True,
            "webhook_url": webhook_url,
            "verify_token": verify_token,
            "message": "Configuração salva! Configure o webhook no Meta Developer Console."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save Meta WhatsApp config: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao salvar configuração: {str(e)}"
        )

@router.get("/whatsapp/status")
async def get_whatsapp_status():
    """
    Check if Meta WhatsApp is configured
    
    Returns:
        connected: Boolean indicating if credentials are configured
        phone_number_id: Configured phone number ID (if exists)
        webhook_url: Webhook URL to use in Meta console
    """
    try:
        # Check database for configuration
        supabase = get_supabase()
        result = supabase.table('clinic_integrations') \
            .select('phone_number_id, waba_id, verify_token') \
            .eq('clinica_id', CLINIC_ID_DEFAULT) \
            .eq('type', 'whatsapp') \
            .eq('is_active', True) \
            .execute()
        
        if result.data and len(result.data) > 0:
            config = result.data[0]
            public_url = os.getenv("PUBLIC_URL", "https://seu-dominio.vercel.app")
            
            return {
                "connected": True,
                "phone_number_id": config.get('phone_number_id'),
                "waba_id": config.get('waba_id'),
                "webhook_url": f"{public_url}/api/webhooks/whatsapp",
                "verify_token": config.get('verify_token')
            }
        
        return {
            "connected": False,
            "message": "WhatsApp não configurado. Configure as credenciais da Meta."
        }
        
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        return {
            "connected": False,
            "error": str(e)
        }

@router.post("/uazapi/connect")
async def connect_uazapi(config: UazAPIConfig):
    """
    Configure UazAPI credentials
    """
    try:
        if not config.instance_name or not config.token:
             raise HTTPException(status_code=400, detail="Instance Name and Token are required")
             
        # Save to database
        supabase = get_supabase()
        
        data = {
            "clinica_id": CLINIC_ID_DEFAULT,
            "type": "whatsapp",
            "instance_name": config.instance_name,
            "token": config.token,
            # Clear Meta fields if switching
            "phone_number_id": None,
            "waba_id": None,
            "access_token": None, 
            "is_active": True,
            "updated_at": str(datetime.now())
        }
        
        if config.base_url:
            # We could store base_url in 'config' json column if we wanted override
            # For now, relying on env var or default
            pass
        
        supabase.table("clinic_integrations").upsert(
            data,
            on_conflict="clinica_id,type"
        ).execute()
        
        return {"success": True, "message": "UazAPI Configured Successfully"}
        
    except Exception as e:
        logger.error(f"UazAPI Config Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/uazapi/status")
async def get_uazapi_status():
    try:
        supabase = get_supabase()
        result = supabase.table('clinic_integrations') \
            .select('instance_name, token') \
            .eq('clinica_id', CLINIC_ID_DEFAULT) \
            .eq('type', 'whatsapp') \
            .eq('is_active', True) \
            .execute()
            
        if result.data and result.data[0].get('instance_name'):
            return {
                "connected": True,
                "instance_name": result.data[0].get('instance_name')
            }
            
        return {"connected": False}
    except Exception as e:
        return {"connected": False, "error": str(e)}

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