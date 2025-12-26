-- =====================================================
-- SOLUÇÃO DEFINITIVA - SALVAR VERIFY TOKEN
-- =====================================================
-- Execute EXATAMENTE esta query no Supabase SQL Editor
-- =====================================================

-- Primeiro, deletar registro existente se houver
DELETE FROM clinic_integrations WHERE type = 'whatsapp';

-- Depois, inserir com todos os campos obrigatórios
INSERT INTO clinic_integrations (
    clinica_id,
    type,
    phone_number_id,
    waba_id,
    access_token,
    verify_token,
    is_active
) VALUES (
    '00000000-0000-0000-0000-000000000001',
    'whatsapp',
    'PENDING',
    'PENDING',
    'PENDING',
    '0addb8a5-a6cd-473d-af75-b8777f510fd9',
    true
);

-- Verificar se salvou
SELECT * FROM clinic_integrations WHERE type = 'whatsapp';

-- Deve retornar:
-- verify_token: 0addb8a5-a6cd-473d-af75-b8777f510fd9
