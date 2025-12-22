# Bem-Querer Hub

Sistema SaaS B2B para centralizar atendimento e vendas em clínicas odontológicas.

## 📁 Estrutura do Projeto

```
sistemabemquerer/
├── backend/              # FastAPI Backend
│   ├── app/
│   │   ├── api/         # Rotas (webhooks, etc.)
│   │   ├── core/        # Config, Database, Security
│   │   └── main.py      # Entry point
│   ├── requirements.txt
│   └── .env.example
├── supabase/            # Database Schema
│   ├── schema.sql       # PostgreSQL + RLS + pgvector
│   └── README.md
└── GEMINI.MD            # Contexto do projeto para IA
```

## 🚀 Quick Start

### 1. Configurar Supabase

1. Crie um projeto em [supabase.com](https://supabase.com)
2. Execute o SQL em `supabase/schema.sql` no SQL Editor
3. Copie as credenciais (URL + anon key)

### 2. Configurar Backend

```bash
cd backend

# Criar ambiente virtual
python -m venv venv
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas credenciais Supabase, Gemini, UazAPI

# Executar servidor
uvicorn app.main:app --reload
```

Acesse: http://localhost:8000/docs

## 🏗️ Arquitetura

- **Frontend**: (Próxima fase) React + Vite + TailwindCSS
- **Backend**: Python 3.11 + FastAPI
- **Database**: Supabase (PostgreSQL + Auth + Storage)
- **AI**: Google Gemini 2.0 Flash
- **WhatsApp**: UazAPI (Webhooks)

### Multi-tenancy

- Todas as tabelas possuem `clinic_id`
- RLS (Row Level Security) garante isolamento
- Middleware injeta `clinic_id` automaticamente

## 📚 Documentação

- [Backend README](backend/README.md)
- [Supabase README](supabase/README.md)
- [GEMINI.MD](GEMINI.MD) - Contexto completo do projeto

## 🎨 Design System

- **Cores**: Bem-Querer Blue (#00A3E0), Soft Lilac (#E0D7F5)
- **Fontes**: Nunito (UI), Roboto Mono (Dados)
- **Estética**: "Pediatric Soft-Tech"

## 🔐 Segurança

- Autenticação via Supabase Auth (JWT)
- RLS no banco de dados
- Middleware de tenant isolation
- Validação de webhooks (TODO)

## 📝 Próximos Passos

- [ ] Implementar serviço de IA (Gemini)
- [ ] Criar endpoints de Chat
- [ ] Desenvolver Frontend (React)
- [ ] Integração com Clinicorp
