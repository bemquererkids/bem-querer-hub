"""
Script para verificar configuração WhatsApp no banco de dados
"""
import os
import sys
from pathlib import Path

# Adicionar o diretório backend ao path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.database import get_supabase

def check_whatsapp_config():
    """Verifica configuração WhatsApp no banco"""
    print("🔍 Verificando configuração WhatsApp no banco de dados...")
    print()
    
    try:
        supabase = get_supabase()
        
        # Buscar todas as integrações WhatsApp
        result = supabase.table('clinic_integrations') \
            .select('*') \
            .eq('type', 'whatsapp') \
            .execute()
        
        if not result.data or len(result.data) == 0:
            print("❌ Nenhuma configuração WhatsApp encontrada no banco")
            print()
            print("Possíveis causas:")
            print("1. As credenciais não foram salvas via endpoint /api/integrations/whatsapp/connect")
            print("2. A migration não foi executada")
            print("3. Os dados foram salvos em outra tabela/formato")
            print()
            return False
        
        print(f"✅ Encontradas {len(result.data)} configuração(ões) WhatsApp")
        print()
        
        for idx, config in enumerate(result.data, 1):
            print(f"Configuração #{idx}:")
            print(f"  Clínica ID: {config.get('clinica_id')}")
            print(f"  Phone Number ID: {config.get('phone_number_id', 'NÃO CONFIGURADO')}")
            print(f"  WABA ID: {config.get('waba_id', 'NÃO CONFIGURADO')}")
            print(f"  Access Token: {'***' + config.get('access_token', '')[-10:] if config.get('access_token') else 'NÃO CONFIGURADO'}")
            print(f"  Verify Token: {config.get('verify_token', 'NÃO CONFIGURADO')}")
            print(f"  Ativo: {config.get('is_active', False)}")
            print(f"  Atualizado em: {config.get('updated_at', 'N/A')}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao consultar banco: {e}")
        print()
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("  VERIFICAÇÃO CONFIGURAÇÃO WHATSAPP")
    print("  Sistema Bem-Querer")
    print("=" * 60)
    print()
    
    check_whatsapp_config()
    
    print("=" * 60)
