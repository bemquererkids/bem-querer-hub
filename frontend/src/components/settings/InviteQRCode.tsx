import React from 'react';
import { QRCodeSVG } from 'qrcode.react';
import { Button } from '../ui/button';
import { DocumentDuplicateIcon } from '@heroicons/react/24/outline';

interface InviteQRCodeProps {
    token?: string;
    codigo?: string;
    tipo: 'email' | 'codigo';
}

export const InviteQRCode: React.FC<InviteQRCodeProps> = ({ token, codigo, tipo }) => {
    // URL base da aplicação (em produção seria https://app.bemquerer.com)
    const baseUrl = window.location.origin;

    // Gera URL de cadastro com token ou código
    const signupUrl = tipo === 'email' && token
        ? `${baseUrl}/signup?token=${token}`
        : `${baseUrl}/signup?codigo=${codigo}`;

    const copiarLink = () => {
        navigator.clipboard.writeText(signupUrl);
        alert('Link copiado!');
    };

    return (
        <div className="mt-4 p-4 bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-indigo-900/20 dark:to-purple-900/20 rounded-lg border border-indigo-200 dark:border-indigo-800">
            <div className="flex flex-col items-center space-y-4">
                {/* QR Code */}
                <div className="bg-white p-4 rounded-lg shadow-sm">
                    <QRCodeSVG
                        value={signupUrl}
                        size={200}
                        level="H"
                        includeMargin={true}
                    />
                </div>

                {/* Informações */}
                <div className="text-center space-y-2 w-full">
                    <p className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
                        {tipo === 'email' ? '📧 Convite por Email' : '🎫 Código de Convite'}
                    </p>
                    {tipo === 'email' && token && (
                        <p className="text-xs text-zinc-500 dark:text-zinc-400 font-mono break-all">
                            Token: {token.substring(0, 16)}...
                        </p>
                    )}
                    {tipo === 'codigo' && codigo && (
                        <p className="text-lg font-mono font-bold text-indigo-600 dark:text-indigo-400">
                            {codigo}
                        </p>
                    )}
                </div>

                {/* Botão Copiar Link */}
                <Button
                    size="sm"
                    variant="outline"
                    onClick={copiarLink}
                    className="w-full"
                >
                    <DocumentDuplicateIcon className="w-4 h-4 mr-2" />
                    Copiar Link de Cadastro
                </Button>

                {/* Instruções */}
                <div className="text-xs text-zinc-500 dark:text-zinc-400 text-center space-y-1">
                    <p>✨ Escaneie o QR Code com o celular</p>
                    <p>ou compartilhe o link acima</p>
                </div>
            </div>
        </div>
    );
};
