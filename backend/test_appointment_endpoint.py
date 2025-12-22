"""
Test Appointment Endpoint Script
Targets /appointment/get_appointment
"""
import asyncio
import sys
import os
from datetime import date

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.clinicorp_service import ClinicorpClient

# CREDENCIAIS FORNECIDAS
TEST_CONFIG = {
    "client_id": "bemquerer",
    "client_secret": "8b6b218c-b536-4db5-97a1-babffc283eec"
}

async def main():
    print("--- Teste de Endpoint de Agendamentos (Schedules) ---")
    client = ClinicorpClient(clinic_id="test", integration_config=TEST_CONFIG)
    
    # Endpoint alternativo comum
    endpoint = "/schedules"
    
    # Parâmetros prováveis
    today_iso = str(date.today())
    
    params_list = [
        {"date": today_iso},
        {"start": f"{today_iso}T00:00:00", "end": f"{today_iso}T23:59:59"},
        {"start_date": today_iso, "end_date": today_iso},
        {} # Sem filtro
    ]

    for params in params_list:
        query_str = "&".join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{endpoint}?{query_str}" if query_str else endpoint
        
        print(f"\nTentando: {full_url}")
        try:
            # Tenta GET
            res = await client._request("GET", full_url)
            print(f"   [SUCESSO] Retorno: {str(res)[:200]}...") 
        except Exception as e:
            print(f"   [FALHA] {e}")

if __name__ == "__main__":
    asyncio.run(main())
