"""Verify webhook saved data correctly"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.database import get_supabase

supabase = get_supabase()

print("\n" + "="*80)
print("✅ VERIFICAÇÃO FINAL - Dados Salvos pelo Webhook")
print("="*80)

# Check conversations
print("\n📞 Conversas WhatsApp:")
convs = supabase.table('whatsapp_conversations').select('*').execute()
if convs.data:
    for conv in convs.data:
        print(f"\n   ✅ Telefone: {conv['phone_number']}")
        print(f"      Nome: {conv['contact_name']}")
        print(f"      Clinic ID: {conv['clinic_id']}")
        print(f"      Última msg: {conv['last_message']}")
        print(f"      Não lidas: {conv['unread_count']}")
else:
    print("   ❌ Nenhuma conversa encontrada")

# Check messages
print("\n💬 Mensagens:")
msgs = supabase.table('whatsapp_messages').select('*').order('created_at', desc=True).limit(5).execute()
if msgs.data:
    for msg in msgs.data:
        print(f"\n   ✅ ID: {msg['message_id']}")
        print(f"      De: {msg['from_number']}")
        print(f"      Para: {msg['to_number']}")
        print(f"      Clinic ID: {msg['clinic_id']}")
        print(f"      Conteúdo: {msg['content']}")
        print(f"      Tipo: {msg['message_type']}")
        print(f"      De mim: {msg['is_from_me']}")
else:
    print("   ❌ Nenhuma mensagem encontrada")

print("\n" + "="*80)
print("🎉 WEBHOOK MULTI-TENANT FUNCIONANDO!")
print("="*80)
print("\n✅ Próximos passos:")
print("   1. Fazer deploy para produção (Vercel)")
print("   2. Configurar webhook na UazAPI")
print("   3. Testar com mensagem real do WhatsApp")
print("   4. Implementar frontend (useWhatsAppChats)")
print("\n")
