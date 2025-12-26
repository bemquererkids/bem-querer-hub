"""Debug instance lookup"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.database import get_supabase

supabase = get_supabase()

print("\n=== DEBUG INSTANCE LOOKUP ===\n")

# Test 1: Direct query
print("1. Query direta:")
result = supabase.table('whatsapp_instances').select('*').execute()
print(f"   Total registros: {len(result.data)}")
if result.data:
    for inst in result.data:
        print(f"   - {inst['instance_name']}: clinic_id={inst['clinic_id'][:8]}...")

# Test 2: Query com filtro
print("\n2. Query com filtro (eq):")
result2 = supabase.table('whatsapp_instances').select('clinic_id').eq('instance_name', 'bemquerer').execute()
print(f"   Resultado: {result2.data}")
print(f"   Quantidade: {len(result2.data) if result2.data else 0}")

# Test 3: Verificar RLS
print("\n3. Verificando se RLS está bloqueando:")
print(f"   RLS ativo: Sim (configurado no migration)")
print(f"   Solução: Usar service_role key ou desabilitar RLS temporariamente")

print("\n=== FIM DEBUG ===\n")
