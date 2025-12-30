"""
Script para testar o endpoint de conversas diretamente com Supabase
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Set environment variables (use your actual values)
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

# Fallback/Override if needed
if not os.getenv('SUPABASE_SERVICE_KEY'):
    print("❌ SUPABASE_SERVICE_KEY não encontrada no arquivo .env")
    sys.exit(1)

from app.core.database import SupabaseClient

def test_conversations():
    print("\n🔍 Testando busca de conversas...")
    
    try:
        supabase = SupabaseClient.get_admin_client()
        
        # Query conversations
        response = supabase.table("whatsapp_conversations") \
            .select("*") \
            .order("last_message_at", desc=True) \
            .limit(10) \
            .execute()
        
        print(f"\n✅ Encontradas {len(response.data)} conversas:")
        
        for conv in response.data:
            print(f"\n  📱 {conv.get('contact_name', 'N/A')}")
            print(f"     Telefone: {conv.get('phone_number', 'N/A')}")
            print(f"     Última msg: {conv.get('last_message', 'N/A')[:50]}...")
            print(f"     ID: {conv.get('id')}")
            
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_conversations()
