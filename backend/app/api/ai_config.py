"""
AI Configuration API
Endpoints for managing dynamic AI assistant configuration
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from pydantic import BaseModel
from app.core.database import get_supabase
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ai-config", tags=["AI Configuration"])

@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify router is loaded"""
    return {"status": "AI Config API is working!", "version": "1.0"}

# Pydantic Models
class PersonaConfig(BaseModel):
    name: str = "Assistente"
    clinic_name: str
    role: str = "assistente virtual"
    tone: str = "Profissional e acolhedor"
    target_audience: str = "Pacientes em geral"
    objective: str = "Ajudar com agendamentos"
    voice_examples: str = ""

class TeamMember(BaseModel):
    name: str
    clinicorp_id: str = ""
    specialty: str = "Geral"
    focus: str = ""
    schedule: str = ""
    position: str = ""

class LocationInfo(BaseModel):
    address: str = ""
    reference: str = ""
    parking: str = ""

class ScheduleInfo(BaseModel):
    weekdays: str = ""
    saturday: str = "Fechado"
    sunday: str = "Fechado"

class PricingInfo(BaseModel):
    consultation: str = ""
    consultation_note: str = ""
    insurance: str = ""
    payment_methods: str = ""

class ContactInfo(BaseModel):
    phone: str = ""
    website: str = ""
    instagram: str = ""

class AdminInfo(BaseModel):
    location: LocationInfo = LocationInfo()
    schedule: ScheduleInfo = ScheduleInfo()
    pricing: PricingInfo = PricingInfo()
    contact: ContactInfo = ContactInfo()

class EmergencyProtocol(BaseModel):
    triggers: str = ""
    steps: List[str] = []

class SchedulingProtocol(BaseModel):
    steps: List[str] = []

class Protocols(BaseModel):
    emergency: EmergencyProtocol = EmergencyProtocol()
    scheduling: SchedulingProtocol = SchedulingProtocol()
    do_rules: List[str] = []
    dont_rules: List[str] = []

class AIConfiguration(BaseModel):
    persona: PersonaConfig
    team: List[TeamMember] = []
    admin_info: AdminInfo = AdminInfo()
    protocols: Protocols = Protocols()

class AIConfigResponse(BaseModel):
    id: str
    clinic_id: str
    config: Dict[str, Any]
    is_active: bool
    version: int
    created_at: str
    updated_at: str

@router.get("/{clinic_id}", response_model=AIConfigResponse)
async def get_ai_config(clinic_id: str):
    """
    Get active AI configuration for a clinic
    """
    try:
        supabase = get_supabase()
        
        result = supabase.table("ai_configurations") \
            .select("*") \
            .eq("clinic_id", clinic_id) \
            .eq("is_active", True) \
            .single() \
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Configuration not found")
        
        return result.data
    
    except Exception as e:
        logger.error(f"Error fetching AI config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{clinic_id}")
async def create_or_update_ai_config(clinic_id: str, config: AIConfiguration):
    """
    Create or update AI configuration for a clinic
    """
    try:
        supabase = get_supabase()
        
        # Check if config exists
        existing = supabase.table("ai_configurations") \
            .select("id, version") \
            .eq("clinic_id", clinic_id) \
            .eq("is_active", True) \
            .execute()
        
        config_dict = config.dict()
        
        if existing.data:
            # Update existing
            config_id = existing.data[0]["id"]
            new_version = existing.data[0]["version"] + 1
            
            result = supabase.table("ai_configurations") \
                .update({
                    "config": config_dict,
                    "version": new_version
                }) \
                .eq("id", config_id) \
                .execute()
        else:
            # Create new
            result = supabase.table("ai_configurations") \
                .insert({
                    "clinic_id": clinic_id,
                    "config": config_dict,
                    "is_active": True,
                    "version": 1
                }) \
                .execute()
        
        return {"message": "Configuration saved successfully", "data": result.data}
    
    except Exception as e:
        logger.error(f"Error saving AI config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{clinic_id}/history")
async def get_config_history(clinic_id: str):
    """
    Get configuration history for a clinic
    """
    try:
        supabase = get_supabase()
        
        result = supabase.table("ai_configurations") \
            .select("id, version, created_at, updated_at, is_active") \
            .eq("clinic_id", clinic_id) \
            .order("version", desc=True) \
            .execute()
        
        return {"history": result.data}
    
    except Exception as e:
        logger.error(f"Error fetching config history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{clinic_id}/restore/{version}")
async def restore_config_version(clinic_id: str, version: int):
    """
    Restore a previous configuration version
    """
    try:
        supabase = get_supabase()
        
        # Get the version to restore
        old_version = supabase.table("ai_configurations") \
            .select("config") \
            .eq("clinic_id", clinic_id) \
            .eq("version", version) \
            .single() \
            .execute()
        
        if not old_version.data:
            raise HTTPException(status_code=404, detail="Version not found")
        
        # Deactivate current
        supabase.table("ai_configurations") \
            .update({"is_active": False}) \
            .eq("clinic_id", clinic_id) \
            .eq("is_active", True) \
            .execute()
        
        # Create new active version with old config
        result = supabase.table("ai_configurations") \
            .insert({
                "clinic_id": clinic_id,
                "config": old_version.data["config"],
                "is_active": True,
                "version": version + 1000  # Mark as restored
            }) \
            .execute()
        
        return {"message": f"Restored version {version}", "data": result.data}
    
    except Exception as e:
        logger.error(f"Error restoring config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{clinic_id}/preview")
async def preview_generated_prompt(clinic_id: str):
    """
    Preview the generated system prompt from current configuration
    """
    try:
        from app.services.ai_config_service import AIConfigService
        
        supabase = get_supabase()
        
        result = supabase.table("ai_configurations") \
            .select("config") \
            .eq("clinic_id", clinic_id) \
            .eq("is_active", True) \
            .single() \
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Configuration not found")
        
        prompt = AIConfigService.generate_system_prompt(result.data["config"])
        
        return {"prompt": prompt}
    
    except Exception as e:
        logger.error(f"Error generating preview: {e}")
        raise HTTPException(status_code=500, detail=str(e))
