-- =====================================================
-- Bem-Querer Hub - Database Schema (Supabase Edition)
-- Multi-tenant Architecture with Row Level Security
-- =====================================================

-- Enable Required Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgvector";

-- =====================================================
-- 1. CLINICS (Tenant Table)
-- =====================================================
CREATE TABLE public.clinics (
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
-- Links to Supabase Auth users
CREATE TABLE public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    clinic_id UUID NOT NULL REFERENCES public.clinics(id) ON DELETE CASCADE,
    
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'receptionist', -- admin, receptionist, dentist
    avatar_url TEXT,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- 3. PATIENTS
-- =====================================================
CREATE TABLE public.patients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinic_id UUID NOT NULL REFERENCES public.clinics(id) ON DELETE CASCADE,
    
    -- Patient Info
    full_name VARCHAR(255) NOT NULL,
    cpf VARCHAR(14) UNIQUE,
    birth_date DATE,
    phone VARCHAR(20),
    email VARCHAR(255),
    
    -- Guardian Info (for pediatric patients)
    guardian_name VARCHAR(255),
    guardian_phone VARCHAR(20),
    guardian_relation VARCHAR(50), -- mother, father, other
    
    -- Address
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(2),
    zip_code VARCHAR(10),
    
    -- Medical Info
    allergies TEXT,
    medical_notes TEXT,
    
    -- Source Tracking (UTM)
    source VARCHAR(100), -- google_ads, instagram, referral
    utm_source VARCHAR(100),
    utm_campaign VARCHAR(100),
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Indexes
    CONSTRAINT unique_patient_clinic UNIQUE(clinic_id, cpf)
);

CREATE INDEX idx_patients_clinic ON public.patients(clinic_id);
CREATE INDEX idx_patients_phone ON public.patients(phone);

-- =====================================================
-- 4. APPOINTMENTS
-- =====================================================
CREATE TABLE public.appointments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinic_id UUID NOT NULL REFERENCES public.clinics(id) ON DELETE CASCADE,
    patient_id UUID NOT NULL REFERENCES public.patients(id) ON DELETE CASCADE,
    
    -- Appointment Details
    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
    duration_minutes INTEGER DEFAULT 60,
    dentist_name VARCHAR(255),
    procedure_type VARCHAR(100), -- consultation, cleaning, emergency
    
    -- Status
    status VARCHAR(50) DEFAULT 'scheduled', -- scheduled, confirmed, completed, no_show, cancelled
    
    -- Clinicorp Sync
    clinicorp_id VARCHAR(100), -- External ID from Clinicorp
    synced_at TIMESTAMP WITH TIME ZONE,
    
    -- Notes
    notes TEXT,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_appointments_clinic ON public.appointments(clinic_id);
CREATE INDEX idx_appointments_patient ON public.appointments(patient_id);
CREATE INDEX idx_appointments_scheduled ON public.appointments(scheduled_at);

-- =====================================================
-- 5. CHATS (WhatsApp Conversations)
-- =====================================================
CREATE TABLE public.chats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinic_id UUID NOT NULL REFERENCES public.clinics(id) ON DELETE CASCADE,
    patient_id UUID REFERENCES public.patients(id) ON DELETE SET NULL,
    
    -- WhatsApp Info
    whatsapp_number VARCHAR(20) NOT NULL,
    whatsapp_name VARCHAR(255),
    
    -- Chat Status
    status VARCHAR(50) DEFAULT 'open', -- open, waiting_human, closed
    assigned_to UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    
    -- Intent Classification
    intent VARCHAR(50), -- booking, emergency, question, complaint
    urgency VARCHAR(20) DEFAULT 'normal', -- low, normal, high, urgent
    
    -- Metadata
    last_message_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_chats_clinic ON public.chats(clinic_id);
CREATE INDEX idx_chats_patient ON public.chats(patient_id);
CREATE INDEX idx_chats_status ON public.chats(status);

-- =====================================================
-- 6. MESSAGES
-- =====================================================
CREATE TABLE public.messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinic_id UUID NOT NULL REFERENCES public.clinics(id) ON DELETE CASCADE,
    chat_id UUID NOT NULL REFERENCES public.chats(id) ON DELETE CASCADE,
    
    -- Message Content
    content TEXT NOT NULL,
    message_type VARCHAR(20) DEFAULT 'text', -- text, audio, image, document
    media_url TEXT,
    
    -- Sender
    sender_type VARCHAR(20) NOT NULL, -- user, ai, human_agent
    sender_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    
    -- UazAPI Metadata
    uazapi_message_id VARCHAR(255),
    uazapi_status VARCHAR(20), -- sent, delivered, read, failed
    
    -- AI Context (for RAG)
    embedding vector(768), -- Gemini embeddings
    ai_confidence FLOAT,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_messages_chat ON public.messages(chat_id);
CREATE INDEX idx_messages_clinic ON public.messages(clinic_id);
CREATE INDEX idx_messages_created ON public.messages(created_at DESC);

-- Vector similarity search index
CREATE INDEX idx_messages_embedding ON public.messages 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- =====================================================
-- 7. WEBHOOK_LOGS (UazAPI Event Tracking)
-- =====================================================
CREATE TABLE public.webhook_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinic_id UUID REFERENCES public.clinics(id) ON DELETE SET NULL,
    
    -- Event Info
    event_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    
    -- Processing
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_webhook_logs_processed ON public.webhook_logs(processed);
CREATE INDEX idx_webhook_logs_created ON public.webhook_logs(created_at DESC);

-- =====================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE public.clinics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.appointments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chats ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.webhook_logs ENABLE ROW LEVEL SECURITY;

-- Profiles: Users can only see their own profile
CREATE POLICY "Users can view own profile" ON public.profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.profiles
    FOR UPDATE USING (auth.uid() = id);

-- Patients: Users can only access patients from their clinic
CREATE POLICY "Users can view clinic patients" ON public.patients
    FOR SELECT USING (
        clinic_id IN (
            SELECT clinic_id FROM public.profiles WHERE id = auth.uid()
        )
    );

CREATE POLICY "Users can insert clinic patients" ON public.patients
    FOR INSERT WITH CHECK (
        clinic_id IN (
            SELECT clinic_id FROM public.profiles WHERE id = auth.uid()
        )
    );

-- Appointments: Users can only access appointments from their clinic
CREATE POLICY "Users can view clinic appointments" ON public.appointments
    FOR SELECT USING (
        clinic_id IN (
            SELECT clinic_id FROM public.profiles WHERE id = auth.uid()
        )
    );

-- Chats: Users can only access chats from their clinic
CREATE POLICY "Users can view clinic chats" ON public.chats
    FOR SELECT USING (
        clinic_id IN (
            SELECT clinic_id FROM public.profiles WHERE id = auth.uid()
        )
    );

-- Messages: Users can only access messages from their clinic
CREATE POLICY "Users can view clinic messages" ON public.messages
    FOR SELECT USING (
        clinic_id IN (
            SELECT clinic_id FROM public.profiles WHERE id = auth.uid()
        )
    );

-- =====================================================
-- FUNCTIONS & TRIGGERS
-- =====================================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to relevant tables
CREATE TRIGGER update_clinics_updated_at BEFORE UPDATE ON public.clinics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_patients_updated_at BEFORE UPDATE ON public.patients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_appointments_updated_at BEFORE UPDATE ON public.appointments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_chats_updated_at BEFORE UPDATE ON public.chats
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- SEED DATA (Optional - for development)
-- =====================================================

-- Insert a demo clinic
INSERT INTO public.clinics (id, name, email, plan, status)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'Clínica Bem-Querer Demo',
    'contato@bemquerer.com.br',
    'premium',
    'active'
);

COMMENT ON TABLE public.clinics IS 'Tenant table - each clinic is isolated';
COMMENT ON TABLE public.messages IS 'Stores all WhatsApp messages with vector embeddings for AI context';
COMMENT ON COLUMN public.messages.embedding IS 'Vector embedding (768-dim) for semantic search using pgvector';
