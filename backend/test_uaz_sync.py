from app.services.uazapi_service import get_uazapi_service
import sys
import os
from dotenv import load_dotenv

# Load env from .env file in the same directory
load_dotenv()

def test_sync(phone):
    print(f"🔄 Testando Sincronização com UazAPI para: {phone}")
    
    uaz = get_uazapi_service()
    
    # 1. Atualizar Status para 'Agendado' (Teste)
    print("1️⃣ Enviando Status 'Agendado'...")
    res = uaz.update_lead(phone, status="Agendado")
    print(f"   Resultado Status: {res}")
    
    # 2. Adicionar Tag 'Agendado' (para ter certeza visual)
    print("2️⃣ Adicionando Tag 'Agendado'...")
    res_tag = uaz.add_tag(phone, "Agendado")
    print(f"   Resultado Tag: {res_tag}")
    
    print("\n✅ Teste Concluído! Verifique no seu painel UazAPI se a tag apareceu.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python test_uaz_sync.py <TELEFONE>")
        print("Ex: python test_uaz_sync.py 5511999999999")
    else:
        test_sync(sys.argv[1])
