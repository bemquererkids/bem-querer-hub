
import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("UAZAPI_BASE_URL", "https://bemquerer.uazapi.com")
if BASE_URL.endswith('/'): BASE_URL = BASE_URL[:-1]
INSTANCE = os.getenv("UAZAPI_INSTANCE", "bemquerer")
TOKEN = os.getenv("UAZAPI_TOKEN")

# Headers com suporte a múltiplos formatos
HEADERS = {
    "apikey": TOKEN,
    "token": TOKEN,
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_delete():
    # 1. Enviar mensagem
    phone = "5511993308484"
    
    print(f"1. Enviando mensagem para {phone} usando {BASE_URL}/send/text ...")
    url_send = f"{BASE_URL}/send/text"
    
    payload = {
        "number": phone,
        "text": "Teste de Delete Automático v2",
        "options": {
            "delay": 1000
        }
    }
    
    msg_id = None
    try:
        res = requests.post(url_send, json=payload, headers=HEADERS)
        print("Send Response:", res.text)
        
        if res.status_code == 200:
            data = res.json()
            # Tentar extrair ID
            if 'key' in data and 'id' in data['key']:
                msg_id = data['key']['id']
            elif 'id' in data:
                msg_id = data['id']
            elif 'messageId' in data:
                msg_id = data['messageId']
        
        if not msg_id:
            print("❌ Não consegui pegar o ID da mensagem enviada.")
            return

        print(f"✅ Mensagem enviada! ID: {msg_id}")
        
        # Esperar 
        print("⏳ Aguardando 3 segundos...")
        time.sleep(3)
        
        # 2. Tentar Deletar (Revoke)
        print("2. Tentando deletar (revoke)...")
        
        endpoints_to_test = [
            f"{BASE_URL}/message/revoke",
            f"{BASE_URL}/message/delete",
            f"{BASE_URL}/chat/revokeMessage",
            f"{BASE_URL}/revoke/message",
             # Tentar endpoint estilo Evolution/Baileys genérico se a URL base fosse diferente, mas vamos tentar na base atual
            f"{BASE_URL}/messages/delete" 
        ]

        # Payloads comuns
        payloads = [
             # Payload 1: Padrão Baileys
            {
                "number": phone,
                "key": {
                    "id": msg_id,
                    "fromMe": True
                }
            },
            # Payload 2: Padrão Z-API
            {
                "phone": phone,
                "messageId": msg_id
            },
            # Payload 3: Simples
            {
                "id": msg_id,
                "remoteJid": f"{phone}@s.whatsapp.net"
            }
        ]
        
        for url in endpoints_to_test:
            print(f"--- Tentando POST {url} ---")
            for p in payloads:
                try:
                    r = requests.delete(url, json=p, headers=HEADERS) # Tentar DELETE
                    if r.status_code == 405 or r.status_code == 404:
                         r = requests.post(url, json=p, headers=HEADERS) # Tentar POST
                    
                    print(f"Payload: {p.keys()} -> Code: {r.status_code}, Resp: {r.text[:100]}")
                    if r.status_code == 200:
                        print("✅ SUCESSO AO DELETAR??")
                        return
                except Exception as e:
                    print(f"Erro ao chamar {url}: {e}")

    except Exception as e:
        print(f"Erro Geral: {e}")

if __name__ == "__main__":
    test_delete()
