import React from 'react';
import { Deal } from '../../types/crm';
import { MoreHorizontal, DollarSign, AlertCircle, Instagram, Facebook, Chrome, Users } from 'lucide-react';
import clsx from 'clsx';
import { DraggableProvided } from '@hello-pangea/dnd';

interface KanbanCardProps {
    deal: Deal;
    provided: DraggableProvided;
    isDragging: boolean;
}

const SourceIcon = ({ source }: { source: string }) => {
    switch (source) {
        case 'instagram':
            return <div className="bg-pink-100 p-1 rounded-full"><Instagram className="w-3 h-3 text-pink-600" /></div>;
        case 'facebook':
            return <div className="bg-blue-100 p-1 rounded-full"><Facebook className="w-3 h-3 text-blue-600" /></div>;
        case 'google':
            return <div className="bg-green-100 p-1 rounded-full"><Chrome className="w-3 h-3 text-green-600" /></div>;
        case 'indication':
            return <div className="bg-orange-100 p-1 rounded-full"><Users className="w-3 h-3 text-orange-600" /></div>;
        default:
            return <div className="bg-gray-100 p-1 rounded-full"><Chrome className="w-3 h-3 text-gray-600" /></div>;
    }
};

const formatSource = (source: string) => {
    const map: Record<string, string> = {
        instagram: 'Instagram',
        facebook: 'Facebook',
        google: 'Google',
        indication: 'Indicação'
    };
    return map[source] || source.charAt(0).toUpperCase() + source.slice(1);
};

export const KanbanCard: React.FC<KanbanCardProps> = ({ deal, provided, isDragging }) => {
    return (
        <div
            ref={provided.innerRef}
            {...provided.draggableProps}
            {...provided.dragHandleProps}
            style={{
                ...provided.draggableProps.style,
            }}
            className={clsx(
                "bg-white p-3 rounded-lg shadow-sm border border-gray-100 transition-all mb-3 group",
                isDragging ? "shadow-lg rotate-2 scale-105 z-50 ring-2 ring-primary/20" : "hover:shadow-md"
            )}
        >
            <div className="flex justify-between items-center mb-2">
                <div className="flex items-center gap-2" title={`Origem: ${deal.source}`}>
                    <SourceIcon source={deal.source} />
                    <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wide">
                        {formatSource(deal.source)}
                    </span>
                </div>
                <button className="text-gray-400 hover:text-gray-600 opacity-0 group-hover:opacity-100 transition-opacity">
                    <MoreHorizontal className="w-4 h-4" />
                </button>
            </div>
            
            <h4 className="font-semibold text-gray-800 mb-1">{deal.patientName}</h4>
            
            {deal.treatmentType && (
                <p className="text-xs text-gray-500 mb-2">{deal.treatmentType}</p>
            )}

            <div className="flex items-center justify-between text-xs text-gray-400 mt-3 pt-2 border-t border-gray-50">
                <div className="flex items-center gap-1">
                    {deal.value ? (
                        <span className="text-green-600 font-bold">
                            {deal.value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                        </span>
                    ) : (
                        <span className="flex items-center gap-1">
                            <AlertCircle className="w-3 h-3" /> Em av.
                        </span>
                    )}
                </div>
                <span>{deal.lastContact}</span>
            </div>
        </div>
    );
};
