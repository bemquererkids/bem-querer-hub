import React from 'react';
import { Card, CardContent } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { 
    Flame, 
    Snowflake, 
    Clock, 
    MessageCircle, 
    Phone, 
    CalendarX, 
    CheckCircle2, 
    ArrowRight 
} from 'lucide-react';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../ui/tabs';

// Mock Data for Follow-up Lists
const HOT_LEADS = [
    { id: 1, name: "Fernanda Costa", reason: "Pediu para chamar hoje", script: "Oi Fernanda! Como combinamos, estou passando para ver sobre o agendamento.", time: "Hoje, 09:00", tags: ["Cartão Virou"] },
    { id: 2, name: "Marcos Silva", reason: "Verificar com esposa", script: "Olá Marcos! Conseguiu conversar com sua esposa sobre o tratamento?", time: "Hoje, 14:00", tags: ["Decisor"] },
];

const WARM_LEADS = [
    { id: 3, name: "Juliana Paes", reason: "Visualizou orçamento há 48h", script: "Oi Juliana, ficou alguma dúvida sobre o valor do clareamento?", time: "Há 2 dias", tags: ["Vácuo"] },
    { id: 4, name: "Roberto Carlos", reason: "Faltou e não reagendou", script: "Roberto, vi que não conseguiu vir. Vamos remarcar para não atrasar o tratamento?", time: "Ontem", tags: ["No-Show"] },
];

const COLD_LEADS = [
    { id: 5, name: "Ana Maria", reason: "Limpeza há 6 meses", script: "Oi Ana! Faz 6 meses do seu último sorriso aqui. Vamos agendar a limpeza?", time: "6 meses", tags: ["Recorrência"] },
    { id: 6, name: "Pedro Bial", reason: "Orçamento antigo (Implante)", script: "Pedro, temos uma condição especial para implantes este mês. Vamos retomar?", time: "1 ano", tags: ["Resgate"] },
];

const FollowUpCard = ({ lead, type }: { lead: any, type: 'hot' | 'warm' | 'cold' }) => {
    let Icon = Clock;
    let iconColor = "text-slate-400";
    let bgIcon = "bg-slate-100";

    if (type === 'hot') { Icon = Flame; iconColor = "text-orange-500"; bgIcon = "bg-orange-100"; }
    if (type === 'warm') { Icon = Clock; iconColor = "text-amber-500"; bgIcon = "bg-amber-100"; }
    if (type === 'cold') { Icon = Snowflake; iconColor = "text-blue-500"; bgIcon = "bg-blue-100"; }

    return (
        <Card className="hover:shadow-md transition-all border-slate-200 group">
            <CardContent className="p-5">
                <div className="flex justify-between items-start mb-3">
                    <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-full ${bgIcon}`}>
                            <Icon className={`w-5 h-5 ${iconColor}`} />
                        </div>
                        <div>
                            <h3 className="font-bold text-slate-800 text-lg">{lead.name}</h3>
                            <p className="text-xs text-slate-500 flex items-center gap-1">
                                {lead.reason} • <span className="font-semibold">{lead.time}</span>
                            </p>
                        </div>
                    </div>
                    <div className="flex gap-1">
                        {lead.tags.map((tag: string) => (
                            <Badge key={tag} variant="outline" className="text-[10px] bg-slate-50 border-slate-200 text-slate-600">
                                {tag}
                            </Badge>
                        ))}
                    </div>
                </div>

                {/* Script Suggestion Box */}
                <div className="bg-slate-50 p-3 rounded-lg border border-slate-100 mb-4 relative">
                    <div className="absolute -top-2 left-4 bg-white px-2 text-[10px] font-bold text-slate-400 uppercase tracking-wide border border-slate-100 rounded">
                        Sugestão de Script
                    </div>
                    <p className="text-sm text-slate-600 italic">"{lead.script}"</p>
                </div>

                <Button className="w-full bg-[#25D366] hover:bg-[#20bd5a] text-white font-bold h-10 gap-2 shadow-sm">
                    <MessageCircle className="w-4 h-4" /> Chamar no WhatsApp
                </Button>
            </CardContent>
        </Card>
    );
};

export const FollowUpPage: React.FC = () => {
    return (
        <div className="p-8 h-full flex flex-col space-y-6 animate-in fade-in duration-500">
            
            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
                    <CheckCircle2 className="w-6 h-6 text-blue-600" /> Follow-up Ativo
                </h1>
                <p className="text-slate-500 mt-1">
                    Lista de contatos prioritários para hoje. Não deixe ninguém esfriar! 🔥
                </p>
            </div>

            {/* Tabs */}
            <Tabs defaultValue="hot" className="w-full">
                <TabsList className="grid w-full grid-cols-3 mb-8 bg-slate-100 p-1 rounded-xl h-12">
                    <TabsTrigger value="hot" className="rounded-lg data-[state=active]:bg-white data-[state=active]:shadow-sm text-slate-500 data-[state=active]:text-orange-600 font-bold transition-all">
                        <Flame className="w-4 h-4 mr-2" /> Quentes (Hoje)
                        <Badge className="ml-2 bg-orange-500 hover:bg-orange-600 border-0">{HOT_LEADS.length}</Badge>
                    </TabsTrigger>
                    <TabsTrigger value="warm" className="rounded-lg data-[state=active]:bg-white data-[state=active]:shadow-sm text-slate-500 data-[state=active]:text-amber-600 font-bold transition-all">
                        <Clock className="w-4 h-4 mr-2" /> Recuperação
                        <Badge className="ml-2 bg-amber-500 hover:bg-amber-600 border-0">{WARM_LEADS.length}</Badge>
                    </TabsTrigger>
                    <TabsTrigger value="cold" className="rounded-lg data-[state=active]:bg-white data-[state=active]:shadow-sm text-slate-500 data-[state=active]:text-blue-600 font-bold transition-all">
                        <Snowflake className="w-4 h-4 mr-2" /> Reativação
                        <Badge className="ml-2 bg-blue-500 hover:bg-blue-600 border-0">{COLD_LEADS.length}</Badge>
                    </TabsTrigger>
                </TabsList>

                <TabsContent value="hot" className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {HOT_LEADS.map(lead => <FollowUpCard key={lead.id} lead={lead} type="hot" />)}
                    </div>
                </TabsContent>

                <TabsContent value="warm" className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {WARM_LEADS.map(lead => <FollowUpCard key={lead.id} lead={lead} type="warm" />)}
                    </div>
                </TabsContent>

                <TabsContent value="cold" className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {COLD_LEADS.map(lead => <FollowUpCard key={lead.id} lead={lead} type="cold" />)}
                    </div>
                </TabsContent>
            </Tabs>

        </div>
    );
};
