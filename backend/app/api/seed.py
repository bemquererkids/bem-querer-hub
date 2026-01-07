from fastapi import APIRouter, HTTPException
from app.core.database import get_supabase
from datetime import datetime, timedelta
import random
import uuid

router = APIRouter(prefix="/api/seed", tags=["seed"])

@router.get("/run")
async def run_seed_crm():
    """
    Popula o banco de dados atual com dados de teste para o CRM/Dashboard.
    Útil para ambientes de desenvolvimento ou demonstração.
    """
    print("🚀 Iniciando Seed de Dados CRM via API...")
    
    supabase = get_supabase()
    
    # Gerar datas nos últimos 30 dias
    base_date = datetime.now()
    
    # Status possíveis e pesos
    statuses = [
        ("crm:new", 0.4),          # Lead
        ("crm:qualifying", 0.2),   # Em negociação
        ("crm:scheduled", 0.15),   # Agendou
        ("crm:attended", 0.1),     # Compareceu
        ("crm:won", 0.1),          # Comprou
        ("crm:noshow", 0.05)       # Faltou
    ]
    
    data_to_insert = []
    
    for i in range(50): # Criar 50 interações
        days_ago = random.randint(0, 30)
        created_at = (base_date - timedelta(days=days_ago)).isoformat()
        
        # Pick status
        r = random.random()
        cumulative = 0
        selected_status = "crm:new"
        for s, weight in statuses:
            cumulative += weight
            if r < cumulative:
                selected_status = s
                break
        
        deal_value = 0
        if selected_status == "crm:won":
            deal_value = random.choice([150, 250, 500, 1200, 3500])
        
        chat_entry = {
            "id": str(uuid.uuid4()),
            "contact_name": f"Paciente Seed {i}",
            "phone_number": f"55119{random.randint(10000000, 99999999)}",
            "created_at": created_at,
            "updated_at": created_at,
            "tags": [selected_status],
            "deal_value": deal_value
        }
        
        data_to_insert.append(chat_entry)

    try:
        res = supabase.table("whatsapp_conversations").insert(data_to_insert).execute()
        return {"status": "success", "message": f"{len(res.data)} registros inseridos com sucesso."}
    except Exception as e:
        print(f"❌ Erro ao inserir: {e}")
        # Tente identificar erros de schema
        if "conversation_id" in str(e):
             return {"status": "error", "message": "Erro de schema: conversation_id faltando?"}
        return {"status": "error", "message": str(e)}

@router.get("/clean")
async def clean_seed_data():
    """
    Remove todos os dados de teste (Paciente Seed % e Paciente Teste %) do banco.
    """
    from app.core.database import SupabaseClient
    supabase = SupabaseClient.get_admin_client()
    try:
        deleted_count = 0
        
        # 1. Remove "Paciente Seed%" (criado via API)
        res1 = supabase.table("whatsapp_conversations") \
            .delete() \
            .ilike("contact_name", "Paciente Seed%") \
            .execute()
        deleted_count += len(res1.data) if res1.data else 0
        
        # 2. Remove "Paciente Teste%" (criado via Script Local)
        res2 = supabase.table("whatsapp_conversations") \
            .delete() \
            .ilike("contact_name", "Paciente Teste%") \
            .execute()
        deleted_count += len(res2.data) if res2.data else 0
            
        return {
            "status": "success", 
            "deleted_total": deleted_count, 
            "message": f"Limpeza concluída. {deleted_count} registros de teste removidos."
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

