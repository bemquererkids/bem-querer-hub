
import React, { createContext, useContext, useState, useEffect } from 'react';
import * as authService from '../services/authService';

// Define User Type
export interface User {
    id: string;
    name: string;
    email: string;
    role: string;
    avatar?: string;
    clinicId?: string;
    clinicName?: string;
}

interface AuthContextType {
    user: User | null;
    isAuthenticated: boolean;
    login: (email: string, password?: string) => Promise<void>;
    logout: () => void;
    isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    // Check for persisted user on mount
    useEffect(() => {
        const storedUser = localStorage.getItem('nexus_user');
        if (storedUser) {
            try {
                setUser(JSON.parse(storedUser));
            } catch (e) {
                console.error("Failed to parse stored user", e);
                localStorage.removeItem('nexus_user');
            }
        }
        setIsLoading(false);
    }, []);

    const login = async (email: string, password?: string) => {
        setIsLoading(true);

        try {
            // Try real authentication first
            if (password) {
                const { user: authUser, error } = await authService.login(email, password);

                if (error) {
                    console.error('[AuthContext] Login error:', error);
                    alert(`Erro ao fazer login: ${error}`);
                    setIsLoading(false);
                    return;
                }

                if (authUser) {
                    const user: User = {
                        id: authUser.id,
                        name: authUser.name,
                        email: authUser.email,
                        role: authUser.role,
                        avatar: authUser.avatar,
                        clinicId: authUser.clinicId,
                        clinicName: authUser.clinicName
                    };

                    setUser(user);
                    localStorage.setItem('nexus_user', JSON.stringify(user));
                    setIsLoading(false);
                    return;
                }
            }

            // Fallback to mock for development (if no password provided)
            console.warn('[AuthContext] Using mock authentication');
            await new Promise(resolve => setTimeout(resolve, 1000));

            const mockUser: User = {
                id: '1',
                name: email.split('@')[0].toUpperCase(),
                email: email,
                role: 'Administrador',
                avatar: `https://ui-avatars.com/api/?name=${email.split('@')[0]}&background=6366f1&color=fff`,
                clinicName: 'Minha Clínica'
            };

            setUser(mockUser);
            localStorage.setItem('nexus_user', JSON.stringify(mockUser));
        } catch (error) {
            console.error('[AuthContext] Unexpected error:', error);
            alert('Erro inesperado ao fazer login');
        }

        setIsLoading(false);
    };

    const logout = () => {
        setUser(null);
        localStorage.removeItem('nexus_user');
    };

    return (
        <AuthContext.Provider value={{
            user,
            isAuthenticated: !!user,
            login,
            logout,
            isLoading
        }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
