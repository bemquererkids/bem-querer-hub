"""
Direct Database Migration Script
Connects to Supabase Postgres via psycopg2 and applies the schema.
"""
import psycopg2
import os

# Configurações do Banco (Tentativa 3: Pooler na porta 6543)
DB_HOST = "aws-0-sa-east-1.pooler.supabase.com"
DB_PORT = "6543" 
DB_NAME = "postgres"
DB_USER = "postgres.kyzzowbhwatythozaqho" 
DB_PASS = "Vanessa123@" # Ou 6543 para pooler transacional
DB_NAME = "postgres"
DB_USER = "postgres.kyzzowbhwatythozaqho" # User padrao do Supabase
DB_PASS = "Vanessa123@"

# Schema SQL (Lendo do arquivo que criamos)
# Ajustando caminho relativo
SCHEMA_FILE = os.path.join(os.path.dirname(__file__), "../supabase/schema_ptbr.sql")

def run_migration():
    print(f"--- Migração Direta via Psycopg2 ---")
    print(f"Conectando em: {DB_HOST}...")
    
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT
        )
        conn.autocommit = True
        cursor = conn.cursor()
        print("✅ Conexão estabelecida!")
        
        # Ler SQL
        print("Lendo schema_ptbr.sql...")
        with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
            sql_commands = f.read()
            
        # Executar
        print("Executando comandos SQL...")
        cursor.execute(sql_commands)
        
        print("✅ Tabelas criadas com sucesso!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        print("\nDica: Se o host estiver errado, tente 'db.kyzzowbhwatythozaqho.supabase.co'")

if __name__ == "__main__":
    run_migration()
