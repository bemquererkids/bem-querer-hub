-- =====================================================
-- VERIFICAÇÃO DA MIGRATION META CLOUD API V2
-- =====================================================
-- Execute estas queries no Supabase SQL Editor para
-- verificar se a migration foi executada corretamente
-- =====================================================

-- 1. Verificar estrutura da tabela
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'clinic_integrations'
ORDER BY ordinal_position;

-- Resultado esperado: Deve mostrar as colunas:
-- - id (uuid)
-- - clinica_id (uuid)
-- - type (text)
-- - config (jsonb)
-- - is_active (boolean)
-- - updated_at (timestamp)
-- - phone_number_id (text) ✅ NOVA
-- - waba_id (text) ✅ NOVA
-- - access_token (text) ✅ NOVA
-- - verify_token (text) ✅ NOVA

-- =====================================================

-- 2. Verificar colunas Meta (deve retornar 4 linhas)
SELECT column_name, data_type
FROM information_schema.columns 
WHERE table_name = 'clinic_integrations' 
AND column_name IN ('phone_number_id', 'waba_id', 'access_token', 'verify_token');

-- Resultado esperado: 4 linhas

-- =====================================================

-- 3. Verificar que colunas UazAPI foram removidas (deve retornar 0 linhas)
SELECT column_name
FROM information_schema.columns 
WHERE table_name = 'clinic_integrations' 
AND column_name IN ('instance_name', 'token', 'qr_code_base64');

-- Resultado esperado: 0 linhas (vazio)

-- =====================================================

-- 4. Verificar índices
SELECT indexname, indexdef
FROM pg_indexes 
WHERE tablename = 'clinic_integrations';

-- Resultado esperado: Deve incluir 'idx_clinic_integrations_phone_number_id'

-- =====================================================

-- 5. Verificar constraints
SELECT conname, contype, pg_get_constraintdef(oid)
FROM pg_constraint
WHERE conrelid = 'public.clinic_integrations'::regclass;

-- Resultado esperado: Deve incluir 'check_whatsapp_fields'

-- =====================================================

-- 6. Verificar políticas RLS
SELECT policyname, cmd, qual
FROM pg_policies
WHERE tablename = 'clinic_integrations';

-- Resultado esperado: Deve incluir 'Isolamento Integrations'

-- =====================================================

-- 7. Testar inserção de dados (TESTE)
-- ATENÇÃO: Substitua o clinica_id por um ID válido do seu banco

/*
INSERT INTO public.clinic_integrations (
    clinica_id,
    type,
    phone_number_id,
    waba_id,
    access_token,
    verify_token,
    is_active
) VALUES (
    '00000000-0000-0000-0000-000000000001', -- SUBSTITUA por um clinica_id real
    'whatsapp',
    '123456789012345',
    '123456789012345',
    'EAA_test_token',
    gen_random_uuid()::TEXT,
    true
);
*/

-- =====================================================

-- 8. Verificar dados inseridos
SELECT 
    id,
    clinica_id,
    type,
    phone_number_id,
    waba_id,
    LEFT(access_token, 10) || '...' as access_token_preview,
    verify_token,
    is_active,
    updated_at
FROM public.clinic_integrations
WHERE type = 'whatsapp';

-- =====================================================

-- 9. Limpar dados de teste (se inseriu)
-- DELETE FROM public.clinic_integrations WHERE phone_number_id = '123456789012345';

-- =====================================================
-- ✅ MIGRATION VERIFICADA COM SUCESSO!
-- =====================================================
