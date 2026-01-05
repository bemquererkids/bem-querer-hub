
-- Add deal_value column to whatsapp_conversations if it doesn't exist
ALTER TABLE public.whatsapp_conversations 
ADD COLUMN IF NOT EXISTS deal_value NUMERIC(10, 2) DEFAULT 0;
