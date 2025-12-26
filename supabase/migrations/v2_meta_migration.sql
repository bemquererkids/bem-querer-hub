-- =====================================================
-- V2 Meta Cloud API Migration (CORRIGIDA)
-- =====================================================
-- Esta migration transforma a tabela clinic_integrations
-- de UazAPI para WhatsApp Business Cloud API (Meta)
--
-- VERSÃO CORRIGIDA: Cria tabela se não existir
-- =====================================================

-- STEP 1: Criar tabela se não existir
CREATE TABLE IF NOT EXISTS public.clinic_integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clinica_id UUID NOT NULL,
    type TEXT NOT NULL,
    config JSONB NOT NULL DEFAULT '{}'::JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraint única
    UNIQUE(clinica_id, type)
);

-- STEP 2: Adicionar colunas Meta (se não existirem)
DO $$ 
BEGIN
    -- Phone Number ID
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'clinic_integrations' 
        AND column_name = 'phone_number_id'
    ) THEN
        ALTER TABLE public.clinic_integrations 
        ADD COLUMN phone_number_id TEXT;
    END IF;

    -- WABA ID
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'clinic_integrations' 
        AND column_name = 'waba_id'
    ) THEN
        ALTER TABLE public.clinic_integrations 
        ADD COLUMN waba_id TEXT;
    END IF;

    -- Access Token
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'clinic_integrations' 
        AND column_name = 'access_token'
    ) THEN
        ALTER TABLE public.clinic_integrations 
        ADD COLUMN access_token TEXT;
    END IF;

    -- Verify Token
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'clinic_integrations' 
        AND column_name = 'verify_token'
    ) THEN
        ALTER TABLE public.clinic_integrations 
        ADD COLUMN verify_token TEXT DEFAULT gen_random_uuid()::TEXT;
    END IF;
END $$;

-- STEP 3: Remover colunas UazAPI (se existirem)
DO $$ 
BEGIN
    -- Instance Name
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'clinic_integrations' 
        AND column_name = 'instance_name'
    ) THEN
        ALTER TABLE public.clinic_integrations 
        DROP COLUMN instance_name;
    END IF;

    -- Token
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'clinic_integrations' 
        AND column_name = 'token'
    ) THEN
        ALTER TABLE public.clinic_integrations 
        DROP COLUMN token;
    END IF;

    -- QR Code Base64
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'clinic_integrations' 
        AND column_name = 'qr_code_base64'
    ) THEN
        ALTER TABLE public.clinic_integrations 
        DROP COLUMN qr_code_base64;
    END IF;
END $$;

-- STEP 4: Criar índice único (se não existir)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE indexname = 'idx_clinic_integrations_phone_number_id'
    ) THEN
        CREATE UNIQUE INDEX idx_clinic_integrations_phone_number_id 
        ON public.clinic_integrations (phone_number_id) 
        WHERE type = 'whatsapp' AND phone_number_id IS NOT NULL;
    END IF;
END $$;

-- STEP 5: Adicionar constraint (se não existir)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'check_whatsapp_fields'
    ) THEN
        ALTER TABLE public.clinic_integrations
        ADD CONSTRAINT check_whatsapp_fields 
        CHECK (
            type != 'whatsapp' OR (
                phone_number_id IS NOT NULL AND
                waba_id IS NOT NULL AND
                access_token IS NOT NULL AND
                verify_token IS NOT NULL
            )
        );
    END IF;
END $$;

-- STEP 6: Adicionar comentários
COMMENT ON COLUMN public.clinic_integrations.phone_number_id IS 
'Meta WhatsApp Business Phone Number ID - Required for whatsapp type';

COMMENT ON COLUMN public.clinic_integrations.waba_id IS 
'Meta WhatsApp Business Account ID - Required for whatsapp type';

COMMENT ON COLUMN public.clinic_integrations.access_token IS 
'Meta permanent access token from System User - Required for whatsapp type';

COMMENT ON COLUMN public.clinic_integrations.verify_token IS 
'Webhook verification token (auto-generated UUID) - Required for whatsapp type';

COMMENT ON TABLE public.clinic_integrations IS 
'V2 - Stores integration credentials. WhatsApp now uses Meta Cloud API instead of UazAPI.';

-- STEP 7: Habilitar RLS (se não estiver habilitado)
ALTER TABLE public.clinic_integrations ENABLE ROW LEVEL SECURITY;

-- STEP 8: Criar política RLS (se não existir)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'clinic_integrations' 
        AND policyname = 'Isolamento Integrations'
    ) THEN
        CREATE POLICY "Isolamento Integrations" 
        ON public.clinic_integrations
        USING (clinica_id IN (
            SELECT clinica_id FROM public.perfis WHERE id = auth.uid()
        ));
    END IF;
END $$;

-- =====================================================
-- Verificação
-- =====================================================
-- Execute para verificar:

SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'clinic_integrations'
ORDER BY ordinal_position;
