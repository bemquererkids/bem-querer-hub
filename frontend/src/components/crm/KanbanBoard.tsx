import React, { useState, useEffect, useMemo } from 'react';
import { WhatsAppModal } from './WhatsAppModal';
import { Deal, CRMStatus } from '../../types/crm';
import { crmService, chatService } from '../../services/api';
import {
    Users,
    Calendar,
    CheckCircle2,
    XCircle,
    DollarSign,
    Phone,
    MessageCircle,
    Clock,
    TrendingUp,
    GripVertical,
    Instagram,
    Search,
    Facebook,
    UserCheck,
    Hash,
    Pencil,
} from 'lucide-react';
import { Card, CardContent } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "../ui/dialog";
import {
    DndContext,
    DragEndEvent,
    DragOverlay,
    DragStartEvent,
    PointerSensor,
    useSensor,
    useSensors,
    closestCorners,
    DragOverEvent,
    useDroppable,
} from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy, useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

// Sales Funnel Stages - 6 RAIAS
const FUNNEL_STAGES = [
    {
        id: 'lead',
        title: 'Lead',
        icon: Users,
        bgLight: 'bg-indigo-50 dark:bg-indigo-900/20',
        cardBg: 'bg-indigo-50/50 dark:bg-indigo-900/10',
        textColor: 'text-indigo-700 dark:text-indigo-300',
        iconColor: 'text-indigo-600 dark:text-indigo-400',
        borderColor: 'border-indigo-200 dark:border-indigo-800',
        statuses: ['new']
    },
    {
        id: 'negotiation',
        title: 'Em Negociação',
        icon: MessageCircle,
        bgLight: 'bg-blue-50 dark:bg-blue-900/20',
        cardBg: 'bg-blue-50/50 dark:bg-blue-900/10',
        textColor: 'text-blue-700 dark:text-blue-300',
        iconColor: 'text-blue-600 dark:text-blue-400',
        borderColor: 'border-blue-200 dark:border-blue-800',
        statuses: ['qualifying']
    },
    {
        id: 'scheduled',
        title: 'Agendado',
        icon: Calendar,
        bgLight: 'bg-purple-50 dark:bg-purple-900/20',
        cardBg: 'bg-purple-50/50 dark:bg-purple-900/10',
        textColor: 'text-purple-700 dark:text-purple-300',
        iconColor: 'text-purple-600 dark:text-purple-400',
        borderColor: 'border-purple-200 dark:border-purple-800',
        statuses: ['scheduled']
    },
    {
        id: 'attended',
        title: 'Compareceu',
        icon: CheckCircle2,
        bgLight: 'bg-emerald-50 dark:bg-emerald-900/20',
        cardBg: 'bg-emerald-50/50 dark:bg-emerald-900/10',
        textColor: 'text-emerald-700 dark:text-emerald-300',
        iconColor: 'text-emerald-600 dark:text-emerald-400',
        borderColor: 'border-emerald-200 dark:border-emerald-800',
        statuses: ['attended']
    },
    {
        id: 'noshow',
        title: 'Faltou',
        icon: XCircle,
        bgLight: 'bg-red-50 dark:bg-red-900/20',
        cardBg: 'bg-red-50/50 dark:bg-red-900/10',
        textColor: 'text-red-700 dark:text-red-300',
        iconColor: 'text-red-600 dark:text-red-400',
        borderColor: 'border-red-200 dark:border-red-800',
        statuses: ['noshow', 'lost']
    },
    {
        id: 'won',
        title: 'Venda',
        icon: DollarSign,
        bgLight: 'bg-amber-50 dark:bg-amber-900/20',
        cardBg: 'bg-amber-50/50 dark:bg-amber-900/10',
        textColor: 'text-amber-700 dark:text-amber-300',
        iconColor: 'text-amber-600 dark:text-amber-400',
        borderColor: 'border-amber-200 dark:border-amber-800',
        statuses: ['won']
    },
];

// Source icons and colors
const getSourceInfo = (source: Deal['source']) => {
    switch (source) {
        case 'instagram':
            return {
                icon: Instagram,
                color: 'text-pink-600 dark:text-pink-400',
                bg: 'bg-pink-50 dark:bg-pink-900/20',
                border: 'border-pink-200 dark:border-pink-800',
                label: 'Instagram'
            };
        case 'google':
            return {
                icon: Search,
                color: 'text-blue-600 dark:text-blue-400',
                bg: 'bg-blue-50 dark:bg-blue-900/20',
                border: 'border-blue-200 dark:border-blue-800',
                label: 'Google Ads'
            };
        case 'facebook':
            return {
                icon: Facebook,
                color: 'text-blue-700 dark:text-blue-400',
                bg: 'bg-blue-50 dark:bg-blue-900/20',
                border: 'border-blue-200 dark:border-blue-800',
                label: 'Facebook'
            };
        case 'indication':
            return {
                icon: UserCheck,
                color: 'text-green-600 dark:text-green-400',
                bg: 'bg-green-50 dark:bg-green-900/20',
                border: 'border-green-200 dark:border-green-800',
                label: 'Indicação'
            };
        default:
            return {
                icon: Search,
                color: 'text-zinc-600 dark:text-zinc-400',
                bg: 'bg-zinc-50 dark:bg-zinc-900/20',
                border: 'border-zinc-200 dark:border-zinc-800',
                label: 'Outros'
            };
    }
};

interface DealCardProps {
    deal: Deal;
    stage: typeof FUNNEL_STAGES[0];
    onWhatsApp: () => void;
    onEditValue: () => void;
    isDragging?: boolean;
}

const DealCard = React.memo<DealCardProps>(({ deal, stage, onWhatsApp, onEditValue, isDragging = false }) => {
    const displayDate = new Date(deal.lastContact).toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' });
    const displayTime = new Date(deal.lastContact).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
    const sourceInfo = getSourceInfo(deal.source);

    return (
        <Card className={`
            ${stage.cardBg}
            border ${stage.borderColor}
            shadow-sm hover:shadow-md transition-all group
            ${isDragging ? 'opacity-50 rotate-2 scale-105' : ''}
        `}>
            <CardContent className="p-3 overflow-hidden">
                <div className="flex items-start gap-2 mb-2">
                    <GripVertical className="w-4 h-4 text-zinc-400 dark:text-zinc-500 cursor-grab active:cursor-grabbing flex-shrink-0 mt-0.5" />
                    <div className="flex-1 min-w-0">
                        <div className="flex justify-between items-start mb-2">
                            <div className="flex items-center gap-1.5">
                                <div className={`rounded-full ${stage.bgLight} border ${stage.borderColor} overflow-hidden w-9 h-9 flex items-center justify-center shrink-0`}>
                                    {deal.patientAvatar ? (
                                        <img src={deal.patientAvatar} alt="A" className="w-full h-full object-cover" />
                                    ) : (
                                        <stage.icon className={`w-5 h-5 ${stage.iconColor}`} />
                                    )}
                                </div>
                                <div className="min-w-0 flex-1 overflow-hidden">
                                    <h3 className="font-bold text-zinc-900 dark:text-foreground text-sm leading-tight truncate max-w-full">{deal.patientName}</h3>
                                    <p className="text-[10px] text-zinc-500 dark:text-muted-foreground truncate">Particular</p>
                                </div>
                            </div>
                            {deal.probability === 'high' && (
                                <Badge className="bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400 border-orange-200 dark:border-orange-800 text-[9px] h-4 px-1.5">
                                    Quente
                                </Badge>
                            )}
                        </div>

                        <div className="space-y-1.5 mb-2.5">
                            {/* Source with logo and campaign ID */}
                            <div className={`flex items-center gap-1.5 p-1.5 rounded-full ${sourceInfo.bg} border ${sourceInfo.border}`}>
                                <sourceInfo.icon className={`w-3.5 h-3.5 ${sourceInfo.color}`} />
                                <div className="flex-1 min-w-0">
                                    <p className={`text-[10px] font-semibold ${sourceInfo.color}`}>{sourceInfo.label}</p>
                                    {deal.campaignId && (
                                        <div className="flex items-center gap-0.5">
                                            <Hash className="w-2.5 h-2.5 text-zinc-400" />
                                            <p className="text-[9px] text-zinc-500 dark:text-zinc-400 font-mono">{deal.campaignId}</p>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {deal.phone && (
                                <div className="flex items-center gap-1.5 text-[11px] text-zinc-600 dark:text-zinc-400">
                                    <Phone className="w-3 h-3" />
                                    <span>{deal.phone}</span>
                                </div>
                            )}
                            <div className="flex items-center gap-1.5 text-[11px] text-zinc-500 dark:text-muted-foreground">
                                <Clock className="w-3 h-3" />
                                <span>{displayDate} às {displayTime}</span>
                                {/* Show "Movido agora" if moved in last 30 seconds */}
                                {(() => {
                                    const movedSecondsAgo = (Date.now() - new Date(deal.lastContact).getTime()) / 1000;
                                    if (movedSecondsAgo < 30) {
                                        return (
                                            <Badge className="bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-300 border-indigo-200 dark:border-indigo-800 text-[8px] h-3.5 px-1 animate-pulse font-semibold">
                                                Movido agora
                                            </Badge>
                                        );
                                    }
                                    return null;
                                })()}
                            </div>
                        </div>

                        {/* Deal Value */}
                        <div className="flex items-center justify-between text-[11px] font-medium text-zinc-700 dark:text-zinc-300 bg-zinc-50 dark:bg-zinc-800/50 p-1 rounded border border-zinc-100 dark:border-zinc-800">
                            <span>{new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(deal.value || 0)}</span>
                            <Button variant="ghost" size="icon" className="h-4 w-4 hover:bg-zinc-200 dark:hover:bg-zinc-700" onClick={(e) => { e.stopPropagation(); onEditValue(); }}>
                                <Pencil className="w-2.5 h-2.5" />
                            </Button>
                        </div>

                        <Button
                            onClick={onWhatsApp}
                            className="w-full bg-[#25D366] hover:bg-[#20bd5a] text-white font-semibold h-7 gap-1 shadow-sm text-[11px]"
                        >
                            <MessageCircle className="w-3 h-3" /> WhatsApp
                        </Button>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
});

DealCard.displayName = 'DealCard';

const SortableDealCard: React.FC<DealCardProps> = (props) => {
    const {
        attributes,
        listeners,
        setNodeRef,
        transform,
        transition,
        isDragging,
    } = useSortable({ id: props.deal.id });

    const style = {
        transform: CSS.Transform.toString(transform),
        transition,
    };

    return (
        <div ref={setNodeRef} style={style} {...attributes} {...listeners} id={`deal-${props.deal.id}`}>
            <DealCard {...props} isDragging={isDragging} />
        </div>
    );
};

// Droppable Column Component
const DroppableColumn: React.FC<{
    stage: typeof FUNNEL_STAGES[0];
    deals: Deal[];
    onWhatsApp: (deal: Deal) => void;
    onEditValue: (deal: Deal) => void;
}> = ({ stage, deals, onWhatsApp, onEditValue }) => {
    const { setNodeRef, isOver } = useDroppable({
        id: stage.id,
    });

    return (
        <div ref={setNodeRef} className="flex flex-col min-h-0 h-full">
            {/* Column Header */}
            <div className={`
                ${stage.bgLight} border ${stage.borderColor} p-2.5 rounded-lg shadow-sm mb-2
                ${isOver ? 'ring-2 ring-offset-2 ring-indigo-500' : ''}
            `}>
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1.5">
                        <stage.icon className={`w-4 h-4 ${stage.iconColor}`} />
                        <h2 className={`text-sm font-bold ${stage.textColor}`}>{stage.title}</h2>
                    </div>
                    <Badge className={`${stage.bgLight} ${stage.textColor} border ${stage.borderColor} text-[10px] h-4 px-1.5`}>
                        {deals.length}
                    </Badge>
                </div>
            </div>

            {/* Cards Container */}
            <SortableContext
                items={deals.map(d => d.id)}
                strategy={verticalListSortingStrategy}
            >
                <div className="flex-1 overflow-y-auto space-y-2 pr-1 min-h-[100px]">
                    {deals.length === 0 ? (
                        <div className="flex flex-col items-center justify-center h-32 text-center">
                            <stage.icon className={`w-8 h-8 ${stage.iconColor} opacity-30 mb-2`} />
                            <p className="text-[11px] text-zinc-400 dark:text-zinc-500">Arraste cards aqui</p>
                        </div>
                    ) : (
                        deals.map(deal => (
                            <SortableDealCard
                                key={deal.id}
                                deal={deal}
                                stage={stage}
                                onWhatsApp={() => onWhatsApp(deal)}
                                onEditValue={() => onEditValue(deal)}
                            />
                        ))
                    )}
                </div>
            </SortableContext>
        </div>
    );
};

export const KanbanBoard: React.FC<{ highlightDealId?: string | null }> = ({ highlightDealId }) => {
    const [deals, setDeals] = useState<Deal[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedDeal, setSelectedDeal] = useState<Deal | null>(null);
    const [showWhatsAppModal, setShowWhatsAppModal] = useState(false);
    const [activeDeal, setActiveDeal] = useState<Deal | null>(null);
    const [activeStage, setActiveStage] = useState<typeof FUNNEL_STAGES[0] | null>(null);

    // Value Editing State
    const [editValueModalOpen, setEditValueModalOpen] = useState(false);
    const [tempValue, setTempValue] = useState('');
    const [editingDeal, setEditingDeal] = useState<Deal | null>(null);

    const sensors = useSensors(
        useSensor(PointerSensor, {
            activationConstraint: {
                distance: 8,
            },
        })
    );

    useEffect(() => {
        const fetchDeals = async () => {
            try {
                const data = await crmService.getDeals();
                setDeals(data);
            } catch (error) {
                console.error("Failed to fetch deals", error);
                setDeals([]);
            } finally {
                setLoading(false);
            }
        };

        fetchDeals();
    }, []);

    useEffect(() => {
        if (highlightDealId && !loading && deals.length > 0) {
            setTimeout(() => {
                const element = document.getElementById(`deal-${highlightDealId}`);
                if (element) {
                    element.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    element.classList.add('ring-4', 'ring-cyan-500', 'ring-offset-2');
                    setTimeout(() => {
                        element.classList.remove('ring-4', 'ring-cyan-500', 'ring-offset-2');
                    }, 3000);
                }
            }, 500);
        }
    }, [highlightDealId, loading, deals]);

    const getDealsByStage = useMemo(() => {
        return (statuses: string[]) => deals.filter(deal => statuses.includes(deal.status));
    }, [deals]);

    const handleDragStart = (event: DragStartEvent) => {
        const { active } = event;
        const deal = deals.find(d => d.id === active.id);
        if (deal) {
            setActiveDeal(deal);
            const stage = FUNNEL_STAGES.find(s => s.statuses.includes(deal.status));
            setActiveStage(stage || null);
        }
    };

    const handleDragOver = (event: DragOverEvent) => {
        const { over } = event;
        if (!over) {
            // Reset to original stage when not over anything
            if (activeDeal) {
                const originalStage = FUNNEL_STAGES.find(s => s.statuses.includes(activeDeal.status));
                setActiveStage(originalStage || null);
            }
            return;
        }

        // Check if hovering over a droppable column
        const targetStage = FUNNEL_STAGES.find(stage => stage.id === over.id);
        if (targetStage) {
            setActiveStage(targetStage);
            return;
        }

        // Check if hovering over a card (get its parent stage)
        const targetDeal = deals.find(d => d.id === over.id);
        if (targetDeal) {
            const targetDealStage = FUNNEL_STAGES.find(s => s.statuses.includes(targetDeal.status));
            if (targetDealStage) {
                setActiveStage(targetDealStage);
            }
        }
    };

    const handleDragEnd = async (event: DragEndEvent) => {
        const { active, over } = event;
        setActiveDeal(null);
        setActiveStage(null);

        if (!over) return;

        const activeId = active.id as string;
        const overId = over.id as string;

        // Find which stage the card was dropped into
        let targetStage = FUNNEL_STAGES.find(stage => stage.id === overId);
        console.log('[DRAG] Dropped on ID:', overId, 'Found stage:', targetStage?.title);

        // If dropped on a card, find that card's stage
        if (!targetStage) {
            const targetDeal = deals.find(d => d.id === overId);
            if (targetDeal) {
                targetStage = FUNNEL_STAGES.find(s => s.statuses.includes(targetDeal.status));
                console.log('[DRAG] Dropped on card, found stage:', targetStage?.title);
            }
        }

        if (targetStage) {
            const currentDeal = deals.find(d => d.id === activeId);
            const isMovingToNewStage = currentDeal && !targetStage.statuses.includes(currentDeal.status);
            console.log('[DRAG] Current status:', currentDeal?.status, 'Target statuses:', targetStage.statuses, 'Is moving?', isMovingToNewStage);

            if (isMovingToNewStage && currentDeal) {
                const newStatus = targetStage.statuses[0] as CRMStatus;

                // Update deal status and timestamp (optimistic update)
                setDeals(prevDeals =>
                    prevDeals.map(deal =>
                        deal.id === activeId
                            ? {
                                ...deal,
                                status: newStatus,
                                lastContact: new Date().toISOString()
                            }
                            : deal
                    )
                );

                // Persist to backend
                try {
                    await crmService.updateDealStatus(activeId, targetStage.title);
                } catch (error) {
                    console.error('Failed to update deal status:', error);
                    // Revert on error
                    setDeals(prevDeals =>
                        prevDeals.map(deal =>
                            deal.id === activeId
                                ? { ...deal, status: currentDeal.status, lastContact: currentDeal.lastContact }
                                : deal
                        )
                    );
                }
            }
        }
    };

    const handleOpenWhatsApp = (deal: Deal) => {
        setSelectedDeal(deal);
        setShowWhatsAppModal(true);
    };

    const handleSendWhatsApp = async (message: string) => {
        if (!selectedDeal) return;
        try {
            console.log("Sending WhatsApp message to", selectedDeal.id);
            await chatService.sendMessage(selectedDeal.id, message);
            setShowWhatsAppModal(false);
            // Optional: Show success toast
        } catch (error) {
            console.error("Failed to send message", error);
            alert("Erro ao enviar mensagem. Verifique a conexão.");
        }
    };

    const handleOpenEditValue = (deal: Deal) => {
        setEditingDeal(deal);
        setTempValue(deal.value?.toString() || '0');
        setEditValueModalOpen(true);
    };

    const handleSaveValue = async () => {
        if (!editingDeal) return;
        try {
            const val = parseFloat(tempValue.replace(',', '.').replace(/^R\$\s?/, '')); // Simple cleanup
            if (isNaN(val)) {
                alert("Valor inválido");
                return;
            }

            await crmService.updateDealValue(editingDeal.id, val);

            // Optimistic update
            setDeals(prev => prev.map(d => d.id === editingDeal.id ? { ...d, value: val } : d));
            setEditValueModalOpen(false);
        } catch (error) {
            console.error("Failed to update value", error);
            alert("Erro ao atualizar valor.");
        }
    };

    if (loading) {
        return (
            <div className="h-full flex items-center justify-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 dark:border-primary"></div>
            </div>
        );
    }

    return (
        <DndContext
            sensors={sensors}
            collisionDetection={closestCorners}
            onDragStart={handleDragStart}
            onDragOver={handleDragOver}
            onDragEnd={handleDragEnd}
        >
            <div className="p-4 h-full flex flex-col animate-in fade-in slide-in-from-bottom-4 duration-300">
                {/* Header */}
                <div className="flex items-center gap-2 mb-3">
                    <div className="p-1.5 bg-indigo-100 dark:bg-indigo-900/20 rounded-lg border border-indigo-200 dark:border-indigo-800">
                        <TrendingUp className="w-4 h-4 text-indigo-600 dark:text-primary" />
                    </div>
                    <div>
                        <h1 className="text-base font-bold text-zinc-900 dark:text-foreground tracking-tight">Funil de Vendas</h1>
                        <p className="text-[11px] text-zinc-500 dark:text-muted-foreground">
                            Arraste os cards entre as raias para mudar de etapa
                        </p>
                    </div>
                </div>

                {/* Kanban Columns - 6 RAIAS */}
                <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-2 flex-1 min-h-0 overflow-x-auto">
                    {FUNNEL_STAGES.map(stage => {
                        const stageDeals = getDealsByStage(stage.statuses);
                        return (
                            <DroppableColumn
                                key={stage.id}
                                stage={stage}
                                deals={stageDeals}
                                onWhatsApp={handleOpenWhatsApp}
                                onEditValue={handleOpenEditValue}
                            />
                        );
                    })}
                </div>

                {/* Drag Overlay - shows card with current stage color */}
                <DragOverlay>
                    {activeDeal && activeStage ? (
                        <DealCard
                            deal={activeDeal}
                            stage={activeStage}
                            onWhatsApp={() => { }}
                            onEditValue={() => { }}
                            isDragging
                        />
                    ) : null}
                </DragOverlay>
            </div>

            {/* WhatsApp Modal */}
            {showWhatsAppModal && selectedDeal && (
                <WhatsAppModal
                    isOpen={showWhatsAppModal}
                    onClose={() => setShowWhatsAppModal(false)}
                    recipientName={selectedDeal.patientName}
                    recipientPhone={selectedDeal.phone || ''}
                    onSend={handleSendWhatsApp}
                />
            )}

            {/* Edit Value Modal */}
            <Dialog open={editValueModalOpen} onOpenChange={setEditValueModalOpen}>
                <DialogContent className="sm:max-w-[425px]">
                    <DialogHeader>
                        <DialogTitle>Editar Valor do Negócio</DialogTitle>
                        <DialogDescription>
                            Insira o valor estimado para este negócio.
                        </DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                        <div className="grid grid-cols-4 items-center gap-4">
                            <Label htmlFor="value" className="text-right">
                                Valor (R$)
                            </Label>
                            <Input
                                id="value"
                                type="number"
                                value={tempValue}
                                onChange={(e) => setTempValue(e.target.value)}
                                className="col-span-3"
                                placeholder="0.00"
                                step="0.01"
                            />
                        </div>
                    </div>
                    <DialogFooter>
                        <Button type="button" variant="outline" onClick={() => setEditValueModalOpen(false)}>Cancelar</Button>
                        <Button type="button" onClick={handleSaveValue}>Salvar</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </DndContext>
    );
};
