"""
Script de Teste WhatsApp - Bem-Querer Hub
==========================================
Este script testa o envio de mensagens via UazAPI.

ANTES DE RODAR:
1. Configure as variáveis no arquivo backend/.env:
   - UAZAPI_BASE_URL (ex: https://api.uazapi.com)
   - UAZAPI_TOKEN (seu token de API)

2. Edite a variável PHONE_NUMBER abaixo com seu número de teste.

3. Execute: python test_whatsapp_integration.py
"""
import asyncio
import sys
import os
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
# Coloque seu número de WhatsApp aqui (com código do país, sem +)
PHONE_NUMBER = "551144361721"  # ALTERE AQUI! Formato: 55 + DDD + Número
INSTANCE_NAME = "bemquerer"  # Nome da instância UazAPI


async def test_whatsapp():
    """Testa o envio de mensagem via WhatsApp"""
    
    print("=" * 60)
    print("🦷 BEM-QUERER HUB - TESTE DE WHATSAPP")
    print("=" * 60)
    print()
    
    # Verificar configuração
    print("📋 Verificando configuração...")
    print(f"   Base URL: {settings.UAZAPI_BASE_URL}")
    print(f"   Token: {'✅ Configurado' if settings.UAZAPI_TOKEN and settings.UAZAPI_TOKEN != 'placeholder_token' else '❌ NÃO CONFIGURADO'}")
    print(f"   Telefone destino: {PHONE_NUMBER}")
    print(f"   Instância: {INSTANCE_NAME}")
    print()
    
    if settings.UAZAPI_TOKEN == "placeholder_token" or not settings.UAZAPI_TOKEN:
        print("❌ ERRO: Configure UAZAPI_TOKEN no arquivo backend/.env")
        return
    
    if PHONE_NUMBER == "5511999999999":
        print("⚠️  ATENÇÃO: Altere a variável PHONE_NUMBER neste script!")
        print()
    
    # Obter serviço
    uazapi = get_uazapi_service()
    
    # Teste 1: Status da Instância
    print("🔍 Teste 1: Verificando status da instância...")
    try:
        status = await uazapi.get_instance_status(INSTANCE_NAME)
        print(f"   ✅ Status: {status}")
    except Exception as e:
        print(f"   ❌ Erro ao verificar status: {str(e)}")
        print("   💡 Verifique se a instância está conectada no painel UazAPI")
        return
    
    print()
    
    # Teste 2: Enviar Mensagem
    print("📤 Teste 2: Enviando mensagem de teste...")
    try:
        message = "🦷 Olá! Esta é uma mensagem de teste do *Bem-Querer Hub*.\n\nSe você recebeu isso, a integração WhatsApp está funcionando perfeitamente! ✅"
        
        result = await uazapi.send_message(
            instance=INSTANCE_NAME,
            phone=PHONE_NUMBER,
            message=message
        )
        
        print(f"   ✅ Mensagem enviada com sucesso!")
        print(f"   📱 ID da mensagem: {result.get('key', {}).get('id', 'N/A')}")
        print()
        print("🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print("   Verifique seu WhatsApp para confirmar o recebimento.")
        
    except Exception as e:
        print(f"   ❌ Erro ao enviar mensagem: {str(e)}")
        print()
        print("💡 Possíveis causas:")
        print("   - Token inválido ou expirado")
        print("   - Instância não conectada")
        print("   - Número de telefone em formato incorreto")
        print("   - Limite de mensagens atingido")
    
    print()
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_whatsapp())
