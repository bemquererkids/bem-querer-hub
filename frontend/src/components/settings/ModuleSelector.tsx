import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent } from '../ui/card';
import {
    CheckCircleIcon
} from '@heroicons/react/24/outline';
import { Cpu, MessageSquare, Smartphone, Calendar, DollarSign } from 'lucide-react';

interface Module {
    id: string;
    name: string;
    description: string;
    icon: React.ComponentType<{ className?: string }>;
    color: string;
    bgColor: string;
    required?: boolean;
}

interface ModuleSelectorProps {
    selectedModules: string[];
    onChange: (modules: string[]) => void;
}

const modules: Module[] = [
    {
        id: 'clinicorp',
        name: 'CliniCorp',
        description: 'Sistema de gestão odontológica',
        icon: Cpu,
        color: 'text-blue-600 dark:text-blue-400',
        bgColor: 'bg-blue-50 dark:bg-blue-900/20',
    },
    {
        id: 'chatgpt',
        name: 'ChatGPT/IA',
        description: 'Assistente inteligente para atendimento',
        icon: MessageSquare,
        color: 'text-purple-600 dark:text-purple-400',
        bgColor: 'bg-purple-50 dark:bg-purple-900/20',
    },
    {
        id: 'whatsapp',
        name: 'WhatsApp Business',
        description: 'Integração com WhatsApp',
        icon: Smartphone,
        color: 'text-green-600 dark:text-green-400',
        bgColor: 'bg-green-50 dark:bg-green-900/20',
    },
    {
        id: 'agenda',
        name: 'Agenda Online',
        description: 'Agendamento online para pacientes',
        icon: Calendar,
        color: 'text-indigo-600 dark:text-indigo-400',
        bgColor: 'bg-indigo-50 dark:bg-indigo-900/20',
        required: true,
    },
    {
        id: 'financeiro',
        name: 'Financeiro',
        description: 'Controle financeiro e faturamento',
        icon: DollarSign,
        color: 'text-emerald-600 dark:text-emerald-400',
        bgColor: 'bg-emerald-50 dark:bg-emerald-900/20',
        required: true,
    },
];

export const ModuleSelector: React.FC<ModuleSelectorProps> = ({ selectedModules, onChange }) => {
    const toggleModule = (moduleId: string, required?: boolean) => {
        if (required) return; // Não permite desativar módulos obrigatórios

        if (selectedModules.includes(moduleId)) {
            onChange(selectedModules.filter(id => id !== moduleId));
        } else {
            onChange([...selectedModules, moduleId]);
        }
    };

    return (
        <div className="space-y-3">
            <div>
                <h3 className="text-base font-semibold text-zinc-900 dark:text-white mb-0.5">
                    Selecione os Módulos
                </h3>
                <p className="text-xs text-zinc-600 dark:text-zinc-400">
                    Escolha as integrações que você deseja habilitar
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
                {modules.map((module) => {
                    const isSelected = selectedModules.includes(module.id) || module.required;
                    const Icon = module.icon;

                    return (
                        <motion.div
                            key={module.id}
                            whileHover={{ scale: module.required ? 1 : 1.02 }}
                            whileTap={{ scale: module.required ? 1 : 0.98 }}
                        >
                            <Card
                                onClick={() => toggleModule(module.id, module.required)}
                                className={`
                                    relative cursor-pointer transition-all duration-200 border-2
                                    ${isSelected
                                        ? 'border-indigo-500 dark:border-indigo-600 bg-white dark:bg-zinc-900'
                                        : 'border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900/50'
                                    }
                                    ${module.required ? 'cursor-default' : 'hover:border-indigo-300 dark:hover:border-indigo-700'}
                                `}
                            >
                                <CardContent className="p-3">
                                    <div className="flex items-start gap-2.5">
                                        {/* Icon */}
                                        <div className={`
                                            flex-shrink-0 w-9 h-9 rounded-lg flex items-center justify-center transition-all
                                            ${isSelected ? module.bgColor : 'bg-zinc-200 dark:bg-zinc-800'}
                                        `}>
                                            <Icon className={`
                                                w-4 h-4 transition-all
                                                ${isSelected ? module.color : 'text-zinc-400 dark:text-zinc-600'}
                                            `} />
                                        </div>

                                        {/* Content */}
                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-center gap-2 mb-0.5">
                                                <h4 className={`
                                                    text-xs font-semibold transition-colors
                                                    ${isSelected ? 'text-zinc-900 dark:text-white' : 'text-zinc-500 dark:text-zinc-500'}
                                                `}>
                                                    {module.name}
                                                </h4>
                                                {module.required && (
                                                    <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-400 font-medium">
                                                        Padrão
                                                    </span>
                                                )}
                                            </div>
                                            <p className={`
                                                text-[11px] transition-colors
                                                ${isSelected ? 'text-zinc-600 dark:text-zinc-400' : 'text-zinc-400 dark:text-zinc-600'}
                                            `}>
                                                {module.description}
                                            </p>
                                        </div>

                                        {/* Checkbox */}
                                        <div className={`
                                            flex-shrink-0 w-4 h-4 rounded border-2 flex items-center justify-center transition-all
                                            ${isSelected
                                                ? 'bg-indigo-600 border-indigo-600'
                                                : 'bg-white dark:bg-zinc-800 border-zinc-300 dark:border-zinc-700'
                                            }
                                        `}>
                                            {isSelected && (
                                                <CheckCircleIcon className="w-3 h-3 text-white" />
                                            )}
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        </motion.div>
                    );
                })}
            </div>

            {/* Info */}
            <div className="mt-4 p-3 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg border border-indigo-200 dark:border-indigo-800">
                <p className="text-xs text-indigo-700 dark:text-indigo-400">
                    💡 Você pode ativar ou desativar módulos depois nas configurações
                </p>
            </div>
        </div>
    );
};
