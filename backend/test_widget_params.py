"""
Test Widget Params Script
Testing endpoints with specific query params provided by user:
- subscriber_id
- code_link
- date
"""
import asyncio
import sys
import os
from datetime import date

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.clinicorp_service import ClinicorpClient

# CREDENCIAIS (Para manter a autenticação Bearer, se necessário)
TEST_CONFIG = {
    "client_id": "bemquerer",
    "client_secret": "8b6b218c-b536-4db5-97a1-babffc283eec"
}

async def main():
    print("--- Teste de Parâmetros do Widget ---")
    client = ClinicorpClient(clinic_id="test", integration_config=TEST_CONFIG)
    
    # Parâmetros Específicos
    query_params = {
        "subscriber_id": "bemquerer",
        "code_link": "90984",
        "date": "2025-12-22" # Data Futura para garantir
    }
    
    # Construir Query String
    qs = "&".join([f"{k}={v}" for k,v in query_params.items()])
    
    endpoints = [
        "/appointment/get_avaliable_times_calendar",
        "/public/appointment/get_avaliable_times_calendar",
        "/agendamento/get_avaliable_times_calendar"
    ]

    for ep in endpoints:
        full_url = f"{ep}?{qs}"
        print(f"\nTentando: {full_url}")
        try:
            # Tenta GET
            res = await client._request("GET", full_url)
            print(f"   [SUCESSO] Retorno: {str(res)[:200]}")
        except Exception as e:
            print(f"   [FALHA] {e}")

if __name__ == "__main__":
    asyncio.run(main())
