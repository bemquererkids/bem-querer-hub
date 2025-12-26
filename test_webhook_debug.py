"""Test webhook with detailed logging"""
import asyncio
import sys
import os
import json
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), 'backend', '.env')
load_dotenv(env_path)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Patch save_whatsapp_message to add logging
from app.api import webhooks
original_save = webhooks.save_whatsapp_message

async def logged_save(*args, **kwargs):
    print(f"\n🔍 save_whatsapp_message chamado com:")
    print(f"   clinic_id: {kwargs.get('clinic_id', args[0] if args else 'N/A')}")
    print(f"   phone: {kwargs.get('phone', args[1] if len(args) > 1 else 'N/A')}")
    print(f"   content: {kwargs.get('content', args[4] if len(args) > 4 else 'N/A')}")
    
    try:
        result = await original_save(*args, **kwargs)
        print(f"   ✅ Salvou com sucesso!")
        return result
    except Exception as e:
        print(f"   ❌ Erro ao salvar: {e}")
        import traceback
        traceback.print_exc()
        raise

webhooks.save_whatsapp_message = logged_save

from app.api.webhooks import receive_whatsapp_message
from fastapi import BackgroundTasks

test_payload = {
    "event": "messages.upsert",
    "instance": "bemquerer",
    "data": {
        "messages": [{
            "key": {
                "remoteJid": "5511999999999@s.whatsapp.net",
                "id": "TEST_MSG_" + str(int(asyncio.get_event_loop().time())),
                "fromMe": False
            },
            "pushName": "João Teste Debug",
            "message": {
                "conversation": "Teste com logging detalhado"
            },
            "messageTimestamp": 1703500000
        }]
    }
}

async def test():
    print("\n" + "="*80)
    print("🧪 TESTE WEBHOOK COM LOGGING DETALHADO")
    print("="*80)
    
    try:
        background_tasks = BackgroundTasks()
        result = await receive_whatsapp_message(test_payload, background_tasks)
        
        print(f"\n📊 Resultado webhook:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Executar background tasks manualmente
        print(f"\n⏳ Executando background tasks...")
        for task in background_tasks.tasks:
            await task.func(*task.args, **task.kwargs)
        
        print(f"\n✅ Background tasks executados!")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test())

# Verificar banco
print("\n" + "="*80)
print("📊 VERIFICANDO BANCO DE DADOS")
print("="*80)

from app.core.database import get_supabase
sb = get_supabase()

convs = sb.table('whatsapp_conversations').select('*').execute()
msgs = sb.table('whatsapp_messages').select('*').execute()

print(f"\n📞 Conversas: {len(convs.data)}")
if convs.data:
    for c in convs.data:
        print(f"   - {c['phone_number']}: {c['contact_name']}")

print(f"\n💬 Mensagens: {len(msgs.data)}")
if msgs.data:
    for m in msgs.data:
        print(f"   - {m['from_number']}: {m['content'][:50]}")

print("\n" + "="*80)
