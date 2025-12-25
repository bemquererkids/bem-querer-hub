-- ============================================
-- WhatsApp Multi-Tenant - SQL Completo
-- Execute este arquivo no Supabase SQL Editor
-- ============================================

-- 1. Adicionar clinic_id nas tabelas existentes
ALTER TABLE whatsapp_conversations 
ADD COLUMN IF NOT EXISTS clinic_id UUID REFERENCES clinicas(id) ON DELETE CASCADE;

ALTER TABLE whatsapp_messages
ADD COLUMN IF NOT EXISTS clinic_id UUID REFERENCES clinicas(id) ON DELETE CASCADE;

-- 2. Criar tabela de instâncias WhatsApp
CREATE TABLE IF NOT EXISTS whatsapp_instances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinic_id UUID REFERENCES clinicas(id) ON DELETE CASCADE,
    instance_name TEXT UNIQUE NOT NULL,
    phone_number TEXT,
    status TEXT DEFAULT 'disconnected',
    qr_code TEXT,
    last_connected_at TIMESTAMPTZ,
    webhook_url TEXT,
    uazapi_token TEXT,
    uazapi_base_url TEXT DEFAULT 'https://free.uazapi.com',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Atualizar constraint unique (phone + clinic)
ALTER TABLE whatsapp_conversations 
DROP CONSTRAINT IF EXISTS whatsapp_conversations_phone_number_key;

ALTER TABLE whatsapp_conversations
ADD CONSTRAINT whatsapp_conversations_phone_clinic_unique 
UNIQUE (phone_number, clinic_id);

-- 4. Criar índices para performance
CREATE INDEX IF NOT EXISTS idx_whatsapp_conversations_clinic 
    ON whatsapp_conversations(clinic_id, last_message_at DESC);

CREATE INDEX IF NOT EXISTS idx_whatsapp_messages_clinic 
    ON whatsapp_messages(clinic_id, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_whatsapp_instances_clinic 
    ON whatsapp_instances(clinic_id);

CREATE INDEX IF NOT EXISTS idx_whatsapp_instances_status 
    ON whatsapp_instances(status);

CREATE INDEX IF NOT EXISTS idx_whatsapp_instances_name 
    ON whatsapp_instances(instance_name);

-- 5. Habilitar Row Level Security (RLS)
ALTER TABLE whatsapp_conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE whatsapp_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE whatsapp_instances ENABLE ROW LEVEL SECURITY;

-- 6. Políticas RLS: Isolamento por clínica
DROP POLICY IF EXISTS "clinic_isolation_conversations" ON whatsapp_conversations;
DROP POLICY IF EXISTS "clinic_isolation_messages" ON whatsapp_messages;
DROP POLICY IF EXISTS "clinic_isolation_instances" ON whatsapp_instances;

CREATE POLICY "clinic_isolation_conversations"
ON whatsapp_conversations
FOR ALL
USING (
    clinic_id IN (
        SELECT clinica_id FROM perfis 
        WHERE id = auth.uid()
    )
);

CREATE POLICY "clinic_isolation_messages"
ON whatsapp_messages
FOR ALL
USING (
    clinic_id IN (
        SELECT clinica_id FROM perfis 
        WHERE id = auth.uid()
    )
);

CREATE POLICY "clinic_isolation_instances"
ON whatsapp_instances
FOR ALL
USING (
    clinic_id IN (
        SELECT clinica_id FROM perfis 
        WHERE id = auth.uid()
    )
);

-- 7. Habilitar Realtime
ALTER PUBLICATION supabase_realtime ADD TABLE whatsapp_messages;
ALTER PUBLICATION supabase_realtime ADD TABLE whatsapp_conversations;
ALTER PUBLICATION supabase_realtime ADD TABLE whatsapp_instances;
