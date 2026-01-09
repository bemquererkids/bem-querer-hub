"""
Script para limpar conversas duplicadas
Mantém apenas a conversa com o telefone do CLIENTE (não da clínica)
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.database import SupabaseClient

supabase = SupabaseClient.get_admin_client()

print("🧹 LIMPEZA DE CONVERSAS DUPLICADAS\n")
print("="*70)

# Buscar todas as conversas
all_convs = supabase.table('whatsapp_conversations') \
    .select('*') \
    .order('created_at', desc=False) \
    .execute()

print(f"\n📊 Total de conversas: {len(all_convs.data)}\n")

# Agrupar por nome
from collections import defaultdict
by_name = defaultdict(list)

for conv in all_convs.data:
    name = conv.get('contact_name', 'Unknown')
    by_name[name].append(conv)

# Encontrar duplicatas
duplicates = {name: convs for name, convs in by_name.items() if len(convs) > 1}

if not duplicates:
    print("✅ Nenhuma duplicata encontrada!")
    exit(0)

print(f"⚠️  Encontradas {len(duplicates)} conversas duplicadas:\n")

# Número da clínica (para identificar conversas erradas)
CLINIC_PHONE = "5511991026844"

to_delete = []

for name, convs in duplicates.items():
    print(f"\n👤 {name} ({len(convs)} conversas):")
    
    # Ordenar: cliente primeiro, clínica depois
    convs_sorted = sorted(convs, key=lambda c: c.get('phone_number') == CLINIC_PHONE)
    
    for i, conv in enumerate(convs_sorted):
        phone = conv.get('phone_number')
        is_clinic = phone == CLINIC_PHONE
        status = "❌ CLÍNICA (DELETAR)" if is_clinic else "✅ CLIENTE (MANTER)"
        
        print(f"   {i+1}. {phone} - {status}")
        print(f"      ID: {conv.get('id')[:8]}...")
        print(f"      Última msg: {conv.get('last_message', '')[:40]}...")
        print(f"      Criada em: {conv.get('created_at')}")
        
        if is_clinic:
            to_delete.append(conv)

if not to_delete:
    print("\n✅ Nenhuma conversa da clínica para deletar!")
    exit(0)

print(f"\n\n🗑️  CONVERSAS A DELETAR: {len(to_delete)}")
print("="*70)

for conv in to_delete:
    print(f"  - {conv.get('contact_name')} ({conv.get('phone_number')})")

print("\n" + "="*70)
response = input("\n⚠️  Confirma a exclusão? (digite 'SIM' para confirmar): ")

if response.strip().upper() != 'SIM':
    print("\n❌ Operação cancelada.")
    exit(0)

print("\n🗑️  Deletando conversas...")

for conv in to_delete:
    conv_id = conv.get('id')
    name = conv.get('contact_name')
    phone = conv.get('phone_number')
    
    # Deletar mensagens associadas primeiro
    msgs = supabase.table('whatsapp_messages') \
        .delete() \
        .eq('conversation_id', conv_id) \
        .execute()
    
    # Deletar conversa
    supabase.table('whatsapp_conversations') \
        .delete() \
        .eq('id', conv_id) \
        .execute()
    
    print(f"  ✅ Deletada: {name} ({phone})")

print(f"\n✅ Limpeza concluída! {len(to_delete)} conversas removidas.")
print("\n" + "="*70)
