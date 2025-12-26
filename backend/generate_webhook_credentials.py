"""
Gerador de Credenciais para Webhook Meta
Gera Verify Token e mostra URL do webhook
"""
import uuid

print("=" * 60)
print("  CONFIGURAÇÃO WEBHOOK META WHATSAPP")
print("=" * 60)
print()

# Gerar Verify Token
verify_token = str(uuid.uuid4())

print("📋 COPIE ESTES VALORES PARA O META DEVELOPER CONSOLE:")
print()
print("1. CALLBACK URL (URL de retorno de chamada):")
print("   https://seu-dominio.vercel.app/api/webhooks/whatsapp")
print()
print("   ⚠️ IMPORTANTE: Substitua 'seu-dominio' pelo domínio real!")
print("   Exemplos:")
print("   - https://sistemabemquerer.vercel.app/api/webhooks/whatsapp")
print("   - https://bemquerer-v2.vercel.app/api/webhooks/whatsapp")
print()

print("2. VERIFY TOKEN (Token de verificação):")
print(f"   {verify_token}")
print()

print("=" * 60)
print()

print("📝 PRÓXIMOS PASSOS:")
print()
print("1. No Meta Developer Console:")
print("   - Cole a Callback URL no campo 'URL de retorno de chamada'")
print("   - Cole o Verify Token no campo 'Verificar token'")
print("   - Clique em 'Verificar e salvar'")
print()

print("2. Subscrever campos:")
print("   - Marque: ✅ messages")
print("   - Marque: ✅ message_status (opcional)")
print()

print("3. Salvar o Verify Token no banco de dados:")
print(f"   UPDATE clinic_integrations")
print(f"   SET verify_token = '{verify_token}'")
print(f"   WHERE type = 'whatsapp';")
print()

print("=" * 60)
print()

# Salvar em arquivo
with open("webhook_credentials.txt", "w") as f:
    f.write("WEBHOOK CREDENTIALS\n")
    f.write("=" * 60 + "\n\n")
    f.write("Callback URL:\n")
    f.write("https://seu-dominio.vercel.app/api/webhooks/whatsapp\n\n")
    f.write("Verify Token:\n")
    f.write(f"{verify_token}\n\n")
    f.write("SQL para salvar no banco:\n")
    f.write(f"UPDATE clinic_integrations SET verify_token = '{verify_token}' WHERE type = 'whatsapp';\n")

print("✅ Credenciais salvas em: webhook_credentials.txt")
print()
