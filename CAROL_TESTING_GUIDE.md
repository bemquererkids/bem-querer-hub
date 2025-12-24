# 🧪 Guia de Testes - Carol (Agente Analítico)

## 📋 Pré-requisitos

- ✅ Backend rodando (local ou produção)
- ✅ Tabelas criadas no Supabase (`carol_ai_schema.sql`)
- ✅ `OPENAI_API_KEY` configurada
- ✅ Dados de teste no CRM (deals)

---

## 🔧 Ferramentas de Teste

### Opção 1: cURL (Terminal)
### Opção 2: Postman/Insomnia
### Opção 3: Python Script

---

## 🎯 Testes de Analytics

### 1. Consultar Leads do Mês

**Endpoint:** `POST /api/conversations/chat`

```json
{
  "message": "Quantos leads tivemos este mês?",
  "clinica_id": "00000000-0000-0000-0000-000000000001",
  "thread_id": null
}
```

**Resposta Esperada:**
```json
{
  "thread_id": "uuid-da-thread",
  "response": "Este mês vocês tiveram X leads novos! Desses, Y foram agendados (Z% de conversão).",
  "created_at": "2025-12-24T..."
}
```

### 2. Taxa de Comparecimento

```json
{
  "message": "Qual a taxa de comparecimento desta semana?",
  "clinica_id": "00000000-0000-0000-0000-000000000001",
  "thread_id": "uuid-da-thread-anterior"
}
```

### 3. Vendas do Mês Passado

```json
{
  "message": "Quantas vendas fizemos no mês passado?",
  "clinica_id": "00000000-0000-0000-0000-000000000001"
}
```

### 4. Conversão de Leads

```json
{
  "message": "Qual nossa taxa de conversão de leads para vendas este ano?",
  "clinica_id": "00000000-0000-0000-0000-000000000001"
}
```

---

## 📚 Testes de RAG (Documentos)

### Passo 1: Upload de Documento

**Endpoint:** `POST /api/knowledge/documents/text`

```json
{
  "titulo": "Tabela de Preços 2024",
  "tipo": "preco",
  "clinica_id": "00000000-0000-0000-0000-000000000001",
  "conteudo": "TABELA DE PREÇOS - BEM-QUERER ODONTOLOGIA\n\nLimpeza: R$ 150,00\nClareamento Dental: R$ 850,00\nImplante Dentário: R$ 3.500,00\nAparelho Ortodôntico: R$ 2.800,00\nExtração de Dente: R$ 200,00\nCanal: R$ 600,00\nRestauração: R$ 180,00"
}
```

**Resposta Esperada:**
```json
{
  "success": true,
  "documento_id": "uuid",
  "chunks_processados": 1
}
```

### Passo 2: Consultar Preços via Carol

```json
{
  "message": "Quanto custa um clareamento dental?",
  "clinica_id": "00000000-0000-0000-0000-000000000001"
}
```

**Resposta Esperada:**
```
"De acordo com nossa tabela de preços, o clareamento dental custa R$ 850,00. [Fonte: Tabela de Preços 2024]"
```

### Passo 3: Consultar Política

**Upload de Política:**
```json
{
  "titulo": "Política de Cancelamento",
  "tipo": "politica",
  "clinica_id": "00000000-0000-0000-0000-000000000001",
  "conteudo": "POLÍTICA DE CANCELAMENTO\n\nCancelamentos devem ser feitos com no mínimo 24 horas de antecedência.\nCancelamentos com menos de 24h de antecedência serão cobrados 50% do valor da consulta.\nFaltas sem aviso prévio serão cobradas 100% do valor."
}
```

**Consulta:**
```json
{
  "message": "Qual a política de cancelamento?",
  "clinica_id": "00000000-0000-0000-0000-000000000001"
}
```

---

## 🔄 Testes de Contexto (Histórico)

### Conversa Sequencial

**Mensagem 1:**
```json
{
  "message": "Quantos leads tivemos este mês?",
  "clinica_id": "xxx"
}
```

**Mensagem 2 (mesma thread):**
```json
{
  "message": "E quantos viraram vendas?",
  "clinica_id": "xxx",
  "thread_id": "thread-da-msg-1"
}
```

**Mensagem 3:**
```json
{
  "message": "Isso é bom ou ruim?",
  "clinica_id": "xxx",
  "thread_id": "thread-da-msg-1"
}
```

A Carol deve manter contexto e responder adequadamente.

---

## 🐍 Script Python para Testes

```python
import requests
import json

BASE_URL = "http://localhost:8000"  # ou URL da Vercel
CLINICA_ID = "00000000-0000-0000-0000-000000000001"

def chat_with_carol(message, thread_id=None):
    """Envia mensagem para Carol."""
    response = requests.post(
        f"{BASE_URL}/api/conversations/chat",
        json={
            "message": message,
            "clinica_id": CLINICA_ID,
            "thread_id": thread_id
        }
    )
    return response.json()

def upload_document(titulo, tipo, conteudo):
    """Upload de documento."""
    response = requests.post(
        f"{BASE_URL}/api/knowledge/documents/text",
        json={
            "titulo": titulo,
            "tipo": tipo,
            "clinica_id": CLINICA_ID,
            "conteudo": conteudo
        }
    )
    return response.json()

# Teste 1: Analytics
print("=== TESTE 1: ANALYTICS ===")
result = chat_with_carol("Quantos leads tivemos este mês?")
print(f"Carol: {result['response']}\n")

# Teste 2: Upload de Documento
print("=== TESTE 2: UPLOAD DOCUMENTO ===")
doc = upload_document(
    "Tabela de Preços",
    "preco",
    "Clareamento: R$ 850,00\nImplante: R$ 3.500,00"
)
print(f"Documento criado: {doc['documento_id']}\n")

# Teste 3: RAG
print("=== TESTE 3: RAG ===")
result = chat_with_carol("Quanto custa um implante?")
print(f"Carol: {result['response']}\n")

# Teste 4: Contexto
print("=== TESTE 4: CONTEXTO ===")
result1 = chat_with_carol("Quantos leads tivemos?")
thread_id = result1['thread_id']
print(f"Carol: {result1['response']}")

result2 = chat_with_carol("E quantos viraram vendas?", thread_id)
print(f"Carol: {result2['response']}\n")
```

---

## ✅ Checklist de Validação

### Analytics
- [ ] Carol responde sobre leads do mês
- [ ] Carol calcula taxa de conversão
- [ ] Carol fornece dados de comparecimento
- [ ] Carol analisa vendas por período

### RAG
- [ ] Upload de documento funciona
- [ ] Embeddings são gerados
- [ ] Busca semântica retorna resultados relevantes
- [ ] Carol cita fontes nas respostas

### Histórico
- [ ] Threads são criadas automaticamente
- [ ] Mensagens são salvas
- [ ] Contexto é mantido entre mensagens
- [ ] Histórico pode ser recuperado

### Integração
- [ ] Carol usa function calling corretamente
- [ ] Escolhe ferramenta certa (analytics vs RAG)
- [ ] Combina múltiplas fontes quando necessário

---

## 🐛 Troubleshooting

### Erro: "clinica_id não fornecido"
**Solução:** Sempre enviar `clinica_id` no body da requisição

### Erro: "Nenhum documento relevante encontrado"
**Solução:** Fazer upload de documentos primeiro via `/api/knowledge/documents/text`

### Carol não responde com dados reais
**Solução:** Verificar se há dados de teste na tabela `deals` do Supabase

### Embeddings não funcionam
**Solução:** 
1. Verificar se `OPENAI_API_KEY` está configurada
2. Verificar se extensão `pgvector` está habilitada no Supabase
3. Verificar logs do backend

---

## 📊 Dados de Teste Sugeridos

### Inserir Deals de Teste (SQL)

```sql
INSERT INTO deals (clinica_id, patient_name, phone, status, created_at, updated_at)
VALUES 
  ('00000000-0000-0000-0000-000000000001', 'João Silva', '11999999999', 'new', NOW() - INTERVAL '5 days', NOW()),
  ('00000000-0000-0000-0000-000000000001', 'Maria Santos', '11888888888', 'scheduled', NOW() - INTERVAL '3 days', NOW()),
  ('00000000-0000-0000-0000-000000000001', 'Pedro Costa', '11777777777', 'attended', NOW() - INTERVAL '1 day', NOW()),
  ('00000000-0000-0000-0000-000000000001', 'Ana Lima', '11666666666', 'won', NOW(), NOW());
```

---

## 🎯 Resultado Esperado

Após os testes, a Carol deve:
- ✅ Responder perguntas analíticas com dados reais do banco
- ✅ Consultar documentos e citar fontes
- ✅ Manter contexto em conversas
- ✅ Escolher a ferramenta certa automaticamente
- ✅ Fornecer insights e sugestões

**Exemplo de Conversa Ideal:**
```
👤: Quantos leads tivemos este mês?
🤖: Este mês vocês tiveram 156 leads novos! Desses, 76 foram agendados (48.7% de conversão).

👤: Isso é bom?
🤖: Sim! A taxa de conversão de 48.7% está acima da média do setor (40%). Parabéns! 🎯

👤: Quanto custa um implante?
🤖: De acordo com nossa tabela de preços, o implante dentário custa R$ 3.500,00. [Fonte: Tabela de Preços 2024]
```
