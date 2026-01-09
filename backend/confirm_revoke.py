
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

def confirm_revoke():
    phone = "5511993308484"
    url_send = f"{BASE_URL}/send/text"
    
    print("Enviando msg...")
    res = requests.post(url_send, json={"number": phone, "text": "Teste Final Revoke", "options": {"delay": 1000}}, headers=HEADERS)
    if res.status_code != 200:
        print("Erro envio")
        return
        
    data = res.json()
    msg_id = None
    if 'key' in data and 'id' in data['key']: msg_id = data['key']['id']
    elif 'id' in data: msg_id = data['id']
    
    if not msg_id:
        print("Sem ID")
        return
        
    print(f"ID: {msg_id}")
    time.sleep(2)
    
    endpoints = [
        f"{BASE_URL}/message/revoke",
        f"{BASE_URL}/message/delete",
        f"{BASE_URL}/messages/delete",
        f"{BASE_URL}/chat/revokeMessage",
        f"{BASE_URL}/message/revokeMessage/{INSTANCE}" # O primeiro que tentei e falhou com 405
    ]
    
    payload = {
        "id": msg_id,
        "remoteJid": f"{phone}@s.whatsapp.net"
    }
    
    print("Tentando Revoke...")
    for url in endpoints:
        print(f"Testing {url}...")
        try:
            # Tentar DELETE e POST
            r = requests.post(url, json=payload, headers=HEADERS)
            if r.status_code == 200:
                print(f"✅ SUCESSO POST em: {url}")
                return
            
            r = requests.delete(url, json=payload, headers=HEADERS)
            if r.status_code == 200:
                print(f"✅ SUCESSO DELETE em: {url}")
                return
                
        except Exception as e:
            print(e)

if __name__ == "__main__":
    confirm_revoke()
