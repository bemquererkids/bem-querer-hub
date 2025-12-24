-- =====================================================
-- Sistema de Módulos para Clínicas
-- =====================================================

-- Tabela de Módulos da Clínica
CREATE TABLE IF NOT EXISTS public.clinicas_modulos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinica_id UUID NOT NULL REFERENCES public.clinicas(id) ON DELETE CASCADE,
    modulo VARCHAR(50) NOT NULL CHECK (modulo IN ('clinicorp', 'chatgpt', 'whatsapp', 'agenda', 'financeiro')),
    ativo BOOLEAN DEFAULT false,
    configurado BOOLEAN DEFAULT false,
    configuracao JSONB DEFAULT '{}',
    ativado_em TIMESTAMP WITH TIME ZONE,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(clinica_id, modulo)
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_clinicas_modulos_clinica ON public.clinicas_modulos(clinica_id);
CREATE INDEX IF NOT EXISTS idx_clinicas_modulos_ativo ON public.clinicas_modulos(ativo) WHERE ativo = true;

-- =====================================================
-- Função: Inicializar Módulos Padrão
-- =====================================================
CREATE OR REPLACE FUNCTION inicializar_modulos_clinica(p_clinica_id UUID)
RETURNS VOID AS $$
BEGIN
    -- Inserir todos os módulos como inativos por padrão
    INSERT INTO public.clinicas_modulos (clinica_id, modulo, ativo, configurado)
    VALUES 
        (p_clinica_id, 'clinicorp', false, false),
        (p_clinica_id, 'chatgpt', false, false),
        (p_clinica_id, 'whatsapp', false, false),
        (p_clinica_id, 'agenda', true, true),  -- Agenda ativa por padrão
        (p_clinica_id, 'financeiro', true, true)  -- Financeiro ativo por padrão
    ON CONFLICT (clinica_id, modulo) DO NOTHING;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- Função: Ativar/Desativar Módulo
-- =====================================================
CREATE OR REPLACE FUNCTION toggle_modulo(
    p_clinica_id UUID,
    p_modulo VARCHAR,
    p_ativo BOOLEAN
)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE public.clinicas_modulos
    SET 
        ativo = p_ativo,
        ativado_em = CASE WHEN p_ativo THEN NOW() ELSE NULL END,
        atualizado_em = NOW()
    WHERE clinica_id = p_clinica_id AND modulo = p_modulo;
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- Função: Atualizar Configuração do Módulo
-- =====================================================
CREATE OR REPLACE FUNCTION atualizar_config_modulo(
    p_clinica_id UUID,
    p_modulo VARCHAR,
    p_configuracao JSONB
)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE public.clinicas_modulos
    SET 
        configuracao = p_configuracao,
        configurado = true,
        atualizado_em = NOW()
    WHERE clinica_id = p_clinica_id AND modulo = p_modulo;
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- Função: Verificar se Módulo está Ativo
-- =====================================================
CREATE OR REPLACE FUNCTION modulo_ativo(
    p_clinica_id UUID,
    p_modulo VARCHAR
)
RETURNS BOOLEAN AS $$
DECLARE
    v_ativo BOOLEAN;
BEGIN
    SELECT ativo INTO v_ativo
    FROM public.clinicas_modulos
    WHERE clinica_id = p_clinica_id AND modulo = p_modulo;
    
    RETURN COALESCE(v_ativo, false);
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- Função: Obter Módulos Ativos
-- =====================================================
CREATE OR REPLACE FUNCTION obter_modulos_ativos(p_clinica_id UUID)
RETURNS TABLE (
    modulo VARCHAR,
    configurado BOOLEAN,
    configuracao JSONB,
    ativado_em TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cm.modulo,
        cm.configurado,
        cm.configuracao,
        cm.ativado_em
    FROM public.clinicas_modulos cm
    WHERE cm.clinica_id = p_clinica_id AND cm.ativo = true;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- RLS Policies para Módulos
-- =====================================================
ALTER TABLE public.clinicas_modulos ENABLE ROW LEVEL SECURITY;

-- Usuários podem ver módulos da sua clínica
CREATE POLICY "Usuarios podem ver modulos da clinica" ON public.clinicas_modulos
    FOR SELECT USING (
        clinica_id IN (
            SELECT clinica_id FROM public.perfis 
            WHERE id = auth.uid()
        )
    );

-- Admins podem atualizar módulos
CREATE POLICY "Admins podem atualizar modulos" ON public.clinicas_modulos
    FOR UPDATE USING (
        clinica_id IN (
            SELECT clinica_id FROM public.perfis 
            WHERE id = auth.uid() AND cargo = 'admin'
        )
    );

-- Admins podem inserir módulos
CREATE POLICY "Admins podem inserir modulos" ON public.clinicas_modulos
    FOR INSERT WITH CHECK (
        clinica_id IN (
            SELECT clinica_id FROM public.perfis 
            WHERE id = auth.uid() AND cargo = 'admin'
        )
    );

COMMENT ON TABLE public.clinicas_modulos IS 'Módulos/funcionalidades habilitadas para cada clínica';
