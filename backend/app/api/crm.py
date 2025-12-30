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
                "value": chat.get("deal_value") or 0,
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

class UpdateDealValueRequest(BaseModel):
    value: float

@router.put("/deals/{deal_id}/value")
async def update_deal_value(
    deal_id: str,
    request: UpdateDealValueRequest,
    supabase: Optional[Client] = Depends(get_supabase)
):
    if not deal_id:
        raise HTTPException(status_code=400, detail="Invalid Deal ID")

    try:
        from app.core.database import SupabaseClient
        admin_supabase = SupabaseClient.get_admin_client()
        
        admin_supabase.table("whatsapp_conversations").update({"deal_value": request.value}).eq("id", deal_id).execute()
        
    except Exception as e:
        print(f"Error updating value: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return {"status": "success", "value": request.value}

@router.put("/deals/{deal_id}/status")
async def update_deal_status(
    deal_id: str,
    request: UpdateDealStatusRequest,
    supabase: Optional[Client] = Depends(get_supabase)
):
    """
    Updates the status of a deal (appointment or lead).
    """
    # Map frontend Portuguese labels to internal keys
    status_map = {
        'Lead': 'new',
        'Em Negociação': 'qualifying',
        'Agendado': 'scheduled',
        'Compareceu': 'attended',
        'Faltou': 'noshow',
        'Venda': 'won',  # Frontend sends this
        'Venda Realizada': 'won',  # Legacy support
        'Perdido': 'lost'
    }
    
    internal_status = status_map.get(request.status, request.status)
    print(f"Updating Deal {deal_id} to status: {request.status} -> {internal_status}")
    
    if not deal_id:
        raise HTTPException(status_code=400, detail="Invalid Deal ID")

    # Update DB (removed UUID length restriction)
    try:
        # Use Admin Client to ensure strict isolation and bypass RLS context
        from app.core.database import SupabaseClient
        admin_supabase = SupabaseClient.get_admin_client()

        # Update Tags based on Status
        new_tag = f"crm:{internal_status}" # e.g. crm:won
        
        # Fetch current tags first
        res = admin_supabase.table("whatsapp_conversations").select("tags").eq("id", deal_id).execute()
        
        if not res.data:
            print(f"Deal {deal_id} not found in DB")
            raise HTTPException(status_code=404, detail="Deal not found")

        current_tags = res.data[0].get("tags") or []
        
        # Remove old status tags
        status_tags = ["crm:new", "crm:qualifying", "crm:scheduled", "crm:attended", "crm:noshow", "crm:won", "crm:lost"]
        updated_tags = [t for t in current_tags if t not in status_tags]
        
        # Avoid duplicates
        if new_tag not in updated_tags:
            updated_tags.append(new_tag)
        
        print(f"Updating tags for {deal_id}: {current_tags} -> {updated_tags}")
        
        update_res = admin_supabase.table("whatsapp_conversations").update({"tags": updated_tags}).eq("id", deal_id).execute()
        print(f"Update Result: {len(update_res.data)} rows affected")
        
    except Exception as e:
        print(f"Error updating Supabase: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return {"status": "success", "new_status": request.status, "message": "Status atualizado com sucesso"}

@router.get("/metrics")
async def get_dashboard_metrics(
    period: str = "month",  # week, month, custom
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Returns aggregated metrics from real WhatsApp/CRM data.
    Supports filtering by time period.
    """
    from datetime import datetime, timedelta
    
    try:
        from app.core.database import SupabaseClient
        admin_supabase = SupabaseClient.get_admin_client()
        
        # Calculate date range based on period
        now = datetime.now()
        
        if period == "week":
            # Start of current week (Monday) to today
            start_dt = now - timedelta(days=now.weekday())
            start_dt = start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "month":
            # Start of current month to today
            start_dt = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == "last7days":
            # Last 7 days from today
            start_dt = now - timedelta(days=7)
        elif period == "last30days":
            # Last 30 days from today
            start_dt = now - timedelta(days=30)
        elif period == "custom" and start_date and end_date:
            start_dt = datetime.fromisoformat(start_date)
            end_dt = datetime.fromisoformat(end_date)
        else:
            # Default to current month
            start_dt = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Fetch conversations filtered by date
        query = admin_supabase.table("whatsapp_conversations").select("id, tags, deal_value, created_at")
        
        if period == "custom" and start_date and end_date:
            query = query.gte("created_at", start_date).lte("created_at", end_date)
        else:
            query = query.gte("created_at", start_dt.isoformat())
        
        res = query.execute()
        raw_chats = res.data or []
        
        total_leads = len(raw_chats)
        scheduled = 0
        attended = 0
        noshow = 0  # Faltou
        qualifying = 0  # Em Negociação
        sales = 0
        revenue = 0.0
        
        for chat in raw_chats:
            tags = chat.get('tags') or []
            val = float(chat.get('deal_value') or 0)

            if 'crm:scheduled' in tags: scheduled += 1
            if 'crm:attended' in tags: attended += 1
            if 'crm:noshow' in tags: noshow += 1
            if 'crm:qualifying' in tags: qualifying += 1
            if 'crm:won' in tags: 
                sales += 1
                revenue += val
            
        # Calculate percentages
        scheduling_rate = (scheduled / total_leads * 100) if total_leads > 0 else 0
        attendance_rate = (attended / scheduled * 100) if scheduled > 0 else 0
        conversion_rate = (sales / total_leads * 100) if total_leads > 0 else 0
        noshow_rate = (noshow / scheduled * 100) if scheduled > 0 else 0
        qualifying_rate = (qualifying / total_leads * 100) if total_leads > 0 else 0
        
        # Funnel (simplified)
        funnel_data = [
            { "name": "Leads", "value": total_leads, "fill": "#4f46e5" },
            { "name": "Agendados", "value": scheduled, "fill": "#6366f1" },
            { "name": "Compareceram", "value": attended, "fill": "#818cf8" },
            { "name": "Vendas", "value": sales, "fill": "#a5b4fc" }
        ]
        
        avg_ticket = revenue / sales if sales > 0 else 0

        return {
            "totalLeads": total_leads,
            "scheduled": scheduled,
            "attended": attended,
            "noshow": noshow,
            "qualifying": qualifying,
            "sales": sales,
            "revenue": revenue,
            "ticket": avg_ticket,
            "funnelData": funnel_data,
            "percentages": {
                "schedulingRate": round(scheduling_rate, 1),
                "attendanceRate": round(attendance_rate, 1),
                "conversionRate": round(conversion_rate, 1),
                "noshowRate": round(noshow_rate, 1),
                "qualifyingRate": round(qualifying_rate, 1)
            }
        }

        
    except Exception as e:
        print(f"Metrics Error: {e}")
        return {
            "totalLeads": 0, "scheduled": 0, "attended": 0, "sales": 0, "revenue": 0, "ticket": 0,
            "funnelData": []
        }
