import { supabase } from './supabase';

export interface UserProfile {
    id: string;
    name: string;
    email: string;
    role: string;
    avatar?: string;
    clinicId: string;
    clinicName: string;
}

export interface AuthResponse {
    user: UserProfile | null;
    error: string | null;
}

/**
 * Authenticate user with email and password
 */
export const login = async (email: string, password: string): Promise<AuthResponse> => {
    try {
        // 1. Authenticate with Supabase Auth
        const { data: authData, error: authError } = await supabase.auth.signInWithPassword({
            email,
            password,
        });

        if (authError) {
            console.error('[Auth Service] Login error:', authError);
            return { user: null, error: authError.message };
        }

        if (!authData.user) {
            return { user: null, error: 'Usuário não encontrado' };
        }

        // 2. Fetch user profile from profiles table
        const { data: profileData, error: profileError } = await supabase
            .from('perfis')
            .select(`
                id,
                nome_completo,
                cargo,
                avatar_url,
                clinica_id,
                clinicas (
                    nome_fantasia
                )
            `)
            .eq('id', authData.user.id)
            .single();

        if (profileError || !profileData) {
            console.error('[Auth Service] Profile fetch error:', profileError);
            return { user: null, error: 'Perfil não encontrado' };
        }

        // 3. Build user object
        const user: UserProfile = {
            id: profileData.id,
            name: profileData.nome_completo,
            email: authData.user.email || email,
            role: profileData.cargo,
            avatar: profileData.avatar_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(profileData.nome_completo)}&background=6366f1&color=fff`,
            clinicId: profileData.clinica_id,
            clinicName: (profileData.clinicas as any)?.nome_fantasia || 'Minha Clínica',
        };

        console.log('[Auth Service] Login successful:', user.name);
        return { user, error: null };

    } catch (error: any) {
        console.error('[Auth Service] Unexpected error:', error);
        return { user: null, error: error.message || 'Erro ao fazer login' };
    }
};

/**
 * Logout current user
 */
export const logout = async (): Promise<void> => {
    try {
        await supabase.auth.signOut();
        console.log('[Auth Service] Logout successful');
    } catch (error) {
        console.error('[Auth Service] Logout error:', error);
    }
};

/**
 * Get current authenticated user
 */
export const getCurrentUser = async (): Promise<UserProfile | null> => {
    try {
        // 1. Check if user is authenticated
        const { data: { user: authUser } } = await supabase.auth.getUser();

        if (!authUser) {
            return null;
        }

        // 2. Fetch profile
        const { data: profileData, error } = await supabase
            .from('perfis')
            .select(`
                id,
                nome_completo,
                cargo,
                avatar_url,
                clinica_id,
                clinicas (
                    nome_fantasia
                )
            `)
            .eq('id', authUser.id)
            .single();

        if (error || !profileData) {
            console.error('[Auth Service] Profile fetch error:', error);
            return null;
        }

        return {
            id: profileData.id,
            name: profileData.nome_completo,
            email: authUser.email || '',
            role: profileData.cargo,
            avatar: profileData.avatar_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(profileData.nome_completo)}&background=6366f1&color=fff`,
            clinicId: profileData.clinica_id,
            clinicName: (profileData.clinicas as any)?.nome_fantasia || 'Minha Clínica',
        };

    } catch (error) {
        console.error('[Auth Service] Get current user error:', error);
        return null;
    }
};

/**
 * Check if Supabase is configured
 */
export const isSupabaseConfigured = (): boolean => {
    const url = import.meta.env.VITE_SUPABASE_URL;
    const key = import.meta.env.VITE_SUPABASE_KEY;
    return !!(url && key && url !== 'seu-url-do-supabase-aqui');
};
