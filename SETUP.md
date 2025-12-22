# 🚀 Guia de Configuração - Bem-Querer Hub

Este guia vai te orientar na configuração completa do ambiente.

## 📋 Pré-requisitos

- [ ] Conta no [Supabase](https://supabase.com) (gratuito)
- [ ] Conta no [Google AI Studio](https://makersuite.google.com) (gratuito)
- [ ] Conta no [UazAPI](https://uazapi.com) (verificar planos)

---

## 1️⃣ Configurar Supabase

### Passo 1: Criar Projeto

1. Acesse [app.supabase.com](https://app.supabase.com)
2. Clique em **"New Project"**
3. Preencha:
   - **Name**: `bem-querer-hub`
   - **Database Password**: Escolha uma senha forte (guarde-a!)
   - **Region**: `South America (São Paulo)` (mais próximo)
   - **Pricing Plan**: `Free` (para começar)
4. Clique em **"Create new project"**
5. Aguarde ~2 minutos para o projeto ser criado

### Passo 2: Executar o Schema SQL

1. No painel do Supabase, vá em **SQL Editor** (ícone de banco de dados na lateral)
2. Clique em **"New Query"**
3. Abra o arquivo `c:\projetos\sistemabemquerer\supabase\schema.sql`
4. Copie **TODO** o conteúdo do arquivo
5. Cole no SQL Editor do Supabase
6. Clique em **"Run"** (ou pressione `Ctrl+Enter`)
7. Aguarde a execução (deve aparecer "Success. No rows returned")

### Passo 3: Verificar Tabelas Criadas

1. Vá em **Table Editor** (ícone de tabela na lateral)
2. Você deve ver 7 tabelas:
   - ✅ `clinics`
   - ✅ `profiles`
   - ✅ `patients`
   - ✅ `appointments`
   - ✅ `chats`
   - ✅ `messages`
   - ✅ `webhook_logs`

### Passo 4: Verificar Extensão pgvector

1. Vá em **Database** > **Extensions**
2. Procure por `vector`
3. Deve estar **habilitado** (verde)

### Passo 5: Copiar Credenciais

1. Vá em **Settings** > **API**
2. Copie os seguintes valores:

```
Project URL: https://xxxxxxxxxxxxx.supabase.co
anon public key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
service_role key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

> ⚠️ **IMPORTANTE**: A `service_role key` tem acesso total ao banco. Nunca exponha no frontend!

---

## 2️⃣ Obter API Key do Google Gemini

1. Acesse [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Faça login com sua conta Google
3. Clique em **"Create API Key"**
4. Copie a chave gerada (formato: `AIzaSy...`)

---

## 3️⃣ Obter Token da UazAPI

1. Acesse [UazAPI](https://uazapi.com)
2. Crie uma conta ou faça login
3. Vá em **Dashboard** > **API**
4. Copie o **Token de Acesso**
5. Anote também a **URL Base** (geralmente `https://api.uazapi.com`)

---

## 4️⃣ Configurar Arquivo .env

### Passo 1: Copiar Template

No terminal (PowerShell), execute:

```powershell
cd c:\projetos\sistemabemquerer\backend
Copy-Item .env.example .env
```

### Passo 2: Editar .env

Abra o arquivo `c:\projetos\sistemabemquerer\backend\.env` no seu editor favorito e preencha:

```env
# Application
APP_NAME=Bem-Querer Hub
APP_VERSION=1.0.0
DEBUG=True

# Supabase Configuration
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co  # ← Cole a Project URL
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # ← Cole a anon key
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # ← Cole a service_role key

# Google Gemini AI
GEMINI_API_KEY=AIzaSy...  # ← Cole sua API key do Gemini
GEMINI_MODEL=gemini-2.0-flash-exp

# UazAPI (WhatsApp Gateway)
UAZAPI_BASE_URL=https://api.uazapi.com  # ← Confirme a URL
UAZAPI_TOKEN=seu-token-aqui  # ← Cole seu token da UazAPI

# Clinicorp Integration (Opcional - deixe vazio por enquanto)
CLINICORP_API_URL=
CLINICORP_API_KEY=

# Security
SECRET_KEY=GERE_UMA_CHAVE_FORTE_AQUI  # ← Veja instruções abaixo
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Passo 3: Gerar SECRET_KEY

Execute no PowerShell:

```powershell
# Opção 1: Usando Python
python -c "import secrets; print(secrets.token_hex(32))"

# Opção 2: Gerar online
# Acesse: https://generate-secret.vercel.app/32
```

Cole o resultado no campo `SECRET_KEY`.

---

## 5️⃣ Testar o Backend

### Passo 1: Iniciar Servidor

```powershell
cd c:\projetos\sistemabemquerer\backend
.\start.bat
```

Você deve ver:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Passo 2: Testar Endpoints

Abra o navegador e acesse:

1. **Swagger Docs**: http://localhost:8000/docs
2. **Health Check**: http://localhost:8000/health

Você deve ver a documentação interativa da API.

### Passo 3: Testar Conexão com Supabase

No Swagger Docs:

1. Vá até o endpoint `GET /health`
2. Clique em **"Try it out"**
3. Clique em **"Execute"**
4. Verifique a resposta (deve retornar status 200)

---

## 6️⃣ Criar Usuário de Teste (Opcional)

Para testar a autenticação:

1. No Supabase, vá em **Authentication** > **Users**
2. Clique em **"Add user"**
3. Preencha:
   - **Email**: `admin@bemquerer.com`
   - **Password**: Escolha uma senha
   - **Auto Confirm User**: ✅ (marque)
4. Clique em **"Create user"**

### Vincular Usuário à Clínica Demo

Execute no **SQL Editor** do Supabase:

```sql
-- Obter o ID do usuário criado
SELECT id, email FROM auth.users WHERE email = 'admin@bemquerer.com';

-- Copie o ID e substitua abaixo
INSERT INTO public.profiles (id, clinic_id, full_name, role)
VALUES (
    'COLE_O_ID_DO_USUARIO_AQUI',
    '00000000-0000-0000-0000-000000000001',  -- Clínica demo
    'Administrador',
    'admin'
);
```

---

## ✅ Checklist Final

- [ ] Projeto Supabase criado
- [ ] Schema SQL executado (7 tabelas criadas)
- [ ] Extensão pgvector habilitada
- [ ] Credenciais Supabase copiadas
- [ ] API Key do Gemini obtida
- [ ] Token da UazAPI obtido
- [ ] Arquivo `.env` configurado
- [ ] SECRET_KEY gerada
- [ ] Backend iniciado com sucesso
- [ ] Swagger Docs acessível
- [ ] Health check retornando 200

---

## 🆘 Problemas Comuns

### Erro: "ModuleNotFoundError: No module named 'fastapi'"

**Solução**: Ative o ambiente virtual primeiro:

```powershell
cd c:\projetos\sistemabemquerer\backend
.\venv\Scripts\Activate.ps1
```

### Erro: "pydantic_core._pydantic_core.ValidationError"

**Solução**: Verifique se todas as variáveis obrigatórias no `.env` estão preenchidas.

### Erro ao conectar no Supabase

**Solução**: Verifique se a `SUPABASE_URL` e `SUPABASE_KEY` estão corretas.

---

## 📞 Próximos Passos

Após concluir este guia, você estará pronto para:

1. Implementar a integração com o Gemini AI
2. Processar webhooks da UazAPI
3. Desenvolver o frontend React
4. Integrar com o Clinicorp

**Dúvidas?** Consulte a documentação em `README.md` ou me pergunte!
