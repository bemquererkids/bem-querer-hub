"""
Script para criar tabela conversation_states no Supabase
Execute este script UMA VEZ antes de fazer deploy
"""

import os
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import get_supabase

def main():
    print("=" * 70)
    print("🗄️  CRIANDO TABELA conversation_states NO SUPABASE")
    print("=" * 70)
    print()
    
    # Ler SQL
    sql_path = Path(__file__).parent.parent / "supabase" / "migrations" / "conversation_states.sql"
    
    if not sql_path.exists():
        print(f"❌ Arquivo SQL não encontrado: {sql_path}")
        return
    
    with open(sql_path, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    print("📄 SQL carregado:")
    print("-" * 70)
    print(sql[:200] + "...")
    print("-" * 70)
    print()
    
    # Executar
    try:
        supabase = get_supabase()
        
        print("⚙️  Executando migration...")
        
        # Supabase Python client não suporta SQL direto
        # Você precisa executar via Dashboard ou psql
        
        print()
        print("⚠️  ATENÇÃO: Execute o SQL manualmente no Supabase Dashboard!")
        print()
        print("Passos:")
        print("1. Acesse: https://supabase.com/dashboard")
        print("2. Vá em: SQL Editor")
        print("3. Cole o conteúdo de: supabase/migrations/conversation_states.sql")
        print("4. Clique em 'Run'")
        print()
        print("Ou use psql:")
        print(f"  psql [CONNECTION_STRING] < {sql_path}")
        print()
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return
    
    print("=" * 70)
    print("✅ INSTRUÇÕES EXIBIDAS")
    print("=" * 70)

if __name__ == "__main__":
    main()
