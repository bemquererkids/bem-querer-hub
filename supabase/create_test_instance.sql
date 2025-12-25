-- ============================================
-- Criar Instância de Teste para WhatsApp
-- Execute no Supabase SQL Editor
-- ============================================

-- 1. Buscar ID da primeira clínica
-- (Copie o UUID retornado para usar abaixo)
SELECT id, nome_fantasia FROM clinicas LIMIT 1;

-- 2. Criar instância de teste
-- SUBSTITUA 'SEU-CLINIC-ID-AQUI' pelo UUID da clínica acima
INSERT INTO whatsapp_instances (
    clinic_id,
    instance_name,
    phone_number,
    status,
    webhook_url,
    uazapi_base_url
) VALUES (
    'SEU-CLINIC-ID-AQUI',  -- ← SUBSTITUIR com o ID da clínica
    'bemquerer',           -- Nome da instância (deve ser o mesmo da UazAPI)
    '5511991026844',       -- Número do WhatsApp conectado
    'connected',
    'https://bem-querer-hub.vercel.app/api/webhooks/whatsapp',
    'https://bemquerer.uazapi.com'
);

-- 3. Verificar se foi criado
SELECT * FROM whatsapp_instances;

-- 4. (Opcional) Se já existe uma instância, atualizar:
-- UPDATE whatsapp_instances 
-- SET clinic_id = 'SEU-CLINIC-ID-AQUI'
-- WHERE instance_name = 'bemquerer';
