-- NUCLEAR OPTION: Reset Realtime Publication
-- Run this in Supabase SQL Editor to guarantee Realtime works

-- 1. Enable replication identity (required for realtime)
ALTER TABLE whatsapp_conversations REPLICA IDENTITY FULL;
ALTER TABLE whatsapp_messages REPLICA IDENTITY FULL;

-- 2. Drop existing publication to clear any partial states
DROP PUBLICATION IF EXISTS supabase_realtime;

-- 3. Create fresh publication for ALL relevant tables
CREATE PUBLICATION supabase_realtime FOR TABLE whatsapp_conversations, whatsapp_messages;

-- 4. Verify (Optional output)
select * from pg_publication_tables where pubname = 'supabase_realtime';
