import { createClient } from '@supabase/supabase-js';

const supabaseUrl = (import.meta.env.VITE_SUPABASE_URL || '').trim();
const supabaseKey = (import.meta.env.VITE_SUPABASE_KEY || '').trim();

// Log para depuração (visível no console do navegador)
console.log("[Supabase Service] Inicializando com URL:", supabaseUrl);
console.log("[Supabase Service] Chave detectada:", supabaseKey ? "SIM (começa com " + supabaseKey.substring(0, 5) + ")" : "NÃO");

if (!supabaseUrl || !supabaseKey) {
    console.error("[Supabase Service] ATENÇÃO: Variáveis de ambiente VITE_SUPABASE_URL ou VITE_SUPABASE_KEY não configuradas!");
}

export const supabase = createClient(supabaseUrl, supabaseKey);
