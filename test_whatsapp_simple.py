"""
Script de Teste WhatsApp SIMPLIFICADO - Bem-Querer Hub
======================================================
Envia uma mensagem de teste diretamente, sem verificar status.
"""
import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from backend/.env
env_path = Path(__file__).parent / "backend" / ".env"
load_dotenv(dotenv_path=env_path)

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.uazapi_service import get_uazapi_service
from app.core.config import settings


# ===== CONFIGURAÇÃO =====
PHONE_NUMBER = "551144361721"  # Número do usuário
INSTANCE_NAME = "bemquerer"  # Nome da instância UazAPI


async def test_send_message():
    """Testa o envio de mensagem via WhatsApp"""
    
    print("=" * 60)
    print("🦷 BEM-QUERER HUB - TESTE DE WHATSAPP (SIMPLIFICADO)")
    print("=" * 60)
    print()
    
    # Verificar configuração
    print("📋 Configuração:")
    print(f"   Base URL: {settings.UAZAPI_BASE_URL}")
    print(f"   Token: {'✅ Configurado' if settings.UAZAPI_TOKEN and settings.UAZAPI_TOKEN != 'placeholder_token' else '❌ NÃO CONFIGURADO'}")
    print(f"   Telefone: {PHONE_NUMBER}")
    print(f"   Instância: {INSTANCE_NAME}")
    print()
    
    if settings.UAZAPI_TOKEN == "placeholder_token" or not settings.UAZAPI_TOKEN:
        print("❌ ERRO: Configure UAZAPI_TOKEN no arquivo backend/.env")
        return
    
    # Obter serviço
    uazapi = get_uazapi_service()
    
    # Enviar Mensagem Diretamente
    print("📤 Enviando mensagem de teste...")
    try:
        message = """🦷 *Bem-Querer Hub - Teste de Integração*

Olá! Esta é uma mensagem de teste do sistema Bem-Querer Hub.

Se você recebeu isso, significa que a integração WhatsApp está funcionando perfeitamente! ✅

_Mensagem enviada automaticamente pelo sistema de testes._"""
        
        result = await uazapi.send_message(
            instance=INSTANCE_NAME,
            phone=PHONE_NUMBER,
            message=message
        )
        
        print(f"   ✅ Mensagem enviada com sucesso!")
        print(f"   📱 Resposta da API:")
        print(f"      {result}")
        print()
        print("🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print("   Verifique seu WhatsApp para confirmar o recebimento.")
        
    except Exception as e:
        print(f"   ❌ Erro ao enviar mensagem:")
        print(f"      {str(e)}")
        print()
        print("💡 Possíveis causas:")
        print("   - Token inválido ou expirado")
        print("   - Instância não conectada no painel UazAPI")
        print("   - Número de telefone em formato incorreto")
        print("   - Endpoint da API mudou (verifique docs.uazapi.com)")
    
    print()
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_send_message())
