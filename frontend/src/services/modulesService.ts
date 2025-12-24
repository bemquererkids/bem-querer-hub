import { supabase } from './supabase';

export interface ClinicModule {
    id: string;
    clinica_id: string;
    modulo: 'clinicorp' | 'chatgpt' | 'whatsapp' | 'agenda' | 'financeiro';
    ativo: boolean;
    configurado: boolean;
    configuracao: Record<string, any>;
    ativado_em?: string;
    criado_em: string;
    atualizado_em: string;
}

export interface ModuleConfig {
    [key: string]: any;
}

/**
 * Obter todos os módulos da clínica
 */
export const getClinicModules = async (
    clinicaId: string
): Promise<ClinicModule[]> => {
    try {
        const { data, error } = await supabase
            .from('clinicas_modulos')
            .select('*')
            .eq('clinica_id', clinicaId)
            .order('modulo');

        if (error) {
            console.error('[Modules Service] Get modules error:', error);
            return [];
        }

        return data || [];
    } catch (error) {
        console.error('[Modules Service] Unexpected error:', error);
        return [];
    }
};

/**
 * Obter apenas módulos ativos
 */
export const getActiveModules = async (
    clinicaId: string
): Promise<string[]> => {
    try {
        const { data, error } = await supabase
            .from('clinicas_modulos')
            .select('modulo')
            .eq('clinica_id', clinicaId)
            .eq('ativo', true);

        if (error) {
            console.error('[Modules Service] Get active modules error:', error);
            return [];
        }

        return data?.map(m => m.modulo) || [];
    } catch (error) {
        console.error('[Modules Service] Unexpected error:', error);
        return [];
    }
};

/**
 * Verificar se um módulo específico está ativo
 */
export const isModuleActive = async (
    clinicaId: string,
    modulo: string
): Promise<boolean> => {
    try {
        const { data, error } = await supabase
            .rpc('modulo_ativo', {
                p_clinica_id: clinicaId,
                p_modulo: modulo
            });

        if (error) {
            console.error('[Modules Service] Check module error:', error);
            return false;
        }

        return data === true;
    } catch (error) {
        console.error('[Modules Service] Unexpected error:', error);
        return false;
    }
};

/**
 * Ativar/Desativar módulo
 */
export const toggleModule = async (
    clinicaId: string,
    modulo: string,
    ativo: boolean
): Promise<boolean> => {
    try {
        const { data, error } = await supabase
            .rpc('toggle_modulo', {
                p_clinica_id: clinicaId,
                p_modulo: modulo,
                p_ativo: ativo
            });

        if (error) {
            console.error('[Modules Service] Toggle module error:', error);
            return false;
        }

        return data === true;
    } catch (error) {
        console.error('[Modules Service] Unexpected error:', error);
        return false;
    }
};

/**
 * Atualizar configuração do módulo
 */
export const updateModuleConfig = async (
    clinicaId: string,
    modulo: string,
    configuracao: ModuleConfig
): Promise<boolean> => {
    try {
        const { data, error } = await supabase
            .rpc('atualizar_config_modulo', {
                p_clinica_id: clinicaId,
                p_modulo: modulo,
                p_configuracao: configuracao
            });

        if (error) {
            console.error('[Modules Service] Update config error:', error);
            return false;
        }

        return data === true;
    } catch (error) {
        console.error('[Modules Service] Unexpected error:', error);
        return false;
    }
};

/**
 * Inicializar módulos padrão para nova clínica
 */
export const initializeClinicModules = async (
    clinicaId: string
): Promise<boolean> => {
    try {
        const { error } = await supabase
            .rpc('inicializar_modulos_clinica', {
                p_clinica_id: clinicaId
            });

        if (error) {
            console.error('[Modules Service] Initialize modules error:', error);
            return false;
        }

        return true;
    } catch (error) {
        console.error('[Modules Service] Unexpected error:', error);
        return false;
    }
};

/**
 * Ativar múltiplos módulos de uma vez (útil no cadastro)
 */
export const activateModules = async (
    clinicaId: string,
    modulos: string[]
): Promise<boolean> => {
    try {
        const promises = modulos.map(modulo =>
            toggleModule(clinicaId, modulo, true)
        );

        const results = await Promise.all(promises);
        return results.every(r => r === true);
    } catch (error) {
        console.error('[Modules Service] Activate modules error:', error);
        return false;
    }
};
