import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.core.database import get_supabase

def debug_tags():
    print("🔍 Inspecionando Tags e Status Reais (Cliente Leitura)...")
    admin_supabase = get_supabase() # Use standard client for read

    
    # Busca 20 conversas mais recentes que NÃO sejam teste
    res = admin_supabase.table("whatsapp_conversations") \
        .select("id, contact_name, tags, deal_value, created_at, phone_number") \
        .not_.ilike("contact_name", "Paciente Teste%") \
        .not_.ilike("contact_name", "Paciente Seed%") \
        .order("created_at", desc=True) \
        .limit(20) \
        .execute()
        
    data = res.data or []
    
    print(f"Encontrados {len(data)} registros recentes.")
    
    for row in data:
        print("---")
        print(f"Nome: {row.get('contact_name')}")
        print(f"Phone: {row.get('phone_number')}")
        print(f"Tags: {row.get('tags')}")
        print(f"Valor: {row.get('deal_value')}")
        print(f"Data: {row.get('created_at')}")

if __name__ == "__main__":
    debug_tags()
