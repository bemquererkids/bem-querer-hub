-- =====================================================
-- BEM-QUERER HUB - V1.0.0 LEGACY BACKUP
-- UazAPI Integration Version
-- Backup Date: 2025-12-26
-- =====================================================
-- 
-- IMPORTANTE: Este é o backup completo da versão V1 do sistema
-- que utiliza UazAPI como provedor de WhatsApp.
-- 
-- Antes de migrar para Meta WhatsApp API, este backup garante
-- que podemos reverter para a versão funcional se necessário.
--
-- =====================================================

-- Enable Required Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgvector";

-- =====================================================
-- 1. CLINICS (Tenant Table)
-- =====================================================
CREATE TABLE IF NOT EXISTS public.clinics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    cnpj VARCHAR(18) UNIQUE,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    
    -- Subscription Info
    plan VARCHAR(50) DEFAULT 'trial', -- trial, basic, premium
    status VARCHAR(20) DEFAULT 'active', -- active, suspended, cancelled
    trial_ends_at TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- 2. PROFILES (Extended User Info)
-- =====================================================
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    clinic_id UUID NOT NULL REFERENCES public.clinics(id) ON DELETE CASCADE,
    
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'receptionist',
    avatar_url TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- 3. PATIENTS
-- =====================================================
CREATE TABLE IF NOT EXISTS public.patients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinic_id UUID NOT NULL REFERENCES public.clinics(id) ON DELETE CASCADE,
    
    full_name VARCHAR(255) NOT NULL,
    cpf VARCHAR(14) UNIQUE,
    birth_date DATE,
    phone VARCHAR(20),
    email VARCHAR(255),
    
    guardian_name VARCHAR(255),
    guardian_phone VARCHAR(20),
    guardian_relation VARCHAR(50),
    
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(2),
    zip_code VARCHAR(10),
    
    allergies TEXT,
    medical_notes TEXT,
    
    source VARCHAR(100),
    utm_source VARCHAR(100),
    utm_campaign VARCHAR(100),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_patient_clinic UNIQUE(clinic_id, cpf)
);

CREATE INDEX IF NOT EXISTS idx_patients_clinic ON public.patients(clinic_id);
CREATE INDEX IF NOT EXISTS idx_patients_phone ON public.patients(phone);

-- =====================================================
-- 4. APPOINTMENTS
-- =====================================================
CREATE TABLE IF NOT EXISTS public.appointments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinic_id UUID NOT NULL REFERENCES public.clinics(id) ON DELETE CASCADE,
    patient_id UUID NOT NULL REFERENCES public.patients(id) ON DELETE CASCADE,
    
    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
    duration_minutes INTEGER DEFAULT 60,
    dentist_name VARCHAR(255),
    procedure_type VARCHAR(100),
    
    status VARCHAR(50) DEFAULT 'scheduled',
    
    clinicorp_id VARCHAR(100),
    synced_at TIMESTAMP WITH TIME ZONE,
    
    notes TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_appointments_clinic ON public.appointments(clinic_id);
CREATE INDEX IF NOT EXISTS idx_appointments_patient ON public.appointments(patient_id);
CREATE INDEX IF NOT EXISTS idx_appointments_scheduled ON public.appointments(scheduled_at);

-- =====================================================
-- 5. CHATS (WhatsApp Conversations - UazAPI)
-- =====================================================
CREATE TABLE IF NOT EXISTS public.chats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinic_id UUID NOT NULL REFERENCES public.clinics(id) ON DELETE CASCADE,
    patient_id UUID REFERENCES public.patients(id) ON DELETE SET NULL,
    
    -- WhatsApp Info (UazAPI Format)
    whatsapp_number VARCHAR(20) NOT NULL,
    whatsapp_name VARCHAR(255),
    
    status VARCHAR(50) DEFAULT 'open',
    assigned_to UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    
    intent VARCHAR(50),
    urgency VARCHAR(20) DEFAULT 'normal',
    
    last_message_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chats_clinic ON public.chats(clinic_id);
CREATE INDEX IF NOT EXISTS idx_chats_patient ON public.chats(patient_id);
CREATE INDEX IF NOT EXISTS idx_chats_status ON public.chats(status);

-- =====================================================
-- 6. MESSAGES (UazAPI Format)
-- =====================================================
CREATE TABLE IF NOT EXISTS public.messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinic_id UUID NOT NULL REFERENCES public.clinics(id) ON DELETE CASCADE,
    chat_id UUID NOT NULL REFERENCES public.chats(id) ON DELETE CASCADE,
    
    content TEXT NOT NULL,
    message_type VARCHAR(20) DEFAULT 'text',
    media_url TEXT,
    
    sender_type VARCHAR(20) NOT NULL,
    sender_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    
    -- UazAPI Specific Fields (V1 LEGACY)
    uazapi_message_id VARCHAR(255),
    uazapi_status VARCHAR(20), -- sent, delivered, read, failed
    
    -- AI Context
    embedding vector(768),
    ai_confidence FLOAT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_messages_chat ON public.messages(chat_id);
CREATE INDEX IF NOT EXISTS idx_messages_clinic ON public.messages(clinic_id);
CREATE INDEX IF NOT EXISTS idx_messages_created ON public.messages(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_messages_embedding ON public.messages 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- =====================================================
-- 7. WEBHOOK_LOGS (UazAPI Events - V1 LEGACY)
-- =====================================================
CREATE TABLE IF NOT EXISTS public.webhook_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinic_id UUID REFERENCES public.clinics(id) ON DELETE SET NULL,
    
    event_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_webhook_logs_processed ON public.webhook_logs(processed);
CREATE INDEX IF NOT EXISTS idx_webhook_logs_created ON public.webhook_logs(created_at DESC);

-- =====================================================
-- 8. CLINIC_INTEGRATIONS (V1 LEGACY - UazAPI Config)
-- =====================================================
-- IMPORTANTE: Esta tabela armazena as configurações do UazAPI
-- Formato do config JSONB para type='whatsapp':
-- {
--   "instance": "bemquerer",
--   "token": "...",
--   "connected_at": "2025-12-26T..."
-- }
CREATE TABLE IF NOT EXISTS public.clinic_integrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinica_id UUID NOT NULL REFERENCES public.clinics(id) ON DELETE CASCADE,
    type TEXT NOT NULL, -- 'clinicorp', 'openai', 'gemini', 'whatsapp'
    config JSONB NOT NULL DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(clinica_id, type)
);

ALTER TABLE public.clinic_integrations ENABLE ROW LEVEL SECURITY;

CREATE POLICY IF NOT EXISTS "Isolamento Integrations" ON public.clinic_integrations
USING (clinica_id IN (SELECT clinic_id FROM public.profiles WHERE id = auth.uid()));

-- =====================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =====================================================

ALTER TABLE public.clinics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.appointments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chats ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.webhook_logs ENABLE ROW LEVEL SECURITY;

-- Profiles
CREATE POLICY IF NOT EXISTS "Users can view own profile" ON public.profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY IF NOT EXISTS "Users can update own profile" ON public.profiles
    FOR UPDATE USING (auth.uid() = id);

-- Patients
CREATE POLICY IF NOT EXISTS "Users can view clinic patients" ON public.patients
    FOR SELECT USING (
        clinic_id IN (
            SELECT clinic_id FROM public.profiles WHERE id = auth.uid()
        )
    );

CREATE POLICY IF NOT EXISTS "Users can insert clinic patients" ON public.patients
    FOR INSERT WITH CHECK (
        clinic_id IN (
            SELECT clinic_id FROM public.profiles WHERE id = auth.uid()
        )
    );

-- Appointments
CREATE POLICY IF NOT EXISTS "Users can view clinic appointments" ON public.appointments
    FOR SELECT USING (
        clinic_id IN (
            SELECT clinic_id FROM public.profiles WHERE id = auth.uid()
        )
    );

-- Chats
CREATE POLICY IF NOT EXISTS "Users can view clinic chats" ON public.chats
    FOR SELECT USING (
        clinic_id IN (
            SELECT clinic_id FROM public.profiles WHERE id = auth.uid()
        )
    );

-- Messages
CREATE POLICY IF NOT EXISTS "Users can view clinic messages" ON public.messages
    FOR SELECT USING (
        clinic_id IN (
            SELECT clinic_id FROM public.profiles WHERE id = auth.uid()
        )
    );

-- =====================================================
-- FUNCTIONS & TRIGGERS
-- =====================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER IF NOT EXISTS update_clinics_updated_at BEFORE UPDATE ON public.clinics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER IF NOT EXISTS update_profiles_updated_at BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER IF NOT EXISTS update_patients_updated_at BEFORE UPDATE ON public.patients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER IF NOT EXISTS update_appointments_updated_at BEFORE UPDATE ON public.appointments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER IF NOT EXISTS update_chats_updated_at BEFORE UPDATE ON public.chats
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- SEED DATA
-- =====================================================

INSERT INTO public.clinics (id, name, email, plan, status)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'Clínica Bem-Querer Demo',
    'contato@bemquerer.com.br',
    'premium',
    'active'
)
ON CONFLICT (id) DO NOTHING;

-- =====================================================
-- COMMENTS & DOCUMENTATION
-- =====================================================

COMMENT ON TABLE public.clinics IS 'V1 LEGACY - Tenant table with UazAPI integration';
COMMENT ON TABLE public.messages IS 'V1 LEGACY - WhatsApp messages via UazAPI with vector embeddings';
COMMENT ON COLUMN public.messages.uazapi_message_id IS 'V1 LEGACY - UazAPI specific message ID';
COMMENT ON COLUMN public.messages.uazapi_status IS 'V1 LEGACY - UazAPI message delivery status';
COMMENT ON TABLE public.webhook_logs IS 'V1 LEGACY - UazAPI webhook event logs';
COMMENT ON TABLE public.clinic_integrations IS 'V1 LEGACY - Stores UazAPI credentials in config JSONB';

-- =====================================================
-- END OF V1.0.0 LEGACY BACKUP
-- =====================================================
