import React, { useState } from 'react';
import { Card, CardContent } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import {
    Flame,
    Clock,
    Archive,
    MessageCircle,
    Sparkles,
    CheckCircle2,
    TrendingUp,
    Zap,
    Star,
} from 'lucide-react';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../ui/tabs';

// Mock Data for Follow-up Lists
const HOT_LEADS = [
    { id: 1, name: "Fernanda Costa", reason: "Pediu para chamar hoje", script: "Oi Fernanda! Como combinamos, estou passando para ver sobre o agendamento.", time: "Hoje, 09:00", tags: ["Cartão Virou"], priority: "urgent" },
    { id: 2, name: "Marcos Silva", reason: "Verificar com esposa", script: "Olá Marcos! Conseguiu conversar com sua esposa sobre o tratamento?", time: "Hoje, 14:00", tags: ["Decisor"], priority: "high" },
    { id: 7, name: "Patricia Alves", reason: "Retornar após exame", script: "Oi Patricia! Vi que você fez os exames. Vamos agendar a consulta?", time: "Hoje, 16:00", tags: ["Retorno"], priority: "high" },
];

const WARM_LEADS = [
    { id: 3, name: "Juliana Paes", reason: "Visualizou orçamento há 48h", script: "Oi Juliana, ficou alguma dúvida sobre o valor do clareamento?", time: "Há 2 dias", tags: ["Vácuo"], priority: "medium" },
    { id: 4, name: "Roberto Carlos", reason: "Faltou e não reagendou", script: "Roberto, vi que não conseguiu vir. Vamos remarcar para não atrasar o tratamento?", time: "Ontem", tags: ["No-Show"], priority: "medium" },
    { id: 8, name: "Lucas Mendes", reason: "Pediu desconto", script: "Lucas, consegui uma condição especial pra você! Vamos conversar?", time: "Há 3 dias", tags: ["Negociação"], priority: "medium" },
];

const COLD_LEADS = [
    { id: 5, name: "Ana Maria", reason: "Limpeza há 6 meses", script: "Oi Ana! Faz 6 meses do seu último sorriso aqui. Vamos agendar a limpeza?", time: "6 meses", tags: ["Recorrência"], priority: "low" },
    { id: 6, name: "Pedro Bial", reason: "Orçamento antigo (Implante)", script: "Pedro, temos uma condição especial para implantes este mês. Vamos retomar?", time: "1 ano", tags: ["Resgate"], priority: "low" },
];

const FollowUpCard = React.memo(({ lead, type }: { lead: any, type: 'hot' | 'warm' | 'cold' }) => {
    const [isHovered, setIsHovered] = useState(false);

    let Icon = Clock;
    let iconBg = "bg-indigo-50 dark:bg-indigo-900/20";
    let iconColor = "text-indigo-600 dark:text-indigo-400";
    let borderColor = "border-indigo-100 dark:border-indigo-800";
    let badgeBg = "bg-indigo-100 dark:bg-indigo-900/30";
    let badgeText = "text-indigo-700 dark:text-indigo-300";
    let badgeBorder = "border-indigo-200 dark:border-indigo-800";

    if (type === 'hot') {
        Icon = Flame;
        iconBg = "bg-orange-50 dark:bg-orange-900/20";
        iconColor = "text-orange-600 dark:text-orange-400";
        borderColor = "border-orange-100 dark:border-orange-800";
        badgeBg = "bg-orange-100 dark:bg-orange-900/30";
        badgeText = "text-orange-700 dark:text-orange-300";
        badgeBorder = "border-orange-200 dark:border-orange-800";
    }
    if (type === 'warm') {
        Icon = Clock;
        iconBg = "bg-amber-50 dark:bg-amber-900/20";
        iconColor = "text-amber-600 dark:text-amber-400";
        borderColor = "border-amber-100 dark:border-amber-800";
        badgeBg = "bg-amber-100 dark:bg-amber-900/30";
        badgeText = "text-amber-700 dark:text-amber-300";
        badgeBorder = "border-amber-200 dark:border-amber-800";
    }

    return (
        <Card
            className={`
                relative overflow-hidden
                hover:shadow-lg hover:scale-[1.01] 
                transition-all duration-300 ease-out
                border-zinc-200 dark:border-border 
                bg-white dark:bg-card
                ${isHovered ? 'shadow-md' : 'shadow-sm'}
            `}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
        >
            {lead.priority === 'urgent' && (
                <div className="absolute top-0 right-0">
                    <div className="relative">
                        <div className="w-0 h-0 border-t-[36px] border-t-red-500 border-l-[36px] border-l-transparent"></div>
                        <Zap className="absolute -top-8 right-0.5 w-3.5 h-3.5 text-white" />
                    </div>
                </div>
            )}

            <CardContent className="p-4">
                <div className="flex justify-between items-start mb-3">
                    <div className="flex items-center gap-2.5">
                        <div className={`
                            p-2 rounded-lg ${iconBg} border ${borderColor}
                            transform transition-transform duration-300
                            ${isHovered ? 'scale-110' : 'scale-100'}
                        `}>
                            <Icon className={`w-4 h-4 ${iconColor}`} />
                        </div>
                        <div>
                            <h3 className="font-bold text-zinc-900 dark:text-foreground text-sm leading-tight flex items-center gap-1.5">
                                {lead.name}
                                {lead.priority === 'urgent' && (
                                    <Star className="w-3 h-3 text-red-500 fill-red-500 animate-pulse" />
                                )}
                            </h3>
                            <p className="text-[11px] text-zinc-500 dark:text-muted-foreground flex items-center gap-1">
                                {lead.reason} • <span className="font-semibold text-indigo-600 dark:text-indigo-400">{lead.time}</span>
                            </p>
                        </div>
                    </div>
                    <div className="flex gap-1 flex-wrap justify-end">
                        {lead.tags.map((tag: string) => (
                            <Badge
                                key={tag}
                                variant="outline"
                                className={`
                                    ${badgeBg} ${badgeText} ${badgeBorder}
                                    text-[10px] h-5 px-2
                                    transform transition-transform duration-200
                                    ${isHovered ? 'scale-105' : 'scale-100'}
                                `}
                            >
                                {tag}
                            </Badge>
                        ))}
                    </div>
                </div>

                <div className="relative bg-zinc-50 dark:bg-zinc-900 p-3 rounded-lg border border-zinc-200 dark:border-zinc-700 mb-3">
                    <div className="absolute -top-2 left-3 bg-gradient-to-r from-indigo-500 to-purple-600 px-2 py-0.5 text-[9px] font-bold text-white uppercase tracking-wide rounded-full shadow-sm flex items-center gap-1">
                        <Sparkles className="w-2.5 h-2.5" />
                        Script IA
                    </div>
                    <p className="text-xs text-zinc-700 dark:text-zinc-300 italic leading-relaxed pt-1">"{lead.script}"</p>
                </div>

                <Button className={`
                    w-full bg-[#25D366] hover:bg-[#20bd5a]
                    text-white font-semibold h-9 gap-2 
                    shadow-sm
                    transform transition-all duration-200
                    ${isHovered ? 'scale-[1.02] shadow-md' : 'scale-100'}
                `}>
                    <MessageCircle className="w-4 h-4" />
                    Chamar no WhatsApp
                </Button>
            </CardContent>
        </Card>
    );
});

FollowUpCard.displayName = 'FollowUpCard';

export const FollowUpPage: React.FC = () => {
    const [activeTab, setActiveTab] = useState('hot');

    const stats = {
        hot: HOT_LEADS.length,
        warm: WARM_LEADS.length,
        cold: COLD_LEADS.length,
        total: HOT_LEADS.length + WARM_LEADS.length + COLD_LEADS.length
    };

    return (
        <div className="p-5 h-full flex flex-col animate-in fade-in slide-in-from-bottom-4 duration-300">

            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-indigo-100 dark:bg-indigo-900/20 rounded-lg border border-indigo-200 dark:border-indigo-800">
                        <TrendingUp className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                    </div>
                    <div>
                        <h1 className="text-xl font-bold text-zinc-900 dark:text-foreground tracking-tight">
                            Follow-up Ativo
                        </h1>
                        <p className="text-xs text-zinc-500 dark:text-muted-foreground">
                            <span className="font-semibold text-indigo-600 dark:text-indigo-400">{stats.total} contatos</span> aguardando retorno
                        </p>
                    </div>
                </div>

                <div className="hidden lg:flex items-center gap-2">
                    <div className="px-3 py-1.5 bg-orange-100 dark:bg-orange-900/30 border border-orange-200 dark:border-orange-800 rounded-lg">
                        <span className="text-xs font-bold text-orange-700 dark:text-orange-300">{stats.hot} Urgentes</span>
                    </div>
                    <div className="px-3 py-1.5 bg-amber-100 dark:bg-amber-900/30 border border-amber-200 dark:border-amber-800 rounded-lg">
                        <span className="text-xs font-bold text-amber-700 dark:text-amber-300">{stats.warm} Médios</span>
                    </div>
                    <div className="px-3 py-1.5 bg-indigo-100 dark:bg-indigo-900/30 border border-indigo-200 dark:border-indigo-800 rounded-lg">
                        <span className="text-xs font-bold text-indigo-700 dark:text-indigo-300">{stats.cold} Baixos</span>
                    </div>
                </div>
            </div>

            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full flex-1 flex flex-col min-h-0">
                <TabsList className="grid w-full grid-cols-3 mb-4 bg-zinc-100 dark:bg-zinc-900 p-1 rounded-xl h-11 gap-1">
                    <TabsTrigger
                        value="hot"
                        className="
                            rounded-lg text-xs
                            data-[state=active]:bg-gradient-to-r data-[state=active]:from-indigo-500 data-[state=active]:to-purple-600
                            data-[state=active]:text-white data-[state=active]:shadow-md
                            data-[state=inactive]:bg-orange-50 data-[state=inactive]:dark:bg-orange-900/20
                            data-[state=inactive]:text-orange-700 data-[state=inactive]:dark:text-orange-300
                            font-semibold transition-all
                            flex items-center justify-center gap-1.5
                        "
                    >
                        <Flame className="w-3.5 h-3.5 flex-shrink-0" />
                        <span className="hidden sm:inline">Quentes</span>
                        <Badge className={`
                            border-0 text-[10px] h-4 px-1.5 flex-shrink-0
                            ${activeTab === 'hot'
                                ? 'bg-white/20 text-white'
                                : 'bg-orange-200 dark:bg-orange-800 text-orange-800 dark:text-orange-200'}
                        `}>
                            {stats.hot}
                        </Badge>
                    </TabsTrigger>
                    <TabsTrigger
                        value="warm"
                        className="
                            rounded-lg text-xs
                            data-[state=active]:bg-gradient-to-r data-[state=active]:from-indigo-500 data-[state=active]:to-purple-600
                            data-[state=active]:text-white data-[state=active]:shadow-md
                            data-[state=inactive]:bg-amber-50 data-[state=inactive]:dark:bg-amber-900/20
                            data-[state=inactive]:text-amber-700 data-[state=inactive]:dark:text-amber-300
                            font-semibold transition-all
                            flex items-center justify-center gap-1.5
                        "
                    >
                        <Clock className="w-3.5 h-3.5 flex-shrink-0" />
                        <span className="hidden sm:inline truncate">Recuperação</span>
                        <Badge className={`
                            border-0 text-[10px] h-4 px-1.5 flex-shrink-0
                            ${activeTab === 'warm'
                                ? 'bg-white/20 text-white'
                                : 'bg-amber-200 dark:bg-amber-800 text-amber-800 dark:text-amber-200'}
                        `}>
                            {stats.warm}
                        </Badge>
                    </TabsTrigger>
                    <TabsTrigger
                        value="cold"
                        className="
                            rounded-lg text-xs
                            data-[state=active]:bg-gradient-to-r data-[state=active]:from-indigo-500 data-[state=active]:to-purple-600
                            data-[state=active]:text-white data-[state=active]:shadow-md
                            data-[state=inactive]:bg-indigo-50 data-[state=inactive]:dark:bg-indigo-900/20
                            data-[state=inactive]:text-indigo-700 data-[state=inactive]:dark:text-indigo-300
                            font-semibold transition-all
                            flex items-center justify-center gap-1.5
                        "
                    >
                        <Archive className="w-3.5 h-3.5 flex-shrink-0" />
                        <span className="hidden sm:inline truncate">Reativação</span>
                        <Badge className={`
                            border-0 text-[10px] h-4 px-1.5 flex-shrink-0
                            ${activeTab === 'cold'
                                ? 'bg-white/20 text-white'
                                : 'bg-indigo-200 dark:bg-indigo-800 text-indigo-800 dark:text-indigo-200'}
                        `}>
                            {stats.cold}
                        </Badge>
                    </TabsTrigger>
                </TabsList>

                <TabsContent value="hot" className="flex-1 overflow-auto mt-0">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {HOT_LEADS.map(lead => <FollowUpCard key={lead.id} lead={lead} type="hot" />)}
                    </div>
                </TabsContent>

                <TabsContent value="warm" className="flex-1 overflow-auto mt-0">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {WARM_LEADS.map(lead => <FollowUpCard key={lead.id} lead={lead} type="warm" />)}
                    </div>
                </TabsContent>

                <TabsContent value="cold" className="flex-1 overflow-auto mt-0">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {COLD_LEADS.map(lead => <FollowUpCard key={lead.id} lead={lead} type="cold" />)}
                    </div>
                </TabsContent>
            </Tabs>

        </div>
    );
};
