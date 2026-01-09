# 🤖 Arquitetura de Agentes - Bem-Querer Odontologia

## 📊 Comparação de Arquiteturas

### **Opção 1: Agente Único (Atual)**

```
┌─────────────────────────────────┐
│         CAROL (Único)            │
│                                  │
│  ├─ Detecta contexto            │
│  ├─ Consulta RAG                │
│  ├─ Responde tudo               │
│  └─ Pode transferir p/ humano   │
└─────────────────────────────────┘
```

**✅ Vantagens:**
- Simples de implementar
- Rápido (1 chamada GPT)
- Menos complexo de manter
- Já está funcionando

**❌ Desvantagens:**
- Menos especializado
- Difícil controlar fluxo
- Pode confundir contextos
- Menos "humano"

**💰 Custo:** ~$0.02 por conversa

---

### **Opção 2: Multi-Agent com Orquestrador (Recomendado)**

```
┌──────────────────────────────────────────┐
│      ORQUESTRADOR (Router)               │
│   Analisa e roteia para agente certo     │
└────────────┬─────────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
┌───▼────┐      ┌─────▼─────┐
│TRIAGEM │      │  HUMANO   │
│ Agent  │      │  Handoff  │
└───┬────┘      └───────────┘
    │
    ├─────────────┐
    │             │
┌───▼────┐   ┌───▼─────┐
│ KIDS   │   │ ADULTO  │
│ Agent  │   │ Agent   │
└───┬────┘   └───┬─────┘
    │            │
    └─────┬──────┘
          │
    ┌─────▼──────┐
    │AGENDAMENTO │
    │   Agent    │
    └────────────┘
```

**✅ Vantagens:**
- Muito mais especializado
- Fluxo controlado (como n8n)
- Linguagem natural
- Handoff suave para humano
- Contexto preservado
- Parece mais humano

**❌ Desvantagens:**
- Mais complexo
- Mais chamadas GPT
- Precisa orquestração

**💰 Custo:** ~$0.05-0.08 por conversa (2-4 agentes)

---

## 🎯 Recomendação: **Opção 2 (Multi-Agent)**

### Por quê?

1. **Você já tem fluxo n8n** - Multi-agent replica isso
2. **Linguagem mais natural** - Cada agente especializado
3. **Handoff profissional** - Humano pode intervir a qualquer momento
4. **Não parece robô** - Conversas mais fluidas
5. **Escalável** - Fácil adicionar novos agentes

---

## 🏗️ Implementação Proposta

### **Fase 1: Agentes Principais** (2 semanas)

#### 1. **Router Agent** (Orquestrador)
```python
Responsabilidade:
- Analisar primeira mensagem
- Detectar intenção (emergência, agendamento, dúvida)
- Detectar tipo (kids, adulto)
- Rotear para agente correto

Output:
{
  "next_agent": "triagem|kids|adulto|humano",
  "patient_type": "kids|adulto|indefinido",
  "intent": "emergencia|agendamento|duvida",
  "confidence": 0.95
}
```

#### 2. **Triagem Agent**
```python
Responsabilidade:
- Primeira interação
- Coletar dados básicos (nome, idade, motivo)
- Identificar se é kids ou adulto
- Transferir para agente especializado

Quando transferir:
- Tem tipo (kids/adulto) + nome + motivo → Transfere
```

#### 3. **Kids Agent**
```python
Responsabilidade:
- Atendimento infantil especializado
- Conhece: Odontopediatria, Ortodontia Kids, OFM, PNE
- Tom: Maternal, acolhedor
- Emojis: 🎈, 💙, 🌟

Quando transferir:
- Decidiu agendar → Agendamento Agent
- Pediu humano → Humano Handoff
```

#### 4. **Adulto Agent**
```python
Responsabilidade:
- Atendimento adulto especializado
- Conhece: Todas especialidades adulto
- Tom: Profissional, empático
- Emojis: 🦷, 💙

Quando transferir:
- Decidiu agendar → Agendamento Agent
- Pediu humano → Humano Handoff
```

#### 5. **Agendamento Agent**
```python
Responsabilidade:
- Finalizar agendamento
- Consultar disponibilidade
- Confirmar dados
- Criar agendamento

Quando transferir:
- Agendou com sucesso → FIM
- Problema → Humano Handoff
```

#### 6. **Humano Handoff**
```python
Responsabilidade:
- Transferir para humano
- Resumir contexto
- Marcar conversa como "aguardando_humano"
- Notificar equipe
- PARAR de responder (humano assumiu)

Gatilhos:
- "quero falar com atendente"
- "falar com humano"
- Reclamação
- Caso complexo
```

---

### **Fase 2: Handoff Inteligente** (1 semana)

#### **Detecção de Handoff:**

```python
GATILHOS_HUMANO = {
    "explícito": [
        "quero falar com atendente",
        "falar com humano",
        "atendente de verdade"
    ],
    "insatisfação": [
        "não está entendendo",
        "péssimo atendimento",
        "não resolve"
    ],
    "complexo": [
        "é complicado",
        "preciso explicar melhor"
    ],
    "reclamação": [
        "reclamação",
        "insatisfeito"
    ]
}
```

#### **Processo de Handoff:**

1. **Detecta gatilho** → Marca conversa
2. **Resumo de contexto:**
   ```
   RESUMO PARA ATENDENTE:
   - Paciente: João (7 anos)
   - Tipo: Kids
   - Motivo: Aparelho ortodôntico
   - Histórico: 3 mensagens
   - Solicitou: Falar com humano
   ```
3. **Notifica equipe** (WhatsApp, Dashboard, etc.)
4. **Mensagem ao paciente:**
   ```
   "Vou transferir você para nossa equipe agora.
   Um atendente vai te responder em instantes! 💙"
   ```
5. **Para de responder** (flag: `human_takeover = true`)

#### **Humano Pode Intervir:**

```python
# Em qualquer momento, humano pode:
1. Ver conversa em andamento
2. Clicar "Assumir conversa"
3. Sistema marca: human_takeover = true
4. IA para de responder
5. Humano continua naturalmente
```

---

## 💬 Exemplo de Conversa Multi-Agent

### **Cenário: Mãe quer agendar aparelho para filho**

```
[ROUTER AGENT]
Paciente: "Olá, preciso agendar"
Router: Analisa → indefinido, precisa triagem
→ Transfere para TRIAGEM AGENT

[TRIAGEM AGENT]
Triagem: "Olá! Será um prazer ajudar! 💙
         É para você ou para seu filho(a)?"

Paciente: "Para meu filho de 8 anos"
Triagem: Detecta KIDS + idade
→ Transfere para KIDS AGENT

[KIDS AGENT]
Kids: "Que ótimo! Qual o nome dele? 🎈"

Paciente: "Pedro"
Kids: "Oi Pedro! Qual o motivo da consulta?"

Paciente: "Precisa de aparelho"
Kids: "Com 8 anos ele está na fase ideal! 💙
      A avaliação vai definir se precisa:
      - OFM (crescimento ósseo)
      - Aparelho fixo (alinhar dentes)
      
      Vocês preferem manhã ou tarde?"

Paciente: "Manhã"
Kids: Decidiu agendar
→ Transfere para AGENDAMENTO AGENT

[AGENDAMENTO AGENT]
Agendamento: Consulta disponibilidade
            "Tenho disponível:
             - Terça 14/01 às 9h com Dra. Jaqueline (OFM)
             - Quarta 15/01 às 10h com Dra. Fernanda
             
             Qual prefere?"

Paciente: "Terça às 9h"
Agendamento: Confirma dados, agenda
            "Agendado! 🎈
             
             Pedro - Terça 14/01 às 9h
             Dra. Jaqueline (Avaliação Ortodôntica)
             
             Nos vemos lá! 💙"

[FIM - SUCESSO]
```

### **Cenário: Paciente quer humano**

```
[KIDS AGENT]
Kids: "Qual o motivo da consulta?"

Paciente: "É complicado, quero falar com atendente"
Kids: Detecta gatilho "quero falar com atendente"
→ Transfere para HUMANO HANDOFF

[HUMANO HANDOFF]
Handoff: 1. Resume contexto
         2. Notifica equipe
         3. Marca: human_takeover = true
         4. Responde: "Vou transferir você para nossa equipe.
                      Um atendente vai te responder em instantes! 💙"

[ATENDENTE HUMANO]
Sistema: Notifica atendente
Dashboard: Mostra conversa + contexto
Atendente: Assume e continua naturalmente

Atendente: "Olá! Sou a Fernanda, atendente da clínica.
           Vi que é para o Pedro. Como posso ajudar?"

[HUMANO ASSUMIU - IA PAROU]
```

---

## 🔧 Implementação Técnica

### **Estrutura de Dados:**

```python
conversation = {
    "id": "conv_123",
    "phone": "5548999999999",
    "current_agent": "kids",  # router, triagem, kids, adulto, agendamento, humano
    "patient_type": "kids",   # kids, adulto, indefinido
    "intent": "agendamento",  # emergencia, agendamento, duvida, institucional
    "human_takeover": False,  # Se humano assumiu
    "collected_data": {
        "patient_name": "Pedro",
        "patient_age": 8,
        "reason": "aparelho",
        "preferred_period": "manhã"
    },
    "agent_history": [
        {"agent": "router", "timestamp": "..."},
        {"agent": "triagem", "timestamp": "..."},
        {"agent": "kids", "timestamp": "..."}
    ],
    "messages": [...]
}
```

### **Fluxo de Processamento:**

```python
async def process_message(phone, message):
    # 1. Carregar conversa
    conv = load_conversation(phone)
    
    # 2. Verificar se humano assumiu
    if conv.human_takeover:
        # Não responder, humano está atendendo
        return None
    
    # 3. Verificar gatilhos de handoff
    if detect_human_handoff_trigger(message):
        return handoff_to_human(conv)
    
    # 4. Obter agente atual
    current_agent = conv.current_agent or "router"
    
    # 5. Processar com agente
    response, next_agent = await agents[current_agent].process(
        message, 
        conv.collected_data
    )
    
    # 6. Atualizar conversa
    conv.current_agent = next_agent
    save_conversation(conv)
    
    # 7. Retornar resposta
    return response
```

---

## 📊 Comparação de Custos

### **Agente Único:**
- 1 chamada GPT por mensagem
- ~$0.02 por conversa (5 mensagens)

### **Multi-Agent:**
- 2-4 chamadas GPT por mensagem (orquestração + agente)
- ~$0.05-0.08 por conversa (5 mensagens)

**Diferença:** +$0.03-0.06 por conversa

**Vale a pena?** **SIM!**
- Conversas mais naturais
- Menos transferências para humano
- Maior satisfação
- Mais conversões

---

## 🎯 Decisão

### **Recomendo: Multi-Agent**

**Motivos:**
1. ✅ Você já tem fluxo n8n (experiência com multi-agent)
2. ✅ Linguagem mais natural
3. ✅ Handoff profissional para humano
4. ✅ Não parece robô
5. ✅ Escalável e mantível

**Próximos Passos:**
1. Aprovar arquitetura
2. Implementar Router + Triagem (1 semana)
3. Implementar Kids + Adulto (1 semana)
4. Implementar Agendamento + Handoff (3 dias)
5. Testar e ajustar (2 dias)

**Total:** ~3 semanas para multi-agent completo

---

**Quer que eu implemente o sistema multi-agent?** 🚀
