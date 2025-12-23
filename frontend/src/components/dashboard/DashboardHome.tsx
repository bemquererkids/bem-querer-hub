import React from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import {
    Users,
    Calendar,
    CheckCircle2,
    TrendingUp,
    RefreshCw,
    Calendar as CalendarIcon,
    FileText,
    Wallet,
    CreditCard,
    DollarSign,
    ArrowUpRight,
    ArrowDownRight
} from 'lucide-react';
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

// Mock Data for Funnel Chart
const funnelData = [
    { name: 'Leads', value: 156, fill: '#06b6d4' }, // Cyan
    { name: 'Agendados', value: 76, fill: '#14b8a6' }, // Teal
    { name: 'Compareceram', value: 37, fill: '#10b981' }, // Emerald
    { name: 'Vendas', value: 6, fill: '#8b5cf6' }, // Purple
];

// Jampack-Style Metric Card
interface MetricCardProps {
    title: string;
    value: string | number;
    subtext?: string;
    icon: any;
    trend?: 'up' | 'down';
    color?: 'cyan' | 'teal' | 'emerald' | 'purple';
}

const MetricCard = ({ title, value, subtext, icon: Icon, trend, color = 'cyan' }: MetricCardProps) => {
    const colorClasses = {
        cyan: 'bg-cyan-50 text-cyan-600',
        teal: 'bg-teal-50 text-teal-600',
        emerald: 'bg-emerald-50 text-emerald-600',
        purple: 'bg-purple-50 text-purple-600'
    };

    return (
        <motion.div
            variants={staggerItem}
            className="bg-white p-6 rounded-2xl shadow-sm hover:shadow-md transition-all border border-slate-100"
        >
            <div className="flex justify-between items-start mb-4">
                <div className={`p-3 rounded-xl ${colorClasses[color as keyof typeof colorClasses]}`}>
                    <Icon className="w-5 h-5" />
                </div>
                {trend && (
                    <div className={`flex items-center gap-1 text-xs font-semibold ${trend === 'up' ? 'text-emerald-600' : 'text-red-600'}`}>
                        {trend === 'up' ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                        {trend === 'up' ? '+12%' : '-5%'}
                    </div>
                )}
            </div>

            <div>
                <p className="text-sm font-medium text-slate-500 mb-1">{title}</p>
                <h3 className="text-3xl font-bold text-slate-900">{value}</h3>
                {subtext && (
                    <p className="text-xs text-slate-400 mt-2">{subtext}</p>
                )}
            </div>
        </motion.div>
    );
};

export const DashboardHome: React.FC = () => {
    return (
        <div className="p-8 space-y-6 min-h-full">

            {/* HEADER */}
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8"
            >
                <div>
                    <h1 className="text-2xl font-bold text-slate-900 mb-1">Dashboard de Vendas</h1>
                    <p className="text-slate-500">Análise do funil de conversão e métricas financeiras</p>
                </div>

                <div className="flex items-center gap-3">
                    <Button variant="outline" className="bg-white border-slate-200 text-slate-600 font-medium hover:bg-slate-50">
                        <CalendarIcon className="w-4 h-4 mr-2" />
                        01/08 - 31/08/2025
                    </Button>
                    <Button className="bg-gradient-to-r from-cyan-500 to-teal-500 hover:from-cyan-600 hover:to-teal-600 text-white shadow-lg shadow-cyan-500/30">
                        <RefreshCw className="w-4 h-4 mr-2" /> Atualizar
                    </Button>
                </div>
            </motion.div>

            {/* MÉTRICAS DE CONVERSÃO */}
            <div>
                <h2 className="text-sm font-semibold text-slate-700 uppercase tracking-wider mb-4">Métricas de Conversão</h2>
                <motion.div
                    variants={staggerContainer}
                    initial="initial"
                    animate="animate"
                    className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
                >
                    <MetricCard
                        title="Total de Leads"
                        value="156"
                        icon={Users}
                        color="cyan"
                        trend="up"
                    />
                    <MetricCard
                        title="Agendamentos"
                        value="76"
                        subtext="48.7% Taxa de agendamentos"
                        icon={Calendar}
                        color="teal"
                        trend="up"
                    />
                    <MetricCard
                        title="Comparecimentos"
                        value="37"
                        subtext="48.7% Taxa de comparecimento"
                        icon={CheckCircle2}
                        color="emerald"
                        trend="up"
                    />
                    <MetricCard
                        title="Vendas"
                        value="6"
                        subtext="16.2% Taxa de conversão"
                        icon={TrendingUp}
                        color="purple"
                        trend="down"
                    />
                </motion.div>
            </div>

            {/* FUNIL DE CONVERSÃO */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
            >
                <h2 className="text-sm font-semibold text-slate-700 uppercase tracking-wider mb-4">Funil de Conversão</h2>
                <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                    <div className="h-[320px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={funnelData} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0" />
                                <XAxis type="number" hide />
                                <YAxis type="category" dataKey="name" tick={{ fontSize: 13, fill: '#64748b', fontWeight: 500 }} width={100} />
                                <Tooltip
                                    cursor={{ fill: 'transparent' }}
                                    contentStyle={{
                                        borderRadius: '12px',
                                        border: 'none',
                                        boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                                        padding: '12px'
                                    }}
                                />
                                <Bar dataKey="value" radius={[0, 8, 8, 0]} barSize={40}>
                                    {funnelData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.fill} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </motion.div>

            {/* MÉTRICAS FINANCEIRAS */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
            >
                <h2 className="text-sm font-semibold text-slate-700 uppercase tracking-wider mb-4">Métricas Financeiras</h2>
                <motion.div
                    variants={staggerContainer}
                    initial="initial"
                    animate="animate"
                    className="grid grid-cols-1 md:grid-cols-3 gap-6"
                >
                    <MetricCard
                        title="Valor Orçado"
                        value="R$ 45.200"
                        icon={FileText}
                        color="cyan"
                    />
                    <MetricCard
                        title="Valor Faturado"
                        value="R$ 12.800"
                        icon={Wallet}
                        color="teal"
                    />
                    <MetricCard
                        title="Valor Pago"
                        value="R$ 8.500"
                        subtext="66% do Faturado"
                        icon={CreditCard}
                        color="emerald"
                        trend="up"
                    />
                </motion.div>
            </motion.div>

        </div>
    );
};
