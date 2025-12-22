# Bem-Querer Hub - Backend

FastAPI backend para o sistema Bem-Querer Hub.

## Estrutura

```
backend/
├── app/
│   ├── api/              # Rotas da API
│   ├── core/             # Configurações e segurança
│   ├── services/         # Lógica de negócio
│   └── main.py           # Entry point
├── requirements.txt      # Dependências Python
└── .env.example          # Template de variáveis de ambiente
```

## Setup

1. **Criar ambiente virtual:**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

2. **Instalar dependências:**
```bash
pip install -r requirements.txt
```

3. **Configurar variáveis de ambiente:**
```bash
cp .env.example .env
# Editar .env com suas credenciais
```

4. **Executar servidor:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints

- `GET /` - Health check
- `GET /health` - Status detalhado
- `POST /webhook/whatsapp` - Webhook UazAPI
- `GET /docs` - Documentação Swagger

## Arquitetura Multi-tenant

Todas as requisições (exceto públicas) passam pelo `TenantMiddleware` que:
1. Valida o token JWT (Supabase Auth)
2. Extrai o `clinic_id` do perfil do usuário
3. Injeta no `request.state` para uso nos endpoints

## Segurança

- RLS (Row Level Security) no Supabase garante isolamento de dados
- Tokens JWT validados em cada requisição
- Middleware bloqueia acesso cross-tenant
