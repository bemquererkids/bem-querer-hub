-- =====================================================
-- Sistema de Convites - Tabela e Funções
-- =====================================================

-- Tabela de Convites
CREATE TABLE public.convites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinica_id UUID NOT NULL REFERENCES public.clinicas(id) ON DELETE CASCADE,
    
    -- Tipo de convite
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('email', 'codigo')),
    
    -- Para convite por email
    email VARCHAR(255),
    token VARCHAR(255) UNIQUE,
    
    -- Para código
    codigo VARCHAR(50) UNIQUE,
    
    -- Configurações
    cargo VARCHAR(50) NOT NULL CHECK (cargo IN ('admin', 'recepcionista', 'dentista')),
    uso_unico BOOLEAN DEFAULT true,
    vezes_usado INTEGER DEFAULT 0,
    max_usos INTEGER DEFAULT 1,
    
    -- Status
    status VARCHAR(20) DEFAULT 'pendente' CHECK (status IN ('pendente', 'usado', 'expirado', 'cancelado')),
    expira_em TIMESTAMP WITH TIME ZONE NOT NULL,
    usado_em TIMESTAMP WITH TIME ZONE,
    usado_por UUID REFERENCES public.perfis(id),
    
    -- Auditoria
    criado_por UUID NOT NULL REFERENCES public.perfis(id),
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT email_required_for_email_type CHECK (
        (tipo = 'email' AND email IS NOT NULL AND token IS NOT NULL) OR
        (tipo = 'codigo' AND codigo IS NOT NULL)
    )
);

-- Índices para performance
CREATE INDEX idx_convites_clinica ON public.convites(clinica_id);
CREATE INDEX idx_convites_token ON public.convites(token) WHERE token IS NOT NULL;
CREATE INDEX idx_convites_codigo ON public.convites(codigo) WHERE codigo IS NOT NULL;
CREATE INDEX idx_convites_status ON public.convites(status);
CREATE INDEX idx_convites_email ON public.convites(email) WHERE email IS NOT NULL;

-- =====================================================
-- Função: Gerar Token Único
-- =====================================================
CREATE OR REPLACE FUNCTION gerar_token_convite()
RETURNS VARCHAR(255) AS $$
DECLARE
    novo_token VARCHAR(255);
    existe BOOLEAN;
BEGIN
    LOOP
        -- Gera token aleatório de 64 caracteres
        novo_token := encode(gen_random_bytes(32), 'hex');
        
        -- Verifica se já existe
        SELECT EXISTS(SELECT 1 FROM public.convites WHERE token = novo_token) INTO existe;
        
        -- Se não existe, retorna
        IF NOT existe THEN
            RETURN novo_token;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- Função: Gerar Código Único
-- =====================================================
CREATE OR REPLACE FUNCTION gerar_codigo_convite()
RETURNS VARCHAR(50) AS $$
DECLARE
    novo_codigo VARCHAR(50);
    existe BOOLEAN;
    ano VARCHAR(4);
    random_part VARCHAR(6);
BEGIN
    ano := EXTRACT(YEAR FROM NOW())::VARCHAR;
    
    LOOP
        -- Gera parte aleatória (6 caracteres alfanuméricos)
        random_part := UPPER(SUBSTRING(MD5(RANDOM()::TEXT) FROM 1 FOR 6));
        
        -- Formato: BQ-2024-ABC123
        novo_codigo := 'BQ-' || ano || '-' || random_part;
        
        -- Verifica se já existe
        SELECT EXISTS(SELECT 1 FROM public.convites WHERE codigo = novo_codigo) INTO existe;
        
        -- Se não existe, retorna
        IF NOT existe THEN
            RETURN novo_codigo;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- Função: Validar Convite
-- =====================================================
CREATE OR REPLACE FUNCTION validar_convite(
    p_token VARCHAR DEFAULT NULL,
    p_codigo VARCHAR DEFAULT NULL,
    p_email VARCHAR DEFAULT NULL
)
RETURNS TABLE (
    valido BOOLEAN,
    convite_id UUID,
    clinica_id UUID,
    cargo VARCHAR,
    mensagem TEXT
) AS $$
DECLARE
    v_convite RECORD;
BEGIN
    -- Busca convite por token ou código
    IF p_token IS NOT NULL THEN
        SELECT * INTO v_convite
        FROM public.convites
        WHERE token = p_token;
    ELSIF p_codigo IS NOT NULL THEN
        SELECT * INTO v_convite
        FROM public.convites
        WHERE codigo = p_codigo;
    ELSE
        RETURN QUERY SELECT false, NULL::UUID, NULL::UUID, NULL::VARCHAR, 'Token ou código não fornecido'::TEXT;
        RETURN;
    END IF;
    
    -- Verifica se convite existe
    IF v_convite.id IS NULL THEN
        RETURN QUERY SELECT false, NULL::UUID, NULL::UUID, NULL::VARCHAR, 'Convite não encontrado'::TEXT;
        RETURN;
    END IF;
    
    -- Verifica se foi cancelado
    IF v_convite.status = 'cancelado' THEN
        RETURN QUERY SELECT false, v_convite.id, NULL::UUID, NULL::VARCHAR, 'Convite cancelado'::TEXT;
        RETURN;
    END IF;
    
    -- Verifica se expirou
    IF v_convite.expira_em < NOW() THEN
        -- Marca como expirado
        UPDATE public.convites SET status = 'expirado' WHERE id = v_convite.id;
        RETURN QUERY SELECT false, v_convite.id, NULL::UUID, NULL::VARCHAR, 'Convite expirado'::TEXT;
        RETURN;
    END IF;
    
    -- Verifica se já foi usado (para uso único)
    IF v_convite.uso_unico AND v_convite.vezes_usado >= v_convite.max_usos THEN
        RETURN QUERY SELECT false, v_convite.id, NULL::UUID, NULL::VARCHAR, 'Convite já foi utilizado'::TEXT;
        RETURN;
    END IF;
    
    -- Verifica email (se for convite por email)
    IF v_convite.tipo = 'email' AND p_email IS NOT NULL AND v_convite.email != p_email THEN
        RETURN QUERY SELECT false, v_convite.id, NULL::UUID, NULL::VARCHAR, 'Email não corresponde ao convite'::TEXT;
        RETURN;
    END IF;
    
    -- Convite válido!
    RETURN QUERY SELECT 
        true, 
        v_convite.id, 
        v_convite.clinica_id, 
        v_convite.cargo, 
        'Convite válido'::TEXT;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- Função: Marcar Convite como Usado
-- =====================================================
CREATE OR REPLACE FUNCTION marcar_convite_usado(
    p_convite_id UUID,
    p_usuario_id UUID
)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE public.convites
    SET 
        vezes_usado = vezes_usado + 1,
        usado_em = NOW(),
        usado_por = p_usuario_id,
        status = CASE 
            WHEN uso_unico OR (vezes_usado + 1) >= max_usos THEN 'usado'
            ELSE 'pendente'
        END
    WHERE id = p_convite_id;
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- RLS Policies para Convites
-- =====================================================
ALTER TABLE public.convites ENABLE ROW LEVEL SECURITY;

-- Admins podem ver convites da sua clínica
CREATE POLICY "Admins podem ver convites da clínica" ON public.convites
    FOR SELECT USING (
        clinica_id IN (
            SELECT clinica_id FROM public.perfis 
            WHERE id = auth.uid() AND cargo = 'admin'
        )
    );

-- Admins podem criar convites
CREATE POLICY "Admins podem criar convites" ON public.convites
    FOR INSERT WITH CHECK (
        clinica_id IN (
            SELECT clinica_id FROM public.perfis 
            WHERE id = auth.uid() AND cargo = 'admin'
        )
    );

-- Admins podem atualizar convites da sua clínica
CREATE POLICY "Admins podem atualizar convites" ON public.convites
    FOR UPDATE USING (
        clinica_id IN (
            SELECT clinica_id FROM public.perfis 
            WHERE id = auth.uid() AND cargo = 'admin'
        )
    );

COMMENT ON TABLE public.convites IS 'Sistema de convites para controlar cadastros de novos usuários';
