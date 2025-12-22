import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { 
    Users, 
    Calendar, 
    CheckCircle2, 
    TrendingUp, 
    RefreshCw, 
    HelpCircle,
    ChevronDown,
    ChevronRight,
    LogOut,
    Calendar as CalendarIcon,
    FileText,
    Wallet,
    CreditCard
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

// Mock Data for Funnel Chart
const funnelData = [
  { name: 'Leads', value: 156, fill: '#60a5fa' }, // Blue
  { name: 'Agendados', value: 76, fill: '#fbbf24' }, // Amber
  { name: 'Compareceram', value: 37, fill: '#34d399' }, // Emerald
  { name: 'Vendas', value: 6, fill: '#818cf8' }, // Indigo
];

// Reusable Metric Card Component
const MetricCard = ({ title, value, subtext, icon: Icon, trend }: any) => (
    <div className="bg-white p-6 rounded-xl border border-slate-100 shadow-sm hover:shadow-md transition-all flex flex-col justify-between h-32">
        <div className="flex justify-between items-start">
            <div>
                <p className="text-sm font-medium text-slate-500">{title}</p>
                <h3 className="text-3xl font-bold text-slate-800 mt-1">{value}</h3>
            </div>
            <div className="p-2 bg-slate-50 rounded-lg text-slate-400">
                <Icon className="w-5 h-5" />
            </div>
        </div>
        {subtext && (
            <p className={`text-xs font-bold flex items-center gap-1 ${trend === 'positive' ? 'text-green-600' : 'text-slate-400'}`}>
                {trend === 'positive' && '↗'} {subtext}
            </p>
        )}
    </div>
);

// Collapsible Section Component
const DashboardSection = ({ title, icon: Icon, children, isOpen = true }: any) => {
    const [open, setOpen] = useState(isOpen);
    
    return (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden mb-6">
            <div 
                className="p-4 flex items-center justify-between cursor-pointer hover:bg-slate-50 transition-colors border-b border-slate-100"
                onClick={() => setOpen(!open)}
            >
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-50 text-blue-600 rounded-lg">
                        <Icon className="w-5 h-5" />
                    </div>
                    <h3 className="font-bold text-slate-800">{title}</h3>
                </div>
                {open ? <ChevronDown className="w-5 h-5 text-slate-400" /> : <ChevronRight className="w-5 h-5 text-slate-400" />}
            </div>
            
            {open && (
                <div className="p-6 bg-slate-50/30 animate-in slide-in-from-top-2 duration-300">
                    {children}
                </div>
            )}
        </div>
    );
};

export const DashboardHome: React.FC = () => {
    return (
        <div className="p-8 space-y-6 min-h-full font-sans text-slate-800">
            
            {/* 1. HEADER */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">Dashboard de Vendas</h1>
                    <p className="text-slate-500">Análise do funil de conversão e métricas financeiras</p>
                </div>
                
                <div className="flex items-center gap-3">
                    <Button variant="outline" className="bg-white border-slate-200 text-slate-600 font-medium">
                        <CalendarIcon className="w-4 h-4 mr-2" />
                        01/08/2025 - 31/08/2025
                    </Button>
                    <Button variant="outline" className="bg-white border-slate-200 text-slate-600 hover:text-red-600 hover:bg-red-50">
                        <LogOut className="w-4 h-4 mr-2" /> Sair
                    </Button>
                </div>
            </div>

            {/* 2. CONTROLS */}
            <div className="flex items-center gap-2 mb-6">
                <Button variant="ghost" size="sm" className="text-slate-500 hover:text-blue-600">
                    <RefreshCw className="w-4 h-4 mr-2" /> Atualizar
                </Button>
                <div className="flex-1" />
                <HelpCircle className="w-5 h-5 text-slate-300 cursor-help" />
            </div>

            {/* 3. SECTION: MÉTRICAS DE CONVERSÃO */}
            <DashboardSection title="Métricas de Conversão" icon={TrendingUp}>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <MetricCard 
                        title="Total de Leads" 
                        value="156" 
                        icon={Users} 
                    />
                    <MetricCard 
                        title="Agendamentos" 
                        value="76" 
                        subtext="48.7% Taxa de agendamentos"
                        trend="positive"
                        icon={Calendar} 
                    />
                    <MetricCard 
                        title="Comparecimentos" 
                        value="37" 
                        subtext="48.7% Taxa de comparecimento"
                        trend="positive"
                        icon={CheckCircle2} 
                    />
                    <MetricCard 
                        title="Vendas" 
                        value="6" 
                        subtext="16.2% Taxa de conversão"
                        trend="positive"
                        icon={TrendingUp} 
                    />
                </div>
            </DashboardSection>

            {/* 4. SECTION: FUNIL DE CONVERSÃO */}
            <DashboardSection title="Funil de Conversão" icon={BarChart}>
                <div className="h-[300px] w-full bg-white p-4 rounded-xl border border-slate-100" style={{ height: 300, minHeight: 300 }}>
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={funnelData} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                            <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0" />
                            <XAxis type="number" hide />
                            <YAxis type="category" dataKey="name" tick={{ fontSize: 12, fill: '#64748b' }} width={100} />
                            <Tooltip 
                                cursor={{ fill: 'transparent' }}
                                contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                            />
                            <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={30}>
                                {funnelData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.fill} />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </DashboardSection>

            {/* 5. SECTION: MÉTRICAS FINANCEIRAS */}
            <DashboardSection title="Métricas Financeiras" icon={DollarSign} isOpen={true}>
                 <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <MetricCard 
                        title="Valor Orçado" 
                        value="R$ 45.200" 
                        icon={FileText} 
                    />
                    <MetricCard 
                        title="Valor Faturado" 
                        value="R$ 12.800" 
                        icon={Wallet} 
                    />
                    <MetricCard 
                        title="Valor Pago" 
                        value="R$ 8.500" 
                        subtext="66% do Faturado"
                        trend="positive"
                        icon={CreditCard} 
                    />
                </div>
            </DashboardSection>

        </div>
    );
};

// Helper for Section 5 Icon (DollarSign was not imported in main list above, importing locally or using lucide-react)
import { DollarSign } from 'lucide-react'; 
