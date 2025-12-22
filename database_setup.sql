create extension if not exists "uuid-ossp";

create table if not exists public.clinicas (
    id uuid primary key default uuid_generate_v4(),
    nome_fantasia text not null,
    cnpj text,
    slug text unique,
    status text default 'ativo',
    criado_em timestamp with time zone default now()
);

create table if not exists public.perfis (
    id uuid primary key references auth.users(id) on delete cascade,
    clinica_id uuid not null references public.clinicas(id),
    nome_completo text,
    cargo text default 'admin',
    avatar_url text
);

create table if not exists public.pacientes (
    id uuid primary key default uuid_generate_v4(),
    clinica_id uuid not null references public.clinicas(id),
    nome text not null,
    telefone text,
    email text,
    origem text,
    criado_em timestamp with time zone default now()
);

create table if not exists public.agendamentos (
    id uuid primary key default uuid_generate_v4(),
    clinica_id uuid not null references public.clinicas(id),
    paciente_id uuid references public.pacientes(id),
    data_horario timestamp with time zone,
    status text default 'agendado',
    obs text
);

alter table public.clinicas enable row level security;
alter table public.pacientes enable row level security;
alter table public.agendamentos enable row level security;

create policy "Isolamento Pacientes" on public.pacientes
using (clinica_id in (select clinica_id from public.perfis where id = auth.uid()));

create policy "Isolamento Agenda" on public.agendamentos
using (clinica_id in (select clinica_id from public.perfis where id = auth.uid()));

insert into public.clinicas (id, nome_fantasia, slug)
values ('00000000-0000-0000-0000-000000000001', 'Bem-Querer Odontologia', 'bem-querer')
on conflict (id) do nothing;