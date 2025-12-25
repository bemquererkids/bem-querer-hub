-- ============================================
-- Fix RLS para Permitir Webhook Salvar Mensagens
-- Execute no Supabase SQL Editor
-- ============================================

-- Problema: Webhook não consegue salvar conversas/mensagens devido ao RLS
-- Solução: Permitir INSERT anônimo (webhook) mas manter SELECT isolado por clínica

-- 1. CONVERSAS - Permitir INSERT para todos, SELECT apenas da própria clínica
DROP POLICY IF EXISTS "clinic_isolation_conversations" ON whatsapp_conversations;

CREATE POLICY "allow_webhook_insert_conversations"
ON whatsapp_conversations
FOR INSERT
WITH CHECK (true);

CREATE POLICY "allow_read_own_clinic_conversations"
ON whatsapp_conversations
FOR SELECT
USING (
    clinic_id IN (
        SELECT clinica_id FROM perfis 
        WHERE id = auth.uid()
    )
);

CREATE POLICY "allow_update_own_clinic_conversations"
ON whatsapp_conversations
FOR UPDATE
USING (
    clinic_id IN (
        SELECT clinica_id FROM perfis 
        WHERE id = auth.uid()
    )
);

-- 2. MENSAGENS - Permitir INSERT para todos, SELECT apenas da própria clínica
DROP POLICY IF EXISTS "clinic_isolation_messages" ON whatsapp_messages;

CREATE POLICY "allow_webhook_insert_messages"
ON whatsapp_messages
FOR INSERT
WITH CHECK (true);

CREATE POLICY "allow_read_own_clinic_messages"
ON whatsapp_messages
FOR SELECT
USING (
    clinic_id IN (
        SELECT clinica_id FROM perfis 
        WHERE id = auth.uid()
    )
);

-- 3. Verificar políticas
SELECT tablename, policyname, cmd 
FROM pg_policies 
WHERE tablename IN ('whatsapp_conversations', 'whatsapp_messages')
ORDER BY tablename, policyname;
