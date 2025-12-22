import React, { useState, useEffect } from 'react';
import { Deal } from '../../types/crm';
import { crmService } from '../../services/api';
import { Loader2, Search, Calendar as CalendarIcon, MoreVertical, Phone, Target, CalendarCheck, CheckCircle2, XCircle } from 'lucide-react';
import { Input } from '../ui/input';
import { Button } from '../ui/button';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../ui/tabs';
import { Card, CardContent } from '../ui/card';
import { Badge } from '../ui/badge';
import clsx from 'clsx';

// --- NEW CARD COMPONENT (Matching Reference) ---
interface CRMCardProps {
    deal: Deal;
    type: 'lead' | 'appointment' | 'sale';
    onStatusUpdate: (id: string, status: string) => void;
}

const CRMCard: React.FC<CRMCardProps> = ({ deal, type, onStatusUpdate }) => {
    // Mock random data for visual fidelity to reference
    const mockId = Math.floor(Math.random() * 90000) + 10000;
    const mockPhone = "5511999999999";
    const mockDate = new Date().toLocaleDateString('pt-BR');
    const mockTime = "09:30";

    return (
        <Card className="hover:shadow-md transition-shadow border-slate-200">
            <CardContent className="p-5">
                {/* Header */}
                <div className="flex justify-between items-start mb-3">
                    <div className="flex flex-col gap-1">
                        <div className="flex items-center gap-2">
                            <span className="text-xs font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
                                {type === 'appointment' ? `Agendamento #${mockId}` : `Lead #${mockId}`}
                            </span>
                            {type === 'lead' && <span className="text-[10px] text-slate-400">há 2 horas</span>}
                            {type === 'appointment' && <span className="text-[10px] text-slate-400">há 11 horas</span>}
                        </div>
                        {type === 'lead' && (
                            <Badge variant="secondary" className="w-fit bg-emerald-100 text-emerald-700 hover:bg-emerald-200 text-[10px] px-2 h-5">
                                Novo
                            </Badge>
                        )}
                        {type === 'appointment' && (
                             <Badge variant="secondary" className="w-fit bg-orange-100 text-orange-700 hover:bg-orange-200 text-[10px] px-2 h-5">
                                Clinicorp: Sincronizado
                            </Badge>
                        )}
                    </div>
                    <Button variant="ghost" size="icon" className="h-6 w-6 text-slate-400">
                        <MoreVertical className="w-4 h-4" />
                    </Button>
                </div>

                {/* Body */}
                <div className="space-y-3 mb-4">
                    <h3 className="font-bold text-slate-800 text-lg">{deal.patientName}</h3>
                    
                    <div className="flex items-center gap-2 text-sm text-slate-500">
                        <Phone className="w-4 h-4" />
                        <span>{mockPhone}</span>
                    </div>

                    {type === 'lead' && (
                        <div className="flex items-center gap-2 text-sm text-slate-500">
                            <Target className="w-4 h-4" />
                            <span className="truncate max-w-[200px]">Mídia: Google Ads (Campanha X)</span>
                        </div>
                    )}

                    {type === 'appointment' && (
                        <div className="flex items-center gap-2 text-sm text-slate-500">
                            <CalendarIcon className="w-4 h-4" />
                            <span>{mockDate}, {mockTime}</span>
                        </div>
                    )}
                </div>

                {/* Footer Actions */}
                <div className="pt-4 border-t border-slate-100 flex gap-3">
                    {type === 'lead' && (
                        <Button 
                            variant="outline" 
                            className="w-full border-slate-200 text-slate-600 hover:text-blue-600 hover:border-blue-200"
                            onClick={() => onStatusUpdate(deal.id, 'scheduled')}
                        >
                            <CalendarIcon className="w-4 h-4 mr-2" /> Agendar Consulta
                        </Button>
                    )}

                    {type === 'appointment' && (
                        <>
                            <Button 
                                className="flex-1 bg-emerald-500 hover:bg-emerald-600 text-white h-9 text-xs"
                                onClick={() => onStatusUpdate(deal.id, 'attended')}
                            >
                                <CheckCircle2 className="w-3 h-3 mr-1.5" /> Compareceu
                            </Button>
                            <Button 
                                variant="destructive" 
                                className="flex-1 h-9 text-xs"
                                onClick={() => onStatusUpdate(deal.id, 'noshow')}
                            >
                                <XCircle className="w-3 h-3 mr-1.5" /> Faltou
                            </Button>
                        </>
                    )}
                </div>
            </CardContent>
        </Card>
    );
};

// --- MAIN PAGE COMPONENT ---

export const KanbanBoard: React.FC = () => {
    const [activeTab, setActiveTab] = useState('leads');
    const [deals, setDeals] = useState<Deal[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchDeals = async () => {
            try {
                 const data = await crmService.getDeals();
                 setDeals(data);
            } catch (error) {
                console.error("Failed to fetch deals", error);
            } finally {
                setLoading(false);
            }
        };
        fetchDeals();
    }, []);

    const handleStatusUpdate = async (id: string, newStatus: string) => {
        // 1. Optimistic Update (Remove from current view instantly)
        setDeals(current => current.filter(d => d.id !== id));
        
        try {
            // 2. Call API
            await crmService.updateDealStatus(id, newStatus);
            console.log(`Deal ${id} updated to ${newStatus}`);
        } catch (error) {
            console.error("Failed to update status", error);
            // Revert would happen here in a robust app
        }
    };

    // Filter deals based on active tab (Mock Logic)
    const getFilteredDeals = () => {
        return deals; 
    };

    const currentDeals = getFilteredDeals();

    if (loading) {
        return <div className="flex justify-center items-center h-full"><Loader2 className="animate-spin text-primary" /></div>;
    }

    return (
        <div className="p-8 h-full flex flex-col space-y-6">
            
            {/* 1. TOP CONTROLS */}
            <div className="flex flex-col md:flex-row gap-4 justify-between bg-white p-4 rounded-xl shadow-sm border border-slate-100">
                <div className="flex items-center gap-3">
                    <Button variant="outline" className="w-[180px] justify-start text-left font-normal text-slate-500">
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        Todas as datas
                    </Button>
                    <Button variant="outline" className="w-[180px] justify-start text-left font-normal text-slate-500">
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        Selecionar período...
                    </Button>
                </div>
                <div className="relative w-full md:w-[300px]">
                     <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
                     <Input placeholder="Buscar por nome ou telefone" className="pl-9 bg-slate-50 border-slate-200" />
                </div>
            </div>

            {/* 2. TABS & GRID */}
            <Tabs defaultValue="leads" className="flex-1 flex flex-col" onValueChange={setActiveTab}>
                <TabsList className="w-full justify-start h-12 bg-transparent p-0 gap-6 border-b border-slate-200 mb-6 rounded-none">
                    <TabsTrigger 
                        value="leads" 
                        className="rounded-none border-b-2 border-transparent data-[state=active]:border-blue-600 data-[state=active]:shadow-none px-4 py-3 text-slate-500 data-[state=active]:text-blue-600 bg-transparent"
                    >
                        <div className="flex items-center gap-2">
                            <span className="font-bold">Leads</span>
                            <Badge variant="secondary" className="bg-slate-100 text-slate-600">1862</Badge>
                        </div>
                    </TabsTrigger>
                    <TabsTrigger 
                        value="appointments" 
                        className="rounded-none border-b-2 border-transparent data-[state=active]:border-blue-600 data-[state=active]:shadow-none px-4 py-3 text-slate-500 data-[state=active]:text-blue-600 bg-transparent"
                    >
                         <div className="flex items-center gap-2">
                            <span className="font-bold">Agendamentos</span>
                            <Badge variant="secondary" className="bg-blue-50 text-blue-600">730</Badge>
                        </div>
                    </TabsTrigger>
                    <TabsTrigger 
                        value="noshows" 
                        className="rounded-none border-b-2 border-transparent data-[state=active]:border-blue-600 data-[state=active]:shadow-none px-4 py-3 text-slate-500 data-[state=active]:text-blue-600 bg-transparent"
                    >
                         <div className="flex items-center gap-2">
                            <span className="font-bold">No-Shows</span>
                            <Badge variant="secondary" className="bg-slate-100 text-slate-600">173</Badge>
                        </div>
                    </TabsTrigger>
                    <TabsTrigger 
                        value="attended" 
                        className="rounded-none border-b-2 border-transparent data-[state=active]:border-blue-600 data-[state=active]:shadow-none px-4 py-3 text-slate-500 data-[state=active]:text-blue-600 bg-transparent"
                    >
                         <div className="flex items-center gap-2">
                            <span className="font-bold">Comparecimentos</span>
                            <Badge variant="secondary" className="bg-slate-100 text-slate-600">481</Badge>
                        </div>
                    </TabsTrigger>
                    <TabsTrigger 
                        value="sales" 
                        className="rounded-none border-b-2 border-transparent data-[state=active]:border-blue-600 data-[state=active]:shadow-none px-4 py-3 text-slate-500 data-[state=active]:text-blue-600 bg-transparent"
                    >
                         <div className="flex items-center gap-2">
                            <span className="font-bold">Vendas</span>
                            <Badge variant="secondary" className="bg-slate-100 text-slate-600">43</Badge>
                        </div>
                    </TabsTrigger>
                </TabsList>

                {/* CONTENT AREA */}
                <div className="flex-1 overflow-y-auto custom-scrollbar">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 pb-20">
                        {currentDeals.map((deal) => (
                            <CRMCard 
                                key={deal.id} 
                                deal={deal} 
                                type={activeTab === 'leads' ? 'lead' : 'appointment'}
                                onStatusUpdate={handleStatusUpdate}
                            />
                        ))}
                         {/* Duplicating data to fill grid for visual check */}
                         {currentDeals.map((deal) => (
                            <CRMCard 
                                key={`${deal.id}-dup`} 
                                deal={deal} 
                                type={activeTab === 'leads' ? 'lead' : 'appointment'}
                                onStatusUpdate={handleStatusUpdate}
                            />
                        ))}
                    </div>
                </div>
            </Tabs>
        </div>
    );
};
