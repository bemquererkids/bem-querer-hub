import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import * as inviteService from '../../services/inviteService';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import {
    EnvelopeIcon,
    TicketIcon,
    CheckCircleIcon,
    XCircleIcon,
    ClockIcon,
    DocumentDuplicateIcon,
    ShieldCheckIcon,
    UserIcon
} from '@heroicons/react/24/outline';

export const InviteManagementPage: React.FC = () => {
    const { user } = useAuth();
    const [loading, setLoading] = useState(false);
    const [convites, setConvites] = useState<inviteService.Convite[]>([]);

    // Form states
    const [emailConvite, setEmailConvite] = useState('');
    const [cargoEmail, setCargoEmail] = useState('usuario');
    const [cargoCodigo, setCargoCodigo] = useState('usuario');
    const [maxUsos, setMaxUsos] = useState(1);
    const [codigoGerado, setCodigoGerado] = useState('');

    useEffect(() => {
        if (user?.clinicId) {
            carregarConvites();
        }
    }, [user]);

    const carregarConvites = async () => {
        if (!user?.clinicId) return;
        const lista = await inviteService.listarConvites(user.clinicId);
        setConvites(lista);
    };

    const handleCriarConviteEmail = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!user?.id || !user?.clinicId) return;

        setLoading(true);
        const result = await inviteService.criarConviteEmail(
            emailConvite,
            cargoEmail,
            user.clinicId,
            user.id
        );

        if (result.success) {
            alert(`Convite criado! Token: ${result.convite?.token}\n\nEm produção, enviaríamos um email para ${emailConvite}`);
            setEmailConvite('');
            carregarConvites();
        } else {
            alert(`Erro: ${result.error}`);
        }
        setLoading(false);
    };

    const handleGerarCodigo = async () => {
        if (!user?.id || !user?.clinicId) return;

        setLoading(true);
        const result = await inviteService.gerarCodigoConvite(
            cargoCodigo,
            maxUsos,
            user.clinicId,
            user.id
        );

        if (result.success && result.convite?.codigo) {
            setCodigoGerado(result.convite.codigo);
            carregarConvites();
        } else {
            alert(`Erro: ${result.error}`);
        }
        setLoading(false);
    };

    const handleCancelar = async (id: string) => {
        if (!confirm('Cancelar este convite?')) return;

        const success = await inviteService.cancelarConvite(id);
        if (success) {
            alert('Convite cancelado!');
            carregarConvites();
        } else {
            alert('Erro ao cancelar convite');
        }
    };

    const copiarCodigo = () => {
        navigator.clipboard.writeText(codigoGerado);
        alert('Código copiado!');
    };

    const getStatusBadge = (status: string) => {
        const styles = {
            pendente: 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-900/20 dark:text-amber-400 dark:border-amber-800',
            usado: 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-900/20 dark:text-emerald-400 dark:border-emerald-800',
            expirado: 'bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-900/20 dark:text-rose-400 dark:border-rose-800',
            cancelado: 'bg-zinc-50 text-zinc-600 border-zinc-200 dark:bg-zinc-900/20 dark:text-zinc-400 dark:border-zinc-800'
        };
        return styles[status as keyof typeof styles] || styles.pendente;
    };

    const getPermissionIcon = (cargo: string) => {
        return cargo === 'admin' ? ShieldCheckIcon : UserIcon;
    };

    return (
        <div className="p-3 max-w-7xl mx-auto space-y-3">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-semibold text-zinc-900 dark:text-white">Gerenciar Acessos</h1>
                <p className="text-sm text-zinc-600 dark:text-zinc-400 mt-0.5">
                    Controle quem pode se cadastrar na plataforma
                </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
                {/* Convite por Email */}
                <Card className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800">
                    <CardHeader className="pb-2 pt-3 px-3">
                        <div className="flex items-center gap-2 mb-1">
                            <div className="w-8 h-8 rounded-lg bg-indigo-50 dark:bg-indigo-900/20 flex items-center justify-center">
                                <EnvelopeIcon className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                            </div>
                            <div>
                                <CardTitle className="text-sm">Convidar por Email</CardTitle>
                                <CardDescription className="text-xs">Envie um convite personalizado</CardDescription>
                            </div>
                        </div>
                    </CardHeader>
                    <CardContent className="px-3 pb-3">
                        <form onSubmit={handleCriarConviteEmail} className="space-y-2.5">
                            <div>
                                <Label htmlFor="email" className="text-xs text-zinc-700 dark:text-zinc-300">Email</Label>
                                <Input
                                    id="email"
                                    type="email"
                                    value={emailConvite}
                                    onChange={(e) => setEmailConvite(e.target.value)}
                                    placeholder="usuario@exemplo.com"
                                    required
                                    className="mt-1 h-8 text-sm bg-white dark:bg-zinc-800 border-zinc-200 dark:border-zinc-700"
                                />
                            </div>
                            <div>
                                <Label htmlFor="cargo-email" className="text-xs text-zinc-700 dark:text-zinc-300">Permissão</Label>
                                <select
                                    id="cargo-email"
                                    value={cargoEmail}
                                    onChange={(e) => setCargoEmail(e.target.value)}
                                    className="mt-1 w-full h-8 px-2 rounded-md border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 text-xs"
                                >
                                    <option value="admin">Admin (Acesso Total)</option>
                                    <option value="usuario">Usuário (Acesso Limitado)</option>
                                </select>
                            </div>
                            <Button type="submit" disabled={loading} className="w-full h-8 text-sm bg-indigo-600 hover:bg-indigo-700 dark:bg-indigo-600 dark:hover:bg-indigo-700">
                                {loading ? 'Criando...' : 'Criar Convite'}
                            </Button>
                        </form>
                    </CardContent>
                </Card>

                {/* Gerar Código */}
                <Card className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800">
                    <CardHeader className="pb-2 pt-3 px-3">
                        <div className="flex items-center gap-2 mb-1">
                            <div className="w-8 h-8 rounded-lg bg-purple-50 dark:bg-purple-900/20 flex items-center justify-center">
                                <TicketIcon className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                            </div>
                            <div>
                                <CardTitle className="text-sm">Gerar Código</CardTitle>
                                <CardDescription className="text-xs">Código para compartilhar manualmente</CardDescription>
                            </div>
                        </div>
                    </CardHeader>
                    <CardContent className="px-3 pb-3 space-y-2.5">
                        <div>
                            <Label htmlFor="cargo-codigo" className="text-xs text-zinc-700 dark:text-zinc-300">Permissão</Label>
                            <select
                                id="cargo-codigo"
                                value={cargoCodigo}
                                onChange={(e) => setCargoCodigo(e.target.value)}
                                className="mt-1 w-full h-8 px-2 rounded-md border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 text-xs"
                            >
                                <option value="admin">Admin (Acesso Total)</option>
                                <option value="usuario">Usuário (Acesso Limitado)</option>
                            </select>
                        </div>
                        <div>
                            <Label htmlFor="max-usos" className="text-xs text-zinc-700 dark:text-zinc-300">Usos Permitidos</Label>
                            <select
                                id="max-usos"
                                value={maxUsos}
                                onChange={(e) => setMaxUsos(Number(e.target.value))}
                                className="mt-1 w-full h-8 px-2 rounded-md border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 text-xs"
                            >
                                <option value="1">1 uso</option>
                                <option value="5">5 usos</option>
                                <option value="10">10 usos</option>
                                <option value="999">Ilimitado</option>
                            </select>
                        </div>
                        <Button onClick={handleGerarCodigo} disabled={loading} className="w-full h-8 text-sm bg-purple-600 hover:bg-purple-700 dark:bg-purple-600 dark:hover:bg-purple-700">
                            {loading ? 'Gerando...' : 'Gerar Código'}
                        </Button>

                        {codigoGerado && (
                            <div className="mt-2 p-2.5 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg border border-indigo-200 dark:border-indigo-800">
                                <p className="text-xs text-zinc-600 dark:text-zinc-400 mb-1.5">Código gerado:</p>
                                <div className="flex items-center gap-2">
                                    <code className="flex-1 text-sm font-mono font-semibold text-indigo-600 dark:text-indigo-400">
                                        {codigoGerado}
                                    </code>
                                    <Button
                                        size="sm"
                                        variant="ghost"
                                        onClick={copiarCodigo}
                                        className="h-7 w-7 p-0"
                                    >
                                        <DocumentDuplicateIcon className="w-3.5 h-3.5" />
                                    </Button>
                                </div>
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>

            {/* Lista de Convites */}
            <Card className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800">
                <CardHeader className="pb-2 pt-3 px-3">
                    <CardTitle className="text-sm">Convites Ativos</CardTitle>
                    <CardDescription className="text-xs">Gerencie os convites criados</CardDescription>
                </CardHeader>
                <CardContent className="px-3 pb-3">
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-zinc-200 dark:border-zinc-800">
                                    <th className="text-left py-3 px-4 text-xs font-medium text-zinc-600 dark:text-zinc-400">Tipo</th>
                                    <th className="text-left py-3 px-4 text-xs font-medium text-zinc-600 dark:text-zinc-400">Email/Código</th>
                                    <th className="text-left py-3 px-4 text-xs font-medium text-zinc-600 dark:text-zinc-400">Permissão</th>
                                    <th className="text-left py-3 px-4 text-xs font-medium text-zinc-600 dark:text-zinc-400">Status</th>
                                    <th className="text-left py-3 px-4 text-xs font-medium text-zinc-600 dark:text-zinc-400">Usos</th>
                                    <th className="text-left py-3 px-4 text-xs font-medium text-zinc-600 dark:text-zinc-400">Ações</th>
                                </tr>
                            </thead>
                            <tbody>
                                {convites.map((convite) => {
                                    const PermissionIcon = getPermissionIcon(convite.cargo);
                                    return (
                                        <tr key={convite.id} className="border-b border-zinc-100 dark:border-zinc-800/50">
                                            <td className="py-3 px-4">
                                                <div className="flex items-center gap-2">
                                                    {convite.tipo === 'email' ? (
                                                        <EnvelopeIcon className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                                                    ) : (
                                                        <TicketIcon className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                                                    )}
                                                    <span className="text-sm text-zinc-700 dark:text-zinc-300">
                                                        {convite.tipo === 'email' ? 'Email' : 'Código'}
                                                    </span>
                                                </div>
                                            </td>
                                            <td className="py-3 px-4 text-sm font-mono text-zinc-700 dark:text-zinc-300">
                                                {convite.tipo === 'email' ? convite.email : convite.codigo}
                                            </td>
                                            <td className="py-3 px-4">
                                                <div className="flex items-center gap-2">
                                                    <PermissionIcon className="w-4 h-4 text-zinc-500 dark:text-zinc-400" />
                                                    <span className="text-sm text-zinc-700 dark:text-zinc-300 capitalize">
                                                        {convite.cargo}
                                                    </span>
                                                </div>
                                            </td>
                                            <td className="py-3 px-4">
                                                <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium rounded-md border ${getStatusBadge(convite.status)}`}>
                                                    {convite.status === 'pendente' && <ClockIcon className="w-3.5 h-3.5" />}
                                                    {convite.status === 'usado' && <CheckCircleIcon className="w-3.5 h-3.5" />}
                                                    {convite.status === 'expirado' && <XCircleIcon className="w-3.5 h-3.5" />}
                                                    {convite.status === 'cancelado' && <XCircleIcon className="w-3.5 h-3.5" />}
                                                    {convite.status}
                                                </span>
                                            </td>
                                            <td className="py-3 px-4 text-sm text-zinc-700 dark:text-zinc-300">
                                                {convite.vezes_usado}/{convite.max_usos}
                                            </td>
                                            <td className="py-3 px-4">
                                                {convite.status === 'pendente' && (
                                                    <Button
                                                        size="sm"
                                                        variant="ghost"
                                                        onClick={() => handleCancelar(convite.id)}
                                                        className="h-8 text-rose-600 hover:text-rose-700 hover:bg-rose-50 dark:hover:bg-rose-900/20"
                                                    >
                                                        Cancelar
                                                    </Button>
                                                )}
                                            </td>
                                        </tr>
                                    );
                                })}
                                {convites.length === 0 && (
                                    <tr>
                                        <td colSpan={6} className="py-12 text-center">
                                            <div className="flex flex-col items-center gap-2">
                                                <div className="w-12 h-12 rounded-full bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center">
                                                    <TicketIcon className="w-6 h-6 text-zinc-400 dark:text-zinc-600" />
                                                </div>
                                                <p className="text-sm text-zinc-500 dark:text-zinc-400">
                                                    Nenhum convite criado ainda
                                                </p>
                                            </div>
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
};
