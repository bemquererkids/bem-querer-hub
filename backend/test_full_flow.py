import requests
import json
import time

BASE_URL = "http://localhost:8000"
WEBHOOK_URL = f"{BASE_URL}/webhooks/whatsapp"
CRM_URL = f"{BASE_URL}/crm/deals"

payload = {
    "event": "messages.upsert",
    "instance": "demo-instance",
    "data": {
        "key": {
            "remoteJid": "5511999999999@s.whatsapp.net",
            "fromMe": False,
            "id": "FINAL_TEST_TOKEN"
        },
        "pushName": "Luiz Teste Verificacao",
        "message": {
            "conversation": "Quero saber sobre implantes, vi no Google"
        }
    }
}

print("1. 📩 Enviando Webhook...")
res1 = requests.post(WEBHOOK_URL, json=payload)
print(f"   Status: {res1.status_code} - {res1.json()}")

print("\n2. ⏳ Aguardando processamento (Mock)...")
time.sleep(2)

print("\n3. 📊 Verificando no CRM...")
res2 = requests.get(CRM_URL)
if res2.status_code == 200:
    deals = res2.json()
    found = False
    for deal in deals:
        if "Luiz Teste Verificacao" in deal.get("patientName", ""):
            print(f"   ✅ Lead encontrado no CRM: {deal}")
            found = True
            break
    if not found:
        print("   ❌ Lead nao encontrado na lista (pode ser delay no mock ou erro de storage)")
else:
    print(f"   ❌ Erro ao acessar CRM: {res2.status_code}")
