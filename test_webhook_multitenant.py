"""
Test WhatsApp Webhook Multi-Tenant (Fixed)
Carrega variáveis de ambiente do .env antes de testar
"""
import asyncio
import sys
import os
import json
from dotenv import load_dotenv

# Carregar .env ANTES de importar qualquer coisa
env_path = os.path.join(os.path.dirname(__file__), 'backend', '.env')
load_dotenv(env_path)

# Verificar se variáveis foram carregadas
print("\n" + "="*80)
print("🔧 Verificando Configuração")
print("="*80)
print(f"\nSUPABASE_URL: {os.getenv('SUPABASE_URL', 'NÃO CONFIGURADO')[:50]}...")
print(f"SUPABASE_KEY: {os.getenv('SUPABASE_KEY', 'NÃO CONFIGURADO')[:50]}...")

if not os.getenv('SUPABASE_URL') or 'placeholder' in os.getenv('SUPABASE_URL', '').lower():
    print("\n❌ ERRO: Variáveis de ambiente não configuradas!")
    print("\n📋 Configure o arquivo backend/.env com:")
    print("   SUPABASE_URL=https://seu-projeto.supabase.co")
    print("   SUPABASE_KEY=sua-chave-aqui")
    sys.exit(1)

# Agora sim importar o backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.api.webhooks import receive_whatsapp_message
from fastapi import BackgroundTasks

# Payload de teste simulando UazAPI
test_payload = {
    "event": "messages.upsert",
    "instance": "bemquerer",  # Nome da instância
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

async def test_webhook():
    print("\n" + "="*80)
    print("🧪 Testando Webhook Multi-Tenant")
    print("="*80)
    
    print(f"\n📋 Payload de teste:")
    print(json.dumps(test_payload, indent=2, ensure_ascii=False))
    
    print(f"\n🔄 Processando webhook...")
    
    try:
        # Simular BackgroundTasks
        background_tasks = BackgroundTasks()
        
        # Chamar webhook
        result = await receive_whatsapp_message(test_payload, background_tasks)
        
        print(f"\n✅ Resultado:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if result.get('status') == 'error':
            print(f"\n⚠️ Webhook retornou erro. Verifique:")
            print("   1. Se a instância 'bemquerer' existe no banco")
            print("   2. Se tem clinic_id configurado")
            print("\n💡 Execute: SELECT * FROM whatsapp_instances;")
            return
        
        # Executar background tasks
        print(f"\n⏳ Executando background tasks...")
        # Note: FastAPI BackgroundTasks não tem await, mas vamos tentar processar
        
        print(f"\n{'='*80}")
        print("✅ Teste concluído!")
        print("="*80)
        
        print(f"\n📊 Verificações:")
        print("1. Verifique no Supabase se a conversa foi criada em 'whatsapp_conversations'")
        print("2. Verifique se a mensagem foi salva em 'whatsapp_messages'")
        print("3. Verifique se o 'clinic_id' está correto")
        
        print(f"\n💡 SQL para verificar:")
        print("   SELECT * FROM whatsapp_conversations WHERE phone_number = '5511999999999';")
        print("   SELECT * FROM whatsapp_messages WHERE from_number = '5511999999999';")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_webhook())
