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
    source: str = "whatsapp", # whatsapp, clinicorp
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Returns aggregated metrics from real WhatsApp/CRM data or Clinicorp.
    Supports filtering by time period.
    """
    from datetime import datetime, timedelta
    import pytz
    # Deployment Trigger check
    
    try:
        from app.core.database import SupabaseClient
        admin_supabase = SupabaseClient.get_admin_client()
        
        # Calculate date range based on period (Force BRT)
        tz_br = pytz.timezone("America/Sao_Paulo")
        now = datetime.now(tz_br)
        
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
            # Parse assuming input is YYYY-MM-DD
            start_dt = datetime.fromisoformat(start_date).replace(tzinfo=tz_br)
            end_dt = datetime.fromisoformat(end_date).replace(tzinfo=tz_br)
        else:
            # Default to current month
            start_dt = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
        # Ensure we have an end_date context for queries if not custom
        if not (period == "custom" and end_date):
            end_dt = now
            
        start_str = start_dt.strftime("%Y-%m-%d")
        end_str = end_dt.strftime("%Y-%m-%d")

        # --- CLINICORP SOURCE ---
        if source == "clinicorp":
            try:
                print(f"[Clinicorp Metrics] Fetching for period: {period} ({start_str} to {end_str})")
                
                # 1. Get Client (using helper logic)
                from app.api.integration import get_clinicorp_client
                client = get_clinicorp_client()
                
                # 2. Fetch Data
                appointments = await client.get_appointments(start_str, end_str)
                financials = await client.get_financials(start_str, end_str)
                
                # Debug: check patients
                try:
                    patients_check = await client.get_patients()
                    patients_count = len(patients_check)
                except:
                    patients_count = -1 # Error fetching patients
                
                print(f"[Clinicorp Metrics] Appointments: {len(appointments)} | Financials: {financials}")
                
                # 3. Calculate Metrics
                # 3. Calculate Metrics (Defensive)
                scheduled_count = 0
                attended_count = 0
                noshow_count = 0
                canceled_count = 0
                
                try:
                    if appointments and isinstance(appointments, list):
                        for appt in appointments:
                            if not isinstance(appt, dict): continue
                            
                            raw_status = str(appt.get("status", appt.get("Status", ""))).lower()
                            
                            if "agendado" in raw_status or "confirmado" in raw_status:
                                scheduled_count += 1
                            elif "atendido" in raw_status or "finalizado" in raw_status or "completed" in raw_status:
                                attended_count += 1
                            elif "faltou" in raw_status or "falta" in raw_status or "missed" in raw_status:
                                noshow_count += 1
                            elif "cancelado" in raw_status or "desmarcado" in raw_status:
                                canceled_count += 1
                            else:
                                scheduled_count += 1 # Default
                    else:
                        print(f"[Clinicorp] Warning: Appointments is not a list: {type(appointments)}")
                except Exception as e:
                    print(f"[Clinicorp] Error parsing statuses: {e}")
                    # Fallback to simple count
                    scheduled_count = len(appointments) if isinstance(appointments, list) else 0

                total_leads = len(appointments) if isinstance(appointments, list) else 0
                scheduled = scheduled_count + attended_count + noshow_count
                attended = attended_count
                noshow = noshow_count      # FIX: Assign variable for return
                qualifying = 0             # FIX: Explicit assignment
                
                # Financials mapping (mock revenue if not found yet)
                sales = financials.get("sales_count", attended) 
                revenue = financials.get("revenue", 0.0)
                
                # Rates
                scheduling_rate = 100
                attendance_rate = round((attended / scheduled * 100), 1) if scheduled > 0 else 0
                noshow_rate = round((noshow / scheduled * 100), 1) if scheduled > 0 else 0
                conversion_rate = round((sales / attended * 100), 1) if attended > 0 else 0
                
                avg_ticket = round(revenue / sales, 2) if sales > 0 else 0
                
                funnel_data = [
                    { "name": "Agendados", "value": scheduled, "fill": "#6366f1" },
                    { "name": "Compareceram", "value": attended, "fill": "#818cf8" },
                    { "name": "Vendas", "value": sales, "fill": "#a5b4fc" }
                ]

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
                    },
                    "debug_info": {
                        "period": period,
                        "dates": f"{start_str} to {end_str}",
                        "appointments_found": len(appointments),
                        "patients_found_check": patients_count,
                        "financials_raw": financials,
                        "client_id_used": client.client_id,
                        # Discovered IDs
                        "subscriber_id": getattr(client, 'context', {}).get('subscriber_id'),
                        "business_id": getattr(client, 'context', {}).get('business_id'),
                        "discovery_raw": getattr(client, 'discovery_raw', 'N/A')
                    }
                }
                
            except Exception as e:
                print(f"Clinicorp Fetch Error: {e}")
                import traceback
                traceback.print_exc()
                # Fallback to empty or error WITH DEBUG INFO
                return {
                    "totalLeads": 0, "scheduled": 0, "attended": 0, "sales": 0, "revenue": 0, "ticket": 0,
                    "funnelData": [],
                    "percentages": {
                        "schedulingRate": 0, "attendanceRate": 0, "conversionRate": 0, "noshowRate": 0, "qualifyingRate": 0
                    },
                    "debug_info": {
                        "error": str(e),
                        "period": period,
                        "dates": f"{start_str} to {end_str}",
                        "client_id_used": getattr(client, 'client_id', 'unknown') if 'client' in locals() else 'init_failed'
                    }
                }

        # --- WHATSAPP SOURCE (DEFAULT) ---
        
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

class DashboardPreferences(BaseModel):
    default_source: str = "whatsapp" # whatsapp, clinicorp

@router.get("/preferences")
async def get_dashboard_preferences():
    """Get saved preferences for the dashboard"""
    from app.api.integration import db_load_config
    config = db_load_config("dashboard_pref")
    return {
        "default_source": config.get("default_source", "whatsapp")
    }

@router.post("/preferences")
async def save_dashboard_preferences(pref: DashboardPreferences):
    """Save dashboard preferences"""
    from app.api.integration import db_save_config
    try:
        db_save_config("dashboard_pref", {"default_source": pref.default_source})
        return {"status": "success", "saved": pref}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
