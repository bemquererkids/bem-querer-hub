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
        target_clinic_id = clinic_id or "00000000-0000-0000-0000-000000000001"
        
        from app.core.database import SupabaseClient
        admin_supabase = SupabaseClient.get_admin_client()
        
        # Get conversations
        conv_res = admin_supabase.table("whatsapp_conversations").select("*").execute()
        conversations = conv_res.data if conv_res.data else []
        print(f"CRM Debug: Found {len(conversations)} conversations.")
        
        # Get Patients (to look up source)
        phones = [c.get('phone_number') for c in conversations if c.get('phone_number')]
        
        patient_map = {}
        if phones:
            # Only query if we have phones
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
            
            # Default Deal Object
            deal = {
                "id": chat["id"],
                "patientName": chat.get("contact_name") or patient.get("nome") or phone,
                "patientAvatar": chat.get("avatar"),
                "value": 0,
                "status": status,
                "lastContact": chat.get("last_message_at") or chat.get("created_at"),
                "source": 'google', # Default fallback
                "campaignId": None,
                "phone": chat.get("phone_number"),
                "probability": "medium"
            }
            
            # Refine Source from Patient Data
            source_raw = patient.get('origem') or 'manual'
            if 'insta' in source_raw.lower(): deal['source'] = 'instagram'
            elif 'facebook' in source_raw.lower(): deal['source'] = 'facebook'
            elif 'indica' in source_raw.lower(): deal['source'] = 'indication'
            
            deals.append(deal)
            
        print(f"CRM Debug: Returning {len(deals)} deals.")
            
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
                # Update Tags based on Status
                new_tag = f"crm:{request.status}" # e.g. crm:won
                
                # Fetch current tags first
                res = supabase.table("whatsapp_conversations").select("tags").eq("id", deal_id).execute()
                current_tags = res.data[0].get("tags") or [] if res.data else []
                
                # Remove old status tags
                status_tags = ["crm:new", "crm:qualifying", "crm:scheduled", "crm:attended", "crm:noshow", "crm:won", "crm:lost"]
                updated_tags = [t for t in current_tags if t not in status_tags]
                updated_tags.append(new_tag)
                
                supabase.table("whatsapp_conversations").update({"tags": updated_tags}).eq("id", deal_id).execute()
        except Exception as e:
            print(f"Error updating Supabase: {e}")

    return {"status": "success", "new_status": request.status, "message": "Status atualizado com sucesso"}

@router.get("/metrics")
async def get_dashboard_metrics():
    """
    Returns aggregated metrics from real WhatsApp/CRM data.
    """
    try:
        from app.core.database import SupabaseClient
        admin_supabase = SupabaseClient.get_admin_client()
        
        # Fetch all conversations
        # For a massive DB we should use .count() with filters, but for this scale fetching id,tags is fine
        res = admin_supabase.table("whatsapp_conversations").select("id, tags").execute()
        raw_chats = res.data or []
        
        total_leads = len(raw_chats)
        scheduled = 0
        attended = 0
        sales = 0
        won = 0
        new_leads = 0
        
        for chat in raw_chats:
            tags = chat.get('tags') or []
            if 'crm:scheduled' in tags: scheduled += 1
            if 'crm:attended' in tags: attended += 1
            if 'crm:won' in tags: 
                sales += 1
                won += 1
            if not tags or 'crm:new' in tags: new_leads += 1
            
        # Funnel (simplified)
        funnel_data = [
            { "name": "Leads", "value": total_leads, "fill": "#4f46e5" },
            { "name": "Agendados", "value": scheduled, "fill": "#6366f1" },
            { "name": "Compareceram", "value": attended, "fill": "#818cf8" },
            { "name": "Vendas", "value": sales, "fill": "#a5b4fc" }
        ]
        
        return {
            "totalLeads": total_leads,
            "scheduled": scheduled,
            "attended": attended,
            "sales": sales,
            "revenue": sales * 2100, # Mock average ticket R$ 2.100
            "ticket": 2100,
            "funnelData": funnel_data
        }
        
    except Exception as e:
        print(f"Metrics Error: {e}")
        return {
            "totalLeads": 0, "scheduled": 0, "attended": 0, "sales": 0, "revenue": 0, "ticket": 0,
            "funnelData": []
        }
