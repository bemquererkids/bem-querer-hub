-- ============================================
-- Fix RLS para Webhook
-- Execute no Supabase SQL Editor
-- ============================================

-- Problema: RLS está bloqueando webhook de acessar whatsapp_instances
-- Solução: Permitir leitura anônima de instâncias (seguro porque só contém metadados)

-- 1. Remover política restritiva existente
DROP POLICY IF EXISTS "clinic_isolation_instances" ON whatsapp_instances;

-- 2. Criar política que permite leitura para todos (necessário para webhook)
CREATE POLICY "allow_read_instances"
ON whatsapp_instances
FOR SELECT
USING (true);

-- 3. Criar política que permite escrita apenas para usuários autenticados da clínica
CREATE POLICY "allow_write_own_clinic_instances"
ON whatsapp_instances
FOR ALL
USING (
    clinic_id IN (
        SELECT clinica_id FROM perfis 
        WHERE id = auth.uid()
    )
);

-- Verificar políticas
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual 
FROM pg_policies 
WHERE tablename = 'whatsapp_instances';
