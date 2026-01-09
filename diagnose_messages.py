"""
Script para diagnosticar e corrigir mensagens órfãs
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.config import settings
from supabase import create_client

# Create direct client
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

print("🔍 DIAGNÓSTICO DE MENSAGENS\n")
print("="*60)

# IDs específicos mencionados
message_ids = [
    "b07c96b2-c35e-4aaa-8680-cf729b12a9ac",
    "e2015804-9b38-41cf-9f52-22e3be8e67ea"
]

print("\n1️⃣ Verificando mensagens específicas:")
print("-"*60)

for msg_id in message_ids:
    result = supabase.table('whatsapp_messages').select('*').eq('id', msg_id).execute()
    
    if result.data:
        msg = result.data[0]
        print(f"\n✅ Mensagem: {msg_id}")
        print(f"   📝 Conteúdo: {msg.get('content')[:60]}...")
        print(f"   📞 De: {msg.get('from_number')}")
        print(f"   📞 Para: {msg.get('to_number')}")
        print(f"   👤 É minha: {msg.get('is_from_me')}")
        print(f"   🔗 Conversa ID: {msg.get('conversation_id')}")
        print(f"   🕐 Criada em: {msg.get('created_at')}")
        
        # Verificar conversa
        conv_id = msg.get('conversation_id')
        if conv_id:
            conv = supabase.table('whatsapp_conversations').select('*').eq('id', conv_id).execute()
            if conv.data:
                c = conv.data[0]
                print(f"   💬 Conversa: {c.get('contact_name')} ({c.get('phone_number')})")
            else:
                print(f"   ⚠️  CONVERSA NÃO ENCONTRADA!")
    else:
        print(f"\n❌ Mensagem NÃO encontrada: {msg_id}")

print("\n\n2️⃣ Últimas 10 mensagens no sistema:")
print("-"*60)

recent = supabase.table('whatsapp_messages') \
    .select('id, content, is_from_me, from_number, to_number, conversation_id, created_at') \
    .order('created_at', desc=True) \
    .limit(10) \
    .execute()

for i, msg in enumerate(recent.data, 1):
    print(f"\n{i}. {msg.get('created_at')}")
    print(f"   Conteúdo: {msg.get('content')[:50]}...")
    print(f"   De: {msg.get('from_number')} → Para: {msg.get('to_number')}")
    print(f"   É minha: {msg.get('is_from_me')} | Conv: {msg.get('conversation_id')[:8]}...")

print("\n\n3️⃣ Conversas ativas:")
print("-"*60)

convs = supabase.table('whatsapp_conversations') \
    .select('id, contact_name, phone_number, last_message, last_message_at') \
    .order('last_message_at', desc=True) \
    .limit(5) \
    .execute()

for i, conv in enumerate(convs.data, 1):
    print(f"\n{i}. {conv.get('contact_name')} ({conv.get('phone_number')})")
    print(f"   ID: {conv.get('id')}")
    print(f"   Última msg: {conv.get('last_message')[:50] if conv.get('last_message') else 'N/A'}...")
    print(f"   Quando: {conv.get('last_message_at')}")
    
    # Contar mensagens nesta conversa
    count = supabase.table('whatsapp_messages') \
        .select('id', count='exact') \
        .eq('conversation_id', conv.get('id')) \
        .execute()
    print(f"   Total de mensagens: {count.count}")

print("\n\n4️⃣ Procurando mensagens órfãs (sem conversa válida):")
print("-"*60)

# Buscar todas as conversas válidas
all_convs = supabase.table('whatsapp_conversations').select('id').execute()
valid_conv_ids = [c['id'] for c in all_convs.data]

# Buscar mensagens
all_msgs = supabase.table('whatsapp_messages') \
    .select('id, conversation_id, content, created_at') \
    .order('created_at', desc=True) \
    .limit(50) \
    .execute()

orphans = [m for m in all_msgs.data if m.get('conversation_id') not in valid_conv_ids]

if orphans:
    print(f"\n⚠️  Encontradas {len(orphans)} mensagens órfãs:")
    for msg in orphans[:5]:
        print(f"   - {msg.get('id')}: {msg.get('content')[:40]}...")
else:
    print("\n✅ Nenhuma mensagem órfã encontrada")

print("\n" + "="*60)
print("✅ Diagnóstico completo!\n")
