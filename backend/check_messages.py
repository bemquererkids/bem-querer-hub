import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

message_ids = [
    "b07c96b2-c35e-4aaa-8680-cf729b12a9ac",
    "e2015804-9b38-41cf-9f52-22e3be8e67ea"
]

print("🔍 Verificando mensagens específicas...\n")

for msg_id in message_ids:
    # Buscar por UUID (id)
    result = supabase.table('whatsapp_messages').select('*').eq('id', msg_id).execute()
    
    if result.data:
        msg = result.data[0]
        print(f"✅ Mensagem encontrada (ID: {msg_id}):")
        print(f"   - message_id: {msg.get('message_id')}")
        print(f"   - conversation_id: {msg.get('conversation_id')}")
        print(f"   - content: {msg.get('content')[:50]}...")
        print(f"   - is_from_me: {msg.get('is_from_me')}")
        print(f"   - from_number: {msg.get('from_number')}")
        print(f"   - to_number: {msg.get('to_number')}")
        print(f"   - created_at: {msg.get('created_at')}")
        
        # Buscar conversa relacionada
        conv_id = msg.get('conversation_id')
        if conv_id:
            conv = supabase.table('whatsapp_conversations').select('*').eq('id', conv_id).execute()
            if conv.data:
                print(f"   - Conversa: {conv.data[0].get('contact_name')} ({conv.data[0].get('phone_number')})")
        print()
    else:
        # Tentar buscar por message_id
        result2 = supabase.table('whatsapp_messages').select('*').eq('message_id', msg_id).execute()
        if result2.data:
            print(f"✅ Mensagem encontrada por message_id: {msg_id}")
            print(f"   UUID real: {result2.data[0].get('id')}")
            print()
        else:
            print(f"❌ Mensagem NÃO encontrada: {msg_id}\n")

# Listar últimas 5 mensagens
print("\n📋 Últimas 5 mensagens no banco:")
recent = supabase.table('whatsapp_messages').select('*').order('created_at', desc=True).limit(5).execute()
for msg in recent.data:
    print(f"  - {msg.get('created_at')} | {msg.get('content')[:30]}... | from_me: {msg.get('is_from_me')}")
