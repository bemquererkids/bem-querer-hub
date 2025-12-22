import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Badge } from '../ui/badge';
import { QrCode, CheckCircle2, AlertCircle, RefreshCw, MessageSquare, Calendar, Key, Link as LinkIcon, Power } from 'lucide-react';
import { integrationService } from '../../services/api';

export const IntegrationsSettings: React.FC = () => {
    // Mock State for Integrations
    const [whatsappStatus, setWhatsappStatus] = useState<'connected' | 'disconnected' | 'connecting'>('connected');
    const [clinicorpStatus, setClinicorpStatus] = useState<'connected' | 'disconnected'>('disconnected');
    const [loading, setLoading] = useState(false);

    // Form States
    const [clinicorpClientId, setClinicorpClientId] = useState('');
    const [clinicorpSecret, setClinicorpSecret] = useState('');

    const handleConnectClinicorp = async () => {
        setLoading(true);
        try {
            await integrationService.connectClinicorp(clinicorpClientId, clinicorpSecret);
            setClinicorpStatus('connected');
            alert("Conectado com sucesso ao Clinicorp!");
        } catch (error) {
            console.error(error);
            alert("Falha na conexão. Verifique suas credenciais.");
        } finally {
            setLoading(false);
        }
    };

    const handleDisconnectWhatsapp = () => {
        if (confirm("Tem certeza? Isso irá parar o atendimento automático.")) {
            setWhatsappStatus('disconnected');
        }
    };

    const handleReconnectWhatsapp = () => {
        setWhatsappStatus('connecting');
        setTimeout(() => setWhatsappStatus('connected'), 2000);
    };

    return (
        <div className="p-6 max-w-5xl mx-auto space-y-8 animate-in fade-in duration-500">
            
            <div className="flex flex-col gap-1">
                <h2 className="text-2xl font-bold tracking-tight">Integrações</h2>
                <p className="text-muted-foreground">Gerencie a conexão com seus canais de atendimento e sistemas externos.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                
                {/* 1. WHATSAPP CARD */}
                <Card className="border-l-4 border-l-green-500 shadow-sm">
                    <CardHeader>
                        <div className="flex justify-between items-start">
                            <div className="flex items-center gap-2">
                                <div className="p-2 bg-green-100 rounded-lg">
                                    <MessageSquare className="w-6 h-6 text-green-600" />
                                </div>
                                <div>
                                    <CardTitle>WhatsApp (UazAPI)</CardTitle>
                                    <CardDescription>Canal principal de atendimento</CardDescription>
                                </div>
                            </div>
                            {whatsappStatus === 'connected' ? (
                                <span className="bg-green-100 text-green-700 text-xs px-2 py-1 rounded-full font-bold flex items-center gap-1">
                                    <CheckCircle2 className="w-3 h-3" /> Online
                                </span>
                            ) : (
                                <span className="bg-red-100 text-red-700 text-xs px-2 py-1 rounded-full font-bold flex items-center gap-1">
                                    <AlertCircle className="w-3 h-3" /> Offline
                                </span>
                            )}
                        </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        {whatsappStatus === 'connected' ? (
                            <div className="bg-slate-50 p-4 rounded-lg border border-slate-100">
                                <div className="flex items-center justify-between mb-2">
                                    <span className="text-sm text-slate-500">Sessão Ativa</span>
                                    <span className="text-sm font-medium text-slate-900">Bem-Querer Matriz</span>
                                </div>
                                <div className="flex items-center justify-between">
                                    <span className="text-sm text-slate-500">Número</span>
                                    <span className="text-sm font-medium text-slate-900">+55 11 99999-9999</span>
                                </div>
                            </div>
                        ) : (
                            <div className="flex flex-col items-center justify-center py-6 bg-slate-50 rounded-lg border border-dashed border-slate-300">
                                <QrCode className="w-16 h-16 text-slate-300 mb-2" />
                                <p className="text-sm text-slate-500 text-center max-w-[200px]">
                                    Escaneie o QR Code para conectar seu WhatsApp
                                </p>
                            </div>
                        )}
                    </CardContent>
                    <CardFooter className="justify-between border-t bg-slate-50/50 p-4">
                        {whatsappStatus === 'connected' ? (
                            <Button variant="destructive" size="sm" onClick={handleDisconnectWhatsapp} className="w-full sm:w-auto gap-2">
                                <Power className="w-4 h-4" /> Desconectar
                            </Button>
                        ) : (
                            <Button size="sm" onClick={handleReconnectWhatsapp} className="w-full sm:w-auto gap-2 bg-green-600 hover:bg-green-700 text-white">
                                <QrCode className="w-4 h-4" /> Gerar Novo QR Code
                            </Button>
                        )}
                    </CardFooter>
                </Card>

                {/* 2. CLINICORP CARD */}
                <Card className="border-l-4 border-l-blue-500 shadow-sm">
                    <CardHeader>
                        <div className="flex justify-between items-start">
                            <div className="flex items-center gap-2">
                                <div className="p-2 bg-blue-100 rounded-lg">
                                    <Calendar className="w-6 h-6 text-blue-600" />
                                </div>
                                <div>
                                    <CardTitle>Clinicorp</CardTitle>
                                    <CardDescription>Agendamento e Prontuário</CardDescription>
                                </div>
                            </div>
                            {clinicorpStatus === 'connected' ? (
                                <span className="bg-green-100 text-green-700 text-xs px-2 py-1 rounded-full font-bold flex items-center gap-1">
                                    <CheckCircle2 className="w-3 h-3" /> Sincronizado
                                </span>
                            ) : (
                                <span className="bg-slate-100 text-slate-600 text-xs px-2 py-1 rounded-full font-bold flex items-center gap-1">
                                    <LinkIcon className="w-3 h-3" /> Não vinculado
                                </span>
                            )}
                        </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        {clinicorpStatus === 'disconnected' ? (
                            <div className="space-y-3">
                                <div className="space-y-1">
                                    <Label htmlFor="client_id">Client ID / Usuário</Label>
                                    <Input 
                                        id="client_id" 
                                        placeholder="Ex: bemquerer ou ID da aplicação" 
                                        value={clinicorpClientId}
                                        onChange={(e) => setClinicorpClientId(e.target.value)}
                                        className="font-mono text-sm"
                                    />
                                </div>
                                <div className="space-y-1">
                                    <Label htmlFor="client_secret">Client Secret / Token API</Label>
                                    <Input 
                                        id="client_secret" 
                                        type="password" 
                                        placeholder="Ex: Token (8b6b...) ou Senha" 
                                        value={clinicorpSecret}
                                        onChange={(e) => setClinicorpSecret(e.target.value)}
                                    />
                                </div>
                                <div className="bg-blue-50 text-blue-700 text-xs p-3 rounded border border-blue-100">
                                    ℹ️ Solicite estas credenciais ao suporte da Clinicorp.
                                </div>
                            </div>
                        ) : (
                            <div className="space-y-4">
                                <div className="bg-slate-50 p-4 rounded-lg border border-slate-100">
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="text-sm text-slate-500">Clínica Vinculada</span>
                                        <span className="text-sm font-medium text-slate-900">Bem-Querer Matriz</span>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm text-slate-500">Última Sincronia</span>
                                        <span className="text-sm font-medium text-slate-900">Há 2 minutos</span>
                                    </div>
                                </div>
                            </div>
                        )}
                    </CardContent>
                    <CardFooter className="justify-between border-t bg-slate-50/50 p-4">
                         {clinicorpStatus === 'disconnected' ? (
                            <Button 
                                onClick={handleConnectClinicorp} 
                                disabled={loading}
                                className="w-full sm:w-auto gap-2"
                            >
                                {loading && <RefreshCw className="w-4 h-4 animate-spin" />}
                                Conectar Clinicorp
                            </Button>
                        ) : (
                             <Button 
                                variant="outline" 
                                onClick={() => setClinicorpStatus('disconnected')}
                                className="w-full sm:w-auto gap-2 text-destructive hover:text-destructive"
                            >
                                <LinkIcon className="w-4 h-4" /> Desvincular
                            </Button>
                        )}
                    </CardFooter>
                </Card>
            </div>
            
            {/* 3. GEMINI AI CARD (Simplified) */}
            <Card className="border-l-4 border-l-purple-500 shadow-sm opacity-80 hover:opacity-100 transition-opacity">
                 <CardHeader>
                    <div className="flex justify-between items-start">
                        <div className="flex items-center gap-2">
                            <div className="p-2 bg-purple-100 rounded-lg">
                                <Key className="w-6 h-6 text-purple-600" />
                            </div>
                            <div>
                                <CardTitle>Inteligência Artificial</CardTitle>
                                <CardDescription>Personalidade e Cérebro da Carol</CardDescription>
                            </div>
                        </div>
                        <span className="bg-purple-100 text-purple-700 text-xs px-2 py-1 rounded-full font-bold flex items-center gap-1">
                            Google Gemini 2.0
                        </span>
                    </div>
                </CardHeader>
                <CardContent>
                     <p className="text-sm text-muted-foreground">
                         A IA está configurada globalmente pelo administrador do sistema. Para ajustes de prompt ou personalidade, contate o suporte técnico.
                     </p>
                </CardContent>
            </Card>

        </div>
    );
};
