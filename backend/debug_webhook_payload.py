import os
from supabase import create_client
from dotenv import load_dotenv
import json

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

print("🔍 Verificando últimas conversas e mensagens...\n")

# Buscar últimas conversas
print("=" * 60)
print("📱 ÚLTIMAS CONVERSAS:")
print("=" * 60)
conversations = supabase.table('whatsapp_conversations').select('*').order('updated_at', desc=True).limit(5).execute()

for conv in conversations.data:
    print(f"\n✅ Conversa ID: {conv.get('id')}")
    print(f"   - Nome: {conv.get('contact_name')}")
    print(f"   - Telefone: {conv.get('phone_number')}")
    print(f"   - Avatar: {conv.get('avatar', 'N/A')[:80] if conv.get('avatar') else 'N/A'}...")
    print(f"   - Última mensagem: {conv.get('last_message', '')[:50]}...")
    print(f"   - Tags: {conv.get('tags')}")
    print(f"   - Updated: {conv.get('updated_at')}")

# Buscar mensagens da conversa do Pedro Reichow
print("\n" + "=" * 60)
print("📨 MENSAGENS DO PEDRO REICHOW:")
print("=" * 60)

# Primeiro encontrar a conversa dele
pedro_conv = supabase.table('whatsapp_conversations').select('*').ilike('contact_name', '%Pedro%').execute()

if pedro_conv.data:
    conv_id = pedro_conv.data[0]['id']
    phone = pedro_conv.data[0]['phone_number']
    print(f"\n📞 Conversa encontrada:")
    print(f"   - ID: {conv_id}")
    print(f"   - Telefone: {phone}")
    print(f"   - Avatar: {pedro_conv.data[0].get('avatar', 'N/A')}")
    
    # Buscar mensagens
    messages = supabase.table('whatsapp_messages').select('*').eq('conversation_id', conv_id).order('timestamp', desc=False).execute()
    
    print(f"\n📬 Total de mensagens: {len(messages.data)}")
    for msg in messages.data:
        direction = "🟢 Recebida" if not msg.get('is_from_me') else "🔵 Enviada"
        print(f"\n{direction}:")
        print(f"   - ID: {msg.get('message_id')}")
        print(f"   - Conteúdo: {msg.get('content')[:80]}...")
        print(f"   - De: {msg.get('from_number')}")
        print(f"   - Para: {msg.get('to_number')}")
        print(f"   - Timestamp: {msg.get('timestamp')}")
else:
    print("❌ Conversa do Pedro não encontrada")

# Verificar se há conversas com número estranho
print("\n" + "=" * 60)
print("🔍 VERIFICANDO NÚMEROS SUSPEITOS:")
print("=" * 60)

all_convs = supabase.table('whatsapp_conversations').select('phone_number, contact_name').execute()
for conv in all_convs.data:
    phone = conv.get('phone_number', '')
    # Números brasileiros devem começar com 55 e ter 12-13 dígitos
    if phone and (not phone.startswith('55') or len(phone) > 15 or len(phone) < 12):
        print(f"⚠️  Número suspeito: {phone} ({conv.get('contact_name')})")
