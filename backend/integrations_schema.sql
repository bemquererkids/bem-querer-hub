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

-- Política de acesso (mesma lógica das outras tabelas)
create policy "Isolamento Integrations" on public.clinic_integrations
using (clinica_id in (select clinica_id from public.perfis where id = auth.uid()));

-- Permitir acesso anônimo/service_role para o backend (se necessário ajustar conforme auth)
-- Para este MVP, o backend usa service_role, então bypassa RLS, mas é bom ter.
