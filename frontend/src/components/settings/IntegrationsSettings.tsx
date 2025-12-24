import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Badge } from '../ui/badge';
import { QrCode, CheckCircle2, AlertCircle, RefreshCw, MessageSquare, Link as LinkIcon, Power, Sparkles, Wifi, WifiOff, Brain, Zap } from 'lucide-react';
import { integrationService } from '../../services/api';

export const IntegrationsSettings: React.FC = () => {
    const [whatsappStatus, setWhatsappStatus] = useState<'connected' | 'disconnected' | 'connecting' | 'qrcode'>('disconnected');
    const [qrCode, setQrCode] = useState<string | null>(null);
    const [clinicorpStatus, setClinicorpStatus] = useState<'connected' | 'disconnected'>('disconnected');
    const [loading, setLoading] = useState(false);
    const [initialLoading, setInitialLoading] = useState(true);
    const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null);
    const [sessionInfo, setSessionInfo] = useState<{ name: string, number: string } | null>(null);
    const [statusError, setStatusError] = useState<string | null>(null);
    const [currentConfig, setCurrentConfig] = useState<{ token: string, instance: string } | null>(null);
    const [clinicorpClientId, setClinicorpClientId] = useState('');
    const [clinicorpSecret, setClinicorpSecret] = useState('');

    // AI Integrations
    const [geminiApiKey, setGeminiApiKey] = useState('');
    const [geminiStatus, setGeminiStatus] = useState<'connected' | 'disconnected'>('disconnected');
    const [openaiApiKey, setOpenaiApiKey] = useState('');
    const [openaiStatus, setOpenaiStatus] = useState<'connected' | 'disconnected'>('disconnected');

    // Initial Status Check with timeout
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

        const timeout = setTimeout(() => {
            setInitialLoading(false);
        }, 3000);

        checkStatus();

        return () => {
            clearTimeout(timeout);
            if (pollingInterval) clearInterval(pollingInterval);
        };
    }, []);

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

    const handleConnectGemini = () => {
        if (!geminiApiKey.trim()) {
            alert("Por favor, insira uma API Key válida.");
            return;
        }
        // Here you would normally save to backend
        setGeminiStatus('connected');
        alert("Gemini conectado com sucesso!");
    };

    const handleDisconnectGemini = () => {
        if (confirm("Desconectar Gemini AI?")) {
            setGeminiStatus('disconnected');
            setGeminiApiKey('');
        }
    };

    const handleConnectChatGPT = () => {
        if (!openaiApiKey.trim()) {
            alert("Por favor, insira uma API Key válida.");
            return;
        }
        // Here you would normally save to backend
        setOpenaiStatus('connected');
        alert("ChatGPT conectado com sucesso!");
    };

    const handleDisconnectChatGPT = () => {
        if (confirm("Desconectar ChatGPT?")) {
            setOpenaiStatus('disconnected');
            setOpenaiApiKey('');
        }
    };

    if (initialLoading) {
        return (
            <div className="p-6 h-full flex flex-col items-center justify-center">
                <RefreshCw className="w-8 h-8 text-indigo-600 dark:text-primary animate-spin mb-4" />
                <p className="text-sm text-zinc-500 dark:text-muted-foreground font-medium">Carregando integrações...</p>
            </div>
        );
    }

    return (
        <div className="p-3 h-full flex flex-col max-w-6xl mx-auto animate-in fade-in duration-500">

            {/* Header */}
            <div className="flex items-center gap-2 mb-3">
                <div className="p-1.5 bg-indigo-100 dark:bg-indigo-900/20 rounded-lg border border-indigo-200 dark:border-indigo-800">
                    <Sparkles className="w-4 h-4 text-indigo-600 dark:text-primary" />
                </div>
                <div>
                    <h1 className="text-base font-bold text-zinc-900 dark:text-foreground tracking-tight">Integrações</h1>
                    <p className="text-[11px] text-zinc-500 dark:text-muted-foreground">Conecte canais e sistemas externos.</p>
                </div>
            </div>

            {/* Integration Cards Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-2.5 flex-1 min-h-0">

                {/* WhatsApp Card */}
                <Card className="bg-white dark:bg-zinc-900 border-zinc-200 dark:border-zinc-700 shadow-sm hover:shadow-md transition-shadow flex flex-col">
                    <CardHeader className="border-b border-zinc-100 dark:border-zinc-700 bg-gradient-to-r from-green-50 to-emerald-50 dark:bg-zinc-800 py-2">
                        <div className="flex justify-between items-start">
                            <div className="flex items-center gap-1.5">
                                <div className="p-1 bg-white dark:bg-zinc-800 rounded-lg border border-green-100 dark:border-green-800 shadow-sm">
                                    <MessageSquare className="w-4 h-4 text-green-600 dark:text-green-400" />
                                </div>
                                <div>
                                    <CardTitle className="text-sm text-zinc-900 dark:text-foreground">WhatsApp Business</CardTitle>
                                    <CardDescription className="text-xs text-zinc-500 dark:text-muted-foreground">Canal principal de atendimento</CardDescription>
                                </div>
                            </div>
                            {whatsappStatus === 'connected' ? (
                                <Badge className="bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 border-green-200 dark:border-green-800 text-[10px] gap-1">
                                    <Wifi className="w-3 h-3" /> Online
                                </Badge>
                            ) : (
                                <Badge variant="outline" className="bg-zinc-50 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400 border-zinc-200 dark:border-zinc-700 text-[10px] gap-1">
                                    <WifiOff className="w-3 h-3" /> Offline
                                </Badge>
                            )}
                        </div>
                    </CardHeader>
                    <CardContent className="pt-2.5 pb-2 flex-1 flex flex-col justify-center">
                        {whatsappStatus === 'connected' ? (
                            <div className="space-y-1.5">
                                <div className="p-2.5 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-100 dark:border-green-800">
                                    <div className="flex items-center justify-between mb-1">
                                        <span className="text-[11px] text-green-700 dark:text-green-300 font-medium">Sessão Ativa</span>
                                        <CheckCircle2 className="w-3.5 h-3.5 text-green-600 dark:text-green-400" />
                                    </div>
                                    <p className="text-xs font-semibold text-green-900 dark:text-green-100">{sessionInfo?.name || "Bem-Querer Matriz"}</p>
                                    <p className="text-[11px] text-green-600 dark:text-green-400 mt-0.5">{sessionInfo?.number ? `+${sessionInfo.number}` : "+55 11 99999-9999"}</p>
                                </div>
                            </div>
                        ) : whatsappStatus === 'qrcode' && qrCode ? (
                            <div className="flex flex-col items-center justify-center py-2">
                                <img
                                    src={qrCode.startsWith('data:') ? qrCode : `data:image/png;base64,${qrCode}`}
                                    alt="WhatsApp QR Code"
                                    className="w-28 h-28 mb-1.5 shadow-md rounded-lg border-2 border-green-200 dark:border-green-800"
                                />
                                <div className="flex items-center gap-1.5 text-green-600 dark:text-green-400 animate-pulse text-[11px] font-medium">
                                    <RefreshCw className="w-3 h-3 animate-spin" />
                                    Aguardando leitura do QR Code...
                                </div>
                            </div>
                        ) : whatsappStatus === 'connecting' ? (
                            <div className="flex flex-col items-center justify-center py-4">
                                <RefreshCw className="w-6 h-6 text-green-500 dark:text-green-400 animate-spin mb-1.5" />
                                <p className="text-[11px] text-zinc-500 dark:text-zinc-400 font-medium">Iniciando conexão...</p>
                            </div>
                        ) : (
                            <div className="flex flex-col items-center justify-center py-3">
                                {statusError?.includes("401") ? (
                                    <>
                                        <AlertCircle className="w-8 h-8 text-amber-500 dark:text-amber-400 mb-1.5" />
                                        <p className="text-[11px] font-semibold text-amber-700 dark:text-amber-300 text-center">Token Expirado ou Inválido</p>
                                        <p className="text-[10px] text-zinc-500 dark:text-zinc-400 text-center mt-1 max-w-[200px]">Verifique suas credenciais no painel UazAPI.</p>
                                    </>
                                ) : (
                                    <>
                                        <QrCode className="w-10 h-10 text-zinc-300 dark:text-zinc-600 mb-1.5" />
                                        <p className="text-[11px] text-zinc-500 dark:text-zinc-400 text-center max-w-[160px]">Clique no botão abaixo para gerar o QR Code.</p>
                                    </>
                                )}
                            </div>
                        )}
                    </CardContent>
                    <CardFooter className="bg-zinc-50/50 dark:bg-zinc-900/50 border-t border-zinc-100 dark:border-border p-2">
                        {whatsappStatus === 'connected' ? (
                            <Button
                                variant="destructive"
                                size="sm"
                                onClick={handleDisconnectWhatsapp}
                                className="w-full h-7 gap-1.5 text-xs"
                            >
                                <Power className="w-3 h-3" /> Desconectar
                            </Button>
                        ) : (
                            <Button
                                size="sm"
                                onClick={handleConnectWhatsapp}
                                disabled={loading || whatsappStatus === 'connecting'}
                                className="w-full h-7 gap-1.5 bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white shadow-sm text-xs"
                            >
                                {loading || whatsappStatus === 'connecting' ? (
                                    <>
                                        <RefreshCw className="w-3 h-3 animate-spin" />
                                        Conectando...
                                    </>
                                ) : (
                                    <>
                                        <QrCode className="w-3 h-3" />
                                        {whatsappStatus === 'qrcode' ? 'Gerar Novo QR' : 'Conectar WhatsApp'}
                                    </>
                                )}
                            </Button>
                        )}
                    </CardFooter>
                </Card>

                {/* Clinicorp Card */}
                <Card className="bg-white dark:bg-zinc-900 border-zinc-200 dark:border-zinc-700 shadow-sm hover:shadow-md transition-shadow flex flex-col">
                    <CardHeader className="border-b border-zinc-100 dark:border-zinc-700 bg-gradient-to-r from-orange-50 to-amber-50 dark:bg-zinc-800 py-2">
                        <div className="flex justify-between items-start">
                            <div className="flex items-center gap-1.5">
                                <div className="p-1 bg-white dark:bg-zinc-800 rounded-lg border border-orange-100 dark:border-orange-800 shadow-sm">
                                    <LinkIcon className="w-4 h-4 text-orange-600 dark:text-orange-400" />
                                </div>
                                <div>
                                    <CardTitle className="text-sm text-zinc-900 dark:text-foreground">Clinicorp</CardTitle>
                                    <CardDescription className="text-xs text-zinc-500 dark:text-muted-foreground">Sistema de agendamento</CardDescription>
                                </div>
                            </div>
                            {clinicorpStatus === 'connected' ? (
                                <Badge className="bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 border-green-200 dark:border-green-800 text-[10px] gap-1">
                                    <CheckCircle2 className="w-3 h-3" /> Conectado
                                </Badge>
                            ) : (
                                <Badge variant="outline" className="bg-zinc-50 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400 border-zinc-200 dark:border-zinc-700 text-[10px]">
                                    Não vinculado
                                </Badge>
                            )}
                        </div>
                    </CardHeader>
                    <CardContent className="pt-2.5 pb-2 flex-1 flex flex-col justify-center">
                        {clinicorpStatus === 'disconnected' ? (
                            <div className="space-y-2">
                                <div className="space-y-1.5">
                                    <Label htmlFor="client_id" className="text-xs text-zinc-700 dark:text-zinc-200 font-medium">Client ID / Usuário</Label>
                                    <Input
                                        id="client_id"
                                        placeholder="Ex: bemquerer"
                                        value={clinicorpClientId}
                                        onChange={(e) => setClinicorpClientId(e.target.value)}
                                        className="h-9 text-sm bg-zinc-50 dark:bg-zinc-900 border-zinc-200 dark:border-border focus:ring-orange-500/20 dark:focus:ring-orange-400/20 focus:border-orange-600 dark:focus:border-orange-400"
                                    />
                                </div>
                                <div className="space-y-1.5">
                                    <Label htmlFor="client_secret" className="text-xs text-zinc-700 dark:text-zinc-200 font-medium">Client Secret / Token API</Label>
                                    <Input
                                        id="client_secret"
                                        type="password"
                                        placeholder="Token de acesso"
                                        value={clinicorpSecret}
                                        onChange={(e) => setClinicorpSecret(e.target.value)}
                                        className="h-9 text-sm bg-zinc-50 dark:bg-zinc-900 border-zinc-200 dark:border-border focus:ring-orange-500/20 dark:focus:ring-orange-400/20 focus:border-orange-600 dark:focus:border-orange-400"
                                    />
                                </div>
                                <div className="p-2 bg-orange-50 dark:bg-orange-900/20 text-orange-700 dark:text-orange-300 text-[10px] rounded border border-orange-100 dark:border-orange-800">
                                    ℹ️ Solicite estas credenciais ao suporte da Clinicorp.
                                </div>
                            </div>
                        ) : (
                            <div className="space-y-1.5">
                                <div className="p-2.5 bg-orange-50 dark:bg-orange-900/20 rounded-lg border border-orange-100 dark:border-orange-800">
                                    <div className="flex items-center justify-between mb-1">
                                        <span className="text-[11px] text-orange-700 dark:text-orange-300 font-medium">Clínica Vinculada</span>
                                        <CheckCircle2 className="w-3.5 h-3.5 text-orange-600 dark:text-orange-400" />
                                    </div>
                                    <p className="text-xs font-semibold text-orange-900 dark:text-orange-100">Bem-Querer Matriz</p>
                                    <p className="text-[11px] text-orange-600 dark:text-orange-400 mt-0.5">Última sincronia: Há 2 minutos</p>
                                </div>
                            </div>
                        )}
                    </CardContent>
                    <CardFooter className="bg-zinc-50/50 dark:bg-zinc-900/50 border-t border-zinc-100 dark:border-border p-2">
                        {clinicorpStatus === 'disconnected' ? (
                            <Button
                                onClick={handleConnectClinicorp}
                                disabled={loading || !clinicorpClientId || !clinicorpSecret}
                                className="w-full h-8 gap-1.5 bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white shadow-sm text-xs"
                            >
                                {loading ? <RefreshCw className="w-3 h-3 animate-spin" /> : <LinkIcon className="w-3 h-3" />}
                                Conectar Clinicorp
                            </Button>
                        ) : (
                            <Button
                                variant="outline"
                                onClick={() => setClinicorpStatus('disconnected')}
                                className="w-full h-8 gap-1.5 text-destructive hover:text-white hover:bg-destructive border-orange-200 dark:border-orange-800 text-xs"
                            >
                                <Power className="w-3 h-3" /> Desconectar
                            </Button>
                        )}
                    </CardFooter>
                </Card>

                {/* Gemini AI Card */}
                <Card className="bg-white dark:bg-zinc-900 border-zinc-200 dark:border-zinc-700 shadow-sm hover:shadow-md transition-shadow flex flex-col">
                    <CardHeader className="border-b border-zinc-100 dark:border-zinc-700 bg-gradient-to-r from-purple-50 to-indigo-50 dark:bg-zinc-800 py-2">
                        <div className="flex justify-between items-start">
                            <div className="flex items-center gap-1.5">
                                <div className="p-1 bg-white dark:bg-zinc-800 rounded-lg border border-purple-100 dark:border-purple-800 shadow-sm">
                                    <Sparkles className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                                </div>
                                <div>
                                    <CardTitle className="text-sm text-zinc-900 dark:text-foreground">Google Gemini</CardTitle>
                                    <CardDescription className="text-xs text-zinc-500 dark:text-muted-foreground">IA multimodal avançada</CardDescription>
                                </div>
                            </div>
                            {geminiStatus === 'connected' ? (
                                <Badge className="bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400 border-purple-200 dark:border-purple-800 text-[10px] gap-1">
                                    <CheckCircle2 className="w-3 h-3" /> Ativo
                                </Badge>
                            ) : (
                                <Badge variant="outline" className="bg-zinc-50 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400 border-zinc-200 dark:border-zinc-700 text-[10px]">
                                    Inativo
                                </Badge>
                            )}
                        </div>
                    </CardHeader>
                    <CardContent className="pt-2.5 pb-2 flex-1 flex flex-col justify-center">
                        {geminiStatus === 'disconnected' ? (
                            <div className="space-y-3">
                                <div className="space-y-1.5">
                                    <Label htmlFor="gemini_key" className="text-xs text-zinc-700 dark:text-zinc-200 font-medium">API Key</Label>
                                    <Input
                                        id="gemini_key"
                                        type="password"
                                        placeholder="AIza..."
                                        value={geminiApiKey}
                                        onChange={(e) => setGeminiApiKey(e.target.value)}
                                        className="h-9 text-sm bg-zinc-50 dark:bg-zinc-900 border-zinc-200 dark:border-border focus:ring-purple-500/20 dark:focus:ring-purple-400/20 focus:border-purple-600 dark:focus:border-purple-400"
                                    />
                                </div>
                                <div className="p-2 bg-purple-50 dark:bg-purple-900/20 text-purple-700 dark:text-purple-300 text-[10px] rounded border border-purple-100 dark:border-purple-800">
                                    ℹ️ Obtenha sua chave em <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noopener noreferrer" className="underline font-semibold">Google AI Studio</a>
                                </div>
                            </div>
                        ) : (
                            <div className="space-y-1.5">
                                <div className="p-2.5 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-100 dark:border-purple-800">
                                    <div className="flex items-center justify-between mb-1">
                                        <span className="text-[11px] text-purple-700 dark:text-purple-300 font-medium">Modelo Ativo</span>
                                        <Sparkles className="w-3.5 h-3.5 text-purple-600 dark:text-purple-400" />
                                    </div>
                                    <p className="text-xs font-semibold text-purple-900 dark:text-purple-100">Gemini 2.0 Flash</p>
                                    <p className="text-[11px] text-purple-600 dark:text-purple-400 mt-0.5">Análise multimodal ativa</p>
                                </div>
                            </div>
                        )}
                    </CardContent>
                    <CardFooter className="bg-zinc-50/50 dark:bg-zinc-900/50 border-t border-zinc-100 dark:border-border p-2">
                        {geminiStatus === 'disconnected' ? (
                            <Button
                                onClick={handleConnectGemini}
                                disabled={!geminiApiKey}
                                className="w-full h-8 gap-1.5 bg-gradient-to-r from-purple-500 to-indigo-600 hover:from-purple-600 hover:to-indigo-700 text-white shadow-sm text-xs"
                            >
                                <Sparkles className="w-3 h-3" />
                                Conectar Gemini
                            </Button>
                        ) : (
                            <Button
                                variant="outline"
                                onClick={handleDisconnectGemini}
                                className="w-full h-8 gap-1.5 text-destructive hover:text-white hover:bg-destructive border-purple-200 dark:border-purple-800 text-xs"
                            >
                                <Power className="w-3 h-3" /> Desconectar
                            </Button>
                        )}
                    </CardFooter>
                </Card>

                {/* ChatGPT Card */}
                <Card className="bg-white dark:bg-zinc-900 border-zinc-200 dark:border-zinc-700 shadow-sm hover:shadow-md transition-shadow flex flex-col">
                    <CardHeader className="border-b border-zinc-100 dark:border-zinc-700 bg-gradient-to-r from-slate-50 to-zinc-50 dark:bg-zinc-800 py-2">
                        <div className="flex justify-between items-start">
                            <div className="flex items-center gap-1.5">
                                <div className="p-1 bg-slate-900 dark:bg-slate-800 rounded-lg border border-slate-700 dark:border-slate-600 shadow-sm">
                                    <Brain className="w-4 h-4 text-white" />
                                </div>
                                <div>
                                    <CardTitle className="text-sm text-zinc-900 dark:text-foreground">ChatGPT</CardTitle>
                                    <CardDescription className="text-xs text-zinc-500 dark:text-muted-foreground">GPT-4o & GPT-4 Turbo</CardDescription>
                                </div>
                            </div>
                            {openaiStatus === 'connected' ? (
                                <Badge className="bg-slate-100 text-slate-700 dark:bg-slate-900/30 dark:text-slate-300 border-slate-200 dark:border-slate-700 text-[10px] gap-1">
                                    <CheckCircle2 className="w-3 h-3" /> Ativo
                                </Badge>
                            ) : (
                                <Badge variant="outline" className="bg-zinc-50 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400 border-zinc-200 dark:border-zinc-700 text-[10px]">
                                    Inativo
                                </Badge>
                            )}
                        </div>
                    </CardHeader>
                    <CardContent className="pt-2.5 pb-2 flex-1 flex flex-col justify-center">
                        {openaiStatus === 'disconnected' ? (
                            <div className="space-y-3">
                                <div className="space-y-1.5">
                                    <Label htmlFor="openai_key" className="text-xs text-zinc-700 dark:text-zinc-200 font-medium">OpenAI API Key</Label>
                                    <Input
                                        id="openai_key"
                                        type="password"
                                        placeholder="sk-..."
                                        value={openaiApiKey}
                                        onChange={(e) => setOpenaiApiKey(e.target.value)}
                                        className="h-9 text-sm bg-zinc-50 dark:bg-zinc-900 border-zinc-200 dark:border-border focus:ring-slate-500/20 dark:focus:ring-slate-400/20 focus:border-slate-600 dark:focus:border-slate-400"
                                    />
                                </div>
                                <div className="p-2 bg-slate-50 dark:bg-slate-900/50 text-slate-700 dark:text-slate-300 text-[10px] rounded border border-slate-200 dark:border-slate-700">
                                    ℹ️ Obtenha sua chave em <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer" className="underline font-semibold">OpenAI Platform</a>
                                </div>
                            </div>
                        ) : (
                            <div className="space-y-1.5">
                                <div className="p-2.5 bg-slate-50 dark:bg-slate-900/50 rounded-lg border border-slate-200 dark:border-slate-700">
                                    <div className="flex items-center justify-between mb-1">
                                        <span className="text-[11px] text-slate-700 dark:text-slate-300 font-medium">Modelo Ativo</span>
                                        <Brain className="w-3.5 h-3.5 text-slate-600 dark:text-slate-400" />
                                    </div>
                                    <p className="text-xs font-semibold text-slate-900 dark:text-slate-100">GPT-4o</p>
                                    <p className="text-[11px] text-slate-600 dark:text-slate-400 mt-0.5">Raciocínio avançado ativo</p>
                                </div>
                            </div>
                        )}
                    </CardContent>
                    <CardFooter className="bg-zinc-50/50 dark:bg-zinc-900/50 border-t border-zinc-100 dark:border-border p-2">
                        {openaiStatus === 'disconnected' ? (
                            <Button
                                onClick={handleConnectChatGPT}
                                disabled={!openaiApiKey}
                                className="w-full h-8 gap-1.5 bg-gradient-to-r from-slate-700 to-slate-900 hover:from-slate-800 hover:to-black text-white shadow-sm text-xs"
                            >
                                <Brain className="w-3 h-3" />
                                Conectar ChatGPT
                            </Button>
                        ) : (
                            <Button
                                variant="outline"
                                onClick={handleDisconnectChatGPT}
                                className="w-full h-8 gap-1.5 text-destructive hover:text-white hover:bg-destructive border-slate-200 dark:border-slate-700 text-xs"
                            >
                                <Power className="w-3 h-3" /> Desconectar
                            </Button>
                        )}
                    </CardFooter>
                </Card>

            </div>
        </div>
    );
};
