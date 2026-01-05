-- =====================================================
-- Manual Configuration for UAZAPI
-- =====================================================
-- Run this in Supabase SQL Editor to configure the integration
-- because API configuration requires authentication (RLS).
-- =====================================================

INSERT INTO public.clinic_integrations (
    clinica_id, 
    type, 
    instance_name, 
    token, 
    is_active,
    updated_at
)
VALUES (
    '00000000-0000-0000-0000-000000000001', -- ID Padrão Bem-Querer
    'whatsapp',
    'bemquerer',                            -- Instance Name (Validado)
    'f2b56a94-37e1-4e6d-8921-7da54069d797', -- Token (Validado no Debug)
    true,
    NOW()
)
ON CONFLICT (clinica_id, type) 
DO UPDATE SET 
    instance_name = EXCLUDED.instance_name,
    token = EXCLUDED.token,
    phone_number_id = NULL, -- Limpa campos Meta para evitar conflito
    waba_id = NULL,
    access_token = NULL,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- Verificação
SELECT instance_name, token, is_active 
FROM public.clinic_integrations 
WHERE type = 'whatsapp';
