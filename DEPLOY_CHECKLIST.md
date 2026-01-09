# 🚀 DEPLOY CHECKLIST - RAG Multiagentes

**Data:** 09/01/2026 12:15
**Status:** ✅ PRONTO PARA DEPLOY

---

## ✅ O QUE FOI FEITO

### 1. **Bug Fix: Fluxo de Conversa** ✅
- **Arquivo:** `backend/app/services/agents.py` (linha 166)
- **Problema:** Carol repetia mensagem de boas-vindas
- **Solução:** Verificação de histórico de agentes
- **Status:** ✅ Corrigido

### 2. **RAG Integrado ao Multiagentes** ✅
- **Arquivo:** `backend/app/services/multi_agent_orchestrator.py` (linhas 116-145)
- **Serviço:** Usando `KnowledgeBaseService` (já existente)
- **Base:** `knowledge_base/` na raiz do projeto (4 documentos .md)
- **Status:** ✅ Integrado

### 3. **Agentes Kids e Adulto com RAG** ✅
- **Arquivo:** `backend/app/services/agents.py` (linhas 257-393)
- **KidsAgent:** Odontopediatria com RAG
- **AdultoAgent:** Odontologia geral com RAG
- **Status:** ✅ Implementados

---

## 📁 ARQUIVOS MODIFICADOS

```
backend/app/services/
├── agents.py ✅ MODIFICADO
│   - Linha 166: Fix fluxo de conversa
│   - Linhas 257-393: Agentes Kids e Adulto
│
└── multi_agent_orchestrator.py ✅ MODIFICADO
    - Linhas 116-145: Integração RAG
```

**Arquivos já existentes (não modificados):**
- `knowledge_base_service.py` ✅ (já funcionando)
- `knowledge_base/*.md` ✅ (4 documentos)

---

## 🎯 COMO TESTAR APÓS DEPLOY

### Teste 1: Fluxo Natural
```
Você: "Bom dia"
Carol: "Boa tarde! Sou a Carol... A consulta é para você ou seu filho?"

Você: "Para meu filho"
Carol: "Qual o nome dele? 🦷" ✅ (não repete mais!)
```

### Teste 2: RAG Funcionando
```
Você: [completar triagem]
Você: "Quanto custa limpeza dental?"
Carol: "De acordo com nossa tabela, a limpeza (profilaxia) para crianças 
       custa R$ 150,00..." ✅ (usando knowledge_base!)
```

### Teste 3: Convênios
```
Você: "Quais convênios vocês aceitam?"
Carol: "Aceitamos: Unimed Odonto, Bradesco Dental, SulAmérica..." ✅
```

---

## 📊 LOGS ESPERADOS NO RAILWAY

```bash
# Sistema iniciando:
📚 Loading 4 knowledge documents...
   ✅ Loaded: Especialidades e Valores
   ✅ Loaded: Preparos para Exames
   ✅ Loaded: Políticas da Clínica
   ✅ Loaded: FAQ
✅ Knowledge base loaded: 4 documents

# Multi-agent ativo:
🤖 Using Multi-Agent System

# RAG funcionando:
📚 RAG: Found relevant knowledge for query
```

---

## ⚙️ VARIÁVEIS DE AMBIENTE (Railway)

```bash
# Já configuradas:
USE_MULTI_AGENT=true
OPENAI_API_KEY=sk-...
SUPABASE_URL=...
SUPABASE_KEY=...
UAZAPI_BASE_URL=https://bemquerer.uazapi.com
UAZAPI_TOKEN=093b971c-f10f-4af1-b0aa-a13c6ad15909
```

**Nenhuma variável nova necessária!** ✅

---

## 🚀 PASSOS PARA DEPLOY

### 1. Commit e Push
```bash
git add .
git commit -m "feat: RAG multiagentes integrado + fix fluxo conversa"
git push origin main
```

### 2. Railway Deploy Automático
- Railway detecta push
- Inicia build (~3-5 min)
- Deploy automático

### 3. Verificar Logs
```bash
# No Railway, procurar por:
📚 Loading 4 knowledge documents...
✅ Knowledge base loaded: 4 documents
🤖 Using Multi-Agent System
```

### 4. Testar via WhatsApp
- Enviar: "Bom dia"
- Enviar: "Para meu filho"
- Verificar se não repete mensagem ✅
- Perguntar: "Quanto custa limpeza?"
- Verificar se usa RAG ✅

---

## 🐛 TROUBLESHOOTING

### Problema: Knowledge base não carrega
**Logs:** `Knowledge base path does not exist`
**Solução:** Verificar se pasta `knowledge_base/` está na raiz do projeto (não em `backend/`)

### Problema: RAG não encontra nada
**Logs:** `📚 RAG: No relevant knowledge found`
**Solução:** Normal para perguntas muito genéricas. Testar com perguntas específicas:
- "Quanto custa neuropediatria?"
- "Quais convênios aceitam?"
- "Preciso fazer jejum?"

### Problema: Carol ainda repete mensagem
**Logs:** Verificar se código novo foi deployado
**Solução:** Verificar timestamp do deploy, fazer redeploy se necessário

---

## 📈 MÉTRICAS DE SUCESSO

### Antes:
- ❌ Carol repetia mensagens
- ❌ Respostas genéricas
- ❌ Não sabia valores/convênios

### Depois (Esperado):
- ✅ Fluxo natural de conversa
- ✅ Respostas com informações reais
- ✅ Conhece valores, convênios, preparos

---

## 📝 PRÓXIMOS PASSOS

### Após Deploy Bem-Sucedido:
1. ✅ Monitorar primeiras conversas
2. ✅ Coletar feedback
3. ✅ Ajustar base de conhecimento se necessário

### Melhorias Futuras:
1. Agente de Agendamento (integração Clinicorp)
2. Botões interativos
3. Métricas e analytics
4. Mais documentos na base

---

**Status:** ✅ **PRONTO PARA DEPLOY**

**Ação Necessária:** Commit + Push → Railway faz o resto!
