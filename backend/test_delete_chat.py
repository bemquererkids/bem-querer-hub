
import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("UAZAPI_BASE_URL", "https://bemquerer.uazapi.com")
if BASE_URL.endswith('/'): BASE_URL = BASE_URL[:-1]
INSTANCE = os.getenv("UAZAPI_INSTANCE", "bemquerer")
TOKEN = os.getenv("UAZAPI_TOKEN")

HEADERS = {
    "apikey": TOKEN,
    "token": TOKEN,
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_delete_chat():
    phone = "5511993308484" # Usar um numero de teste real
    
    print(f"Testing Delete Chat for {phone}")
    
    # 1. Enviar msg para garantir que existe chat
    requests.post(f"{BASE_URL}/send/text", json={"number": phone, "text": "Msg para apagar"}, headers=HEADERS)
    

    endpoints = [
         # Tentar endpoints comuns de Evolution/UazAPI
        f"{BASE_URL}/chat/delete/{INSTANCE}",
        f"{BASE_URL}/chat/clear/{INSTANCE}",
        f"{BASE_URL}/chat/deleteChat/{INSTANCE}", # Legacy?
        
        # Sem instance no path (UazAPI v2?)
        f"{BASE_URL}/chat/delete",
        f"{BASE_URL}/chat/clear",
        
        # Outras variacoes
        f"{BASE_URL}/messages/delete", # As vezes serve pra chat se passar all?
    ]
    
    # Payloads variados
    payloads = [
        {"number": phone},
        {"phone": phone},
        {"remoteJid": f"{phone}@s.whatsapp.net"},
        {"id": f"{phone}@s.whatsapp.net"}
    ]
    
    for url in endpoints:
        print(f"\n--- Testing Endpoint: {url} ---")
        for p in payloads:
            try:
                # Test POST
                r = requests.post(url, json=p, headers=HEADERS)
                print(f"POST {p.keys()} -> {r.status_code} | {r.text[:100]}")
                if r.status_code == 200 and "error" not in r.text.lower():
                    print("✅ SUCESSO POST?")
                    
                # Test DELETE
                r = requests.delete(url, json=p, headers=HEADERS)
                print(f"DELETE {p.keys()} -> {r.status_code} | {r.text[:100]}")
                if r.status_code == 200 and "error" not in r.text.lower():
                    print("✅ SUCESSO DELETE?")
            except Exception as e:
                print(f"Err: {e}")


if __name__ == "__main__":
    test_delete_chat()
