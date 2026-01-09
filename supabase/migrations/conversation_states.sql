-- Tabela para persistir estados de conversação multiagentes
-- Permite manter contexto entre mensagens e deploys

CREATE TABLE IF NOT EXISTS conversation_states (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone VARCHAR(20) NOT NULL,
    clinic_id UUID NOT NULL,
    current_agent VARCHAR(50) NOT NULL DEFAULT 'router',
    patient_type VARCHAR(20) DEFAULT 'indefinido',
    intent VARCHAR(50) DEFAULT 'indefinido',
    human_takeover BOOLEAN DEFAULT FALSE,
    collected_data JSONB DEFAULT '{}'::jsonb,
    agent_history JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Índices para performance
    UNIQUE(phone, clinic_id)
);

-- Índice para busca rápida por telefone
CREATE INDEX IF NOT EXISTS idx_conversation_states_phone ON conversation_states(phone);

-- Índice para busca por clínica
CREATE INDEX IF NOT EXISTS idx_conversation_states_clinic ON conversation_states(clinic_id);

-- Função para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_conversation_states_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para atualizar updated_at
DROP TRIGGER IF EXISTS trigger_update_conversation_states_updated_at ON conversation_states;
CREATE TRIGGER trigger_update_conversation_states_updated_at
    BEFORE UPDATE ON conversation_states
    FOR EACH ROW
    EXECUTE FUNCTION update_conversation_states_updated_at();

-- Comentários
COMMENT ON TABLE conversation_states IS 'Armazena estados de conversações multiagentes para persistência entre mensagens';
COMMENT ON COLUMN conversation_states.collected_data IS 'Dados coletados durante a conversa (nome, idade, motivo, etc)';
COMMENT ON COLUMN conversation_states.agent_history IS 'Histórico de transições entre agentes';
