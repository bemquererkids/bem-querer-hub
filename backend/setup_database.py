import asyncio
import sys
import os
from dotenv import load_dotenv

# Force load .env from the same directory as the script (or parent)
# Assuming script is in backend/, .env is in backend/
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
# Actually the script is in backend/, so dirname(abspath) is backend/.
# But let's be safe.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), '../.env')) # Try parent if running from root
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')) # Try current

from supabase import create_client, Client
from app.core.config import settings

async def setup_db():
    print("--- Verificando Conexão e Tabelas ---")
    
    # 1. Conexão
    try:
        # Using Service Key for Admin tasks
        key = settings.SUPABASE_SERVICE_KEY or settings.SUPABASE_KEY
        url = settings.SUPABASE_URL
        
        if "placeholder" in url:
            print("❌ Erro: Credenciais ainda são placeholders no .env")
            return

        supabase: Client = create_client(url, key)
        print(f"✅ Conectado em: {url}")
    except Exception as e:
        print(f"❌ Erro de Conexão: {e}")
        return

    # 2. Testar Inserção (Seed)
    print("\n--- Tentando Cadastrar Clínica (Bem-Querer) ---")
    try:
        clinic_data = {
            "id": "00000000-0000-0000-0000-000000000001",
            "nome_fantasia": "Bem-Querer Odontologia",
            "slug": "bem-querer",
            "status": "ativo"
        }
        # Upsert = Insert or Update
        res = supabase.table("clinicas").upsert(clinic_data).execute()
        
        if res.data:
            print("✅ SUCESSO! A tabela 'clinicas' existe e a clínica foi cadastrada.")
            print("🚀 O banco de dados está pronto para uso.")
        else:
            print("⚠️ A API respondeu sem dados (mas sem erro de tabela).")

    except Exception as e:
        error_msg = str(e)
        if "relation" in error_msg and "does not exist" in error_msg:
            print("❌ ERRO CRÍTICO: As tabelas NÃO existem.")
            print("👉 Você PRECISA rodar o código SQL no Painel do Supabase.")
        else:
            print(f"❌ Erro Genérico: {e}")

if __name__ == "__main__":
    asyncio.run(setup_db())
