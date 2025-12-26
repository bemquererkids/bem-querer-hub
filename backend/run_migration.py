"""
Script para executar a migração Meta Cloud API V2
Executa a migration SQL e verifica o resultado
"""
import os
import sys
from pathlib import Path

# Adicionar o diretório backend ao path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.database import get_supabase

def run_migration():
    """Executa a migration SQL via Supabase client"""
    print("🚀 Iniciando migração Meta Cloud API V2...")
    print()
    
    # Ler arquivo SQL
    migration_file = backend_dir.parent / "supabase" / "migrations" / "v2_meta_migration.sql"
    
    if not migration_file.exists():
        print(f"❌ Arquivo de migração não encontrado: {migration_file}")
        return False
    
    print(f"📄 Lendo migration: {migration_file.name}")
    with open(migration_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Executar via Supabase
    try:
        supabase = get_supabase()
        print("✅ Conectado ao Supabase")
        print()
        
        # Nota: Supabase Python client não executa SQL diretamente
        # Precisamos usar a API REST ou executar manualmente
        print("⚠️  ATENÇÃO: Execute a migration manualmente no Supabase Dashboard")
        print()
        print("Passos:")
        print("1. Acesse: https://supabase.com/dashboard")
        print("2. Selecione seu projeto")
        print("3. Vá em: SQL Editor")
        print("4. Cole o conteúdo do arquivo:")
        print(f"   {migration_file}")
        print("5. Clique em 'Run'")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def verify_migration():
    """Verifica se a migration foi executada com sucesso"""
    print("🔍 Verificando migração...")
    print()
    
    try:
        supabase = get_supabase()
        
        # Verificar se as novas colunas existem
        result = supabase.table('clinic_integrations').select('*').limit(1).execute()
        
        if result.data:
            sample = result.data[0] if len(result.data) > 0 else {}
            
            # Verificar colunas Meta
            meta_columns = ['phone_number_id', 'waba_id', 'access_token', 'verify_token']
            uazapi_columns = ['instance_name', 'token', 'qr_code_base64']
            
            print("Verificando colunas Meta:")
            for col in meta_columns:
                exists = col in sample or True  # Supabase pode não retornar colunas NULL
                status = "✅" if exists else "❌"
                print(f"  {status} {col}")
            
            print()
            print("Verificando remoção de colunas UazAPI:")
            for col in uazapi_columns:
                exists = col in sample
                status = "❌" if exists else "✅"
                print(f"  {status} {col} {'(ainda existe!)' if exists else '(removida)'}")
            
            print()
            print("✅ Verificação concluída!")
            
        else:
            print("⚠️  Tabela clinic_integrations está vazia")
            print("   Isso é normal se ainda não houver integrações configuradas")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return False

def main():
    """Função principal"""
    print("=" * 60)
    print("  MIGRAÇÃO META CLOUD API V2")
    print("  Sistema Bem-Querer")
    print("=" * 60)
    print()
    
    # Executar migration
    if not run_migration():
        sys.exit(1)
    
    # Perguntar se quer verificar
    print()
    response = input("Deseja verificar a migração agora? (s/n): ")
    
    if response.lower() in ['s', 'sim', 'y', 'yes']:
        print()
        verify_migration()
    
    print()
    print("=" * 60)
    print("  Próximos passos:")
    print("  1. Configure as credenciais Meta no sistema")
    print("  2. Acesse: Settings → Integrações → WhatsApp")
    print("  3. Preencha: Phone Number ID, WABA ID, Access Token")
    print("=" * 60)

if __name__ == "__main__":
    main()
