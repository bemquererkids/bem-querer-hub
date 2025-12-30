-- Enable RLS (if not enabled) but allow access for now
ALTER TABLE whatsapp_conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE whatsapp_messages ENABLE ROW LEVEL SECURITY;

-- Policy for Conversations: Allow anyone (anon/authenticated) to READ
DROP POLICY IF EXISTS "Allow public read conversations" ON whatsapp_conversations;
CREATE POLICY "Allow public read conversations"
ON whatsapp_conversations FOR SELECT
TO anon, authenticated, service_role
USING (true);

-- Policy for Messages: Allow anyone (anon/authenticated) to READ
DROP POLICY IF EXISTS "Allow public read messages" ON whatsapp_messages;
CREATE POLICY "Allow public read messages"
ON whatsapp_messages FOR SELECT
TO anon, authenticated, service_role
USING (true);

-- Also allow insert/update for service_role logic (already usually default bypass, but good to be explicit if using client)
DROP POLICY IF EXISTS "Allow service_role full access conversations" ON whatsapp_conversations;
CREATE POLICY "Allow service_role full access conversations"
ON whatsapp_conversations FOR ALL
TO service_role
USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Allow service_role full access messages" ON whatsapp_messages;
CREATE POLICY "Allow service_role full access messages"
ON whatsapp_messages FOR ALL
TO service_role
USING (true) WITH CHECK (true);
