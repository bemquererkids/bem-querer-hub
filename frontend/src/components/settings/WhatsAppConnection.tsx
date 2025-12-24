import React, { useState, useEffect } from 'react';
import { QrCodeIcon, CheckCircleIcon, XCircleIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Button } from '../ui/button';
import { QRCodeSVG } from 'qrcode.react';

interface WhatsAppConnectionProps {
    clinicaId: string;
}

interface ConnectionStatus {
    connected: boolean;
    qrcode?: string;
    error?: string;
    instance?: {
        name?: string;
        phone?: string;
    };
}

export const WhatsAppConnection: React.FC<WhatsAppConnectionProps> = ({ clinicaId }) => {
    const [status, setStatus] = useState<ConnectionStatus | null>(null);
    const [loading, setLoading] = useState(false);
    const [qrCode, setQrCode] = useState<string | null>(null);
    const [polling, setPolling] = useState(false);

    // Verificar status da conexão
    const checkStatus = async () => {
        try {
            const response = await fetch('/api/integrations/whatsapp/status');
            const data = await response.json();
            setStatus(data);

            // Se conectado, parar polling
            if (data.connected) {
                setPolling(false);
                setQrCode(null);
            }
        } catch (error) {
            console.error('Erro ao verificar status:', error);
            setStatus({ connected: false, error: 'Erro ao verificar status' });
        }
    };

    // Gerar QR Code
    const generateQRCode = async () => {
        setLoading(true);
        try {
            const response = await fetch('/api/integrations/whatsapp/connect', {
                method: 'POST',
            });
            const data = await response.json();

            if (data.qrcode) {
                setQrCode(data.qrcode);
                setPolling(true); // Iniciar polling para verificar conexão
            } else if (data.error) {
                setStatus({ connected: false, error: data.error });
            }
        } catch (error) {
            console.error('Erro ao gerar QR Code:', error);
            setStatus({ connected: false, error: 'Erro ao gerar QR Code' });
        } finally {
            setLoading(false);
        }
    };

    // Polling para verificar se conectou
    useEffect(() => {
        if (polling) {
            const interval = setInterval(() => {
                checkStatus();
            }, 3000); // Verifica a cada 3 segundos

            return () => clearInterval(interval);
        }
    }, [polling]);

    // Verificar status inicial
    useEffect(() => {
        checkStatus();
    }, []);

    return (
        <Card className="bg-white dark:bg-card border border-zinc-200 dark:border-border">
            <CardHeader>
                <div className="flex items-center justify-between">
                    <div>
                        <CardTitle className="text-xl font-semibold text-zinc-900 dark:text-foreground">
                            WhatsApp Business
                        </CardTitle>
                        <CardDescription className="text-sm text-zinc-500 dark:text-muted-foreground mt-1">
                            Conecte sua conta do WhatsApp para enviar mensagens
                        </CardDescription>
                    </div>

                    {/* Status Badge */}
                    {status && (
                        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium ${status.connected
                            ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-400'
                            : 'bg-zinc-100 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400'
                            }`}>
                            {status.connected ? (
                                <>
                                    <CheckCircleIcon className="w-4 h-4" />
                                    Conectado
                                </>
                            ) : (
                                <>
                                    <XCircleIcon className="w-4 h-4" />
                                    Desconectado
                                </>
                            )}
                        </div>
                    )}
                </div>
            </CardHeader>

            <CardContent className="space-y-6">
                {/* Conectado */}
                {status?.connected && (
                    <div className="p-6 bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20 rounded-lg">
                        <div className="flex items-start gap-4">
                            <div className="p-3 bg-emerald-100 dark:bg-emerald-500/20 rounded-lg">
                                <CheckCircleIcon className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
                            </div>
                            <div className="flex-1">
                                <h3 className="text-lg font-semibold text-emerald-900 dark:text-emerald-300 mb-1">
                                    WhatsApp Conectado!
                                </h3>
                                <p className="text-sm text-emerald-700 dark:text-emerald-400 mb-3">
                                    Sua conta está ativa e pronta para enviar mensagens.
                                </p>
                                {status.instance?.phone && (
                                    <p className="text-xs font-mono text-emerald-600 dark:text-emerald-500">
                                        Número: {status.instance.phone}
                                    </p>
                                )}
                            </div>
                        </div>
                    </div>
                )}

                {/* QR Code */}
                {!status?.connected && qrCode && (
                    <div className="space-y-4">
                        <div className="p-6 bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-border rounded-lg">
                            <div className="flex flex-col items-center gap-4">
                                <div className="p-4 bg-white dark:bg-zinc-800 rounded-lg shadow-sm">
                                    <QRCodeSVG
                                        value={qrCode}
                                        size={256}
                                        level="H"
                                        includeMargin={true}
                                    />
                                </div>

                                <div className="text-center max-w-md">
                                    <h3 className="text-lg font-semibold text-zinc-900 dark:text-foreground mb-2">
                                        Escaneie o QR Code
                                    </h3>
                                    <ol className="text-sm text-zinc-600 dark:text-muted-foreground space-y-2 text-left">
                                        <li className="flex items-start gap-2">
                                            <span className="flex-shrink-0 w-5 h-5 bg-indigo-100 dark:bg-primary/10 text-indigo-600 dark:text-primary rounded-full flex items-center justify-center text-xs font-bold">1</span>
                                            <span>Abra o WhatsApp no seu celular</span>
                                        </li>
                                        <li className="flex items-start gap-2">
                                            <span className="flex-shrink-0 w-5 h-5 bg-indigo-100 dark:bg-primary/10 text-indigo-600 dark:text-primary rounded-full flex items-center justify-center text-xs font-bold">2</span>
                                            <span>Toque em <strong>Mais opções</strong> (⋮) e depois em <strong>Aparelhos conectados</strong></span>
                                        </li>
                                        <li className="flex items-start gap-2">
                                            <span className="flex-shrink-0 w-5 h-5 bg-indigo-100 dark:bg-primary/10 text-indigo-600 dark:text-primary rounded-full flex items-center justify-center text-xs font-bold">3</span>
                                            <span>Toque em <strong>Conectar um aparelho</strong></span>
                                        </li>
                                        <li className="flex items-start gap-2">
                                            <span className="flex-shrink-0 w-5 h-5 bg-indigo-100 dark:bg-primary/10 text-indigo-600 dark:text-primary rounded-full flex items-center justify-center text-xs font-bold">4</span>
                                            <span>Aponte a câmera para este QR Code</span>
                                        </li>
                                    </ol>
                                </div>

                                {polling && (
                                    <div className="flex items-center gap-2 text-sm text-zinc-500 dark:text-muted-foreground">
                                        <ArrowPathIcon className="w-4 h-4 animate-spin" />
                                        Aguardando conexão...
                                    </div>
                                )}
                            </div>
                        </div>

                        <Button
                            variant="outline"
                            onClick={generateQRCode}
                            disabled={loading}
                            className="w-full"
                        >
                            <ArrowPathIcon className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                            Gerar Novo QR Code
                        </Button>
                    </div>
                )}

                {/* Desconectado - Botão para conectar */}
                {!status?.connected && !qrCode && (
                    <div className="space-y-4">
                        <div className="p-6 bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-border rounded-lg text-center">
                            <div className="inline-flex p-4 bg-zinc-100 dark:bg-zinc-800 rounded-full mb-4">
                                <QrCodeIcon className="w-8 h-8 text-zinc-400 dark:text-zinc-500" />
                            </div>
                            <h3 className="text-lg font-semibold text-zinc-900 dark:text-foreground mb-2">
                                WhatsApp não conectado
                            </h3>
                            <p className="text-sm text-zinc-600 dark:text-muted-foreground mb-4">
                                Conecte sua conta do WhatsApp Business para começar a enviar mensagens automáticas para seus pacientes.
                            </p>
                        </div>

                        <Button
                            onClick={generateQRCode}
                            disabled={loading}
                            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white dark:bg-primary dark:hover:bg-primary/90"
                        >
                            {loading ? (
                                <>
                                    <ArrowPathIcon className="w-4 h-4 mr-2 animate-spin" />
                                    Gerando QR Code...
                                </>
                            ) : (
                                <>
                                    <QrCodeIcon className="w-4 h-4 mr-2" />
                                    Conectar WhatsApp
                                </>
                            )}
                        </Button>
                    </div>
                )}

                {/* Erro */}
                {status?.error && !status.connected && (
                    <div className="p-4 bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 rounded-lg">
                        <div className="flex items-start gap-3">
                            <XCircleIcon className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
                            <div className="flex-1">
                                <h4 className="text-sm font-semibold text-red-900 dark:text-red-300 mb-1">
                                    Erro na Conexão
                                </h4>
                                <p className="text-sm text-red-700 dark:text-red-400">
                                    {status.error}
                                </p>
                            </div>
                        </div>
                    </div>
                )}

                {/* Informações */}
                <div className="pt-4 border-t border-zinc-200 dark:border-border">
                    <h4 className="text-sm font-semibold text-zinc-900 dark:text-foreground mb-2">
                        ℹ️ Informações Importantes
                    </h4>
                    <ul className="text-xs text-zinc-600 dark:text-muted-foreground space-y-1">
                        <li>• Use uma conta WhatsApp Business para melhores resultados</li>
                        <li>• O QR Code expira em 60 segundos</li>
                        <li>• Mantenha o celular conectado à internet</li>
                        <li>• A conexão é mantida mesmo após fechar o navegador</li>
                    </ul>
                </div>
            </CardContent>
        </Card>
    );
};
