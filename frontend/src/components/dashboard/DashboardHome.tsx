import React from 'react';
import { motion } from 'framer-motion';
import { Button } from '../ui/button';
import {
    UserGroupIcon,
    CalendarIcon,
    CheckCircleIcon,
    ArrowTrendingUpIcon,
    ArrowPathIcon,
    DocumentTextIcon,
    WalletIcon,
    CreditCardIcon,
    ArrowUpRightIcon,
    ArrowDownRightIcon,
    XCircleIcon,
} from '@heroicons/react/24/outline';
import { MessageCircle } from 'lucide-react';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Cell
} from 'recharts';
import { staggerContainer, staggerItem } from '../../utils/animations';

// Catalyst Palette for Funnel (Indigo Theme)
const funnelData = [
    { name: 'Leads', value: 156, fill: '#4f46e5' }, // Indigo-600
    { name: 'Agendados', value: 76, fill: '#6366f1' }, // Indigo-500
    { name: 'Compareceram', value: 37, fill: '#818cf8' }, // Indigo-400
    { name: 'Vendas', value: 6, fill: '#a5b4fc' }, // Indigo-300
];

interface MetricCardProps {
    title: string;
    value: string | number;
    subtext?: string;
    icon: any;
    trend?: 'up' | 'down';
    color?: 'zinc' | 'primary';
}

const MetricCard = ({ title, value, subtext, icon: Icon, trend, color = 'zinc' }: MetricCardProps) => {
    // Catalyst Style: Clean, Indigo-based
    const iconColors = {
        zinc: 'bg-indigo-50 text-indigo-600 dark:bg-primary/10 dark:text-primary',
        primary: 'bg-indigo-600 text-white dark:bg-primary dark:text-white' // Strong contrast for primary
    };

    return (
        <motion.div
            variants={staggerItem}
            className="bg-white dark:bg-card p-6 rounded-xl border border-zinc-200 dark:border-border shadow-sm hover:shadow-md transition-all group"
        >
            <div className="flex justify-between items-start mb-4">
                <div className={`p-2.5 rounded-lg border border-indigo-100 dark:border-primary/20 transition-colors ${iconColors[color] || iconColors.zinc}`}>
                    <Icon className="w-5 h-5" />
                </div>
                {trend && (
                    <div className={`flex items-center gap-1 text-xs font-medium px-2 py-1 rounded-full ${trend === 'up'
                        ? 'bg-emerald-50 text-emerald-700 border border-emerald-100 dark:bg-emerald-900/20 dark:text-emerald-400 dark:border-emerald-900/30'
                        : 'bg-red-50 text-red-700 border border-red-100 dark:bg-red-900/20 dark:text-red-400 dark:border-red-900/30'
                        }`}>
                        {trend === 'up' ? <ArrowUpRightIcon className="w-3 h-3" /> : <ArrowDownRightIcon className="w-3 h-3" />}
                        {trend === 'up' ? '+12%' : '-5%'}
                    </div>
                )}
            </div>

            <div>
                <p className="text-sm font-medium text-zinc-500 dark:text-muted-foreground mb-1">{title}</p>
                <h3 className="text-2xl font-semibold text-zinc-900 dark:text-foreground tracking-tight">{value}</h3>
                {subtext && (
                    <p className="text-xs text-zinc-400 dark:text-zinc-500 mt-2">{subtext}</p>
                )}
            </div>
        </motion.div>
    );
};

export const DashboardHome: React.FC = () => {
    const [period, setPeriod] = React.useState('month'); // week, month, custom
    const [source, setSource] = React.useState('whatsapp'); // Default, will be updated by DB
    const [isLoadingPref, setIsLoadingPref] = React.useState(true);

    // Load preference from DB on mount
    React.useEffect(() => {
        const loadPref = async () => {
            try {
                const res = await fetch(`${import.meta.env.VITE_API_URL}/api/crm/preferences`);
                const data = await res.json();
                if (data && data.default_source) {
                    setSource(data.default_source);
                }
            } catch (e) {
                console.error("Failed to load preferences", e);
            } finally {
                setIsLoadingPref(false);
            }
        };
        loadPref();
    }, []);

    const [metrics, setMetrics] = React.useState({
        totalLeads: 0,
        scheduled: 0,
        attended: 0,
        noshow: 0,
        qualifying: 0,
        sales: 0,
        revenue: 0,
        ticket: 0,
        funnelData: [
            { name: 'Leads', value: 0, fill: '#4f46e5' },
            { name: 'Agendados', value: 0, fill: '#6366f1' },
            { name: 'Compareceram', value: 0, fill: '#818cf8' },
            { name: 'Vendas', value: 0, fill: '#a5b4fc' },
        ],
        percentages: {
            schedulingRate: 0,
            attendanceRate: 0,
            conversionRate: 0,
            noshowRate: 0,
            qualifyingRate: 0
        }
    });

    // Add debug state
    const [debugInfo, setDebugInfo] = React.useState<any>(null);

    // Save source to DB whenever it changes (skip initial load)
    React.useEffect(() => {
        if (isLoadingPref) return;

        const savePref = async () => {
            try {
                await fetch(`${import.meta.env.VITE_API_URL}/api/crm/preferences`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ default_source: source })
                });
            } catch (e) {
                console.error("Failed to save preference", e);
            }
        };
        savePref();
    }, [source, isLoadingPref]);

    React.useEffect(() => {
        if (isLoadingPref) return; // Wait for source to load before fetching metrics

        const fetchMetrics = async () => {
            try {
                const res = await fetch(`${import.meta.env.VITE_API_URL}/api/crm/metrics?period=${period}&source=${source}`);
                const data = await res.json();
                if (data) {
                    setMetrics(data);
                    if (data.debug_info) setDebugInfo(data.debug_info);
                    else setDebugInfo(null);
                }
            } catch (error) {
                console.error("Failed to fetch dashboard metrics", error);
            }
        };

        fetchMetrics();
    }, [period, source, isLoadingPref]);

    return (
        <div className="p-8 space-y-8 min-h-full max-w-7xl mx-auto">
            {source === 'clinicorp' && debugInfo && (
                <div className="bg-blue-50 border border-blue-200 p-4 rounded text-xs text-blue-800 font-mono mb-4">
                    <strong>DEBUG MODE (Clinicorp):</strong><br />
                    Periodo: {debugInfo.dates} ({debugInfo.period})<br />
                    Encontrados: {debugInfo.appointments_found}<br />
                    ID Usado: {debugInfo.client_id_used}
                </div>
            )}

            {/* HEADER */}
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex flex-col md:flex-row md:items-center justify-between gap-4"
            >
                <div className="flex flex-col gap-2">
                    <div>
                        <h1 className="text-2xl font-semibold text-zinc-900 dark:text-foreground tracking-tight mb-1">Visão Geral</h1>
                        <p className="text-zinc-500 dark:text-muted-foreground text-sm">Acompanhe o desempenho da sua clínica em tempo real.</p>
                    </div>
                    {/* Source Selector */}
                    <div className="flex items-center gap-2 mt-2">
                        <span className="text-xs font-medium text-zinc-500 uppercase tracking-wider">Fonte de Dados:</span>
                        <div className="flex bg-zinc-100 dark:bg-muted p-1 rounded-lg">
                            <button
                                onClick={() => setSource('whatsapp')}
                                className={`px-3 py-1 text-xs font-medium rounded-md transition-all ${source === 'whatsapp' ? 'bg-white dark:bg-card text-indigo-600 shadow-sm' : 'text-zinc-500 hover:text-zinc-900'}`}
                            >
                                WhatsApp (CRM)
                            </button>
                            <button
                                onClick={() => setSource('clinicorp')}
                                className={`px-3 py-1 text-xs font-medium rounded-md transition-all ${source === 'clinicorp' ? 'bg-white dark:bg-card text-indigo-600 shadow-sm' : 'text-zinc-500 hover:text-zinc-900'}`}
                            >
                                Clinicorp (Real)
                            </button>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    <Button
                        variant="outline"
                        onClick={() => setPeriod('week')}
                        className={`h-9 text-xs ${period === 'week' ? 'bg-indigo-50 border-indigo-200 text-indigo-700' : 'bg-white border-zinc-200 text-zinc-600'} dark:bg-card dark:border-border dark:text-muted-foreground font-medium hover:bg-zinc-50 dark:hover:bg-accent hover:text-zinc-900 dark:hover:text-foreground shadow-sm`}
                    >
                        <CalendarIcon className="w-4 h-4 mr-2" />
                        Esta Semana
                    </Button>
                    <Button
                        variant="outline"
                        onClick={() => setPeriod('month')}
                        className={`h-9 text-xs ${period === 'month' ? 'bg-indigo-50 border-indigo-200 text-indigo-700' : 'bg-white border-zinc-200 text-zinc-600'} dark:bg-card dark:border-border dark:text-muted-foreground font-medium hover:bg-zinc-50 dark:hover:bg-accent hover:text-zinc-900 dark:hover:text-foreground shadow-sm`}
                    >
                        <CalendarIcon className="w-4 h-4 mr-2" />
                        Este Mês
                    </Button>
                    <Button
                        variant="outline"
                        onClick={() => setPeriod('last7days')}
                        className={`h-9 text-xs ${period === 'last7days' ? 'bg-indigo-50 border-indigo-200 text-indigo-700' : 'bg-white border-zinc-200 text-zinc-600'} dark:bg-card dark:border-border dark:text-muted-foreground font-medium hover:bg-zinc-50 dark:hover:bg-accent hover:text-zinc-900 dark:hover:text-foreground shadow-sm`}
                    >
                        Últimos 7 dias
                    </Button>
                    <Button
                        variant="outline"
                        onClick={() => setPeriod('last30days')}
                        className={`h-9 text-xs ${period === 'last30days' ? 'bg-indigo-50 border-indigo-200 text-indigo-700' : 'bg-white border-zinc-200 text-zinc-600'} dark:bg-card dark:border-border dark:text-muted-foreground font-medium hover:bg-zinc-50 dark:hover:bg-accent hover:text-zinc-900 dark:hover:text-foreground shadow-sm`}
                    >
                        Últimos 30 dias
                    </Button>
                    <Button
                        onClick={() => {
                            const fetchMetrics = async () => {
                                try {
                                    const res = await fetch(`${import.meta.env.VITE_API_URL}/api/crm/metrics?period=${period}`);
                                    const data = await res.json();
                                    if (data && data.funnelData) {
                                        setMetrics(data);
                                    }
                                } catch (error) {
                                    console.error("Failed to fetch dashboard metrics", error);
                                }
                            };
                            fetchMetrics();
                        }}
                        className="h-9 text-xs bg-indigo-600 dark:bg-primary text-white dark:text-primary-foreground hover:bg-indigo-700 dark:hover:bg-primary/90 shadow-sm"
                    >
                        <ArrowPathIcon className="w-4 h-4 mr-2" /> Atualizar
                    </Button>
                </div>
            </motion.div>

            {/* METRICS GRID */}
            <div>
                <motion.div
                    variants={staggerContainer}
                    initial="initial"
                    animate="animate"
                    className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-6"
                >
                    <MetricCard
                        title="Total de Leads"
                        value={metrics.totalLeads}
                        icon={UserGroupIcon}
                        color="zinc"
                        trend="up"
                    />
                    <MetricCard
                        title="Em Negociação"
                        value={metrics.qualifying}
                        subtext={`${metrics.percentages.qualifyingRate}% dos leads`}
                        icon={MessageCircle}
                        color="zinc"
                        trend="up"
                    />
                    <MetricCard
                        title="Agendamentos"
                        value={metrics.scheduled}
                        subtext={`${metrics.percentages.schedulingRate}% de conversão`}
                        icon={CalendarIcon}
                        color="zinc"
                        trend="up"
                    />
                    <MetricCard
                        title="Comparecimentos"
                        value={metrics.attended}
                        subtext={`${metrics.percentages.attendanceRate}% de presença`}
                        icon={CheckCircleIcon}
                        color="zinc"
                        trend="up"
                    />
                    <MetricCard
                        title="Faltou (No-Show)"
                        value={metrics.noshow}
                        subtext={`${metrics.percentages.noshowRate}% dos agendados`}
                        icon={XCircleIcon}
                        color="zinc"
                        trend="down"
                    />
                    <MetricCard
                        title="Vendas Realizadas"
                        value={metrics.sales}
                        subtext={`${metrics.percentages.conversionRate}% de conversão`}
                        icon={ArrowTrendingUpIcon}
                        color="zinc"
                        trend="up"
                    />
                </motion.div>
            </div>

            {/* CHARTS SECTION */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6"
            >
                {/* Funnel Chart */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="bg-white dark:bg-card p-6 rounded-xl border border-zinc-200 dark:border-border shadow-sm"
                >
                    <div className="flex items-center justify-between mb-6">
                        <h2 className="text-base font-semibold text-zinc-900 dark:text-card-foreground">Funil de Vendas</h2>
                        <Button variant="ghost" size="sm" className="text-zinc-400 dark:text-muted-foreground hover:text-zinc-600 dark:hover:text-foreground">
                            <DocumentTextIcon className="w-5 h-5" />
                        </Button>
                    </div>

                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={metrics.funnelData} layout="vertical" margin={{ top: 0, right: 0, left: 40, bottom: 0 }}>
                                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f4f4f5" className="dark:stroke-zinc-800" />
                                <XAxis type="number" hide />
                                <YAxis
                                    type="category"
                                    dataKey="name"
                                    tick={{ fontSize: 12, fill: '#71717a', fontWeight: 500 }}
                                    width={100}
                                    axisLine={false}
                                    tickLine={false}
                                />
                                <Tooltip
                                    cursor={{ fill: 'transparent' }} // Fixed: Use transparent cursor
                                    contentStyle={{
                                        borderRadius: '8px',
                                        border: '1px solid #e4e4e7',
                                        boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.05)',
                                        padding: '8px 12px',
                                        fontSize: '12px',
                                        backgroundColor: '#fff', // Could be dynamic
                                        color: '#000'
                                    }}
                                />
                                <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={32}>
                                    {metrics.funnelData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.fill} className="dark:fill-primary" />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </motion.div>

                {/* Financial Summary */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="grid grid-cols-1 gap-6"
                >
                    <MetricCard
                        title="Faturamento (Mês)"
                        value={`R$ ${metrics.revenue.toLocaleString()}`}
                        icon={WalletIcon}
                        color="zinc"
                        trend="up"
                    />
                    <MetricCard
                        title="Ticket Médio"
                        value={`R$ ${metrics.ticket.toLocaleString()}`}
                        icon={CreditCardIcon}
                        color="zinc"
                    />

                    <div className="bg-gradient-to-br from-indigo-600 to-purple-700 dark:from-primary dark:to-purple-600 dark:border dark:border-border rounded-xl p-6 text-white shadow-lg relative overflow-hidden group cursor-pointer hover:from-indigo-700 hover:to-purple-800 dark:hover:from-primary/90 dark:hover:to-purple-700 transition-all">
                        <div className="relative z-10">
                            <h3 className="text-sm font-medium text-indigo-100 dark:text-indigo-200 mb-1">Meta Mensal</h3>
                            <div className="flex items-end gap-2 mb-4">
                                <span className="text-3xl font-bold text-white">28%</span>
                                <span className="text-xs text-indigo-200 mb-1.5">atingida</span>
                            </div>
                            <div className="w-full bg-indigo-800/40 dark:bg-white/20 rounded-full h-1.5 mb-2">
                                <div className="bg-white dark:bg-white h-1.5 rounded-full" style={{ width: '28%' }}></div>
                            </div>
                            <p className="text-xs text-indigo-200">Faltam R$ 32.200</p>
                        </div>
                        {/* Subtle glow effect */}
                        <div className="absolute -right-6 -bottom-6 w-24 h-24 bg-white/10 rounded-full blur-2xl group-hover:bg-white/20 transition-all"></div>
                    </div>
                </motion.div>
            </div>

        </div>
    );
};
