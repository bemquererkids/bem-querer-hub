# 🧪 Guia de Testes - Multi-Agent System (Fase 1)

## 📋 Checklist Pré-Teste

### ✅ Verificar Deploy:
1. Aguardar Railway completar deploy (~5 minutos)
2. Verificar logs: Procurar por "🤖 Using Multi-Agent System"
3. Confirmar que `USE_MULTI_AGENT=true` está configurado

### ✅ Verificar Variável de Ambiente:
```bash
# No Railway, adicionar:
USE_MULTI_AGENT=true
```

---

## 🎯 Cenários de Teste

### **Teste 1: Triagem Básica (Kids)**

**Objetivo:** Verificar se Triagem coleta dados corretamente

**Conversa Esperada:**
```
Você: "Olá"

Carol (Triagem): "Olá! Será um prazer ajudar! 💙
                  É para você ou para seu filho(a)?"

Você: "Para meu filho"

Carol (Triagem): "Qual o nome dele? 🎈"

Você: "Pedro"

Carol (Triagem): "Oi Pedro! Qual o motivo da consulta?"

Você: "Precisa de aparelho"

Carol (Triagem): [Deve coletar: tipo=kids, nome=Pedro, motivo=aparelho]
                 [Deve tentar transferir para Kids Agent]
                 [Como Kids Agent não existe ainda, pode dar erro ou fallback]
```

**✅ Sucesso se:**
- Carol faz perguntas uma por vez
- Extrai informações corretamente
- Linguagem natural e amigável

**❌ Falha se:**
- Faz todas perguntas de uma vez
- Não extrai informações
- Responde de forma robótica

---

### **Teste 2: Triagem Básica (Adulto)**

**Objetivo:** Verificar detecção de adulto

**Conversa Esperada:**
```
Você: "Olá"

Carol (Triagem): "Olá! Será um prazer ajudar! 💙
                  É para você ou para seu filho(a)?"

Você: "Para mim"

Carol (Triagem): "Qual o seu nome?"

Você: "Maria"

Carol (Triagem): "Oi Maria! Qual o motivo da consulta?"

Você: "Quero fazer clareamento"

Carol (Triagem): [Deve coletar: tipo=adulto, nome=Maria, motivo=clareamento]
                 [Deve tentar transferir para Adulto Agent]
```

**✅ Sucesso se:**
- Detecta que é adulto
- Adapta linguagem (sem "🎈", mais profissional)
- Coleta dados corretamente

---

### **Teste 3: Router Detecta Tipo Automaticamente**

**Objetivo:** Verificar se Router detecta tipo sem perguntar

**Conversa Esperada:**
```
Você: "Meu filho de 7 anos precisa de aparelho"

Carol (Router): [Detecta: tipo=kids, motivo=aparelho, idade=7]
                [Roteia direto para Triagem com contexto]

Carol (Triagem): "Qual o nome dele? 🎈"
                 [Não pergunta se é criança, já sabe!]
```

**✅ Sucesso se:**
- Não pergunta se é criança (já detectou)
- Vai direto para próxima pergunta
- Contexto preservado

---

### **Teste 4: Handoff para Humano (Explícito)**

**Objetivo:** Verificar transferência para humano

**Conversa Esperada:**
```
Você: "Quero falar com atendente"

Carol: "Vou transferir você para nossa equipe agora.
       Um atendente vai te responder em instantes! 💙"

[Sistema marca: human_takeover = true]
[Carol NÃO responde mais mensagens]

Você: "Olá?" (teste)

Carol: [SEM RESPOSTA - humano assumiu]
```

**✅ Sucesso se:**
- Detecta gatilho "falar com atendente"
- Responde com mensagem de transferência
- Para de responder depois

**❌ Falha se:**
- Continua respondendo após handoff
- Não detecta gatilho

---

### **Teste 5: Handoff para Humano (Insatisfação)**

**Objetivo:** Verificar detecção de insatisfação

**Conversa Esperada:**
```
Você: "Não está entendendo nada"

Carol: "Vou transferir você para nossa equipe agora.
       Um atendente vai te responder em instantes! 💙"

[Handoff ativado]
```

**Gatilhos para testar:**
- "não está entendendo"
- "péssimo atendimento"
- "não resolve"
- "horrível"

---

### **Teste 6: Emergência**

**Objetivo:** Verificar detecção de emergência

**Conversa Esperada:**
```
Você: "Socorro! Meu filho caiu e quebrou o dente!"

Carol (Router): [Detecta: intent=emergencia]
                [Deve priorizar]

Carol (Triagem): "Meu Deus, imagino o susto! 🚨
                  Para a Dra. te ligar AGORA, me confirme:
                  1. Nome dele e idade?
                  2. Seu telefone é esse mesmo do WhatsApp?"
```

**✅ Sucesso se:**
- Detecta emergência
- Linguagem urgente
- Prioriza atendimento

---

### **Teste 7: Fallback para Single-Agent**

**Objetivo:** Verificar que funciona mesmo se multi-agent falhar

**Como testar:**
1. Desativar multi-agent: `USE_MULTI_AGENT=false`
2. Enviar mensagem
3. Deve usar sistema antigo (single-agent)

**✅ Sucesso se:**
- Continua funcionando
- Usa RAG normalmente
- Sem erros

---

## 📊 Logs para Verificar

### **No Railway, procure por:**

```bash
# Multi-agent ativado:
🤖 Using Multi-Agent System

# Router processando:
Router: [reasoning] → triagem

# Triagem coletando dados:
Conversation 5548999999999: Collected nome = Pedro

# Transição de agente:
Conversation 5548999999999: triagem → kids (Agent decision)

# Handoff para humano:
Conversation 5548999999999: Handed off to human (Gatilho detectado)
```

---

## 🐛 Problemas Comuns

### **Problema 1: Carol não responde**
**Causa:** Multi-agent pode estar falhando
**Solução:** 
1. Verificar logs
2. Desativar multi-agent temporariamente
3. Verificar se `phone` está no contexto

### **Problema 2: Carol responde tudo de uma vez**
**Causa:** Triagem não está funcionando
**Solução:**
1. Verificar logs do Triagem Agent
2. Pode estar caindo no fallback

### **Problema 3: Não detecta handoff**
**Causa:** Gatilhos não configurados
**Solução:**
1. Testar gatilhos exatos: "quero falar com atendente"
2. Verificar logs

### **Problema 4: Erro 500**
**Causa:** Algum agente não implementado
**Solução:**
1. Verificar logs de erro
2. Pode estar tentando usar Kids/Adulto Agent (não implementados ainda)
3. Normal na Fase 1!

---

## 📝 Relatório de Teste

### **Preencha após testar:**

```
[ ] Teste 1: Triagem Kids - ✅ / ❌
[ ] Teste 2: Triagem Adulto - ✅ / ❌
[ ] Teste 3: Router Auto-detect - ✅ / ❌
[ ] Teste 4: Handoff Explícito - ✅ / ❌
[ ] Teste 5: Handoff Insatisfação - ✅ / ❌
[ ] Teste 6: Emergência - ✅ / ❌
[ ] Teste 7: Fallback Single-Agent - ✅ / ❌

Observações:
_________________________________
_________________________________
_________________________________
```

---

## 🎯 Critérios de Sucesso (Fase 1)

### **Mínimo Aceitável:**
- ✅ Triagem coleta dados (nome, tipo, motivo)
- ✅ Perguntas uma por vez
- ✅ Handoff para humano funciona

### **Ideal:**
- ✅ Router detecta tipo automaticamente
- ✅ Linguagem natural e fluida
- ✅ Todos os gatilhos de handoff funcionam
- ✅ Emergências detectadas

---

## 🚀 Próximos Passos Após Teste

### **Se tudo OK:**
1. Implementar Kids Agent
2. Implementar Adulto Agent
3. Implementar Agendamento Agent

### **Se houver problemas:**
1. Reportar erros encontrados
2. Ajustar prompts
3. Corrigir bugs
4. Testar novamente

---

## 📞 Suporte

**Encontrou algum problema?**
1. Copie os logs do Railway
2. Descreva o comportamento esperado vs. real
3. Informe qual teste falhou

**Dúvidas?**
- Verifique `MULTI_AGENT_PROPOSAL.md` para arquitetura
- Verifique logs para debug

---

**Boa sorte nos testes!** 🚀

Aguardando seu feedback para continuar com a Fase 2! 💙
