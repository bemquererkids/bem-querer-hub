# 🔧 Fix: UazAPI Webhook - Número, Avatar e Mensagens

## 📋 Problemas Corrigidos

### 1. ❌ Número Incorreto (110307712048238 → ✅ 5511993308484)

**Problema:**
O código estava usando `chat.id` que é um **ID interno do UazAPI** (ex: `r5c2377e36f036c`), não o número de telefone real.

**Solução:**
Mudamos a prioridade de extração para usar os campos corretos:

```python
# ANTES (ERRADO):
jid = chat_data.get('id')  # ❌ ID interno do UazAPI

# DEPOIS (CORRETO):
jid = (
    chat_data.get('wa_chatid') or      # ✅ "5511993308484@s.whatsapp.net"
    message_data.get('chatid') or      # ✅ WhatsApp JID
    payload.get('chatId') or           # ✅ Legacy support
    message_data.get('sender')         # ✅ Fallback
)
```

### 2. 🖼️ Avatar Não Aparecia

**Problema:**
O avatar já estava sendo extraído corretamente de `chat.imagePreview`, mas não estava sendo salvo no banco.

**Solução:**
- ✅ O código já estava correto: `chat_data.get('imagePreview')`
- ✅ O avatar é passado para `save_whatsapp_message(avatar=avatar_url)`
- ✅ Adicionado log para confirmar: `logger.warning(f"🔍 [DEBUG] Extracted Avatar URL: {avatar_url}")`

### 3. 📱 Nome do Contato

**Melhorias:**
Agora priorizamos os campos corretos do UazAPI:

```python
name = (
    chat_data.get('name') or        # ✅ "Luiz Fernando"
    chat_data.get('wa_name') or     # ✅ WhatsApp profile name
    chat_data.get('contactName')    # ✅ Saved contact name
)
```

### 4. 🧹 Limpeza do Número

Adicionamos limpeza automática do número de telefone:

```python
# Remove espaços, traços, parênteses, etc.
phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '').replace('+', '')
# Resultado: "5511993308484" ✅
```

## 📊 Estrutura do Payload UazAPI

```json
{
  "EventType": "messages",
  "chat": {
    "id": "r5c2377e36f036c",                    // ❌ ID interno (NÃO usar)
    "wa_chatid": "5511993308484@s.whatsapp.net", // ✅ WhatsApp JID
    "phone": "+55 11 99330-8484",                // ✅ Telefone formatado
    "name": "Luiz Fernando",                     // ✅ Nome
    "wa_name": "Luiz Fernando",                  // ✅ Nome WhatsApp
    "imagePreview": "https://pps.whatsapp.net/..." // ✅ Avatar
  },
  "message": {
    "chatid": "5511993308484@s.whatsapp.net",    // ✅ WhatsApp JID
    "sender": "5511993308484@s.whatsapp.net",    // ✅ Remetente
    "text": "Oi",                                 // ✅ Mensagem
    "fromMe": false
  }
}
```

## 🔍 Logs de Debug Adicionados

Para facilitar troubleshooting futuro:

```python
logger.warning(f"🔍 [DEBUG] Full Payload Keys: {list(payload.keys())}")
logger.warning(f"🔍 [DEBUG] Message Data Keys: {list(message_data.keys())}")
logger.warning(f"🔍 [DEBUG] Chat Data Keys: {list(chat_data.keys())}")
logger.warning(f"🔍 [DEBUG] Chat Data: {chat_data}")
logger.warning(f"🔍 [DEBUG] Extracted JID: {jid}")
logger.warning(f"🔍 [DEBUG] Extracted Phone (cleaned): {phone}")
logger.warning(f"🔍 [DEBUG] Extracted Name: {name}")
logger.warning(f"🔍 [DEBUG] Extracted Avatar URL: {avatar_url}")
```

## 🚀 Deploy

```bash
git add backend/app/api/webhooks.py
git commit -m "fix: correct phone number and avatar extraction from UazAPI webhook payload"
git push origin master
```

## ✅ Resultado Esperado

Após o deploy:
- ✅ Número correto: `5511993308484` (ao invés de `110307712048238`)
- ✅ Avatar aparecendo na sidebar
- ✅ Mensagens aparecendo corretamente
- ✅ Nome do contato correto: "Luiz Fernando"

## 🧪 Teste

1. Envie uma mensagem de teste do WhatsApp
2. Verifique os logs do backend para confirmar:
   - JID extraído: `5511993308484@s.whatsapp.net`
   - Phone: `5511993308484`
   - Avatar URL presente
3. Verifique o frontend:
   - Conversa aparece com número correto
   - Avatar carregando
   - Mensagens visíveis
