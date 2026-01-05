-- Add avatar column to whatsapp_conversations if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'whatsapp_conversations' AND column_name = 'avatar') THEN
        ALTER TABLE whatsapp_conversations ADD COLUMN avatar TEXT;
    END IF;
END $$;
