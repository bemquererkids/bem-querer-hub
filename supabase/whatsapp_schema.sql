-- ============================================
-- WhatsApp Integration - Database Schema
-- ============================================

-- Tabela de conversas do WhatsApp
CREATE TABLE IF NOT EXISTS whatsapp_conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone_number TEXT UNIQUE NOT NULL,
    contact_name TEXT,
    profile_pic_url TEXT,
    last_message TEXT,
    last_message_at TIMESTAMPTZ,
    unread_count INTEGER DEFAULT 0,
    is_archived BOOLEAN DEFAULT false,
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela de mensagens do WhatsApp
CREATE TABLE IF NOT EXISTS whatsapp_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES whatsapp_conversations(id) ON DELETE CASCADE,
    message_id TEXT UNIQUE NOT NULL,
    from_number TEXT NOT NULL,
    to_number TEXT NOT NULL,
    message_type TEXT DEFAULT 'text',
    content TEXT,
    media_url TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    status TEXT DEFAULT 'sent',
    is_from_me BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_whatsapp_conversations_phone 
    ON whatsapp_conversations(phone_number);

CREATE INDEX IF NOT EXISTS idx_whatsapp_conversations_last_message 
    ON whatsapp_conversations(last_message_at DESC);

CREATE INDEX IF NOT EXISTS idx_whatsapp_messages_conversation 
    ON whatsapp_messages(conversation_id, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_whatsapp_messages_message_id 
    ON whatsapp_messages(message_id);

-- Habilitar Realtime (executar separadamente se necessário)
-- ALTER PUBLICATION supabase_realtime ADD TABLE whatsapp_messages;
-- ALTER PUBLICATION supabase_realtime ADD TABLE whatsapp_conversations;

-- Comentários para documentação
COMMENT ON TABLE whatsapp_conversations IS 'Armazena conversas do WhatsApp Business';
COMMENT ON TABLE whatsapp_messages IS 'Armazena mensagens individuais do WhatsApp';
COMMENT ON COLUMN whatsapp_conversations.phone_number IS 'Número no formato internacional sem +';
COMMENT ON COLUMN whatsapp_messages.is_from_me IS 'true se mensagem foi enviada pelo sistema';
