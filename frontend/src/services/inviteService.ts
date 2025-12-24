import { supabase } from './supabase';

export interface Convite {
    id: string;
    clinica_id: string;
    tipo: 'email' | 'codigo';
    email?: string;
    token?: string;
    codigo?: string;
    cargo: string;
    uso_unico: boolean;
    vezes_usado: number;
    max_usos: number;
    status: 'pendente' | 'usado' | 'expirado' | 'cancelado';
    expira_em: string;
    usado_em?: string;
    criado_em: string;
}

export interface ConviteValidacao {
    valido: boolean;
    convite_id?: string;
    clinica_id?: string;
    cargo?: string;
    mensagem: string;
}

/**
 * Criar convite por email
 */
export const criarConviteEmail = async (
    email: string,
    cargo: string,
    clinicaId: string,
    criadoPor: string
): Promise<{ success: boolean; error?: string; convite?: Convite }> => {
    try {
        // Gerar token único
        const { data: tokenData, error: tokenError } = await supabase
            .rpc('gerar_token_convite');

        if (tokenError || !tokenData) {
            return { success: false, error: 'Erro ao gerar token' };
        }

        // Criar convite
        const { data, error } = await supabase
            .from('convites')
            .insert({
                clinica_id: clinicaId,
                tipo: 'email',
                email: email,
                token: tokenData,
                cargo: cargo,
                uso_unico: true,
                max_usos: 1,
                expira_em: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(), // 7 dias
                criado_por: criadoPor
            })
            .select()
            .single();

        if (error) {
            console.error('[Invite Service] Create email invite error:', error);
            return { success: false, error: error.message };
        }

        return { success: true, convite: data };
    } catch (error: any) {
        console.error('[Invite Service] Unexpected error:', error);
        return { success: false, error: error.message };
    }
};

/**
 * Gerar código de convite
 */
export const gerarCodigoConvite = async (
    cargo: string,
    maxUsos: number,
    clinicaId: string,
    criadoPor: string
): Promise<{ success: boolean; error?: string; convite?: Convite }> => {
    try {
        // Gerar código único
        const { data: codigoData, error: codigoError } = await supabase
            .rpc('gerar_codigo_convite');

        if (codigoError || !codigoData) {
            return { success: false, error: 'Erro ao gerar código' };
        }

        // Criar convite
        const { data, error } = await supabase
            .from('convites')
            .insert({
                clinica_id: clinicaId,
                tipo: 'codigo',
                codigo: codigoData,
                cargo: cargo,
                uso_unico: maxUsos === 1,
                max_usos: maxUsos,
                expira_em: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(), // 30 dias
                criado_por: criadoPor
            })
            .select()
            .single();

        if (error) {
            console.error('[Invite Service] Create code invite error:', error);
            return { success: false, error: error.message };
        }

        return { success: true, convite: data };
    } catch (error: any) {
        console.error('[Invite Service] Unexpected error:', error);
        return { success: false, error: error.message };
    }
};

/**
 * Validar convite (token ou código)
 */
export const validarConvite = async (
    token?: string,
    codigo?: string,
    email?: string
): Promise<ConviteValidacao> => {
    try {
        const { data, error } = await supabase
            .rpc('validar_convite', {
                p_token: token || null,
                p_codigo: codigo || null,
                p_email: email || null
            })
            .single();

        if (error) {
            console.error('[Invite Service] Validate error:', error);
            return { valido: false, mensagem: 'Erro ao validar convite' };
        }

        const result = data as any;
        return {
            valido: result.valido,
            convite_id: result.convite_id,
            clinica_id: result.clinica_id,
            cargo: result.cargo,
            mensagem: result.mensagem
        };
    } catch (error: any) {
        console.error('[Invite Service] Unexpected error:', error);
        return { valido: false, mensagem: 'Erro inesperado' };
    }
};

/**
 * Marcar convite como usado
 */
export const marcarConviteUsado = async (
    conviteId: string,
    usuarioId: string
): Promise<boolean> => {
    try {
        const { data, error } = await supabase
            .rpc('marcar_convite_usado', {
                p_convite_id: conviteId,
                p_usuario_id: usuarioId
            });

        if (error) {
            console.error('[Invite Service] Mark as used error:', error);
            return false;
        }

        return data === true;
    } catch (error) {
        console.error('[Invite Service] Unexpected error:', error);
        return false;
    }
};

/**
 * Listar convites da clínica
 */
export const listarConvites = async (
    clinicaId: string
): Promise<Convite[]> => {
    try {
        const { data, error } = await supabase
            .from('convites')
            .select('*')
            .eq('clinica_id', clinicaId)
            .order('criado_em', { ascending: false });

        if (error) {
            console.error('[Invite Service] List error:', error);
            return [];
        }

        return data || [];
    } catch (error) {
        console.error('[Invite Service] Unexpected error:', error);
        return [];
    }
};

/**
 * Cancelar convite
 */
export const cancelarConvite = async (
    conviteId: string
): Promise<boolean> => {
    try {
        const { error } = await supabase
            .from('convites')
            .update({ status: 'cancelado' })
            .eq('id', conviteId);

        if (error) {
            console.error('[Invite Service] Cancel error:', error);
            return false;
        }

        return true;
    } catch (error) {
        console.error('[Invite Service] Unexpected error:', error);
        return false;
    }
};
