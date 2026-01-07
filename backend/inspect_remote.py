import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.core.database import get_supabase

def inspect():
    print("🔍 Inspecionando Banco Remoto (Configuração Local)...")
    db = get_supabase()
    res = db.table("whatsapp_conversations").select("contact_name").limit(10).order("created_at", desc=True).execute()
    print("Últimos 10 contatos:")
    for row in res.data:
        print(f" - {row.get('contact_name')}")

if __name__ == "__main__":
    inspect()
