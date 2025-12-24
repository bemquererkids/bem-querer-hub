-- =====================================================
-- Sistema de Conversas (Threads) para IA Carol
-- =====================================================

-- Extensão para UUID (se ainda não existir)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabela de Threads (Conversas)
CREATE TABLE IF NOT EXISTS public.conversation_threads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinica_id UUID NOT NULL REFERENCES public.clinicas(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    titulo VARCHAR(255),
    canal VARCHAR(50) DEFAULT 'chat', -- 'chat', 'whatsapp', 'email'
    status VARCHAR(20) DEFAULT 'ativa', -- 'ativa', 'arquivada', 'resolvida'
    metadata JSONB DEFAULT '{}',
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de Mensagens
CREATE TABLE IF NOT EXISTS public.conversation_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    thread_id UUID NOT NULL REFERENCES public.conversation_threads(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system', 'tool')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}', -- tool_calls, function_results, etc
    tokens_used INTEGER,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_threads_clinica ON public.conversation_threads(clinica_id);
CREATE INDEX IF NOT EXISTS idx_threads_user ON public.conversation_threads(user_id);
CREATE INDEX IF NOT EXISTS idx_threads_status ON public.conversation_threads(status);
CREATE INDEX IF NOT EXISTS idx_threads_updated ON public.conversation_threads(atualizado_em DESC);
CREATE INDEX IF NOT EXISTS idx_messages_thread ON public.conversation_messages(thread_id);
CREATE INDEX IF NOT EXISTS idx_messages_created ON public.conversation_messages(criado_em);

-- =====================================================
-- Tabela de Documentos de Conhecimento
-- =====================================================
CREATE TABLE IF NOT EXISTS public.documentos_conhecimento (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinica_id UUID NOT NULL REFERENCES public.clinicas(id) ON DELETE CASCADE,
    titulo VARCHAR(255) NOT NULL,
    tipo VARCHAR(50) CHECK (tipo IN ('preco', 'politica', 'procedimento', 'faq', 'outro')),
    conteudo TEXT NOT NULL,
    arquivo_url TEXT,
    metadata JSONB DEFAULT '{}',
    ativo BOOLEAN DEFAULT true,
    criado_por UUID REFERENCES auth.users(id),
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_docs_clinica ON public.documentos_conhecimento(clinica_id);
CREATE INDEX IF NOT EXISTS idx_docs_tipo ON public.documentos_conhecimento(tipo);
CREATE INDEX IF NOT EXISTS idx_docs_ativo ON public.documentos_conhecimento(ativo) WHERE ativo = true;

-- =====================================================
-- Tabela de Embeddings (Vetores)
-- =====================================================
-- Habilitar extensão pgvector
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS public.embeddings_conhecimento (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    documento_id UUID NOT NULL REFERENCES public.documentos_conhecimento(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding vector(1536), -- OpenAI text-embedding-3-small
    metadata JSONB DEFAULT '{}',
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índice para busca vetorial (ivfflat para cosine similarity)
CREATE INDEX IF NOT EXISTS idx_embeddings_vector 
ON public.embeddings_conhecimento 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_embeddings_documento ON public.embeddings_conhecimento(documento_id);

-- =====================================================
-- Funções Auxiliares
-- =====================================================

-- Função: Criar nova thread
CREATE OR REPLACE FUNCTION criar_thread(
    p_clinica_id UUID,
    p_user_id UUID DEFAULT NULL,
    p_titulo VARCHAR DEFAULT 'Nova Conversa',
    p_canal VARCHAR DEFAULT 'chat'
)
RETURNS UUID AS $$
DECLARE
    v_thread_id UUID;
BEGIN
    INSERT INTO public.conversation_threads (clinica_id, user_id, titulo, canal)
    VALUES (p_clinica_id, p_user_id, p_titulo, p_canal)
    RETURNING id INTO v_thread_id;
    
    RETURN v_thread_id;
END;
$$ LANGUAGE plpgsql;

-- Função: Adicionar mensagem à thread
CREATE OR REPLACE FUNCTION adicionar_mensagem(
    p_thread_id UUID,
    p_role VARCHAR,
    p_content TEXT,
    p_metadata JSONB DEFAULT '{}',
    p_tokens INTEGER DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_message_id UUID;
BEGIN
    INSERT INTO public.conversation_messages (thread_id, role, content, metadata, tokens_used)
    VALUES (p_thread_id, p_role, p_content, p_metadata, p_tokens)
    RETURNING id INTO v_message_id;
    
    -- Atualizar timestamp da thread
    UPDATE public.conversation_threads
    SET atualizado_em = NOW()
    WHERE id = p_thread_id;
    
    RETURN v_message_id;
END;
$$ LANGUAGE plpgsql;

-- Função: Obter histórico da thread
CREATE OR REPLACE FUNCTION obter_historico_thread(p_thread_id UUID, p_limit INTEGER DEFAULT 50)
RETURNS TABLE (
    id UUID,
    role VARCHAR,
    content TEXT,
    metadata JSONB,
    criado_em TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cm.id,
        cm.role,
        cm.content,
        cm.metadata,
        cm.criado_em
    FROM public.conversation_messages cm
    WHERE cm.thread_id = p_thread_id
    ORDER BY cm.criado_em ASC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Função: Busca semântica em documentos
CREATE OR REPLACE FUNCTION buscar_documentos_similares(
    p_embedding vector(1536),
    p_clinica_id UUID,
    p_limit INTEGER DEFAULT 5
)
RETURNS TABLE (
    documento_id UUID,
    titulo VARCHAR,
    chunk_text TEXT,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        d.id,
        d.titulo,
        e.chunk_text,
        1 - (e.embedding <=> p_embedding) as similarity
    FROM public.embeddings_conhecimento e
    JOIN public.documentos_conhecimento d ON e.documento_id = d.id
    WHERE d.clinica_id = p_clinica_id AND d.ativo = true
    ORDER BY e.embedding <=> p_embedding
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- RLS Policies
-- =====================================================

-- Threads
ALTER TABLE public.conversation_threads ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Usuarios podem ver threads da clinica" ON public.conversation_threads
    FOR SELECT USING (
        clinica_id IN (
            SELECT clinica_id FROM public.perfis WHERE id = auth.uid()
        )
    );

CREATE POLICY "Usuarios podem criar threads" ON public.conversation_threads
    FOR INSERT WITH CHECK (
        clinica_id IN (
            SELECT clinica_id FROM public.perfis WHERE id = auth.uid()
        )
    );

-- Messages
ALTER TABLE public.conversation_messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Usuarios podem ver mensagens das threads da clinica" ON public.conversation_messages
    FOR SELECT USING (
        thread_id IN (
            SELECT id FROM public.conversation_threads 
            WHERE clinica_id IN (
                SELECT clinica_id FROM public.perfis WHERE id = auth.uid()
            )
        )
    );

CREATE POLICY "Usuarios podem criar mensagens" ON public.conversation_messages
    FOR INSERT WITH CHECK (
        thread_id IN (
            SELECT id FROM public.conversation_threads 
            WHERE clinica_id IN (
                SELECT clinica_id FROM public.perfis WHERE id = auth.uid()
            )
        )
    );

-- Documentos
ALTER TABLE public.documentos_conhecimento ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Usuarios podem ver documentos da clinica" ON public.documentos_conhecimento
    FOR SELECT USING (
        clinica_id IN (
            SELECT clinica_id FROM public.perfis WHERE id = auth.uid()
        )
    );

CREATE POLICY "Admins podem gerenciar documentos" ON public.documentos_conhecimento
    FOR ALL USING (
        clinica_id IN (
            SELECT clinica_id FROM public.perfis 
            WHERE id = auth.uid() AND cargo = 'admin'
        )
    );

-- Embeddings
ALTER TABLE public.embeddings_conhecimento ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Usuarios podem ver embeddings dos documentos da clinica" ON public.embeddings_conhecimento
    FOR SELECT USING (
        documento_id IN (
            SELECT id FROM public.documentos_conhecimento
            WHERE clinica_id IN (
                SELECT clinica_id FROM public.perfis WHERE id = auth.uid()
            )
        )
    );

-- Comentários
COMMENT ON TABLE public.conversation_threads IS 'Threads de conversação com a IA Carol';
COMMENT ON TABLE public.conversation_messages IS 'Mensagens individuais dentro de cada thread';
COMMENT ON TABLE public.documentos_conhecimento IS 'Base de conhecimento da clínica para RAG';
COMMENT ON TABLE public.embeddings_conhecimento IS 'Vetores (embeddings) dos documentos para busca semântica';
