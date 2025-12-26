"""Check webhook test results"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.database import get_supabase

supabase = get_supabase()

print("\n" + "="*80)
print("📊 Verificando Resultados do Teste")
print("="*80)

# Check instances
print("\n1. Instâncias WhatsApp:")
instances = supabase.table('whatsapp_instances').select('*').execute()
if instances.data:
    for inst in instances.data:
        print(f"   ✅ {inst['instance_name']} (clinic: {inst['clinic_id'][:8]}...)")
else:
    print("   ❌ Nenhuma instância encontrada")

# Check conversations
print("\n2. Conversas:")
convs = supabase.table('whatsapp_conversations').select('*').execute()
if convs.data:
    for conv in convs.data:
        print(f"   ✅ {conv['phone_number']} - {conv['contact_name']}")
        print(f"      Clinic: {conv['clinic_id'][:8]}...")
        print(f"      Última msg: {conv['last_message'][:50]}...")
else:
    print("   ❌ Nenhuma conversa encontrada")

# Check messages
print("\n3. Mensagens:")
msgs = supabase.table('whatsapp_messages').select('*').limit(5).execute()
if msgs.data:
    for msg in msgs.data:
        print(f"   ✅ De: {msg['from_number']}")
        print(f"      Clinic: {msg['clinic_id'][:8]}...")
        print(f"      Conteúdo: {msg['content'][:50]}...")
else:
    print("   ❌ Nenhuma mensagem encontrada")

print("\n" + "="*80)
