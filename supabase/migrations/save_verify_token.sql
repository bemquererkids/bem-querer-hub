-- =====================================================
-- SALVAR VERIFY TOKEN (CORRIGIDO)
-- =====================================================
-- Inclui todos os campos obrigatórios para WhatsApp
-- =====================================================

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
    'PENDING',  -- Será preenchido depois
    'PENDING',  -- Será preenchido depois
    'PENDING',  -- Será preenchido depois
    '0addb8a5-a6cd-473d-af75-b8777f510fd9',
    true
)
ON CONFLICT (clinica_id, type) 
DO UPDATE SET 
    verify_token = '0addb8a5-a6cd-473d-af75-b8777f510fd9',
    phone_number_id = COALESCE(clinic_integrations.phone_number_id, 'PENDING'),
    waba_id = COALESCE(clinic_integrations.waba_id, 'PENDING'),
    access_token = COALESCE(clinic_integrations.access_token, 'PENDING'),
    is_active = true,
    updated_at = NOW();

-- =====================================================
-- Verificar
-- =====================================================

SELECT * FROM clinic_integrations WHERE type = 'whatsapp';
