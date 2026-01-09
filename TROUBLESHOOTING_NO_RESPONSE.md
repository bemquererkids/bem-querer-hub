# 🚨 TROUBLESHOOTING: Sistema Não Responde Mensagens

**Data:** 08/01/2026 17:40  
**Problema:** IA não está respondendo mensagens recebidas

---

## ✅ Checklist de Diagnóstico

### 1. **Webhook está recebendo mensagens?**
- [ ] Verificar logs do Railway: `📨 Message from ...`
- [ ] Se NÃO aparece → Problema na configuração do webhook UazAPI
- [ ] Se SIM → Continuar checklist

### 2. **Mensagem está sendo salva no banco?**
- [ ] Verificar logs: `💾 [process_uazapi_message] Calling save_whatsapp_message...`
- [ ] Verificar logs: `✅ [process_uazapi_message] Message saved successfully`
- [ ] Se NÃO → Erro no `save_whatsapp_message`
- [ ] Se SIM → Continuar

### 3. **IA está sendo chamada?**
- [ ] Verificar logs: `🤖 Generating AI response...`
- [ ] Se NÃO → Verificar condição `if not is_from_me and conversation_id:`
- [ ] Se SIM → Continuar

### 4. **IA está gerando resposta?**
- [ ] Verificar logs: `🤖 AI Response generated: ...`
- [ ] Se NÃO → Problema no GPT Service
- [ ] Se SIM → Continuar

### 5. **Resposta está sendo enviada?**
- [ ] Verificar logs: `📤 Sending response to ...`
- [ ] Verificar logs: `✅ Response sent successfully!`
- [ ] Se NÃO → Problema no UazAPI Service

### 6. **Webhook de confirmação está sendo ignorado?**
- [ ] Verificar logs: `⏭️ Ignoring fromMe webhook callback`
- [ ] Se NÃO aparece → Webhook pode estar criando loop
- [ ] Se SIM → Correto

---

## 🔍 Possíveis Causas

### **Causa 1: Filtro `fromMe` muito restritivo**
**Sintoma:** Nenhuma mensagem é processada  
**Logs esperados:** `⏭️ Ignoring fromMe webhook callback` para TODAS as mensagens  
**Solução:** Ajustar lógica de filtro

### **Causa 2: `conversation_id` é None**
**Sintoma:** Mensagem salva mas IA não responde  
**Logs esperados:** `Message saved successfully. Conversation: None`  
**Solução:** Investigar por que `save_whatsapp_message` retorna None

### **Causa 3: GPT Service com erro**
**Sintoma:** IA não gera resposta  
**Logs esperados:** Erro no `gpt_service.process_message`  
**Solução:** Verificar configuração OpenAI, créditos, rate limits

### **Causa 4: UazAPI Service com erro**
**Sintoma:** Resposta gerada mas não enviada  
**Logs esperados:** `❌ Failed to send WhatsApp message`  
**Solução:** Verificar token UazAPI, instância ativa

### **Causa 5: Webhook não configurado**
**Sintoma:** Nenhum log de mensagem recebida  
**Logs esperados:** Nada  
**Solução:** Reconfigurar webhook na UazAPI

---

## 🛠️ Comandos de Diagnóstico

### **Verificar última mensagem no banco:**
```sql
SELECT * FROM whatsapp_messages 
ORDER BY created_at DESC 
LIMIT 5;
```

### **Verificar conversas:**
```sql
SELECT id, contact_name, phone_number, last_message, last_message_at 
FROM whatsapp_conversations 
ORDER BY last_message_at DESC 
LIMIT 5;
```

### **Verificar se IA está configurada:**
```sql
SELECT * FROM ai_configurations 
WHERE clinic_id = '00000000-0000-0000-0000-000000000001';
```

---

## 🚀 Soluções Rápidas

### **Se webhook não está recebendo:**
1. Ir na UazAPI Dashboard
2. Verificar se webhook está ativo
3. Testar com Postman/Insomnia

### **Se IA não responde:**
1. Verificar créditos OpenAI
2. Verificar se `ai_configurations` tem registro
3. Testar endpoint `/api/chat/send-message` manualmente

### **Se UazAPI não envia:**
1. Verificar token no `.env`
2. Verificar se instância está conectada
3. Testar endpoint `/message/send` diretamente

---

## 📋 Informações Necessárias para Debug

Por favor, me envie:

1. **Logs do Railway (Backend)** - Últimas 40 linhas
2. **Print da tela** - Mostrando o chat
3. **Resultado desta query:**
```sql
SELECT * FROM whatsapp_messages 
WHERE created_at > NOW() - INTERVAL '10 minutes'
ORDER BY created_at DESC;
```

---

## ⚡ Fix Temporário

Se precisar voltar a funcionar AGORA, posso:

1. **Desabilitar filtro fromMe** temporariamente
2. **Forçar IA a responder** todas as mensagens
3. **Adicionar logs extras** para debug

**Qual prefere?**
