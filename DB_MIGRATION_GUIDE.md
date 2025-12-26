# 🗄️ Guia de Migração do Banco de Dados

Para ativar a persistência definitiva das integrações (que funciona em qualquer dispositivo e resiste a refreshs), você precisa criar a tabela de integrações no seu banco de dados Supabase.

## 📋 Passo a Passo

### 1. Acesse o Supabase
1. Vá para [supabase.com/dashboard](https://supabase.com/dashboard)
2. Selecione seu projeto **bem-querer-hub**

### 2. Abra o Editor SQL
1. No menu lateral esquerdo, clique em **SQL Editor** (ícone `>_`)
2. Clique em **New query** (botão verde)

### 3. Cole e Execute o Código
Copie todo o código abaixo e cole no editor:

```sql
-- Tabela para armazenar configurações de integrações por clínica
create table if not exists public.clinic_integrations (
    id uuid primary key default uuid_generate_v4(),
    clinica_id uuid not null references public.clinicas(id) on delete cascade,
    type text not null, -- 'clinicorp', 'openai', 'whatsapp'
    config jsonb not null default '{}'::jsonb,
    is_active boolean default true,
    updated_at timestamp with time zone default now(),
    
    -- Garante apenas uma configuração por tipo por clínica
    unique(clinica_id, type)
);

-- Habilitar RLS (Segurança)
alter table public.clinic_integrations enable row level security;

-- Política de acesso
-- Nota: Se der erro de "policy already exists", pode ignorar
create policy "Isolamento Integrations" on public.clinic_integrations
using (clinica_id in (select clinica_id from public.perfis where id = auth.uid()));
```

3. Clique em **RUN** (canto inferior direito ou Ctrl+Enter)

### 4. Pronto!
Agora o sistema irá salvar suas credenciais no banco de dados automaticamente. Você pode conectar pelo PC e acessar pelo celular que continuará conectado.

---
**Nota:** Se você não rodar este script, o sistema continuará tentando usar arquivos locais ou variáveis de ambiente, que podem não funcionar corretamente entre sessões diferentes.
