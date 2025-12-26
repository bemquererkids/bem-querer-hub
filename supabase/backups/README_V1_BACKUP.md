# 📦 Backup V1.0.0 - Legacy UazAPI Version

**Data do Backup:** 2025-12-26  
**Versão:** V1.0.0-legacy  
**Provedor WhatsApp:** UazAPI

## 🎯 Propósito

Este backup foi criado antes da migração para a Meta WhatsApp Business API. Ele preserva a versão funcional do sistema que utiliza UazAPI como provedor de WhatsApp.

## 📁 Conteúdo do Backup

### 1. SQL Schema Completo
**Arquivo:** `backup_v1_full_uazapi.sql`

Contém:
- ✅ Todas as tabelas do sistema
- ✅ Índices e constraints
- ✅ Row Level Security (RLS) policies
- ✅ Functions e triggers
- ✅ Tabela `clinic_integrations` com estrutura UazAPI
- ✅ Campos específicos do UazAPI:
  - `messages.uazapi_message_id`
  - `messages.uazapi_status`
  - `webhook_logs` (eventos UazAPI)

### 2. Código de Referência
**Arquivo:** `backend/app/services/uazapi_service.py`

Serviço completo do UazAPI com:
- Envio de mensagens de texto e imagem
- Gerenciamento de status da instância
- Geração de QR Code
- Configuração de webhooks
- Marcação de mensagens como lidas

### 3. Git Tag
**Tag:** `v1.0.0-legacy`

Marca o último commit estável com UazAPI.

## 🔄 Como Restaurar

### Opção 1: Restaurar apenas o Banco de Dados

```sql
-- No SQL Editor do Supabase, execute:
-- (Atenção: isso irá recriar todas as tabelas)

-- 1. Faça backup dos dados atuais primeiro!
-- 2. Execute o arquivo backup_v1_full_uazapi.sql
```

### Opção 2: Reverter Código Completo

```bash
# Voltar para a versão V1 com UazAPI
git checkout v1.0.0-legacy

# Ou criar uma branch de recuperação
git checkout -b recovery/v1-uazapi v1.0.0-legacy
```

## 📊 Estrutura da Tabela `clinic_integrations` (V1)

```sql
CREATE TABLE public.clinic_integrations (
    id UUID PRIMARY KEY,
    clinica_id UUID NOT NULL,
    type TEXT NOT NULL, -- 'whatsapp', 'clinicorp', 'openai', 'gemini'
    config JSONB NOT NULL, -- Configurações específicas
    is_active BOOLEAN DEFAULT TRUE,
    updated_at TIMESTAMP WITH TIME ZONE
);
```

### Exemplo de Config para WhatsApp (UazAPI):
```json
{
  "instance": "bemquerer",
  "token": "...",
  "connected_at": "2025-12-26T10:00:00Z"
}
```

## 🔑 Variáveis de Ambiente (V1)

```env
# UazAPI (V1 Legacy)
UAZAPI_BASE_URL=https://bemquerer.uazapi.com
UAZAPI_TOKEN=...
UAZAPI_INSTANCE=bemquerer
PUBLIC_URL=https://bem-querer-hub.vercel.app

# Outras integrações (mantidas)
CLINICORP_CLIENT_ID=...
CLINICORP_CLIENT_SECRET=...
OPENAI_API_KEY=...
GEMINI_API_KEY=...
```

## ⚠️ Diferenças para V2 (Meta API)

| Aspecto | V1 (UazAPI) | V2 (Meta API) |
|---------|-------------|---------------|
| Provedor | UazAPI | Meta WhatsApp Business |
| Autenticação | Token único | Access Token + Phone Number ID |
| Webhooks | UazAPI format | Meta Webhook format |
| Message ID | `uazapi_message_id` | `meta_message_id` |
| Status | `uazapi_status` | `meta_status` |
| QR Code | Gerado via UazAPI | Não aplicável (Business API) |

## 📝 Notas Importantes

1. **Não delete este backup!** Ele é a única forma de reverter para UazAPI se a migração para Meta API falhar.

2. **Dados de produção:** Este backup contém apenas a estrutura (DDL). Para backup completo de dados, use:
   ```bash
   # Exportar dados via Supabase Dashboard
   # Database → Backups → Create Backup
   ```

3. **Compatibilidade:** O código V1 é 100% funcional e testado em produção até 26/12/2025.

## 🆘 Suporte

Se precisar restaurar este backup:
1. Verifique se há dados importantes na versão atual
2. Faça backup dos dados atuais
3. Execute o SQL de restauração
4. Faça checkout do código via git tag
5. Reconfigure as variáveis de ambiente da Vercel

---

**Última atualização:** 2025-12-26  
**Mantido por:** Equipe Bem-Querer
