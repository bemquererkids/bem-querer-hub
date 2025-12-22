"""
Integration Endpoints
Exposes external system capabilities (Clinicorp) to the Frontend and AI.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.services.clinicorp_service import ClinicorpClient

router = APIRouter(prefix="/integrations", tags=["integrations"])

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