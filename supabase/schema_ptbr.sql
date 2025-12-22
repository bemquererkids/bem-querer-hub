-- =====================================================
-- Bem-Querer Hub - Esquema de Banco de Dados (PT-BR)
-- Arquitetura Multi-inquilino (Multi-tenant) com Segurança RLS
-- =====================================================

-- Habilitar Extensões
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgvector"; -- Para Inteligência Artificial

-- =====================================================
-- 1. CLINICAS (A Tabela Pai / Tenant)
-- =====================================================
CREATE TABLE public.clinicas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome_fantasia VARCHAR(255) NOT NULL,
    cnpj VARCHAR(18) UNIQUE,
    email_contato VARCHAR(255) NOT NULL,
    
    -- Configurações
    plano VARCHAR(50) DEFAULT 'trial', -- trial, pro, enterprise
    status VARCHAR(20) DEFAULT 'ativo',
    
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- 2. PERFIS (Usuários do Sistema)
-- =====================================================
-- Vincula ao sistema de Auth do Supabase
CREATE TABLE public.perfis (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    clinica_id UUID NOT NULL REFERENCES public.clinicas(id) ON DELETE CASCADE,
    
    nome_completo VARCHAR(255) NOT NULL,
    funcao VARCHAR(50) DEFAULT 'recepcionista', -- admin, dentista, recepcionista
    avatar_url TEXT,
    
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- 3. PACIENTES
-- =====================================================
CREATE TABLE public.pacientes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinica_id UUID NOT NULL REFERENCES public.clinicas(id) ON DELETE CASCADE,
    
    nome_completo VARCHAR(255) NOT NULL,
    cpf VARCHAR(14),
    telefone VARCHAR(20), -- Chave principal para WhatsApp
    email VARCHAR(255),
    
    -- Dados de Marketing (Rastreamento)
    origem_campanha VARCHAR(100), -- google, instagram, indicacao
    utm_source VARCHAR(100),
    
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_pacientes_telefone ON public.pacientes(telefone);

-- =====================================================
-- 4. AGENDAMENTOS (Espelho do Clinicorp)
-- =====================================================
CREATE TABLE public.agendamentos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinica_id UUID NOT NULL REFERENCES public.clinicas(id) ON DELETE CASCADE,
    paciente_id UUID NOT NULL REFERENCES public.pacientes(id) ON DELETE CASCADE,
    
    data_horario TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(50) DEFAULT 'agendado', -- agendado, compareceu, faltou, cancelado
    
    id_externo_clinicorp VARCHAR(100), -- Para sincronia
    
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- 5. ATENDIMENTOS (Chats / CRM)
-- =====================================================
CREATE TABLE public.atendimentos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinica_id UUID NOT NULL REFERENCES public.clinicas(id) ON DELETE CASCADE,
    paciente_id UUID REFERENCES public.pacientes(id),
    
    whatsapp_origem VARCHAR(20),
    
    -- Funil de Vendas
    etapa_funil VARCHAR(50) DEFAULT 'lead', -- lead, triagem, agendado, venda
    responsavel_id UUID REFERENCES public.perfis(id),
    
    ultima_mensagem_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- 6. MENSAGENS (Histórico do Chat)
-- =====================================================
CREATE TABLE public.mensagens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    atendimento_id UUID NOT NULL REFERENCES public.atendimentos(id) ON DELETE CASCADE,
    
    conteudo TEXT NOT NULL,
    tipo VARCHAR(20) DEFAULT 'texto', -- texto, audio, imagem
    remetente VARCHAR(20), -- cliente, ia, atendente
    
    -- IA (Embeddings)
    embedding vector(768), 
    
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- SEGURANÇA MULTI-TENANT (RLS)
-- =====================================================
-- A Regra de Ouro: Um usuário só vê dados onde clinica_id bate com o perfil dele.

ALTER TABLE public.pacientes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agendamentos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.atendimentos ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Ver apenas dados da minha clínica" ON public.pacientes
    FOR ALL USING (
        clinica_id IN (
            SELECT clinica_id FROM public.perfis WHERE id = auth.uid()
        )
    );

-- (Repetir a política acima para todas as tabelas)
