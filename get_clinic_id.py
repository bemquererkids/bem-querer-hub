"""
Get Clinic ID for Testing
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.database import get_supabase

def get_clinic_id():
    print("\n" + "="*80)
    print("Buscando ID da Clínica")
    print("="*80)
    
    try:
        supabase = get_supabase()
        result = supabase.table('clinicas').select('id, nome_fantasia').limit(1).execute()
        
        if result.data:
            clinic = result.data[0]
            print(f"\n✅ Clínica encontrada:")
            print(f"   ID: {clinic['id']}")
            print(f"   Nome: {clinic['nome_fantasia']}")
            print(f"\n📋 Use este ID no SQL:")
            print(f"   clinic_id = '{clinic['id']}'")
            return clinic['id']
        else:
            print("\n❌ Nenhuma clínica encontrada")
            return None
            
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    get_clinic_id()
