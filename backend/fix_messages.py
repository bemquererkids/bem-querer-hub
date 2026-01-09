"""
Script de diagnóstico e correção - roda no contexto do backend
"""
from app.core.database import SupabaseClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def diagnose_and_fix():
    supabase = SupabaseClient.get_admin_client()
    
    print("\n" + "="*70)
    print("🔍 DIAGNÓSTICO COMPLETO DE MENSAGENS")
    print("="*70)
    
    # IDs específicos
    message_ids = [
        "b07c96b2-c35e-4aaa-8680-cf729b12a9ac",
        "e2015804-9b38-41cf-9f52-22e3be8e67ea"
    ]
    
    print("\n1️⃣ Verificando mensagens específicas:")
    print("-"*70)
    
    problematic_messages = []
    
    for msg_id in message_ids:
        result = supabase.table('whatsapp_messages').select('*').eq('id', msg_id).execute()
        
        if result.data:
            msg = result.data[0]
            print(f"\n✅ Mensagem encontrada: {msg_id}")
            print(f"   📝 Conteúdo: {msg.get('content')[:60]}...")
            print(f"   📞 De: {msg.get('from_number')}")
            print(f"   📞 Para: {msg.get('to_number')}")
            print(f"   👤 fromMe: {msg.get('is_from_me')}")
            print(f"   🔗 Conversa: {msg.get('conversation_id')}")
            
            # Verificar se a conversa existe
            conv_id = msg.get('conversation_id')
            if conv_id:
                conv = supabase.table('whatsapp_conversations').select('*').eq('id', conv_id).execute()
                if conv.data:
                    c = conv.data[0]
                    print(f"   💬 Conversa válida: {c.get('contact_name')} ({c.get('phone_number')})")
                    
                    # Verificar se o telefone está correto
                    msg_phone = msg.get('to_number') if msg.get('is_from_me') else msg.get('from_number')
                    conv_phone = c.get('phone_number')
                    
                    if msg_phone != conv_phone and msg_phone != 'system':
                        print(f"   ⚠️  PROBLEMA: Telefone não bate!")
                        print(f"      Mensagem aponta para: {msg_phone}")
                        print(f"      Conversa é de: {conv_phone}")
                        problematic_messages.append({
                            'msg': msg,
                            'conv': c,
                            'correct_phone': msg_phone
                        })
                else:
                    print(f"   ❌ CONVERSA NÃO EXISTE!")
                    problematic_messages.append({'msg': msg, 'conv': None})
        else:
            print(f"\n❌ Mensagem NÃO encontrada: {msg_id}")
    
    print("\n\n2️⃣ Últimas 10 mensagens do sistema:")
    print("-"*70)
    
    recent = supabase.table('whatsapp_messages') \
        .select('*') \
        .order('created_at', desc=True) \
        .limit(10) \
        .execute()
    
    for i, msg in enumerate(recent.data, 1):
        print(f"\n{i}. [{msg.get('created_at')}]")
        print(f"   {msg.get('content')[:50]}...")
        print(f"   De: {msg.get('from_number')} → Para: {msg.get('to_number')}")
        print(f"   fromMe: {msg.get('is_from_me')} | Conv: {msg.get('conversation_id')[:8] if msg.get('conversation_id') else 'N/A'}...")
    
    print("\n\n3️⃣ Conversas ativas:")
    print("-"*70)
    
    convs = supabase.table('whatsapp_conversations') \
        .select('*') \
        .order('last_message_at', desc=True) \
        .limit(5) \
        .execute()
    
    for i, conv in enumerate(convs.data, 1):
        print(f"\n{i}. {conv.get('contact_name')} ({conv.get('phone_number')})")
        print(f"   ID: {conv.get('id')[:8]}...")
        print(f"   Última: {conv.get('last_message')[:40] if conv.get('last_message') else 'N/A'}...")
        
        # Contar mensagens
        count_result = supabase.table('whatsapp_messages') \
            .select('id', count='exact') \
            .eq('conversation_id', conv.get('id')) \
            .execute()
        print(f"   Total msgs: {count_result.count}")
    
    # CORREÇÃO
    if problematic_messages:
        print("\n\n4️⃣ CORREÇÃO DE MENSAGENS PROBLEMÁTICAS:")
        print("-"*70)
        print(f"\nEncontradas {len(problematic_messages)} mensagens para corrigir\n")
        
        for item in problematic_messages:
            msg = item['msg']
            correct_phone = item.get('correct_phone')
            
            if not correct_phone:
                print(f"⏭️  Pulando {msg.get('id')[:8]}... - sem telefone identificável")
                continue
            
            print(f"\n🔧 Corrigindo mensagem {msg.get('id')[:8]}...")
            print(f"   Telefone correto: {correct_phone}")
            
            # Buscar ou criar conversa correta
            correct_conv = supabase.table('whatsapp_conversations') \
                .select('*') \
                .eq('phone_number', correct_phone) \
                .execute()
            
            if correct_conv.data:
                target_conv_id = correct_conv.data[0]['id']
                print(f"   ✅ Conversa correta encontrada: {correct_conv.data[0].get('contact_name')}")
            else:
                # Criar nova conversa
                print(f"   ⚠️  Conversa não existe, criando...")
                new_conv = {
                    'clinic_id': msg.get('clinic_id'),
                    'phone_number': correct_phone,
                    'contact_name': f"Lead {correct_phone[-4:]}",
                    'last_message': msg.get('content'),
                    'last_message_at': msg.get('created_at'),
                    'unread_count': 0,
                    'tags': []
                }
                created = supabase.table('whatsapp_conversations').insert(new_conv).execute()
                target_conv_id = created.data[0]['id']
                print(f"   ✅ Nova conversa criada: {target_conv_id[:8]}...")
            
            # Mover mensagem
            supabase.table('whatsapp_messages') \
                .update({'conversation_id': target_conv_id}) \
                .eq('id', msg.get('id')) \
                .execute()
            
            print(f"   ✅ Mensagem movida para conversa correta!")
    
    print("\n" + "="*70)
    print("✅ DIAGNÓSTICO E CORREÇÃO COMPLETOS!")
    print("="*70 + "\n")

if __name__ == "__main__":
    diagnose_and_fix()
