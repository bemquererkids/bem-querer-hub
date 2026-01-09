import sys
sys.path.insert(0, 'c:/projetos/sistemabemquerer-v2/backend')

from app.core.database import SupabaseClient

supabase = SupabaseClient.get_admin_client()

message_ids = [
    "b07c96b2-c35e-4aaa-8680-cf729b12a9ac",
    "e2015804-9b38-41cf-9f52-22e3be8e67ea"
]

print("🔍 Verificando mensagens específicas...\n")

for msg_id in message_ids:
    result = supabase.table('whatsapp_messages').select('*').eq('id', msg_id).execute()
    
    if result.data:
        msg = result.data[0]
        print(f"✅ Mensagem ID: {msg_id}")
        print(f"   message_id: {msg.get('message_id')}")
        print(f"   conversation_id: {msg.get('conversation_id')}")
        print(f"   content: {msg.get('content')[:60]}...")
        print(f"   is_from_me: {msg.get('is_from_me')}")
        print(f"   from: {msg.get('from_number')}")
        print(f"   to: {msg.get('to_number')}")
        print(f"   created_at: {msg.get('created_at')}")
        
        conv_id = msg.get('conversation_id')
        if conv_id:
            conv = supabase.table('whatsapp_conversations').select('*').eq('id', conv_id).execute()
            if conv.data:
                print(f"   Conversa: {conv.data[0].get('contact_name')} - {conv.data[0].get('phone_number')}")
        print()
    else:
        print(f"❌ Mensagem NÃO encontrada: {msg_id}\n")

print("\n📋 Últimas 5 mensagens:")
recent = supabase.table('whatsapp_messages').select('*').order('created_at', desc=True).limit(5).execute()
for msg in recent.data:
    print(f"  {msg.get('created_at')} | {msg.get('content')[:40]}... | from_me: {msg.get('is_from_me')}")
