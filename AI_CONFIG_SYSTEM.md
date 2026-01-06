# 🚀 Sistema de Configuração Dinâmica da IA - Multi-Tenant

## 📋 Visão Geral

Sistema escalável que permite configurar a IA de cada clínica através de um **Wizard Visual**, sem necessidade de código hardcoded.

---

## 🏗️ Arquitetura

### 1. **Banco de Dados** (`ai_configurations`)
```sql
- id: UUID
- clinic_id: UUID (FK para clinicas)
- config: JSONB (configuração completa)
- is_active: BOOLEAN
- version: INTEGER (histórico de versões)
- created_at, updated_at
```

### 2. **Backend**

#### `ai_config_service.py`
- **Função:** Gera prompts dinamicamente a partir da configuração JSON
- **Método principal:** `generate_system_prompt(config)`
- **Input:** JSON com persona, team, admin_info, protocols
- **Output:** Prompt completo formatado

#### `ai_config.py` (API)
- `GET /api/ai-config/{clinic_id}` - Buscar configuração ativa
- `POST /api/ai-config/{clinic_id}` - Criar/Atualizar configuração
- `GET /api/ai-config/{clinic_id}/history` - Histórico de versões
- `POST /api/ai-config/{clinic_id}/restore/{version}` - Restaurar versão
- `GET /api/ai-config/{clinic_id}/preview` - Preview do prompt gerado

#### `gpt_service.py` (Atualizado)
- Carrega configuração do banco **por request**
- Fallback para prompt hardcoded da Bem-Querer
- Suporta multi-tenant automaticamente

### 3. **Frontend** (A Implementar)

#### Wizard de Configuração
```
Passo 1: Persona
  - Nome da assistente
  - Nome da clínica
  - Tom de voz
  - Público-alvo
  
Passo 2: Equipe Médica
  - Adicionar profissionais
  - Especialidades
  - Horários de atendimento
  - ID Clinicorp
  
Passo 3: Informações Administrativas
  - Endereço
  - Horários
  - Valores
  - Convênios
  - Contatos
  
Passo 4: Protocolos
  - Emergência
  - Agendamento
  - Regras (Fazer/Não Fazer)
  
Passo 5: Preview & Salvar
  - Visualizar prompt gerado
  - Testar com mensagem exemplo
  - Salvar configuração
```

---

## 📊 Estrutura do JSON de Configuração

```json
{
  "persona": {
    "name": "Carol",
    "clinic_name": "Bem-Querer Odontokids",
    "role": "secretária virtual",
    "tone": "Empática, acolhedora e eficiente",
    "target_audience": "Mães preocupadas",
    "objective": "Agendar consultas",
    "voice_examples": "Use 'pequeno(a)', 'mamãe'"
  },
  "team": [
    {
      "name": "Dra. Fernanda",
      "clinicorp_id": "6113706666688512",
      "specialty": "Ortodontia",
      "focus": "Aparelhos fixos",
      "schedule": "Seg, Qua, Sex, Sáb"
    }
  ],
  "admin_info": {
    "location": {
      "address": "Rua X, 123",
      "reference": "Próximo ao Y",
      "parking": "Estacionamento Z"
    },
    "schedule": {
      "weekdays": "08h às 19h",
      "saturday": "09h às 16h"
    },
    "pricing": {
      "consultation": "R$ 250,00",
      "consultation_note": "Grátis se fechar tratamento",
      "insurance": "Não atendemos. Emitimos NF",
      "payment_methods": "PIX, Cartão"
    },
    "contact": {
      "phone": "(11) 1234-5678",
      "website": "clinica.com.br",
      "instagram": "@clinica"
    }
  },
  "protocols": {
    "emergency": {
      "triggers": "Trauma, dor, sangramento",
      "steps": [
        "Acolher imediatamente",
        "Coletar dados",
        "Orientar sem medicar"
      ]
    },
    "scheduling": {
      "steps": [
        "Coletar nome e idade",
        "Perguntar período",
        "Oferecer 2 opções"
      ]
    },
    "do_rules": [
      "Sempre coletar telefone",
      "Ser transparente"
    ],
    "dont_rules": [
      "NUNCA inventar horários",
      "NUNCA medique"
    ]
  }
}
```

---

## 🔄 Fluxo de Funcionamento

### 1. **Configuração Inicial** (Uma vez por clínica)
```
Admin acessa Wizard → Preenche dados → Salva no banco
```

### 2. **Runtime** (A cada mensagem)
```
Usuário envia mensagem
  ↓
Backend identifica clinic_id
  ↓
GPT Service carrega config do banco
  ↓
Gera prompt dinamicamente
  ↓
Processa mensagem com OpenAI
  ↓
Retorna resposta personalizada
```

### 3. **Atualização** (Quando necessário)
```
Admin edita config no Wizard
  ↓
Nova versão salva no banco
  ↓
Versão anterior arquivada (histórico)
  ↓
Próxima mensagem usa nova config
```

---

## ✅ Vantagens do Sistema

### 1. **Escalabilidade**
- ✅ Adicionar nova clínica = preencher wizard (5 min)
- ✅ Sem código hardcoded
- ✅ Multi-tenant nativo

### 2. **Flexibilidade**
- ✅ Cada clínica tem sua persona
- ✅ Equipes diferentes
- ✅ Protocolos customizados

### 3. **Manutenção**
- ✅ Histórico de versões
- ✅ Rollback fácil
- ✅ Preview antes de salvar

### 4. **Experiência do Usuário**
- ✅ Wizard visual intuitivo
- ✅ Sem necessidade de entender código
- ✅ Teste em tempo real

---

## 🚧 Próximos Passos

### Backend ✅ (Concluído)
- [x] Criar tabela `ai_configurations`
- [x] Criar `AIConfigService`
- [x] Criar API REST
- [x] Integrar com `GPTService`

### Frontend 🔄 (A Implementar)
- [ ] Criar página de Configuração da IA
- [ ] Implementar Wizard multi-step
- [ ] Formulários para cada seção
- [ ] Preview do prompt gerado
- [ ] Teste com mensagem exemplo
- [ ] Histórico de versões

### Testes 🧪 (A Fazer)
- [ ] Testar criação de config
- [ ] Testar geração de prompt
- [ ] Testar multi-tenant
- [ ] Testar rollback de versão

---

## 📝 Exemplo de Uso da API

### Criar Configuração
```bash
POST /api/ai-config/00000000-0000-0000-0000-000000000001
{
  "persona": {...},
  "team": [...],
  "admin_info": {...},
  "protocols": {...}
}
```

### Buscar Configuração Ativa
```bash
GET /api/ai-config/00000000-0000-0000-0000-000000000001
```

### Preview do Prompt
```bash
GET /api/ai-config/00000000-0000-0000-0000-000000000001/preview
```

### Histórico
```bash
GET /api/ai-config/00000000-0000-0000-0000-000000000001/history
```

### Restaurar Versão
```bash
POST /api/ai-config/00000000-0000-0000-0000-000000000001/restore/3
```

---

## 🎯 Resultado Final

**Antes:** Criar arquivo Python hardcoded para cada clínica (2-3 horas)

**Depois:** Preencher wizard visual (5-10 minutos)

**Escalabilidade:** 1 clínica → 100 clínicas sem mudança de código! 🚀
