import React, { useEffect, useState } from 'react';
import { useModules } from '../../hooks/useModules';
import { ModuleSelector } from './ModuleSelector';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { CheckCircleIcon } from '@heroicons/react/24/outline';

export const ModulesSettingsPage: React.FC = () => {
    const { modules, activeModules, loading, toggleModule, refreshModules } = useModules();
    const [selectedModules, setSelectedModules] = useState<string[]>([]);
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        setSelectedModules(activeModules);
    }, [activeModules]);

    const handleSave = async () => {
        setSaving(true);

        // Determinar quais módulos foram ativados/desativados
        const toActivate = selectedModules.filter(m => !activeModules.includes(m));
        const toDeactivate = activeModules.filter(m => !selectedModules.includes(m));

        try {
            // Ativar novos módulos
            for (const moduleId of toActivate) {
                await toggleModule(moduleId, true);
            }

            // Desativar módulos removidos
            for (const moduleId of toDeactivate) {
                await toggleModule(moduleId, false);
            }

            await refreshModules();
            alert('Módulos atualizados com sucesso!');
        } catch (error) {
            console.error('Error saving modules:', error);
            alert('Erro ao salvar módulos');
        } finally {
            setSaving(false);
        }
    };

    const hasChanges = JSON.stringify(selectedModules.sort()) !== JSON.stringify(activeModules.sort());

    if (loading) {
        return (
            <div className="p-3 max-w-4xl mx-auto">
                <div className="flex items-center justify-center h-64">
                    <p className="text-zinc-500 dark:text-zinc-400">Carregando módulos...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="p-3 max-w-4xl mx-auto space-y-3">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-semibold text-zinc-900 dark:text-white">Módulos e Integrações</h1>
                <p className="text-sm text-zinc-600 dark:text-zinc-400 mt-0.5">
                    Gerencie as funcionalidades habilitadas para sua clínica
                </p>
            </div>

            {/* Module Selector */}
            <Card className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800">
                <CardHeader className="pb-2 pt-3 px-3">
                    <CardTitle className="text-sm">Módulos Disponíveis</CardTitle>
                    <CardDescription className="text-xs">
                        Selecione os módulos que deseja utilizar
                    </CardDescription>
                </CardHeader>
                <CardContent className="px-3 pb-3">
                    <ModuleSelector
                        selectedModules={selectedModules}
                        onChange={setSelectedModules}
                    />
                </CardContent>
            </Card>

            {/* Save Button */}
            {hasChanges && (
                <div className="flex items-center justify-end gap-3 p-3 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg border border-indigo-200 dark:border-indigo-800">
                    <p className="text-sm text-indigo-700 dark:text-indigo-400 flex-1">
                        Você tem alterações não salvas
                    </p>
                    <Button
                        variant="outline"
                        onClick={() => setSelectedModules(activeModules)}
                        className="h-9"
                    >
                        Cancelar
                    </Button>
                    <Button
                        onClick={handleSave}
                        disabled={saving}
                        className="h-9 bg-indigo-600 hover:bg-indigo-700 dark:bg-indigo-600 dark:hover:bg-indigo-700"
                    >
                        {saving ? 'Salvando...' : 'Salvar Alterações'}
                    </Button>
                </div>
            )}

            {/* Active Modules Summary */}
            <Card className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800">
                <CardHeader className="pb-3 pt-4 px-4">
                    <CardTitle className="text-base">Módulos Ativos</CardTitle>
                    <CardDescription className="text-xs">
                        Funcionalidades habilitadas atualmente
                    </CardDescription>
                </CardHeader>
                <CardContent className="px-4 pb-4">
                    {activeModules.length > 0 ? (
                        <div className="space-y-2">
                            {modules
                                .filter(m => m.ativo)
                                .map(module => (
                                    <div
                                        key={module.id}
                                        className="flex items-center gap-2 p-2 rounded-lg bg-zinc-50 dark:bg-zinc-800/50"
                                    >
                                        <CheckCircleIcon className="w-4 h-4 text-green-600 dark:text-green-400" />
                                        <span className="text-sm text-zinc-700 dark:text-zinc-300 capitalize">
                                            {module.modulo}
                                        </span>
                                        {module.configurado && (
                                            <span className="text-xs px-2 py-0.5 rounded-full bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400">
                                                Configurado
                                            </span>
                                        )}
                                    </div>
                                ))}
                        </div>
                    ) : (
                        <p className="text-sm text-zinc-500 dark:text-zinc-400 text-center py-4">
                            Nenhum módulo ativo
                        </p>
                    )}
                </CardContent>
            </Card>
        </div>
    );
};
