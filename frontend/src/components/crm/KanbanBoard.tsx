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
    pointerWithin,
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

// Helper for phone formatting
const formatPhone = (phone: string) => {
    if (!phone) return '';
    const digits = phone.replace(/\D/g, '');
    let clean = digits;
    // Remove prefix 55 if present
    if ((clean.length === 12 || clean.length === 13) && clean.startsWith('55')) {
        clean = clean.substring(2);
    }
    if (clean.length === 11) {
        return `(${clean.substring(0, 2)}) ${clean.substring(2, 7)}-${clean.substring(7)}`;
    }
    if (clean.length === 10) {
        return `(${clean.substring(0, 2)}) ${clean.substring(2, 6)}-${clean.substring(6)}`;
    }
    return phone;
};

// Official Brand Icons (Simple SVG Components)
const GoogleIcon = ({ className }: { className?: string }) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M23.766 12.2764C23.766 11.4607 23.6999 10.6406 23.5588 9.83807H12.24V14.4591H18.7217C18.4528 15.9494 17.5885 17.2678 16.323 18.1056V21.1039H20.19C22.4608 19.0139 23.766 15.9274 23.766 12.2764Z" fill="#4285F4" />
        <path d="M12.2401 24.0008C15.4766 24.0008 18.2059 22.9382 20.1945 21.1039L16.3275 18.1055C15.2517 18.8375 13.8627 19.252 12.2445 19.252C9.11388 19.252 6.45946 17.1399 5.50705 14.3003H1.5166V17.3912C3.55371 21.4434 7.7029 24.0008 12.2401 24.0008Z" fill="#34A853" />
        <path d="M5.50253 14.3003C5.00236 12.8099 5.00236 11.1961 5.50253 9.70575V6.61481H1.51649C-0.18551 10.0056 -0.18551 14.0004 1.51649 17.3912L5.50253 14.3003Z" fill="#FBBC05" />
        <path d="M12.2401 4.74966C13.9509 4.7232 15.6044 5.36697 16.8434 6.54867L20.2695 3.12262C18.1001 1.0855 15.2208 -0.0344664 12.2401 0.000808666C7.7029 0.000808666 3.55371 2.55822 1.5166 6.61481L5.50264 9.70575C6.45064 6.86173 9.10947 4.74966 12.2401 4.74966Z" fill="#EA4335" />
    </svg>
);

const MetaIcon = ({ className }: { className?: string }) => (
    <svg className={className} viewBox="0 0 24 24" fill="#0668E1" xmlns="http://www.w3.org/2000/svg">
        <path d="M24 12.073C24 5.405 18.627 0 12 0S0 5.405 0 12.073C0 18.1 4.415 23.094 10.125 24v-8.437H7.078v-3.49h3.047v-2.642c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.49h-2.796V24C19.585 23.094 24 18.1 24 12.073z" />
    </svg>
);

const InstagramIcon = ({ className }: { className?: string }) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect width="24" height="24" rx="6" fill="url(#ig-grad)" />
        <path d="M12 5.838c3.375 0 3.775.013 5.107.074 1.233.056 1.903.262 2.348.435.59.229 1.01.5 1.452.942.44.44.712.861.94 1.451.173.445.38.1.115.436 2.348.06 1.332.074 1.732.074 5.108 0 3.375-.013 3.775-.074 5.107-.056 1.233-.263 1.903-.436 2.348-.228.59-.5 1.01-.941 1.452-.44.44-.86.712-1.451.94-.445.174-1.115.38-2.348.437-1.332.06-1.732.074-5.107.074-3.375 0-3.775-.013-5.107-.074-1.233-.056-1.903-.263-2.348-.436-.59-.229-1.01-.5-1.452-.942-.44-.44-.712-.86-1.451-.94-.445-.173-1.115-.38-2.348-.436C2.013 15.775 2 15.375 2 12c0-3.375.013-3.775.074-5.107.056-1.233.262-1.903.435-2.348.229-.59.5-1.01.942-1.452.44-.44.861-.712 1.451-.94.174-.445.38-.115.436-2.348.061-1.332.074-1.732.074-5.108zm0-1.838c-3.432 0-3.863.015-5.213.076-1.346.062-2.268.275-3.076.589-.835.325-1.543.76-2.25 1.467-.707.707-1.143 1.415-1.468 2.25-.314.808-.527 1.73-.588 3.076C-1.823 8.137-1.838 8.568-1.838 12s.015 3.863.076 5.213c.061 1.346.274 2.268.588 3.076.325.835.761 1.543 1.468 2.25.707.707 1.415 1.143 2.25 1.468.808.314 1.73.527 3.076.588 1.35.061 1.78.076 5.213.076s3.863-.015 5.213-.076c1.346-.061 2.268-.274 3.076-.588.835-.325 1.543-.76 2.25-1.468.707-.707 1.143-1.415 1.468-2.25.314-.808.527-1.73.588-3.076.061-1.35.076-1.78.076-5.213s-.015-3.863-.076-5.213c-.061-1.346-.274-2.268-.588-3.076-.325-.835-.76-1.543-1.468-2.25-.707-.707-1.415-1.143-2.25-1.468-.808-.314-1.73-.527-3.076-.588-1.35-.061-1.78-.076-5.213-.076z" fill="#fff" />
        <path d="M12 8.824A3.176 3.176 0 1015.176 12 3.18 3.18 0 0012 8.824zm0 8.191A5.015 5.015 0 1117.015 12 5.02 5.02 0 0112 17.015z" fill="#fff" />
        <circle cx="18.406" cy="5.594" r="1.226" fill="#fff" />
        <defs>
            <linearGradient id="ig-grad" x1="2" y1="22" x2="22" y2="2" gradientUnits="userSpaceOnUse">
                <stop stopColor="#f09433" />
                <stop offset=".25" stopColor="#e6683c" />
                <stop offset=".5" stopColor="#dc2743" />
                <stop offset=".75" stopColor="#cc2366" />
                <stop offset="1" stopColor="#bc1888" />
            </linearGradient>
        </defs>
    </svg>
);

// Source icons and colors - Updated with SVGs
const getSourceInfo = (source: Deal['source']) => {
    switch (source) {
        case 'instagram':
            return {
                icon: InstagramIcon,
                color: '', // SVGs have own colors
                bg: 'bg-transparent',
                border: '',
                label: 'Instagram'
            };
        case 'google':
            return {
                icon: GoogleIcon,
                color: '',
                bg: 'bg-white border-zinc-200 dark:bg-zinc-800 dark:border-zinc-700 hover:bg-gray-50',
                border: 'shadow-sm border',
                label: 'Google Ads'
            };
        case 'facebook':
            return {
                icon: MetaIcon,
                color: '',
                bg: 'bg-transparent',
                border: '',
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
    // Format simplified date (e.g. "Hoje 14:00" or "29/12")
    const dateObj = new Date(deal.lastContact);
    const isToday = dateObj.toDateString() === new Date().toDateString();
    const displayDate = isToday
        ? `Hoje ${dateObj.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}`
        : dateObj.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' });

    const sourceInfo = getSourceInfo(deal.source);

    return (
        <Card className={`
            ${stage.cardBg}
            border ${stage.borderColor}
            shadow-sm hover:shadow-md transition-all group relative
            ${isDragging ? 'opacity-50 rotate-2 scale-105' : ''}
        `}>
            <CardContent className="p-2">
                {/* Header: Avatar + Name + Source Icon */}
                <div className="flex items-center gap-2 mb-2">
                    {/* Drag Handle (Hidden unless hovering) */}
                    <div className="absolute left-1 top-3 opacity-0 group-hover:opacity-100 cursor-grab active:cursor-grabbing">
                        <GripVertical className="w-3 h-3 text-zinc-400" />
                    </div>

                    <div className={`rounded-full ${stage.bgLight} border ${stage.borderColor} w-7 h-7 flex items-center justify-center shrink-0 ml-1`}>
                        {deal.patientAvatar ? (
                            <img src={deal.patientAvatar} alt="A" className="w-full h-full object-cover rounded-full" />
                        ) : (
                            <stage.icon className={`w-3.5 h-3.5 ${stage.iconColor}`} />
                        )}
                    </div>

                    <div className="min-w-0 flex-1">
                        <div className="flex items-center justify-between">
                            <h3 className="font-bold text-zinc-900 dark:text-foreground text-xs leading-tight truncate mr-1" title={deal.patientName}>
                                {deal.patientName}
                            </h3>
                            {/* Source Icon Only */}
                            <div title={sourceInfo.label} className={`${sourceInfo.bg} p-1 rounded-full shrink-0`}>
                                <sourceInfo.icon className={`w-3 h-3 ${sourceInfo.color}`} />
                            </div>
                        </div>
                        <div className="flex items-center gap-1 mt-0.5">
                            {deal.probability === 'high' && (
                                <span className="w-1.5 h-1.5 rounded-full bg-orange-500" title="Quente"></span>
                            )}
                            <span className="text-[10px] text-zinc-500 truncate">{formatPhone(deal.phone) || 'Sem fone'}</span>
                        </div>
                    </div>
                </div>

                {/* Footer: Value + Actions */}
                <div className="flex items-center justify-between mt-2 pt-2 border-t border-zinc-100 dark:border-zinc-800/50">
                    <div
                        className="text-[10px] font-semibold text-zinc-700 dark:text-zinc-300 cursor-pointer hover:bg-black/5 rounded px-1 transition-colors"
                        onClick={(e) => { e.stopPropagation(); onEditValue(); }}
                        title="Clique para editar valor"
                    >
                        {deal.value > 0
                            ? new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(deal.value)
                            : <span className="text-zinc-400">R$ --</span>
                        }
                    </div>

                    <div className="flex items-center gap-1">
                        <div className="text-[9px] text-zinc-400 font-medium">
                            {displayDate}
                        </div>
                        <Button
                            onClick={(e) => { e.stopPropagation(); onWhatsApp(); }}
                            size="icon"
                            className="h-6 w-6 bg-[#25D366] hover:bg-[#20bd5a] text-white shadow-sm rounded-full ml-1"
                            title="Abrir WhatsApp"
                        >
                            <MessageCircle className="w-3.5 h-3.5" />
                        </Button>
                    </div>
                </div>

                {/* Campaign ID Mini Badge if exists */}
                {deal.campaignId && (
                    <div className="absolute top-0 right-0 -mt-1 -mr-1">
                        <span className="flex h-2 w-2 relative">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
                        </span>
                    </div>
                )}
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
        data: {
            type: 'column',
            stage: stage
        }
    });

    return (
        <div
            ref={setNodeRef}
            className="flex flex-col min-h-0 h-full"
            data-droppable="true"
            data-stage-id={stage.id}
        >
            {/* Column Header */}
            <div className={`
                ${stage.bgLight} border ${stage.borderColor} p-1.5 rounded-lg shadow-sm mb-1.5
                ${isOver ? 'ring-2 ring-offset-2 ring-indigo-500' : ''}
            `}>
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1.5">
                        <stage.icon className={`w-3.5 h-3.5 ${stage.iconColor}`} />
                        <h2 className={`text-xs font-bold ${stage.textColor} truncate`}>{stage.title}</h2>
                    </div>
                    <Badge className={`${stage.bgLight} ${stage.textColor} border ${stage.borderColor} text-[9px] h-3.5 px-1`}>
                        {deals.length}
                    </Badge>
                </div>
            </div>

            {/* Cards Container */}
            <SortableContext
                items={deals.map(d => d.id)}
                strategy={verticalListSortingStrategy}
            >
                <div className="flex-1 overflow-y-auto space-y-1.5 pr-1 min-h-[100px] custom-scrollbar">
                    {deals.length === 0 ? (
                        <div className="flex flex-col items-center justify-center h-24 text-center">
                            <stage.icon className={`w-6 h-6 ${stage.iconColor} opacity-20 mb-1`} />
                            <p className="text-[10px] text-zinc-400 dark:text-zinc-500">Vazio</p>
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
            if (activeDeal) {
                const originalStage = FUNNEL_STAGES.find(s => s.statuses.includes(activeDeal.status));
                setActiveStage(originalStage || null);
            }
            return;
        }

        const targetStage = FUNNEL_STAGES.find(stage => stage.id === over.id);
        if (targetStage) {
            setActiveStage(targetStage);
            return;
        }

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

        let targetStage = FUNNEL_STAGES.find(stage => stage.id === overId);

        if (!targetStage) {
            const targetDeal = deals.find(d => d.id === overId);
            if (targetDeal) {
                targetStage = FUNNEL_STAGES.find(s => s.statuses.includes(targetDeal.status));
            }
        }

        if (targetStage) {
            const currentDeal = deals.find(d => d.id === activeId);
            const isMovingToNewStage = currentDeal && !targetStage.statuses.includes(currentDeal.status);

            if (isMovingToNewStage && currentDeal) {
                const newStatus = targetStage.statuses[0] as CRMStatus;

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

                try {
                    await crmService.updateDealStatus(activeId, targetStage.title);
                } catch (error) {
                    console.error('Failed to update deal status:', error);
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
            const val = parseFloat(tempValue.replace(',', '.').replace(/^R\$\s?/, ''));
            if (isNaN(val)) {
                alert("Valor inválido");
                return;
            }

            await crmService.updateDealValue(editingDeal.id, val);

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
            collisionDetection={pointerWithin}
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
                            Visualização compacta
                        </p>
                    </div>
                </div>

                {/* Custom Scrollbar Styles */}
                <style>{`
                    .custom-scrollbar::-webkit-scrollbar {
                        width: 4px;
                        height: 4px;
                    }
                    .custom-scrollbar::-webkit-scrollbar-track {
                        background: transparent;
                    }
                    .custom-scrollbar::-webkit-scrollbar-thumb {
                        background-color: rgba(156, 163, 175, 0.3);
                        border-radius: 10px;
                    }
                    .custom-scrollbar::-webkit-scrollbar-thumb:hover {
                        background-color: rgba(156, 163, 175, 0.5);
                    }
                `}</style>

                {/* Kanban Columns - Layout Compacto Fixo (Sem Scroll Horizontal Global) */}
                <div className="flex flex-1 min-h-0 gap-1.5 h-full overflow-hidden">
                    {FUNNEL_STAGES.map(stage => {
                        const stageDeals = getDealsByStage(stage.statuses);
                        return (
                            <div key={stage.id} className="flex-1 min-w-0 h-full flex flex-col">
                                <DroppableColumn
                                    stage={stage}
                                    deals={stageDeals}
                                    onWhatsApp={handleOpenWhatsApp}
                                    onEditValue={handleOpenEditValue}
                                />
                            </div>
                        );
                    })}
                </div>
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
