# Guia de Integração - Meta WhatsApp Business Cloud API

## Visão Geral

Este documento descreve como configurar e usar a **Meta WhatsApp Business Cloud API** no Sistema Bem-Querer V2.

A Meta Cloud API é a solução oficial do WhatsApp para empresas, substituindo gateways de terceiros como a UazAPI.

---

## Pré-requisitos

### 1. Meta Business Account
- Acesse: https://business.facebook.com
- Crie uma conta comercial (se não tiver)
- Verifique sua empresa

### 2. WhatsApp Business App
- Acesse: https://developers.facebook.com/apps
- Crie um novo app do tipo "Business"
- Adicione o produto "WhatsApp"

### 3. Número de Telefone
- Você precisa de um número de telefone que não esteja registrado no WhatsApp
- O número será vinculado à sua conta comercial
- Não pode ser um número pessoal já em uso

---

## Configuração Passo a Passo

### Etapa 1: Obter Credenciais da Meta

#### 1.1 Phone Number ID
1. No Meta Developer Console, vá em **WhatsApp** → **API Setup**
2. Copie o **Phone Number ID** (número longo, ex: `123456789012345`)

#### 1.2 WABA ID (WhatsApp Business Account ID)
1. No mesmo painel, procure por **WhatsApp Business Account ID**
2. Ou acesse: **WhatsApp** → **Getting Started**
3. Copie o **WABA ID**

#### 1.3 Access Token (Token Permanente)
1. Vá em **WhatsApp** → **API Setup**
2. Clique em **Generate Access Token**
3. **IMPORTANTE**: Este é um token temporário (24h)
4. Para token permanente:
   - Vá em **Business Settings** → **System Users**
   - Crie um System User
   - Atribua permissões: `whatsapp_business_management`, `whatsapp_business_messaging`
   - Gere um token permanente
   - **Salve este token com segurança!**

---

### Etapa 2: Configurar no Sistema Bem-Querer

#### 2.1 Acessar Configurações
1. Faça login no sistema
2. Vá em **Configurações** → **Integrações** → **WhatsApp**

#### 2.2 Preencher Credenciais
```
Phone Number ID: [Cole o Phone Number ID]
WABA ID: [Cole o WABA ID]
Access Token: [Cole o Access Token permanente]
```

#### 2.3 Salvar e Obter Webhook
1. Clique em **Salvar**
2. O sistema irá gerar:
   - **Webhook URL**: URL para configurar no Meta Console
   - **Verify Token**: Token de verificação

---

### Etapa 3: Configurar Webhook na Meta

#### 3.1 Acessar Configuração de Webhook
1. No Meta Developer Console, vá em **WhatsApp** → **Configuration**
2. Clique em **Edit** na seção **Webhook**

#### 3.2 Configurar URL e Token
```
Callback URL: [Cole a Webhook URL do sistema]
Verify Token: [Cole o Verify Token do sistema]
```

#### 3.3 Subscrever Eventos
Marque os seguintes eventos:
- ✅ `messages` (obrigatório)
- ✅ `message_status` (opcional - para status de entrega)

#### 3.4 Verificar
1. Clique em **Verify and Save**
2. O Meta irá fazer uma requisição GET para validar
3. Se tudo estiver correto, aparecerá ✅ **Verified**

---

## Testando a Integração

### Teste 1: Enviar Mensagem de Teste
1. No Meta Developer Console, vá em **WhatsApp** → **API Setup**
2. Use a ferramenta **Send Test Message**
3. Envie uma mensagem para o seu número pessoal
4. Verifique se recebeu no WhatsApp

### Teste 2: Receber Mensagem
1. Do seu WhatsApp pessoal, envie uma mensagem para o número comercial
2. Verifique nos logs do backend se a mensagem foi recebida
3. A IA Carol deve responder automaticamente

### Teste 3: Verificar no CRM
1. Acesse o CRM do sistema
2. Verifique se a conversa apareceu
3. Confirme que as mensagens estão sendo salvas

---

## Estrutura de Dados

### Tabela: `clinic_integrations`

```sql
CREATE TABLE clinic_integrations (
    id UUID PRIMARY KEY,
    clinica_id UUID NOT NULL,
    type TEXT NOT NULL, -- 'whatsapp'
    phone_number_id TEXT, -- Meta Phone Number ID
    waba_id TEXT, -- WhatsApp Business Account ID
    access_token TEXT, -- Token permanente
    verify_token TEXT, -- Token de verificação do webhook
    is_active BOOLEAN DEFAULT TRUE,
    updated_at TIMESTAMP
);
```

---

## Endpoints da API

### POST /api/integrations/whatsapp/connect
Salva as credenciais da Meta.

**Request Body:**
```json
{
  "phone_number_id": "123456789012345",
  "waba_id": "123456789012345",
  "access_token": "EAAxxxxxxxxxx"
}
```

**Response:**
```json
{
  "success": true,
  "webhook_url": "https://seu-dominio.vercel.app/api/webhooks/whatsapp",
  "verify_token": "uuid-gerado-automaticamente",
  "message": "Configuração salva! Configure o webhook no Meta Developer Console."
}
```

### GET /api/integrations/whatsapp/status
Verifica se o WhatsApp está configurado.

**Response (Configurado):**
```json
{
  "connected": true,
  "phone_number_id": "123456789012345",
  "waba_id": "123456789012345",
  "webhook_url": "https://seu-dominio.vercel.app/api/webhooks/whatsapp",
  "verify_token": "uuid-token"
}
```

**Response (Não Configurado):**
```json
{
  "connected": false,
  "message": "WhatsApp não configurado. Configure as credenciais da Meta."
}
```

---

## Webhook Protocol

### GET /api/webhooks/whatsapp (Verificação)
Meta envia uma requisição GET para verificar o webhook.

**Query Parameters:**
- `hub.mode`: "subscribe"
- `hub.verify_token`: Token configurado
- `hub.challenge`: String aleatória para retornar

**Response:**
- Retorna o `hub.challenge` como plain text se o token for válido
- Retorna 403 se o token for inválido

### POST /api/webhooks/whatsapp (Mensagens)
Meta envia mensagens recebidas via POST.

**Payload Example:**
```json
{
  "object": "whatsapp_business_account",
  "entry": [{
    "id": "WABA_ID",
    "changes": [{
      "value": {
        "messaging_product": "whatsapp",
        "metadata": {
          "phone_number_id": "123456789"
        },
        "messages": [{
          "from": "5511999999999",
          "id": "wamid.xxx",
          "timestamp": "1234567890",
          "type": "text",
          "text": {"body": "Olá!"}
        }]
      }
    }]
  }]
}
```

---

## Tipos de Mensagem Suportados

### Texto
```json
{
  "type": "text",
  "text": {"body": "Mensagem de texto"}
}
```

### Imagem
```json
{
  "type": "image",
  "image": {
    "id": "media_id",
    "caption": "Legenda da imagem"
  }
}
```

### Vídeo
```json
{
  "type": "video",
  "video": {
    "id": "media_id",
    "caption": "Legenda do vídeo"
  }
}
```

### Documento
```json
{
  "type": "document",
  "document": {
    "id": "media_id",
    "filename": "arquivo.pdf"
  }
}
```

### Áudio
```json
{
  "type": "audio",
  "audio": {"id": "media_id"}
}
```

---

## Limitações e Quotas

### Tier System
A Meta usa um sistema de tiers baseado em qualidade:

- **Tier 1**: 1.000 conversas únicas/dia
- **Tier 2**: 10.000 conversas únicas/dia
- **Tier 3**: 100.000 conversas únicas/dia
- **Tier 4**: Ilimitado

### Quality Rating
- **Green**: Boa qualidade
- **Yellow**: Atenção necessária
- **Red**: Qualidade baixa (pode ter restrições)

### Janela de 24 Horas
- Você pode responder gratuitamente dentro de 24h após a última mensagem do cliente
- Após 24h, precisa usar **Message Templates** (aprovados pela Meta)

---

## Troubleshooting

### Webhook não verifica
- ✅ Verifique se o `verify_token` está correto
- ✅ Confirme que a URL está acessível publicamente
- ✅ Verifique os logs do backend

### Mensagens não chegam
- ✅ Confirme que subscreveu o evento `messages`
- ✅ Verifique se o webhook está ativo
- ✅ Teste com a ferramenta de teste da Meta

### Token inválido
- ✅ Verifique se usou um token permanente (System User)
- ✅ Confirme as permissões do token
- ✅ Regenere o token se necessário

### Erro 403 ao enviar mensagens
- ✅ Verifique se o número está verificado
- ✅ Confirme que está dentro da janela de 24h
- ✅ Use templates para mensagens fora da janela

---

## Recursos Adicionais

- **Documentação Oficial**: https://developers.facebook.com/docs/whatsapp/cloud-api
- **API Reference**: https://developers.facebook.com/docs/whatsapp/cloud-api/reference
- **Meta Business Help**: https://www.facebook.com/business/help
- **WhatsApp Business API**: https://business.whatsapp.com

---

## Migração da UazAPI

Se você está migrando da UazAPI:

1. ✅ Execute a migration SQL: `supabase/migrations/v2_meta_migration.sql`
2. ✅ Configure as credenciais da Meta no sistema
3. ✅ Configure o webhook no Meta Developer Console
4. ✅ Teste o envio e recebimento de mensagens
5. ✅ Desative a UazAPI antiga

**IMPORTANTE**: A migração remove as colunas da UazAPI (`instance_name`, `token`, `qr_code_base64`). Faça backup antes!

---

## Suporte

Para dúvidas ou problemas:
- Consulte a documentação oficial da Meta
- Verifique os logs do sistema
- Entre em contato com o suporte técnico
