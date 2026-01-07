import asyncio
import sys
import os

# Add global path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SupabaseClient

def cleanup_remote_db():
    print("🧹 Iniciando Limpeza Cirúrgica (ADMIN)...")
    # Use Admin Client to bypass RLS
    supabase = SupabaseClient.get_admin_client()
    
    try:
        # 1. Buscar IDs para deletar (Paciente Teste)
        print("Buscando IDs de 'Paciente Teste'...")
        res = supabase.table("whatsapp_conversations") \
            .select("id, contact_name") \
            .like("contact_name", "Paciente Teste%") \
            .execute()
            
        test_ids = [row['id'] for row in res.data]
        print(f"Encontrados {len(test_ids)} registros de 'Paciente Teste'.")
        
        # 2. Buscar IDs para deletar (Paciente Seed)
        print("Buscando IDs de 'Paciente Seed'...")
        res_seed = supabase.table("whatsapp_conversations") \
            .select("id, contact_name") \
            .like("contact_name", "Paciente Seed%") \
            .execute()
            
        seed_ids = [row['id'] for row in res_seed.data]
        print(f"Encontrados {len(seed_ids)} registros de 'Paciente Seed'.")
        
        all_ids = test_ids + seed_ids
        
        if not all_ids:
            print("Nada para deletar.")
            return

        print(f"Deletando {len(all_ids)} registros...")
        
        # Delete in batches of 20 to avoid URL length limits
        batch_size = 20
        total_deleted = 0
        
        for i in range(0, len(all_ids), batch_size):
            batch = all_ids[i:i+batch_size]
            del_res = supabase.table("whatsapp_conversations").delete().in_("id", batch).execute()
            count = len(del_res.data) if del_res.data else 0
            total_deleted += count
            print(f" - Batch {i//batch_size + 1}: Deletados {count}")
            
        print(f"✅ Limpeza Concluída! Total removidos: {total_deleted}")

    except Exception as e:
        print(f"❌ Erro: {e}")


if __name__ == "__main__":
    cleanup_remote_db()
