import requests
import json
import time

URL = "http://localhost:8000/webhooks/whatsapp"

payload = {
    "event": "messages.upsert",
    "instance": "demo-instance",
    "data": {
        "key": {
            "remoteJid": "5511999999999@s.whatsapp.net",
            "fromMe": False,
            "id": "SIMULATION_TEST_123"
        },
        "pushName": "Luiz Teste",
        "message": {
            "conversation": "Ola, vi voces no Google e gostaria de agendar uma limpeza"
        }
    }
}

print(f"🚀 Enviando payload para {URL}...")
try:
    response = requests.post(URL, json=payload)
    print(f"✅ Status Code: {response.status_code}")
    print(f"📦 Resposta: {response.json()}")
    
    # Aguarda um pouco para os logs de background aparecerem
    print("\n⏳ Aguardando processamento da IA...")
    time.sleep(5)
except Exception as e:
    print(f"❌ Erro: {e}")
