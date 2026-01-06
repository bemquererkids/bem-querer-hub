-- Tabela para configuração dinâmica da IA por clínica
-- Permite parametrização completa sem código hardcoded

CREATE TABLE IF NOT EXISTS ai_configurations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id UUID NOT NULL REFERENCES clinicas(id) ON DELETE CASCADE,
    
    -- Configuração completa em JSON
    config JSONB NOT NULL DEFAULT '{}'::jsonb,
    
    -- Metadados
    is_active BOOLEAN DEFAULT true,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES perfis(id),
    
    -- Índices para performance
    CONSTRAINT unique_active_config_per_clinic UNIQUE (clinic_id, is_active)
);

-- Índice para busca rápida por clínica
CREATE INDEX IF NOT EXISTS idx_ai_config_clinic ON ai_configurations(clinic_id);

-- Índice para busca por configurações ativas
CREATE INDEX IF NOT EXISTS idx_ai_config_active ON ai_configurations(clinic_id, is_active) WHERE is_active = true;

-- Índice GIN para busca dentro do JSON
CREATE INDEX IF NOT EXISTS idx_ai_config_jsonb ON ai_configurations USING GIN (config);

-- Trigger para atualizar updated_at
CREATE OR REPLACE FUNCTION update_ai_config_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER ai_config_update_timestamp
    BEFORE UPDATE ON ai_configurations
    FOR EACH ROW
    EXECUTE FUNCTION update_ai_config_timestamp();

-- Comentários para documentação
COMMENT ON TABLE ai_configurations IS 'Configurações dinâmicas da IA por clínica - permite parametrização via wizard';
COMMENT ON COLUMN ai_configurations.config IS 'JSON com persona, team, admin_info, protocols, etc.';
COMMENT ON COLUMN ai_configurations.version IS 'Versão da configuração para histórico';

-- Inserir configuração exemplo para Bem-Querer
INSERT INTO ai_configurations (clinic_id, config) VALUES (
    '00000000-0000-0000-0000-000000000001', -- Clinic ID padrão
    '{
        "persona": {
            "name": "Carol",
            "clinic_name": "Bem-Querer Odontokids",
            "role": "secretária virtual",
            "tone": "Empática, acolhedora e eficiente",
            "target_audience": "Mães preocupadas e pacientes ocupados",
            "objective": "Conduzir conversas naturalmente e direcionar para agendamento"
        },
        "team": [
            {
                "name": "Dra. Fernanda Battistini",
                "clinicorp_id": "6113706666688512",
                "specialty": "Ortodontia",
                "focus": "Ortodontia Fixa",
                "schedule": "Segunda, Quarta, Sexta e Sábado"
            }
        ],
        "admin_info": {
            "location": {
                "address": "Rua Siqueira Campos, 1068 – Centro – Santo André"
            },
            "pricing": {
                "consultation": "R$ 250,00"
            }
        },
        "protocols": {
            "do_rules": ["Sempre coletar telefone", "Ser transparente"],
            "dont_rules": ["NUNCA inventar horários", "NUNCA medique"]
        }
    }'::jsonb
) ON CONFLICT (clinic_id, is_active) WHERE is_active = true DO UPDATE SET config = EXCLUDED.config;
