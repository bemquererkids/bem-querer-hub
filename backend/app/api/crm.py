"""
CRM API Endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_supabase, Client

router = APIRouter(prefix="/crm", tags=["crm"])

from datetime import date
from app.services.clinicorp_service import ClinicorpClient

@router.get("/deals")
async def get_deals(
    clinic_id: Optional[str] = None, # In real multi-tenant, this comes from token
    supabase: Optional[Client] = Depends(get_supabase)
):
    """
    Fetch deals (chats/patients) for the Kanban board.
    Merges local chats with Clinicorp appointments.
    """
    deals = []
    
    # 1. Fetch from Supabase (Local Chats)
    try:
        from app.core.config import settings
        if supabase and "placeholder" not in settings.SUPABASE_URL:
            query = supabase.table("chats").select("*, patients(*)")
            if clinic_id:
                query = query.eq("clinic_id", clinic_id)
            response = query.execute()
            
            for chat in response.data:
                patient = chat.get("patients")
                if not patient: continue
                
                status = "new"
                if chat.get("intent") == "booking": status = "qualifying"
                elif chat.get("status") == "closed": status = "won"
                
                deals.append({
                    "id": chat["id"],
                    "patientName": patient["full_name"],
                    "patientAvatar": None,
                    "value": 0, 
                    "status": status,
                    "lastContact": chat["last_message_at"],
                    "source": "google", # Default
                    "treatmentType": chat.get("intent", "Geral"),
                    "probability": "medium" 
                })
    except Exception as e:
        print(f"Supabase Fetch Error: {e}")

    # 2. Fetch from Clinicorp (Real Appointments)
    try:
        # Using the hardcoded credentials we validated
        client = ClinicorpClient(clinic_id="bemquerer", integration_config={
            "client_id": "bemquerer",
            "client_secret": "8b6b218c-b536-4db5-97a1-babffc283eec"
        })
        
        appointments = await client.get_appointments(str(date.today()))
        
        for appt in appointments:
            deals.append({
                "id": str(appt.get("id", "appt_unknown")),
                "patientName": appt.get("patientName") or appt.get("patient", {}).get("name") or "Paciente Clinicorp",
                "patientAvatar": None,
                "value": 0,
                "status": "scheduled", # Force status for CRM
                "lastContact": appt.get("date") or str(date.today()),
                "source": "indication", # Assume integration
                "treatmentType": "Consulta",
                "probability": "high"
            })
            
    except Exception as e:
        print(f"Clinicorp Fetch Error: {e}")

from pydantic import BaseModel

class UpdateDealStatusRequest(BaseModel):
    status: str # 'attended', 'noshow', 'scheduled', 'won', 'lost'

@router.put("/deals/{deal_id}/status")
async def update_deal_status(
    deal_id: str,
    request: UpdateDealStatusRequest,
    supabase: Optional[Client] = Depends(get_supabase)
):
    """
    Updates the status of a deal (appointment or lead).
    """
    print(f"Updating Deal {deal_id} to status: {request.status}")
    
    # 1. If it's a Supabase ID (UUID), update DB
    if len(deal_id) == 36: # Simple UUID check
        try:
            if supabase:
                # Try updating chat first
                supabase.table("chats").update({"status": request.status}).eq("id", deal_id).execute()
                # Or appointment if we had that table sync
        except Exception as e:
            print(f"Error updating Supabase: {e}")

    # 2. If it's a Mock or Clinicorp ID, just return success
    # (In a real scenario with full write access, we would call Clinicorp PUT endpoint here)
    
    return {"status": "success", "new_status": request.status, "message": "Status atualizado com sucesso"}
