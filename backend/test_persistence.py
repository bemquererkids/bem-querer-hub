"""
Script de diagnóstico para verificar se persistência está funcionando
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import get_supabase

def main():
    print("=" * 70)
    print("🔍 DIAGNÓSTICO: Verificando Persistência")
    print("=" * 70)
    print()
    
    try:
        supabase = get_supabase()
        
        # 1. Verificar se tabela existe
        print("1️⃣ Verificando se tabela conversation_states existe...")
        result = supabase.table("conversation_states").select("*").limit(1).execute()
        print("   ✅ Tabela existe!")
        print()
        
        # 2. Listar conversas existentes
        print("2️⃣ Listando conversas existentes...")
        result = supabase.table("conversation_states").select("*").execute()
        
        if result.data:
            print(f"   📊 Encontradas {len(result.data)} conversas:")
            for conv in result.data:
                print(f"      - Phone: {conv['phone']}")
                print(f"        Collected Data: {conv['collected_data']}")
                print(f"        Current Agent: {conv['current_agent']}")
                print(f"        Updated: {conv['updated_at']}")
                print()
        else:
            print("   ℹ️  Nenhuma conversa encontrada (normal se ainda não testou)")
        print()
        
        # 3. Testar insert
        print("3️⃣ Testando insert/upsert...")
        test_data = {
            "phone": "5511999999999",
            "clinic_id": "00000000-0000-0000-0000-000000000001",
            "current_agent": "triagem",
            "patient_type": "kids",
            "intent": "agendamento",
            "human_takeover": False,
            "collected_data": {"tipo": "kids", "nome": "Teste"},
            "agent_history": [{"from": "router", "to": "triagem"}]
        }
        
        result = supabase.table("conversation_states").upsert(test_data, on_conflict="phone,clinic_id").execute()
        print("   ✅ Insert/Upsert funcionando!")
        print()
        
        # 4. Testar select
        print("4️⃣ Testando select...")
        result = supabase.table("conversation_states") \
            .select("*") \
            .eq("phone", "5511999999999") \
            .execute()
        
        if result.data:
            print("   ✅ Select funcionando!")
            print(f"   📦 Dados recuperados: {result.data[0]['collected_data']}")
        else:
            print("   ❌ Erro ao recuperar dados!")
        print()
        
        # 5. Limpar teste
        print("5️⃣ Limpando dados de teste...")
        supabase.table("conversation_states").delete().eq("phone", "5511999999999").execute()
        print("   ✅ Limpeza concluída!")
        print()
        
        print("=" * 70)
        print("✅ DIAGNÓSTICO COMPLETO - TUDO FUNCIONANDO!")
        print("=" * 70)
        print()
        print("Se Carol ainda está repetindo, o problema pode ser:")
        print("1. Deploy ainda não completou (aguarde ~5 min)")
        print("2. Código antigo ainda em cache")
        print("3. Verificar logs do Railway para erros")
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        print()
        print("Possíveis causas:")
        print("1. Tabela não foi criada no Supabase")
        print("2. Credenciais do Supabase incorretas")
        print("3. Conexão com Supabase falhou")

if __name__ == "__main__":
    main()
