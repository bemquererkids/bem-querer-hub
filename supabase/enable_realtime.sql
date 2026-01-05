-- Enable Realtime for WhatsApp tables
-- This is required for the Frontend subscription to work!

-- 1. Enable replication on tables (if not already)
ALTER TABLE whatsapp_conversations REPLICA IDENTITY FULL;
ALTER TABLE whatsapp_messages REPLICA IDENTITY FULL;

-- 2. Add tables to the realtime publication
-- Note: 'supabase_realtime' is the default publication name
begin;
  drop publication if exists supabase_realtime;
  create publication supabase_realtime for table whatsapp_conversations, whatsapp_messages;
commit;
