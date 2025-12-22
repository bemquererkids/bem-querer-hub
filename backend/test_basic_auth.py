
"""
Test Basic Auth Credentials
Testing with User/Pass provided:
User: luiz.bezerra@bemquerer
Pass: Vanessa123@backend/
"""
import asyncio
import sys
import httpx
import base64

async def test_basic_auth():
    print("--- Teste de Autenticação Básica (Login Real) ---")
    
    username = "luiz.bezerra@bemquerer"
    password = "Vanessa123@backend/"
    
    # Encode Basic Auth
    auth_str = f"{username}:{password}"
    auth_bytes = auth_str.encode('ascii')
    base64_bytes = base64.b64encode(auth_bytes)
    base64_auth = base64_bytes.decode('ascii')
    
    headers = {
        "Authorization": f"Basic {base64_auth}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        # Tentativas de Header de Contexto
        "subscriber_id": "bemquerer",
        "X-Clinic-ID": "bemquerer"
    }
    
    base_url = "https://api.clinicorp.com/v1"
    
    endpoints = [
        "/appointments?date=2025-12-22", # Tentar com parametro
        "/professionals",
        "/users/me", # Quem sou eu?
        "/me"
    ]
    
    async with httpx.AsyncClient() as client:
        for ep in endpoints:
            print(f"\nTentando: {ep}")
            try:
                # Tenta sem data primeiro
                res = await client.get(f"{base_url}{ep}", headers=headers)
                print(f"   Status: {res.status_code}")
                if res.status_code == 200:
                    print(f"   [SUCESSO] Dados: {str(res.json())[:100]}...")
                elif res.status_code == 401:
                    print("   [ERRO] 401 Não Autorizado (Credenciais rejeitadas)")
                else:
                    print(f"   [ERRO] {res.status_code}: {res.text[:100]}")
                    
            except Exception as e:
                print(f"   [FALHA] {e}")

if __name__ == "__main__":
    asyncio.run(test_basic_auth())
