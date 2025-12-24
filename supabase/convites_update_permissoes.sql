-- =====================================================
-- Atualização: Mudar de "cargo" para "permissão"
-- =====================================================

-- Atualizar constraint para aceitar 'usuario' além dos valores existentes
ALTER TABLE public.convites DROP CONSTRAINT IF EXISTS convites_cargo_check;
ALTER TABLE public.convites ADD CONSTRAINT convites_cargo_check 
    CHECK (cargo IN ('admin', 'recepcionista', 'dentista', 'usuario'));

-- Opcional: Migrar dados existentes
-- UPDATE public.convites SET cargo = 'usuario' WHERE cargo IN ('recepcionista', 'dentista');

COMMENT ON COLUMN public.convites.cargo IS 'Permissão do usuário: admin (acesso total) ou usuario (acesso limitado)';
