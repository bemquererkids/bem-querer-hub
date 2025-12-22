-- =====================================================
-- INVENTORY & INVOICES (New Module)
-- =====================================================

-- 1. PRODUCTS
CREATE TABLE public.products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinic_id UUID NOT NULL REFERENCES public.clinics(id) ON DELETE CASCADE,
    
    name VARCHAR(255) NOT NULL,
    code VARCHAR(100), -- Internal code / SKU
    barcode VARCHAR(100), -- EAN/GTIN
    description TEXT,
    
    cost_price DECIMAL(10, 2) DEFAULT 0.00,
    selling_price DECIMAL(10, 2) DEFAULT 0.00,
    stock_quantity INTEGER DEFAULT 0,
    min_stock_alert INTEGER DEFAULT 5,
    
    category VARCHAR(100),
    brand VARCHAR(100),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_product_code_clinic UNIQUE(clinic_id, code)
);

CREATE INDEX idx_products_clinic ON public.products(clinic_id);
CREATE INDEX idx_products_barcode ON public.products(barcode);

-- 2. INVOICES (Notas Fiscais)
CREATE TABLE public.invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinic_id UUID NOT NULL REFERENCES public.clinics(id) ON DELETE CASCADE,
    
    access_key VARCHAR(44) NOT NULL, -- Chave de Acesso NF-e
    number VARCHAR(20),
    series VARCHAR(5),
    
    issuer_cnpj VARCHAR(18),
    issuer_name VARCHAR(255),
    issue_date DATE,
    
    total_value DECIMAL(10, 2),
    status VARCHAR(50) DEFAULT 'imported', -- imported, pending, cancelled
    
    xml_url TEXT, -- Link to stored XML if needed
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_invoice_access_key_clinic UNIQUE(clinic_id, access_key)
);

CREATE INDEX idx_invoices_clinic ON public.invoices(clinic_id);
CREATE INDEX idx_invoices_date ON public.invoices(issue_date);

-- 3. INVOICE ITEMS
CREATE TABLE public.invoice_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    invoice_id UUID NOT NULL REFERENCES public.invoices(id) ON DELETE CASCADE,
    product_id UUID REFERENCES public.products(id) ON DELETE SET NULL, -- Link to internal product
    
    -- Data from the Invoice
    product_code_in_invoice VARCHAR(100),
    product_name_in_invoice VARCHAR(255),
    ncm VARCHAR(20),
    cfop VARCHAR(10),
    unit VARCHAR(10),
    
    quantity DECIMAL(10, 4),
    unit_price DECIMAL(10, 4),
    total_price DECIMAL(10, 2),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_invoice_items_invoice ON public.invoice_items(invoice_id);

-- RLS Policies

ALTER TABLE public.products ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.invoice_items ENABLE ROW LEVEL SECURITY;

-- Products Policies
CREATE POLICY "Users can view clinic products" ON public.products
    FOR SELECT USING (clinic_id IN (SELECT clinic_id FROM public.profiles WHERE id = auth.uid()));

CREATE POLICY "Users can insert clinic products" ON public.products
    FOR INSERT WITH CHECK (clinic_id IN (SELECT clinic_id FROM public.profiles WHERE id = auth.uid()));

CREATE POLICY "Users can update clinic products" ON public.products
    FOR UPDATE USING (clinic_id IN (SELECT clinic_id FROM public.profiles WHERE id = auth.uid()));

-- Invoices Policies
CREATE POLICY "Users can view clinic invoices" ON public.invoices
    FOR SELECT USING (clinic_id IN (SELECT clinic_id FROM public.profiles WHERE id = auth.uid()));

CREATE POLICY "Users can insert clinic invoices" ON public.invoices
    FOR INSERT WITH CHECK (clinic_id IN (SELECT clinic_id FROM public.profiles WHERE id = auth.uid()));

-- Invoice Items Policies
CREATE POLICY "Users can view clinic invoice items" ON public.invoice_items
    FOR SELECT USING (
        invoice_id IN (
            SELECT id FROM public.invoices WHERE clinic_id IN (
                SELECT clinic_id FROM public.profiles WHERE id = auth.uid()
            )
        )
    );

CREATE POLICY "Users can insert clinic invoice items" ON public.invoice_items
    FOR INSERT WITH CHECK (
        invoice_id IN (
            SELECT id FROM public.invoices WHERE clinic_id IN (
                SELECT clinic_id FROM public.profiles WHERE id = auth.uid()
            )
        )
    );

-- Trigger for Updated At
CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON public.products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_invoices_updated_at BEFORE UPDATE ON public.invoices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
