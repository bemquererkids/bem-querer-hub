
"""
Show Available Slots Script
Fetches and displays REAL available slots from Clinicorp (Public Widget API).
"""
import asyncio
import sys
import os
import json
from datetime import date

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.clinicorp_service import ClinicorpClient

# CREDENCIAIS (Widget)
TEST_CONFIG = {
    "client_id": "bemquerer",
    "client_secret": "8b6b218c-b536-4db5-97a1-babffc283eec"
}

async def main():
    print("--- 🔍 Buscando Vagas Livres (Dados Reais) ---")
    
    client = ClinicorpClient(clinic_id="test", integration_config=TEST_CONFIG)
    
    # Parametros Obrigatórios do Widget
    params = {
        "date": "2025-12-22", # Data de hoje (ou futura para testar)
        "subscriber_id": "bemquerer",
        "code_link": "90984"
    }
    
    endpoint = "/appointment/get_avaliable_times_calendar"
    full_url = f"{endpoint}?date={params['date']}&subscriber_id={params['subscriber_id']}&code_link={params['code_link']}"
    
    print(f"📡 Chamando: {endpoint}")
    print(f"📅 Data: {params['date']}")
    
    try:
        res = await client._request("GET", full_url)
        
        print("\n--- 📦 RESULTADO ---")
        if not res:
            print("🚫 Lista vazia retornada (Sem vagas ou dia bloqueado).")
        else:
            print(json.dumps(res, indent=2, ensure_ascii=False))
            print(f"\n✅ Total de Slots Livres: {len(res)}")

    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    asyncio.run(main())
