"""Test webhook and save results to file"""
import asyncio
import sys
import os
import json
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), 'backend', '.env')
load_dotenv(env_path)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.api.webhooks import receive_whatsapp_message
from fastapi import BackgroundTasks

test_payload = {
    "event": "messages.upsert",
    "instance": "bemquerer",
    "data": {
        "messages": [{
            "key": {
                "remoteJid": "5511999999999@s.whatsapp.net",
                "id": "TEST_MESSAGE_123",
                "fromMe": False
            },
            "pushName": "João Teste",
            "message": {
                "conversation": "Olá, gostaria de agendar uma consulta"
            },
            "messageTimestamp": 1703500000
        }]
    }
}

async def test():
    result_file = open('test_result.txt', 'w', encoding='utf-8')
    
    try:
        result_file.write("=== TESTE WEBHOOK ===\n\n")
        
        background_tasks = BackgroundTasks()
        result = await receive_whatsapp_message(test_payload, background_tasks)
        
        result_file.write(f"Resultado: {json.dumps(result, indent=2, ensure_ascii=False)}\n\n")
        
        if result.get('status') == 'upsert_processed':
            result_file.write("✅ SUCESSO! Webhook processado.\n")
            result_file.write(f"Clinic ID: {result.get('clinic_id')}\n")
        else:
            result_file.write(f"❌ ERRO: {result.get('message', 'Unknown')}\n")
        
        result_file.close()
        print("✅ Resultado salvo em test_result.txt")
        
    except Exception as e:
        result_file.write(f"ERRO: {str(e)}\n")
        result_file.close()
        print(f"❌ Erro: {e}")

asyncio.run(test())
