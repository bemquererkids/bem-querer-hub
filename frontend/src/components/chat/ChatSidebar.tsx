import React, { useState } from 'react';
import { ChatContact } from '../../types/chat';
import { Search, Filter, User, CheckCircle2, Calendar, XCircle, DollarSign } from 'lucide-react';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Tabs, TabsList, TabsTrigger } from '../ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import clsx from 'clsx';

interface ChatSidebarProps {
    chats: ChatContact[];
    activeChatId?: string;
    onSelectChat: (chatId: string) => void;
}

export const ChatSidebar: React.FC<ChatSidebarProps> = ({ chats, activeChatId, onSelectChat }) => {
    const [filterTab, setFilterTab] = useState<'all' | 'unread'>('all');
    const [funnelStage, setFunnelStage] = useState<string>('all');

    // Funil Icons Map
    const getStageIcon = (stage: string) => {
        switch(stage) {
            case 'lead': return <User className="w-3 h-3" />;
            case 'scheduled': return <Calendar className="w-3 h-3" />;
            case 'attended': return <CheckCircle2 className="w-3 h-3" />;
            case 'noshow': return <XCircle className="w-3 h-3" />;
            case 'won': return <DollarSign className="w-3 h-3" />;
            default: return null;
        }
    };

    // Filter Logic (Mocked for now as mock data might not have all fields)
    const filteredChats = chats.filter(chat => {
        if (filterTab === 'unread' && chat.unreadCount === 0) return false;
        // if (funnelStage !== 'all' && chat.stage !== funnelStage) return false; // Needs stage in mock data
        return true;
    });

    return (
        <div className="w-80 flex flex-col h-full border-r border-border bg-white">
            
            {/* 1. SEARCH */}
            <div className="p-4 pb-2">
                <div className="relative">
                    <Input 
                        type="text" 
                        placeholder="Buscar contato..." 
                        className="pl-9 bg-slate-50 border-slate-200 rounded-lg"
                    />
                    <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                </div>
            </div>

            {/* 2. TABS (Todas | Não lidas) */}
            <div className="px-4 pb-3">
                 <Tabs defaultValue="all" onValueChange={(v) => setFilterTab(v as any)} className="w-full">
                    <TabsList className="w-full grid grid-cols-2 bg-slate-100 p-1 rounded-lg">
                        <TabsTrigger value="all" className="data-[state=active]:bg-[#1a97d4] data-[state=active]:text-white rounded-md text-xs font-bold transition-all">
                            Todas
                        </TabsTrigger>
                        <TabsTrigger value="unread" className="data-[state=active]:bg-[#1a97d4] data-[state=active]:text-white rounded-md text-xs font-bold transition-all gap-2">
                            Não lidas 
                            <span className="bg-green-500 text-white text-[9px] px-1.5 py-0.5 rounded-full">26</span>
                        </TabsTrigger>
                    </TabsList>
                </Tabs>
            </div>

            {/* 3. FILTERS (Etapa do Funil) */}
            <div className="px-4 pb-3 border-b border-slate-100">
                <div className="flex items-center gap-2">
                    <Filter className="w-4 h-4 text-slate-400" />
                    <span className="text-sm text-slate-500 font-medium">Filtros:</span>
                    
                    <Select defaultValue="all" onValueChange={setFunnelStage}>
                        <SelectTrigger className="w-[140px] h-8 text-xs border-slate-200 bg-white shadow-sm rounded-md">
                            <SelectValue placeholder="Etapa do Funil" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="all">Todas as etapas</SelectItem>
                            <SelectItem value="lead">
                                <div className="flex items-center gap-2"><User className="w-3 h-3 text-slate-500"/> Lead</div>
                            </SelectItem>
                            <SelectItem value="scheduled">
                                <div className="flex items-center gap-2"><Calendar className="w-3 h-3 text-amber-500"/> Agendado</div>
                            </SelectItem>
                            <SelectItem value="attended">
                                <div className="flex items-center gap-2"><CheckCircle2 className="w-3 h-3 text-green-500"/> Compareceu</div>
                            </SelectItem>
                            <SelectItem value="noshow">
                                <div className="flex items-center gap-2"><XCircle className="w-3 h-3 text-red-500"/> Faltou</div>
                            </SelectItem>
                            <SelectItem value="won">
                                <div className="flex items-center gap-2"><DollarSign className="w-3 h-3 text-purple-500"/> Venda</div>
                            </SelectItem>
                        </SelectContent>
                    </Select>
                </div>
            </div>

            {/* 4. CHAT LIST */}
            <div className="flex-1 overflow-y-auto custom-scrollbar bg-slate-50/30">
                
                {/* Archived Header (Visual Reference) */}
                <div className="flex items-center gap-3 px-4 py-3 cursor-pointer hover:bg-slate-50 border-b border-slate-100 opacity-60">
                    <div className="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center border border-slate-200">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-slate-400"><rect width="20" height="5" x="2" y="3" rx="1"/><path d="M4 8v11a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8"/><path d="M10 12h4"/></svg>
                    </div>
                    <div>
                        <h4 className="text-sm font-bold text-slate-700">Arquivadas</h4>
                        <p className="text-xs text-slate-500">Conversas arquivadas</p>
                    </div>
                </div>

                {filteredChats.map((chat) => (
                    <div 
                        key={chat.id}
                        onClick={() => onSelectChat(chat.id)}
                        className={clsx(
                            "px-4 py-3 cursor-pointer transition-all border-b border-slate-100 hover:bg-white",
                            activeChatId === chat.id ? "bg-blue-50/50" : "bg-transparent"
                        )}
                    >
                        <div className="flex justify-between items-start mb-1">
                            <div className="flex items-center gap-3 w-full">
                                <div className="relative">
                                    <div className="w-10 h-10 rounded-full bg-slate-200 overflow-hidden">
                                        <img src={`https://ui-avatars.com/api/?name=${chat.name.replace(' ', '+')}&background=random`} alt={chat.name} />
                                    </div>
                                    {/* Online Status Dot */}
                                    <div className="absolute bottom-0 right-0 w-2.5 h-2.5 bg-green-500 border-2 border-white rounded-full"></div>
                                </div>
                                
                                <div className="flex-1 min-w-0">
                                    <div className="flex justify-between items-center mb-0.5">
                                        <h3 className="font-bold text-sm text-slate-800 truncate max-w-[120px]">
                                            {chat.name}
                                        </h3>
                                        <span className={clsx("text-[10px]", chat.unreadCount > 0 ? "text-green-600 font-bold" : "text-slate-400")}>
                                            {chat.lastMessageTime}
                                        </span>
                                    </div>
                                    
                                    <p className="text-xs text-slate-500 truncate mb-1.5 flex items-center gap-1">
                                        {/* Read Receipt Mock */}
                                        <span className="text-blue-500">✓✓</span> 
                                        {chat.lastMessage}
                                    </p>

                                    {/* Funnel Stage Badge */}
                                    <div className="flex gap-1.5 flex-wrap">
                                        {/* Mocking Stage based on tags for now */}
                                        <Badge 
                                            variant="outline" 
                                            className="text-[10px] px-2 py-0 h-5 font-normal border-slate-200 bg-white text-slate-600 gap-1"
                                        >
                                            <User className="w-3 h-3 text-slate-400" /> Lead
                                        </Badge>
                                        
                                        {chat.tags.includes('financial') && (
                                             <Badge variant="outline" className="text-[10px] px-2 py-0 h-5 font-normal border-purple-200 bg-purple-50 text-purple-700 gap-1">
                                                <DollarSign className="w-3 h-3" /> Venda
                                            </Badge>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};
