"""
Test Webhooks Endpoint
Targets /webhooks to see if we can register listeners.
"""
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.clinicorp_service import ClinicorpClient

TEST_CONFIG = {
    "client_id": "bemquerer",
    "client_secret": "8b6b218c-b536-4db5-97a1-babffc283eec"
}

async def main():
    print("--- Teste de Webhooks ---")
    client = ClinicorpClient(clinic_id="test", integration_config=TEST_CONFIG)
    
    try:
        # Tenta listar webhooks existentes
        print("1. Tentando listar webhooks configurados...")
        res = await client._request("GET", "/webhooks")
        print(f"   [SUCESSO] Webhooks: {res}")
    except Exception as e:
        print(f"   [FALHA] GET /webhooks: {e}")

    try:
        # Tenta endpoint alternativo de configurações
        print("\n2. Tentando acessar configurações da conta...")
        res = await client._request("GET", "/settings") # Ou /account
        print(f"   [SUCESSO] Configs: {str(res)[:100]}")
    except Exception as e:
        print(f"   [FALHA] GET /settings: {e}")

if __name__ == "__main__":
    asyncio.run(main())

