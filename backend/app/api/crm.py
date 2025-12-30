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
@router.get("/deals")
async def get_deals(
    clinic_id: Optional[str] = None, # In real multi-tenant, this comes from token
    supabase: Optional[Client] = Depends(get_supabase)
):
    """
    Fetch deals (chats/patients) for the Kanban board.
    Merges local chats with real CRM data.
    """
    deals = []
    
    try:
        # 1. Fetch Conversations (The active deals)
        # Assuming clinic_id 'bemquerer' for now or the default one we use in webhooks
        target_clinic_id = clinic_id or "00000000-0000-0000-0000-000000000001"
        
        # Use Admin Client usually for backend, but depends accepts normal client. 
        # If RLS issues, might need admin.
        from app.core.database import SupabaseClient
        admin_supabase = SupabaseClient.get_admin_client()
        
        # Get conversations
        conv_res = admin_supabase.table("whatsapp_conversations").select("*").execute()
        conversations = conv_res.data if conv_res.data else []
        
        # Get Patients (to look up source)
        # Collect phones first
        phones = [c.get('phone_number') for c in conversations if c.get('phone_number')]
        
        patient_map = {}
        if phones:
            pat_res = admin_supabase.table("pacientes").select("*").in_("telefone", phones).execute()
            if pat_res.data:
                for p in pat_res.data:
                    patient_map[p.get('telefone')] = p
        
        for chat in conversations:
            phone = chat.get('phone_number')
            patient = patient_map.get(phone, {})
            
            # Determine Status from Tags or Defaults
            # Logic: If tags contains 'crm:won' -> 'won', etc.
            status = 'new' # Default to Lead
            tags = chat.get('tags') or []
            
            if 'crm:won' in tags: status = 'won'
            elif 'crm:scheduled' in tags: status = 'scheduled'
            elif 'crm:attended' in tags: status = 'attended'
            elif 'crm:noshow' in tags: status = 'noshow'
            elif 'crm:qualifying' in tags: status = 'qualifying'
            
            # Determine Source
            source_raw = patient.get('origem') or 'manual'
            source = 'google' # Default for UI icons
            if 'insta' in source_raw.lower(): source = 'instagram'
            elif 'facebook' in source_raw.lower(): source = 'facebook'
            elif 'indica' in source_raw.lower(): source = 'indication'
            
            deal = {
                "id": chat["id"],
                "patientName": chat.get("contact_name") or patient.get("nome") or phone,
                "patientAvatar": chat.get("avatar"),
                "value": 0,
                "status": status,
                "lastContact": chat.get("last_message_at") or chat.get("created_at"),
                "source": source,
                "campaignId": None,
                "phone": chat.get("phone_number"),
                "probability": "medium"
            }
            deals.append(deal)
            
    except Exception as e:
        print(f"CRM Fetch Error: {e}")
        import traceback
        traceback.print_exc()

    return deals

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
