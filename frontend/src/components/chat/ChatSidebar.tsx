import React, { useState } from 'react';
import { ChatContact } from '../../types/chat';
import { Search, Filter, User, CheckCircle2, Calendar, XCircle, DollarSign, MessageCircle } from 'lucide-react';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
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
    const [searchQuery, setSearchQuery] = useState('');

    // Filter Logic
    const filteredChats = chats.filter(chat => {
        if (filterTab === 'unread' && chat.unreadCount === 0) return false;
        if (searchQuery && !chat.name.toLowerCase().includes(searchQuery.toLowerCase())) return false;
        return true;
    });

    const totalUnread = chats.reduce((sum, chat) => sum + (chat.unreadCount || 0), 0);

    return (
        <div className="w-80 flex flex-col h-full border-r border-zinc-200 dark:border-border bg-white dark:bg-card">

            {/* 1. SEARCH */}
            <div className="p-3 pb-2 border-b border-zinc-100 dark:border-border">
                <div className="relative">
                    <Input
                        type="text"
                        placeholder="Buscar contato..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="pl-8 h-9 bg-zinc-50 dark:bg-zinc-900 border-zinc-200 dark:border-border rounded-lg text-sm focus:ring-indigo-500/20 dark:focus:ring-indigo-400/20 focus:border-indigo-600 dark:focus:border-indigo-400"
                    />
                    <Search className="w-3.5 h-3.5 text-zinc-400 dark:text-zinc-500 absolute left-2.5 top-2.5" />
                </div>
            </div>

            {/* 2. TABS (Todas | Não lidas) */}
            <div className="px-3 py-2 border-b border-zinc-100 dark:border-border">
                <Tabs defaultValue="all" onValueChange={(v) => setFilterTab(v as any)} className="w-full">
                    <TabsList className="w-full grid grid-cols-2 bg-zinc-100 dark:bg-zinc-900 p-0.5 rounded-lg h-9">
                        <TabsTrigger
                            value="all"
                            className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-indigo-500 data-[state=active]:to-purple-600 data-[state=active]:text-white rounded-md text-xs font-semibold transition-all shadow-sm"
                        >
                            <MessageCircle className="w-3 h-3 mr-1" />
                            Todas
                        </TabsTrigger>
                        <TabsTrigger
                            value="unread"
                            className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-indigo-500 data-[state=active]:to-purple-600 data-[state=active]:text-white rounded-md text-xs font-semibold transition-all gap-1.5 shadow-sm"
                        >
                            Não lidas
                            {totalUnread > 0 && (
                                <Badge className="bg-indigo-700 dark:bg-indigo-600 hover:bg-indigo-800 border-0 text-white text-[9px] h-4 px-1.5 ml-1">
                                    {totalUnread}
                                </Badge>
                            )}
                        </TabsTrigger>
                    </TabsList>
                </Tabs>
            </div>

            {/* 3. FILTERS (Etapa do Funil) */}
            <div className="px-3 py-2 border-b border-zinc-100 dark:border-border">
                <div className="flex items-center gap-2">
                    <Filter className="w-3.5 h-3.5 text-zinc-400 dark:text-zinc-500" />
                    <span className="text-xs text-zinc-500 dark:text-muted-foreground font-medium">Filtros:</span>

                    <Select defaultValue="all" onValueChange={setFunnelStage}>
                        <SelectTrigger className="w-[130px] h-7 text-xs border-zinc-200 dark:border-border bg-white dark:bg-zinc-900 shadow-sm rounded-md">
                            <SelectValue placeholder="Etapa" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="all">Todas as etapas</SelectItem>
                            <SelectItem value="lead">
                                <div className="flex items-center gap-2"><User className="w-3 h-3 text-indigo-500" /> Lead</div>
                            </SelectItem>
                            <SelectItem value="scheduled">
                                <div className="flex items-center gap-2"><Calendar className="w-3 h-3 text-purple-500" /> Agendado</div>
                            </SelectItem>
                            <SelectItem value="attended">
                                <div className="flex items-center gap-2"><CheckCircle2 className="w-3 h-3 text-emerald-500" /> Compareceu</div>
                            </SelectItem>
                            <SelectItem value="noshow">
                                <div className="flex items-center gap-2"><XCircle className="w-3 h-3 text-red-500" /> Faltou</div>
                            </SelectItem>
                            <SelectItem value="won">
                                <div className="flex items-center gap-2"><DollarSign className="w-3 h-3 text-amber-500" /> Venda</div>
                            </SelectItem>
                        </SelectContent>
                    </Select>
                </div>
            </div>

            {/* 4. CHAT LIST */}
            <div className="flex-1 overflow-y-auto bg-zinc-50/30 dark:bg-zinc-900/30">
                {filteredChats.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full p-4 text-center">
                        <MessageCircle className="w-12 h-12 text-zinc-300 dark:text-zinc-600 mb-2" />
                        <p className="text-sm text-zinc-500 dark:text-muted-foreground">Nenhuma conversa encontrada</p>
                        <p className="text-xs text-zinc-400 dark:text-zinc-500 mt-1">Tente ajustar os filtros</p>
                    </div>
                ) : (
                    filteredChats.map((chat) => (
                        <div
                            key={chat.id}
                            onClick={() => onSelectChat(chat.id)}
                            className={clsx(
                                "px-3 py-2.5 cursor-pointer transition-all border-b border-zinc-100 dark:border-border hover:bg-zinc-50 dark:hover:bg-zinc-800/50",
                                activeChatId === chat.id
                                    ? "bg-indigo-50/60 dark:bg-indigo-900/20 border-l-4 border-l-indigo-500 dark:border-l-indigo-400"
                                    : "bg-transparent border-l-4 border-l-transparent"
                            )}
                        >
                            <div className="flex justify-between items-start mb-1">
                                <div className="flex items-center gap-2 w-full">
                                    <div className="relative">
                                        <div className="w-9 h-9 rounded-full bg-zinc-200 dark:bg-zinc-700 overflow-hidden flex-shrink-0">
                                            <img
                                                src={`https://ui-avatars.com/api/?name=${chat.name.replace(' ', '+')}&background=random&size=128`}
                                                alt={chat.name}
                                                className="w-full h-full object-cover"
                                            />
                                        </div>
                                        {/* Online Status Dot */}
                                        <div className="absolute bottom-0 right-0 w-2 h-2 bg-emerald-500 border-2 border-white dark:border-card rounded-full"></div>
                                    </div>

                                    <div className="flex-1 min-w-0">
                                        <div className="flex justify-between items-center mb-0.5">
                                            <h3 className="font-bold text-sm text-zinc-800 dark:text-foreground truncate max-w-[140px]">
                                                {chat.name}
                                            </h3>
                                            <span className={clsx("text-[10px]", chat.unreadCount > 0 ? "text-indigo-600 dark:text-indigo-400 font-bold" : "text-zinc-400 dark:text-zinc-500")}>
                                                {chat.lastMessageTime}
                                            </span>
                                        </div>

                                        <p className="text-xs text-zinc-500 dark:text-muted-foreground truncate mb-1 flex items-center gap-1">
                                            {/* Read Receipt Mock */}
                                            <span className="text-indigo-500 dark:text-indigo-400">✓✓</span>
                                            {chat.lastMessage}
                                        </p>

                                        {/* Funnel Stage Badge */}
                                        <div className="flex gap-1 flex-wrap">
                                            <Badge
                                                variant="outline"
                                                className="text-[9px] px-1.5 py-0 h-4 font-normal border-indigo-200 dark:border-indigo-800 bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 gap-0.5"
                                            >
                                                <User className="w-2.5 h-2.5" /> Lead
                                            </Badge>

                                            {chat.tags.includes('financial') && (
                                                <Badge variant="outline" className="text-[9px] px-1.5 py-0 h-4 font-normal border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300 gap-0.5">
                                                    <DollarSign className="w-2.5 h-2.5" /> Venda
                                                </Badge>
                                            )}

                                            {chat.unreadCount > 0 && (
                                                <Badge className="bg-indigo-600 dark:bg-indigo-500 text-white border-0 text-[9px] h-4 px-1.5 ml-auto">
                                                    {chat.unreadCount}
                                                </Badge>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};
