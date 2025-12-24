import React from 'react';
import { motion } from 'framer-motion';
import { Button } from '../ui/button';
import { Card, CardContent } from '../ui/card';
import {
    ChatBubbleLeftRightIcon,
    QrCodeIcon,
    CheckCircleIcon,
    CogIcon,
    DevicePhoneMobileIcon,
    ArrowRightIcon
} from '@heroicons/react/24/outline';

export const WhatsAppEmptyState: React.FC = () => {
    const handleGoToSettings = () => {
        // Navigate to settings
        window.location.hash = '#/settings';
    };

    const steps = [
        {
            icon: CogIcon,
            title: 'Acesse as Configurações',
            description: 'Clique em "Configurações" no menu lateral e depois em "Integrações"',
        },
        {
            icon: QrCodeIcon,
            title: 'Escaneie o QR Code',
            description: 'Use seu WhatsApp Business para escanear o código QR exibido',
        },
        {
            icon: CheckCircleIcon,
            title: 'Comece a Conversar',
            description: 'Suas conversas aparecerão aqui automaticamente após a conexão',
        }
    ];

    return (
        <div className="h-full flex items-center justify-center p-4 bg-zinc-50 dark:bg-zinc-950">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4 }}
                className="max-w-2xl w-full"
            >
                <Card className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 shadow-sm">
                    <CardContent className="p-6 md:p-8">
                        {/* Icon */}
                        <div className="flex justify-center mb-6">
                            <div className="w-16 h-16 rounded-2xl bg-indigo-50 dark:bg-indigo-900/20 flex items-center justify-center">
                                <ChatBubbleLeftRightIcon className="w-8 h-8 text-indigo-600 dark:text-indigo-400" />
                            </div>
                        </div>

                        {/* Title */}
                        <div className="text-center mb-6">
                            <h2 className="text-2xl font-semibold text-zinc-900 dark:text-white mb-2">
                                Conecte seu WhatsApp
                            </h2>
                            <p className="text-zinc-600 dark:text-zinc-400">
                                Configure a integração para gerenciar suas conversas
                            </p>
                        </div>

                        {/* Steps */}
                        <div className="space-y-3 mb-6">
                            {steps.map((step, index) => (
                                <motion.div
                                    key={index}
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: index * 0.1 + 0.2 }}
                                    className="flex items-start gap-3 p-3 rounded-lg bg-zinc-50 dark:bg-zinc-800/50 border border-zinc-200 dark:border-zinc-700"
                                >
                                    <div className="flex-shrink-0 w-9 h-9 rounded-lg bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-700 flex items-center justify-center">
                                        <step.icon className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                                    </div>
                                    <div className="flex-1 pt-0.5">
                                        <h3 className="text-sm font-medium text-zinc-900 dark:text-white mb-1">
                                            {step.title}
                                        </h3>
                                        <p className="text-sm text-zinc-600 dark:text-zinc-400">
                                            {step.description}
                                        </p>
                                    </div>
                                    <div className="flex-shrink-0 w-6 h-6 rounded-full bg-indigo-50 dark:bg-indigo-900/20 flex items-center justify-center">
                                        <span className="text-xs font-semibold text-indigo-600 dark:text-indigo-400">
                                            {index + 1}
                                        </span>
                                    </div>
                                </motion.div>
                            ))}
                        </div>

                        {/* Info Box */}
                        <div className="mb-6 p-3 rounded-lg bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-200 dark:border-indigo-800">
                            <div className="flex items-start gap-3">
                                <DevicePhoneMobileIcon className="w-5 h-5 text-indigo-600 dark:text-indigo-400 flex-shrink-0 mt-0.5" />
                                <div>
                                    <h4 className="text-sm font-medium text-indigo-900 dark:text-indigo-300 mb-1">
                                        WhatsApp Business Necessário
                                    </h4>
                                    <p className="text-sm text-indigo-700 dark:text-indigo-400">
                                        Certifique-se de estar usando o WhatsApp Business para conectar sua conta.
                                        A integração é segura e suas conversas ficam sincronizadas em tempo real.
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* CTA Button */}
                        <Button
                            onClick={handleGoToSettings}
                            className="w-full h-11 bg-indigo-600 hover:bg-indigo-700 dark:bg-indigo-600 dark:hover:bg-indigo-700 text-white font-medium"
                        >
                            Ir para Configurações
                            <ArrowRightIcon className="w-4 h-4 ml-2" />
                        </Button>

                        {/* Footer */}
                        <div className="mt-4 pt-4 border-t border-zinc-200 dark:border-zinc-800">
                            <p className="text-xs text-center text-zinc-500 dark:text-zinc-500">
                                Conexão segura e criptografada • Sincronização em tempo real
                            </p>
                        </div>
                    </CardContent>
                </Card>
            </motion.div>
        </div>
    );
};
