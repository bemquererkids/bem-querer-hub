
"""
Test Specific Endpoint Script
Targets /appointment/get_avaliable_times_calendar
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
    print("--- Teste de Endpoint Específico ---")
    client = ClinicorpClient(clinic_id="test", integration_config=TEST_CONFIG)
    
    # Lista de tentativas (Variações de URL)
    endpoints = [
        "/appointment/get_avaliable_times_calendar", # Como solicitado
        "/appointment/get_available_times_calendar", # Correção de inglês
        "/appointments/get_avaliable_times_calendar", # Plural
        "/appointments/get_available_times_calendar"
    ]
    
    # Parâmetros prováveis
    params = {
        "date": str(date.today()),
        "start_date": str(date.today()),
        "professional_id": "0" # Tenta pegar de todos ou id generico
    }

    for ep in endpoints:
        print(f"\nTentando: {ep}")
        try:
            # Tenta GET
            res = await client._request("GET", f"{ep}?date={params['date']}")
            print(f"   [SUCESSO] Retorno: {res}")
            break # Parar se funcionar
        except Exception as e:
            print(f"   [FALHA] {e}")

if __name__ == "__main__":
    asyncio.run(main())
