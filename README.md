# 🏥 Bem-Querer Hub

Sistema SaaS B2B completo para centralizar atendimento, vendas e agendamentos em clínicas odontológicas.

## 🌟 Funcionalidades Ativas

### ✅ Integrações em Produção
- **WhatsApp Business** - Atendimento via UazAPI
- **Clinicorp** - Sistema de agendamento odontológico
- **OpenAI GPT-4o** - IA conversacional para agendamentos
- **Google Gemini 2.0** - IA multimodal avançada
- **Supabase** - Banco de dados PostgreSQL com autenticação

### ✅ Features Implementadas
- 🤖 **Chat AI (Carol)** - Assistente virtual para agendamentos
- 📅 **Agendamento Inteligente** - Interpretação de datas naturais ("amanhã", "segunda")
- 👥 **Multi-tenancy** - Isolamento por clínica com RLS
- 💾 **Persistência de Integrações** - Configurações salvas no Supabase
- 📊 **CRM** - Gestão de leads e pacientes
- 🔔 **Webhooks** - Processamento de mensagens WhatsApp

## 📁 Estrutura do Projeto

```
sistemabemquerer/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/               # Rotas da API
│   │   │   ├── chat.py        # Endpoints do chat AI
│   │   │   ├── integration.py # Integrações (Clinicorp, OpenAI, etc)
│   │   │   └── webhooks.py    # Webhooks WhatsApp
│   │   ├── services/          # Lógica de negócio
│   │   │   ├── gpt_service.py       # OpenAI GPT-4o
│   │   │   ├── gemini_service.py    # Google Gemini
│   │   │   ├── clinicorp_service.py # API Clinicorp
│   │   │   └── uazapi_service.py    # WhatsApp
│   │   ├── core/              # Config, Database, Security
│   │   └── main.py            # Entry point
│   ├── requirements.txt
│   └── .env
├── frontend/                   # React + Vite + TypeScript
│   ├── src/
│   │   ├── components/        # Componentes React
│   │   │   ├── chat/          # Interface de chat
│   │   │   ├── settings/      # Configurações e integrações
│   │   │   └── crm/           # CRM e leads
│   │   ├── services/          # API clients
│   │   └── App.tsx
│   └── package.json
├── supabase/                   # Database Schema
│   ├── schema.sql             # PostgreSQL + RLS
│   └── integrations_schema.sql # Tabela de integrações
└── DB_MIGRATION_GUIDE.md      # Guia de migração do BD
```

## 🚀 Deploy em Produção

### Plataforma
**Railway** - Deploy automático via GitHub

### URL de Produção
**Frontend + Backend**: Configurado na Railway

### Variáveis de Ambiente (Railway)

Configure no painel da Railway em **Variables**:

```env
# Supabase
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# OpenAI (ChatGPT)
OPENAI_API_KEY=sk-...

# Google Gemini
GEMINI_API_KEY=AIzaSy...

# Clinicorp (Opcional - pode ser configurado via UI)
CLINICORP_CLIENT_ID=bemquerer
CLINICORP_CLIENT_SECRET=...

# WhatsApp (UazAPI)
UAZAPI_BASE_URL=https://bemquerer.uazapi.com
UAZAPI_TOKEN=...
UAZAPI_INSTANCE=bemquerer
PUBLIC_URL=https://bem-querer-hub.vercel.app
```

## 🗄️ Configuração do Banco de Dados

### 1. Criar Tabelas Principais
Execute no SQL Editor do Supabase:
```sql
-- Ver arquivo: supabase/schema.sql
```

### 2. Criar Tabela de Integrações (IMPORTANTE!)
Execute no SQL Editor do Supabase:
```sql
-- Ver arquivo: backend/integrations_schema.sql
```

Esta tabela é essencial para a persistência das credenciais das integrações.

## 🔧 Desenvolvimento Local

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Acesse: http://localhost:8000/docs

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Acesse: http://localhost:5173

## 🏗️ Arquitetura

### Stack Tecnológico
- **Frontend**: React 18 + Vite + TypeScript + TailwindCSS
- **Backend**: Python 3.11 + FastAPI
- **Database**: Supabase (PostgreSQL + Auth + RLS)
- **AI**: OpenAI GPT-4o + Google Gemini 2.0 Flash
- **WhatsApp**: UazAPI
- **Deploy**: Railway (Container-based)

### Fluxo de Agendamento com IA

1. **Usuário** envia mensagem via WhatsApp
2. **UazAPI** envia webhook para `/api/webhooks/whatsapp`
3. **Backend** processa com GPT-4o usando Function Calling
4. **GPT** chama `check_availability` do Clinicorp
5. **Carol (IA)** sugere horários disponíveis
6. **Usuário** confirma e agendamento é criado

### Persistência de Integrações

As credenciais são salvas na tabela `clinic_integrations` do Supabase:
- Permite configurar via UI
- Persiste entre sessões e dispositivos
- Fallback para variáveis de ambiente

## 📚 Documentação Adicional

- [SETUP.md](SETUP.md) - Guia completo de configuração inicial
- [DB_MIGRATION_GUIDE.md](DB_MIGRATION_GUIDE.md) - Como criar a tabela de integrações
- [Backend API](backend/API.md) - Documentação dos endpoints
- [GEMINI.MD](GEMINI.MD) - Contexto completo do projeto para IA

## 🎨 Design System

- **Cores Primárias**: 
  - Bem-Querer Blue: `#00A3E0`
  - Soft Lilac: `#E0D7F5`
- **Fontes**: 
  - UI: Nunito
  - Dados: Roboto Mono
- **Estética**: "Pediatric Soft-Tech" - Moderno, acolhedor e profissional

## 🔐 Segurança

- ✅ Autenticação via Supabase Auth (JWT)
- ✅ Row Level Security (RLS) no banco
- ✅ Middleware de tenant isolation
- ✅ Credenciais criptografadas no Supabase
- ✅ CORS configurado para domínio específico
- ✅ Validação de webhooks

## 📊 Status do Projeto

### ✅ Concluído
- [x] Backend FastAPI completo
- [x] Frontend React com UI moderna
- [x] Integração WhatsApp (UazAPI)
- [x] Integração Clinicorp (agendamentos)
- [x] Chat AI com GPT-4o
- [x] Persistência de integrações
- [x] Deploy em produção (Vercel)
- [x] Interpretação inteligente de datas
- [x] Nomes de profissionais nos horários

### 🚧 Em Desenvolvimento
- [ ] Dashboard de métricas
- [ ] Relatórios de atendimento
- [ ] Integração com mais sistemas de agenda

## 🆘 Suporte

Para problemas ou dúvidas:
1. Verifique os logs no painel da Railway
2. Consulte a documentação em `/docs`
3. Revise as variáveis de ambiente

## 📝 Changelog

### v1.0.0 (2025-12-26)
- ✅ Sistema completo em produção
- ✅ Todas as integrações funcionais
- ✅ Persistência via Supabase implementada
- ✅ Chat AI com agendamento inteligente
