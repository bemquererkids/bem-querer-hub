import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import * as modulesService from '../services/modulesService';

export interface UseModulesReturn {
    modules: modulesService.ClinicModule[];
    activeModules: string[];
    loading: boolean;
    isModuleActive: (moduleId: string) => boolean;
    toggleModule: (moduleId: string, active: boolean) => Promise<boolean>;
    refreshModules: () => Promise<void>;
}

export const useModules = (): UseModulesReturn => {
    const { user } = useAuth();
    const [modules, setModules] = useState<modulesService.ClinicModule[]>([]);
    const [activeModules, setActiveModules] = useState<string[]>([]);
    const [loading, setLoading] = useState(true);

    const loadModules = async () => {
        if (!user?.clinicId) {
            setLoading(false);
            return;
        }

        setLoading(true);
        try {
            const [allModules, active] = await Promise.all([
                modulesService.getClinicModules(user.clinicId),
                modulesService.getActiveModules(user.clinicId)
            ]);

            setModules(allModules);
            setActiveModules(active);
        } catch (error) {
            console.error('[useModules] Error loading modules:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadModules();
    }, [user?.clinicId]);

    const isModuleActive = (moduleId: string): boolean => {
        return activeModules.includes(moduleId);
    };

    const toggleModule = async (moduleId: string, active: boolean): Promise<boolean> => {
        if (!user?.clinicId) return false;

        const success = await modulesService.toggleModule(user.clinicId, moduleId, active);

        if (success) {
            await loadModules(); // Refresh modules after toggle
        }

        return success;
    };

    const refreshModules = async () => {
        await loadModules();
    };

    return {
        modules,
        activeModules,
        loading,
        isModuleActive,
        toggleModule,
        refreshModules
    };
};
