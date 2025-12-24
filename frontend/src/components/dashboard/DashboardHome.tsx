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
} from '@heroicons/react/24/outline';
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
    return (
        <div className="p-8 space-y-8 min-h-full max-w-7xl mx-auto">

            {/* HEADER */}
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex flex-col md:flex-row md:items-center justify-between gap-4"
            >
                <div>
                    <h1 className="text-2xl font-semibold text-zinc-900 dark:text-foreground tracking-tight mb-1">Visão Geral</h1>
                    <p className="text-zinc-500 dark:text-muted-foreground text-sm">Acompanhe o desempenho da sua clínica em tempo real.</p>
                </div>

                <div className="flex items-center gap-3">
                    <Button variant="outline" className="h-9 text-xs bg-white dark:bg-card border-zinc-200 dark:border-border text-zinc-600 dark:text-muted-foreground font-medium hover:bg-zinc-50 dark:hover:bg-accent hover:text-zinc-900 dark:hover:text-foreground shadow-sm">
                        <CalendarIcon className="w-4 h-4 mr-2" />
                        Este Mês
                    </Button>
                    <Button className="h-9 text-xs bg-indigo-600 dark:bg-primary text-white dark:text-primary-foreground hover:bg-indigo-700 dark:hover:bg-primary/90 shadow-sm">
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
                    className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
                >
                    <MetricCard
                        title="Total de Leads"
                        value="156"
                        icon={UserGroupIcon}
                        color="zinc"
                        trend="up"
                    />
                    <MetricCard
                        title="Agendamentos"
                        value="76"
                        subtext="48.7% de conversão"
                        icon={CalendarIcon}
                        color="zinc"
                        trend="up"
                    />
                    <MetricCard
                        title="Comparecimentos"
                        value="37"
                        subtext="48.7% de presença"
                        icon={CheckCircleIcon}
                        color="zinc"
                        trend="up"
                    />
                    <MetricCard
                        title="Vendas Realizadas"
                        value="6"
                        subtext="Ticket Médio R$ 2.1k"
                        icon={ArrowTrendingUpIcon}
                        color="zinc"
                        trend="down"
                    />
                </motion.div>
            </div>

            {/* CHARTS SECTION */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Funnel Chart */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="lg:col-span-2 bg-white dark:bg-card p-6 rounded-xl border border-zinc-200 dark:border-border shadow-sm"
                >
                    <div className="flex items-center justify-between mb-6">
                        <h2 className="text-base font-semibold text-zinc-900 dark:text-card-foreground">Funil de Vendas</h2>
                        <Button variant="ghost" size="sm" className="text-zinc-400 dark:text-muted-foreground hover:text-zinc-600 dark:hover:text-foreground">
                            <DocumentTextIcon className="w-5 h-5" />
                        </Button>
                    </div>

                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={funnelData} layout="vertical" margin={{ top: 0, right: 0, left: 40, bottom: 0 }}>
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
                                    {funnelData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.fill} className="dark:fill-primary" />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </motion.div>

                {/* Financial Summary (Mini) */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="space-y-6"
                >
                    <MetricCard
                        title="Faturamento (Mês)"
                        value="R$ 12.800"
                        icon={WalletIcon}
                        color="zinc"
                        trend="up"
                    />
                    <MetricCard
                        title="Ticket Médio"
                        value="R$ 2.133"
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
