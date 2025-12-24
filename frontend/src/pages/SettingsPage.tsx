import React from 'react';
import { WhatsAppConnection } from '../components/settings/WhatsAppConnection';
import {
    Cog6ToothIcon,
    ChatBubbleLeftRightIcon,
    BuildingOfficeIcon,
    UserGroupIcon
} from '@heroicons/react/24/outline';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';

export const SettingsPage: React.FC = () => {
    const [activeTab, setActiveTab] = React.useState('whatsapp');

    const tabs = [
        { id: 'whatsapp', name: 'WhatsApp', icon: ChatBubbleLeftRightIcon },
        { id: 'clinicorp', name: 'Clinicorp', icon: BuildingOfficeIcon },
        { id: 'users', name: 'Usuários', icon: UserGroupIcon },
        { id: 'general', name: 'Geral', icon: Cog6ToothIcon },
    ];

    return (
        <div className="min-h-screen bg-zinc-50 dark:bg-background">
            <div className="container mx-auto py-10 px-4 sm:px-6 lg:px-8">
                <div className="max-w-4xl mx-auto">
                    <div className="mb-10">
                        <h1 className="text-3xl font-bold text-zinc-900 dark:text-foreground mb-2">
                            Configurações
                        </h1>
                        <p className="text-zinc-600 dark:text-muted-foreground">
                            Gerencie as integrações e configurações da clínica
                        </p>
                    </div>

                    {/* Tabs */}
                    <div className="border-b border-zinc-200 dark:border-border mb-8">
                        <nav className="flex gap-8">
                            {tabs.map((tab) => {
                                const Icon = tab.icon;
                                const isActive = activeTab === tab.id;

                                return (
                                    <button
                                        key={tab.id}
                                        onClick={() => setActiveTab(tab.id)}
                                        className={`
                      flex items-center gap-2 pb-4 px-1 border-b-2 font-medium text-sm transition-colors
                      ${isActive
                                                ? 'border-indigo-500 dark:border-primary text-indigo-600 dark:text-primary'
                                                : 'border-transparent text-zinc-500 dark:text-muted-foreground hover:text-zinc-700 dark:hover:text-zinc-300'
                                            }
                    `}
                                    >
                                        <Icon className="w-5 h-5" />
                                        {tab.name}
                                    </button>
                                );
                            })}
                        </nav>
                    </div>

                    {/* Content */}
                    <div className="space-y-6">
                        {activeTab === 'whatsapp' && (
                            <WhatsAppConnection clinicaId="00000000-0000-0000-0000-000000000001" />
                        )}

                        {activeTab === 'clinicorp' && (
                            <Card>
                                <CardHeader>
                                    <CardTitle>Integração Clinicorp</CardTitle>
                                    <CardDescription>
                                        Configure a integração com o sistema Clinicorp
                                    </CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <p className="text-sm text-zinc-600 dark:text-muted-foreground">
                                        Em desenvolvimento...
                                    </p>
                                </CardContent>
                            </Card>
                        )}

                        {activeTab === 'users' && (
                            <Card>
                                <CardHeader>
                                    <CardTitle>Gerenciar Usuários</CardTitle>
                                    <CardDescription>
                                        Adicione e gerencie os usuários da clínica
                                    </CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <p className="text-sm text-zinc-600 dark:text-muted-foreground">
                                        Em desenvolvimento...
                                    </p>
                                </CardContent>
                            </Card>
                        )}

                        {activeTab === 'general' && (
                            <Card>
                                <CardHeader>
                                    <CardTitle>Configurações Gerais</CardTitle>
                                    <CardDescription>
                                        Personalize as configurações da clínica
                                    </CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <p className="text-sm text-zinc-600 dark:text-muted-foreground">
                                        Em desenvolvimento...
                                    </p>
                                </CardContent>
                            </Card>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};
