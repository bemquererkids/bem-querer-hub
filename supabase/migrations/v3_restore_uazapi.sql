-- =====================================================
-- V3 Restore UazAPI Migration
-- =====================================================
-- Restores instance_name and token columns for UazAPI support
-- and relaxes constraints to allow either Meta or UazAPI.
-- =====================================================

-- STEP 1: Restore UazAPI Columns
DO $$ 
BEGIN
    -- Instance Name
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'clinic_integrations' 
        AND column_name = 'instance_name'
    ) THEN
        ALTER TABLE public.clinic_integrations 
        ADD COLUMN instance_name TEXT;
    END IF;

    -- Token
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'clinic_integrations' 
        AND column_name = 'token'
    ) THEN
        ALTER TABLE public.clinic_integrations 
        ADD COLUMN token TEXT;
    END IF;
    
    -- API Key (just in case we need it for future)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'clinic_integrations' 
        AND column_name = 'api_key'
    ) THEN
        ALTER TABLE public.clinic_integrations 
        ADD COLUMN api_key TEXT;
    END IF;
END $$;

-- STEP 2: Drop Strict Meta Constraints
ALTER TABLE public.clinic_integrations 
DROP CONSTRAINT IF EXISTS check_whatsapp_fields;

-- STEP 3: Add Flexible Constraint
ALTER TABLE public.clinic_integrations
ADD CONSTRAINT check_integration_fields 
CHECK (
    (type = 'whatsapp' AND (
        -- Option A: Meta (all 4 fields present)
        (phone_number_id IS NOT NULL AND waba_id IS NOT NULL AND access_token IS NOT NULL) OR
        -- Option B: UazAPI (instance_name and token present)
        (instance_name IS NOT NULL AND token IS NOT NULL)
    )) OR
    (type != 'whatsapp')
);

COMMENT ON COLUMN public.clinic_integrations.instance_name IS 'UazAPI Instance Name';
COMMENT ON COLUMN public.clinic_integrations.token IS 'UazAPI Token (or API Key)';

-- STEP 4: Update existing record for 'bemquerer' if it exists as Meta type but wants to be Uaz
-- (Optional cleanup, leaving manual for safety)
