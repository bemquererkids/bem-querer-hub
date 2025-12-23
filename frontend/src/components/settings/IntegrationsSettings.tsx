import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Badge } from '../ui/badge';
import { QrCode, CheckCircle2, AlertCircle, RefreshCw, MessageSquare, Calendar, Key, Link as LinkIcon, Power } from 'lucide-react';
import { integrationService } from '../../services/api';

export const IntegrationsSettings: React.FC = () => {
    // State for Integrations
    const [whatsappStatus, setWhatsappStatus] = useState<'connected' | 'disconnected' | 'connecting' | 'qrcode'>('disconnected');
    const [qrCode, setQrCode] = useState<string | null>(null);
    const [clinicorpStatus, setClinicorpStatus] = useState<'connected' | 'disconnected'>('disconnected');
    const [loading, setLoading] = useState(false);
    const [initialLoading, setInitialLoading] = useState(true);
    const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null);
    const [sessionInfo, setSessionInfo] = useState<{ name: string, number: string } | null>(null);
    const [statusError, setStatusError] = useState<string | null>(null);
    const [showAdvanced, setShowAdvanced] = useState(false);
    const [currentConfig, setCurrentConfig] = useState<{ token: string, instance: string } | null>(null);

    // Initial Status Check
    React.useEffect(() => {
        const checkStatus = async () => {
            try {
                const status = await integrationService.getWhatsAppStatus();
                if (status.status?.connected) {
                    setWhatsappStatus('connected');
                    setSessionInfo({
                        name: status.instance?.profileName || status.instance?.name || "Instância conectada",
                        number: status.instance?.owner || status.status?.jid?.split(':')[0] || "Desconhecido"
                    });
                    setStatusError(null);
                } else {
                    setWhatsappStatus('disconnected');
                    if (status.error) setStatusError(status.error);
                }

                // Always capture current backend config for debugging
                if (status.config) {
                    setCurrentConfig(status.config);
                }
            } catch (error) {
                console.error("Failed to check initial status:", error);
                setWhatsappStatus('disconnected');
            } finally {
                setInitialLoading(false);
            }
        };
        checkStatus();

        return () => {
            if (pollingInterval) clearInterval(pollingInterval);
        };
    }, []);

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
            if (pollingInterval) clearInterval(pollingInterval);
            setWhatsappStatus('disconnected');
            setQrCode(null);
        }
    };

    const startPollingStatus = () => {
        const interval = setInterval(async () => {
            try {
                const status = await integrationService.getWhatsAppStatus();
                if (status.status?.connected) {
                    setWhatsappStatus('connected');
                    setSessionInfo({
                        name: status.instance?.profileName || status.instance?.name || "Instância conectada",
                        number: status.instance?.owner || status.status?.jid?.split(':')[0] || "Desconhecido"
                    });
                    setStatusError(null);
                    if (interval) clearInterval(interval);
                } else if (status.status_code === 401) {
                    // If we get 401 during polling, it means the session died or token is invalid
                    setWhatsappStatus('disconnected');
                    setStatusError(status.error);
                    if (interval) clearInterval(interval);
                }
            } catch (error) {
                console.error("Polling error:", error);
            }
        }, 5000);
        setPollingInterval(interval);
    };

    const handleConnectWhatsapp = async () => {
        setLoading(true);
        setWhatsappStatus('connecting');
        try {
            const result = await integrationService.connectWhatsApp();
            if (result.qrcode) {
                setQrCode(result.qrcode);
                setWhatsappStatus('qrcode');
                startPollingStatus();
            } else if (result.status?.connected) {
                setWhatsappStatus('connected');
            }
        } catch (error: any) {
            console.error("Connection error:", error);
            setWhatsappStatus('disconnected');

            const is503 = error.response?.status === 503;
            if (is503) {
                alert("Servidor UazAPI temporariamente offline ou instável (Erro 503). Por favor, tente novamente em alguns instantes.");
            } else {
                alert("Erro ao conectar WhatsApp. Verifique sua rede ou tente novamente.");
            }
        } finally {
            setLoading(false);
        }
    };

    if (initialLoading) {
        return (
            <div className="p-6 max-w-5xl mx-auto flex flex-col items-center justify-center min-h-[400px]">
                <RefreshCw className="w-8 h-8 text-cyan-500 animate-spin mb-4" />
                <p className="text-slate-500 font-medium">Carregando integrações...</p>
            </div>
        );
    }

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
                                    <span className="text-sm font-medium text-slate-900">{sessionInfo?.name || "Bem-Querer Matriz"}</span>
                                </div>
                                <div className="flex items-center justify-between">
                                    <span className="text-sm text-slate-500">Número</span>
                                    <span className="text-sm font-medium text-slate-900">
                                        {sessionInfo?.number ? `+${sessionInfo.number}` : "+55 11 99999-9999"}
                                    </span>
                                </div>
                            </div>
                        ) : whatsappStatus === 'qrcode' && qrCode ? (
                            <div className="flex flex-col items-center justify-center py-6 bg-white rounded-lg border-2 border-dashed border-cyan-200 animate-in zoom-in duration-300">
                                <img
                                    src={qrCode.startsWith('data:') ? qrCode : `data:image/png;base64,${qrCode}`}
                                    alt="WhatsApp QR Code"
                                    className="w-48 h-48 mb-4 shadow-md rounded-md border border-slate-100"
                                />
                                <div className="flex items-center gap-2 text-cyan-600 animate-pulse text-sm font-medium">
                                    <RefreshCw className="w-4 h-4 animate-spin" />
                                    Aguardando leitura do QR Code...
                                </div>
                            </div>
                        ) : whatsappStatus === 'connecting' ? (
                            <div className="flex flex-col items-center justify-center py-12 bg-slate-50 rounded-lg border border-slate-200">
                                <RefreshCw className="w-10 h-10 text-cyan-500 animate-spin mb-4" />
                                <p className="text-sm text-slate-500 font-medium">Iniciando conexão...</p>
                            </div>
                        ) : (
                            <div className="flex flex-col items-center justify-center py-8 bg-slate-50 rounded-lg border border-dashed border-slate-300">
                                {statusError?.includes("401") ? (
                                    <>
                                        <AlertCircle className="w-12 h-12 text-amber-500 mb-2" />
                                        <p className="text-sm font-semibold text-amber-700 text-center px-4">
                                            Token Expirado ou Inválido
                                        </p>
                                        <p className="text-xs text-slate-500 text-center px-6 mt-1">
                                            A conexão com a UazAPI falhou. Por favor, verifique suas credenciais no painel ou gere um novo QR Code.
                                        </p>
                                    </>
                                ) : (
                                    <>
                                        <QrCode className="w-16 h-16 text-slate-300 mb-2" />
                                        <p className="text-sm text-slate-500 text-center max-w-[200px]">
                                            Clique no botão abaixo para gerar o QR Code.
                                        </p>
                                    </>
                                )}
                            </div>
                        )}

                        {/* Advanced Config Debug */}
                        <div className="pt-2 border-t mt-4">
                            <button
                                onClick={() => setShowAdvanced(!showAdvanced)}
                                className="text-[10px] text-slate-400 hover:text-slate-600 transition-colors flex items-center gap-1"
                            >
                                <Key className="w-3 h-3" />
                                {showAdvanced ? 'Esconder Configuração' : 'Ver Configuração Técnica'}
                            </button>
                            {showAdvanced && currentConfig && (
                                <div className="mt-2 p-2 bg-slate-900 rounded text-[10px] font-mono text-slate-300 overflow-x-auto">
                                    <div className="flex justify-between border-b border-slate-700 pb-1 mb-1">
                                        <span>Instância:</span>
                                        <span className="text-cyan-400">{currentConfig.instance}</span>
                                    </div>
                                    <div className="flex flex-col gap-1">
                                        <span>Token Atual (no .env):</span>
                                        <span className="text-amber-400 break-all">{currentConfig.token}</span>
                                    </div>
                                    <p className="mt-2 text-slate-500 italic">
                                        Se o token acima for diferente do seu painel UazAPI, atualize seu arquivo .env.
                                    </p>
                                </div>
                            )}
                        </div>
                    </CardContent>
                    <CardFooter className="justify-between border-t bg-slate-50/50 p-4">
                        {whatsappStatus === 'connected' ? (
                            <Button variant="destructive" size="sm" onClick={handleDisconnectWhatsapp} className="w-full sm:w-auto gap-2">
                                <Power className="w-4 h-4" /> Desconectar Sessão
                            </Button>
                        ) : (
                            <Button
                                size="sm"
                                onClick={handleConnectWhatsapp}
                                disabled={loading || whatsappStatus === 'connecting'}
                                className="w-full sm:w-auto gap-2 bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white shadow-lg shadow-green-500/30"
                            >
                                {loading || whatsappStatus === 'connecting' ? (
                                    <>
                                        <RefreshCw className="w-4 h-4 animate-spin" />
                                        <span>Conectando...</span>
                                    </>
                                ) : (
                                    <>
                                        <QrCode className="w-4 h-4" />
                                        <span>{whatsappStatus === 'qrcode' ? 'Gerar Outro QR Code' : 'Conectar WhatsApp'}</span>
                                    </>
                                )}
                            </Button>
                        )}
                    </CardFooter>
                </Card>

                {/* 2. CLINICORP CARD */}
                <Card className="border-l-4 border-l-orange-500 shadow-sm">
                    <CardHeader>
                        <div className="flex justify-between items-start">
                            <div className="flex items-center gap-2">
                                <div className="p-1 bg-white rounded-lg border border-orange-100 shadow-sm overflow-hidden flex items-center justify-center w-10 h-10">
                                    <img
                                        src="/assets/clinicorp-logo.png"
                                        alt="Clinicorp Logo"
                                        className="w-full h-full object-contain"
                                    />
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
                                        className="font-mono text-sm focus:ring-orange-500"
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
                                        className="focus:ring-orange-500"
                                    />
                                </div>
                                <div className="bg-orange-50 text-orange-700 text-xs p-3 rounded border border-orange-100">
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
                                className="w-full sm:w-auto gap-2 bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white shadow-lg shadow-orange-500/30 font-bold"
                            >
                                {loading && <RefreshCw className="w-4 h-4 animate-spin" />}
                                Conectar Clinicorp
                            </Button>
                        ) : (
                            <Button
                                variant="outline"
                                onClick={() => setClinicorpStatus('disconnected')}
                                className="w-full sm:w-auto gap-2 text-destructive hover:text-destructive border-orange-200"
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
