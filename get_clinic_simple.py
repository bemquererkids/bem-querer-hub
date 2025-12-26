"""Simple clinic ID getter"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.database import get_supabase

supabase = get_supabase()
result = supabase.table('clinicas').select('id, nome_fantasia').limit(1).execute()

if result.data:
    clinic = result.data[0]
    print(f"ID: {clinic['id']}")
    print(f"Nome: {clinic['nome_fantasia']}")
    
    # Salvar em arquivo
    with open('clinic_id.txt', 'w') as f:
        f.write(clinic['id'])
else:
    print("Nenhuma clínica encontrada")
