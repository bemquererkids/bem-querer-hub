# 🐛 DEBUG: Problema de Repetição da Carol

**Status:** 🔴 EM INVESTIGAÇÃO  
**Última Tentativa:** Deploy com logs de debug (12:40)

---

## 📋 PROBLEMA

Carol continua repetindo a mensagem de boas-vindas:

```
Usuário: "Olá"
Carol: "Boa tarde! Sou a Carol... A consulta é para você ou seu filho?"

Usuário: "Minha filha"
Carol: "Boa tarde! Sou a Carol... A consulta é para você ou seu filho?" ❌ REPETE
```

---

## 🔍 INVESTIGAÇÃO

### Tentativa 1: Verificar agent_history
**Código:**
```python
is_first_interaction = len(state.agent_history) <= 1
```

**Problema:** `agent_history` sempre tem 1 item quando Router → Triagem, então sempre mostra saudação!

---

### Tentativa 2: Contar aparições de Triagem
**Código:**
```python
triagem_count = sum(1 for h in state.agent_history if h.get("to") == "triagem")
is_first_interaction = triagem_count <= 1
```

**Problema:** Toda mensagem passa pelo Router novamente, então `triagem_count` sempre é 1!

---

### Tentativa 3: Verificar collected_data
**Código:**
```python
has_any_data = bool(collected and len(collected) > 0)
if not has_any_data:
    # Mostra saudação
```

**Problema Suspeito:** `collected_data` pode estar vazio na segunda mensagem se o **estado não estiver sendo persistido**!

---

## 🚨 HIPÓTESE PRINCIPAL

**O estado não está sendo mantido entre mensagens!**

### Evidências:
1. `ConversationManager` usa cache **em memória** (dict Python)
2. Railway **reinicia o servidor** a cada deploy
3. Pode haver **múltiplas instâncias** do servidor
4. Estado não está sendo salvo em banco de dados

### Código Problemático:
```python
# conversation_manager.py linha 136
class ConversationManager:
    def __init__(self):
        # ❌ Cache em memória - perde tudo ao reiniciar!
        self._conversations: Dict[str, ConversationState] = {}
```

---

## 🧪 DEPLOY ATUAL (12:40)

**Mudanças:**
- ✅ Adicionados logs detalhados no Triagem Agent
- ✅ Logs mostrarão:
  - `collected_data` atual
  - `agent_history` completo
  - Se tem dados ou não

**Logs Esperados:**
```
🔍 Triagem Debug: collected_data = {}
🔍 Triagem Debug: agent_history length = 1
🔍 Triagem Debug: agent_history = [{"from": "router", "to": "triagem", ...}]
🔍 Triagem Debug: has_any_data = False
🔍 Triagem: Mostrando saudação (primeira interação)
```

**Segunda Mensagem (se estado for mantido):**
```
🔍 Triagem Debug: collected_data = {"tipo": "kids"}
🔍 Triagem Debug: has_any_data = True
🔍 Triagem: NÃO é primeira interação, processando normalmente
```

**Segunda Mensagem (se estado for PERDIDO):**
```
🔍 Triagem Debug: collected_data = {}  ❌ VAZIO DE NOVO!
🔍 Triagem Debug: has_any_data = False
🔍 Triagem: Mostrando saudação (primeira interação)  ❌ REPETE!
```

---

## 📊 PRÓXIMOS PASSOS

### 1. Aguardar Deploy (~5 min)
- ETA: 12:45

### 2. Testar Novamente
```
Mensagem 1: "Olá"
Mensagem 2: "Minha filha"
```

### 3. Verificar Logs no Railway
Procurar por:
```
🔍 Triagem Debug: collected_data = ...
```

### 4. Analisar Resultados

**Se collected_data está vazio na 2ª mensagem:**
- ✅ Confirma que estado não está sendo persistido
- ✅ Solução: Salvar estado em banco de dados (Supabase)

**Se collected_data tem dados na 2ª mensagem:**
- ❌ Problema está em outro lugar
- ❌ Investigar lógica de extração de dados

---

## 💡 SOLUÇÕES POSSÍVEIS

### Solução 1: Persistir Estado no Supabase (RECOMENDADO)
```python
# Salvar estado no banco após cada mensagem
def save(self, state: ConversationState):
    supabase.table("conversation_states").upsert({
        "phone": state.phone,
        "clinic_id": state.clinic_id,
        "collected_data": state.collected_data,
        "agent_history": state.agent_history,
        ...
    }).execute()
```

### Solução 2: Usar Redis (Rápido mas requer infra)
```python
import redis
redis_client.set(f"conv:{phone}", json.dumps(state.to_dict()))
```

### Solução 3: Extrair Dados da Mensagem Diretamente (Workaround)
```python
# Não depender de estado persistido
# Extrair "minha filha" → tipo=kids diretamente
if "filha" in message or "filho" in message:
    # Já sabe que não é primeira vez
    return "Qual o nome?"
```

---

## 🎯 AÇÃO IMEDIATA

**Aguardar logs do próximo teste para confirmar hipótese!**

Após confirmar, implementar Solução 1 (Supabase) para persistência real do estado.

---

**Última Atualização:** 12:40  
**Próximo Deploy:** Aguardando resultados dos logs
