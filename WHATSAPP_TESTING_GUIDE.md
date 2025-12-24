# 📱 Guia de Teste - Integração WhatsApp

## 🎯 Objetivo
Validar a conexão do WhatsApp via QR Code usando UazAPI e testar o envio de mensagens.

---

## 📋 Pré-requisitos

### Backend
- ✅ `UAZAPI_BASE_URL` configurada no `.env`
- ✅ `UAZAPI_TOKEN` configurada (Global Token da UazAPI)
- ⚠️ **Token válido** - Verifique no painel da UazAPI

### Frontend
- ✅ Componente `WhatsAppConnection` criado
- ✅ Página `SettingsPage` criada
- ✅ Rota `/settings` configurada

---

## 🧪 Testes

### 1. Acessar Página de Configurações

**Passo a passo:**
1. Fazer login no sistema
2. No menu lateral, clicar em **"Configurações"**
3. Verificar se a página carrega corretamente
4. Clicar na aba **"WhatsApp"**

**Resultado Esperado:**
- ✅ Página de configurações carrega
- ✅ Aba WhatsApp está selecionada
- ✅ Card "WhatsApp Business" é exibido
- ✅ Status mostra "Desconectado" (se não conectado)

---

### 2. Gerar QR Code

**Passo a passo:**
1. Na página de configurações WhatsApp
2. Clicar no botão **"Conectar WhatsApp"**
3. Aguardar geração do QR Code

**Resultado Esperado:**
- ✅ Botão muda para "Gerando QR Code..." com spinner
- ✅ QR Code é exibido na tela (imagem quadrada)
- ✅ Instruções de como escanear aparecem
- ✅ Mensagem "Aguardando conexão..." com spinner

**Possíveis Erros:**
- ❌ **Token inválido**: Verificar `UAZAPI_TOKEN` no `.env`
- ❌ **URL inválida**: Verificar `UAZAPI_BASE_URL`
- ❌ **Timeout**: Verificar conexão com internet

---

### 3. Escanear QR Code

**Passo a passo:**
1. Abrir WhatsApp no celular
2. Ir em **Mais opções (⋮)** → **Aparelhos conectados**
3. Tocar em **"Conectar um aparelho"**
4. Escanear o QR Code exibido na tela

**Resultado Esperado:**
- ✅ WhatsApp reconhece o QR Code
- ✅ Conexão é estabelecida no celular
- ✅ Após ~3 segundos, o status no sistema muda para "Conectado"
- ✅ QR Code desaparece
- ✅ Card verde de "WhatsApp Conectado!" aparece
- ✅ Número do telefone é exibido (se disponível)

**Troubleshooting:**
- ⏱️ **QR Code expira**: Clicar em "Gerar Novo QR Code"
- 📱 **Celular sem internet**: Conectar à rede
- 🔄 **Status não atualiza**: Aguardar até 10 segundos (polling)

---

### 4. Verificar Status da Conexão

**Passo a passo:**
1. Com WhatsApp conectado
2. Recarregar a página (F5)
3. Voltar para Configurações → WhatsApp

**Resultado Esperado:**
- ✅ Status permanece "Conectado"
- ✅ Não pede para escanear QR novamente
- ✅ Badge verde "Conectado" visível

---

### 5. Enviar Mensagem de Teste

**Endpoint:** `POST /api/whatsapp/send`

**cURL:**
```bash
curl -X POST http://localhost:8000/api/whatsapp/send \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "5511999999999",
    "message": "Olá! Esta é uma mensagem de teste do sistema NEXUS."
  }'
```

**Resultado Esperado:**
```json
{
  "status": "success",
  "data": {
    "key": {
      "id": "message-id-here"
    }
  }
}
```

**Validação:**
- ✅ Mensagem chega no WhatsApp do destinatário
- ✅ Mensagem aparece como enviada pelo número conectado
- ✅ Não há erros no console

---

### 6. Testar Envio via CRM

**Passo a passo:**
1. Ir para **CRM** (Kanban)
2. Clicar em um card de lead/agendamento
3. Clicar no botão de WhatsApp (ícone verde)
4. Escrever mensagem no modal
5. Clicar em "Enviar"

**Resultado Esperado:**
- ✅ Modal de WhatsApp abre
- ✅ Número do paciente pré-preenchido
- ✅ Mensagem é enviada com sucesso
- ✅ Modal fecha automaticamente
- ✅ Notificação de sucesso aparece

---

## 🐛 Troubleshooting Comum

### Erro: "Token inválido ou expirado (401)"

**Solução:**
1. Acessar painel da UazAPI
2. Ir em **Settings** → **Global Token**
3. Copiar o token
4. Atualizar `UAZAPI_TOKEN` no `.env`
5. Reiniciar backend

### Erro: "Nenhum documento relevante encontrado"

**Causa:** Endpoint errado ou instância não existe

**Solução:**
1. Verificar `UAZAPI_BASE_URL` (deve terminar sem `/`)
2. Exemplo correto: `https://api.uazapi.com`
3. Exemplo errado: `https://api.uazapi.com/`

### QR Code não aparece

**Solução:**
1. Abrir DevTools (F12)
2. Ver console para erros
3. Verificar Network tab
4. Verificar se `/api/integrations/whatsapp/connect` retorna 200

### Status não atualiza após escanear

**Solução:**
1. Aguardar até 10 segundos (polling a cada 3s)
2. Recarregar página manualmente
3. Verificar se `/api/integrations/whatsapp/status` retorna `connected: true`

---

## 📊 Checklist de Validação

### Conexão
- [ ] Página de configurações carrega
- [ ] Botão "Conectar WhatsApp" funciona
- [ ] QR Code é gerado e exibido
- [ ] QR Code pode ser escaneado
- [ ] Status muda para "Conectado" após scan
- [ ] Conexão persiste após reload

### Envio de Mensagens
- [ ] Endpoint `/api/whatsapp/send` funciona
- [ ] Mensagem chega no destinatário
- [ ] Modal do CRM abre corretamente
- [ ] Envio via modal funciona
- [ ] Erros são tratados adequadamente

### UI/UX
- [ ] Tema dark/light funciona
- [ ] Animações são suaves
- [ ] Feedback visual adequado
- [ ] Mensagens de erro são claras
- [ ] Layout responsivo

---

## 🎯 Resultado Final Esperado

Após todos os testes:
- ✅ WhatsApp conectado via QR Code
- ✅ Status "Conectado" visível
- ✅ Mensagens podem ser enviadas
- ✅ Integração com CRM funciona
- ✅ Webhook configurado automaticamente

---

## 📝 Notas Importantes

1. **QR Code expira em 60 segundos** - Gerar novo se necessário
2. **Polling automático** - Verifica status a cada 3 segundos
3. **Webhook auto-config** - Configurado automaticamente ao conectar
4. **Persistência** - Conexão mantida mesmo após fechar navegador
5. **Multi-device** - WhatsApp Web/Desktop pode ser usado simultaneamente

---

## 🔗 Endpoints Úteis

```bash
# Gerar QR Code
POST /api/integrations/whatsapp/connect

# Verificar Status
GET /api/integrations/whatsapp/status

# Enviar Mensagem
POST /api/whatsapp/send
{
  "phone": "5511999999999",
  "message": "Texto da mensagem"
}

# Enviar Imagem
POST /api/whatsapp/send-image
{
  "phone": "5511999999999",
  "image_url": "https://example.com/image.jpg",
  "caption": "Legenda opcional"
}
```

---

## ✅ Critérios de Sucesso

A integração está **100% funcional** quando:
1. QR Code é gerado sem erros
2. Conexão é estabelecida após scan
3. Status persiste após reload
4. Mensagens são enviadas com sucesso
5. UI/UX está polida e responsiva
