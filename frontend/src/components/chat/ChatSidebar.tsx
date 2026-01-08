import React, { useState } from 'react';
import { ChatContact } from '../../types/chat';
import { supabase } from '../../services/supabase';
import { chatService } from '../../services/api';
import {
    Search, Filter, MoreVertical, MessageCircle, ChevronDown, Archive,
    BellOff, PinOff, Mail, Heart, Ban, Trash2
} from 'lucide-react';
import { Input } from '../ui/input';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "../ui/dropdown-menu";
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from "../ui/alert-dialog";
import clsx from 'clsx';

// --- Phosphor Icons (Light Weight: 12px stroke on 256px viewbox) ---
const PhUserLight = ({ className }: { className?: string }) => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" className={className} fill="none" stroke="currentColor" strokeWidth="16" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="128" cy="96" r="64" strokeWidth="12" />
        <path d="M30.989,215.99064a112.03731,112.03731,0,0,1,194.02311.002" strokeWidth="12" />
    </svg>
);
const PhTrendUpLight = ({ className }: { className?: string }) => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" className={className} fill="none" stroke="currentColor" strokeWidth="16" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="232 56 136 152 96 112 24 184" strokeWidth="12" />
        <polyline points="232 120 232 56 168 56" strokeWidth="12" />
    </svg>
);
const PhCalendarCheckLight = ({ className }: { className?: string }) => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" className={className} fill="none" stroke="currentColor" strokeWidth="16" strokeLinecap="round" strokeLinejoin="round">
        <rect x="40" y="40" width="176" height="176" rx="8" strokeWidth="12" />
        <line x1="176" y1="24" x2="176" y2="56" strokeWidth="12" />
        <line x1="80" y1="24" x2="80" y2="56" strokeWidth="12" />
        <line x1="40" y1="88" x2="216" y2="88" strokeWidth="12" />
        <polyline points="84 140 108 164 172 100" strokeWidth="12" />
    </svg>
);
const PhCheckCircleLight = ({ className }: { className?: string }) => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" className={className} fill="none" stroke="currentColor" strokeWidth="16" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="172 104 113.333 160 84 132" strokeWidth="12" />
        <circle cx="128" cy="128" r="96" strokeWidth="12" />
    </svg>
);
const PhXCircleLight = ({ className }: { className?: string }) => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" className={className} fill="none" stroke="currentColor" strokeWidth="16" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="128" cy="128" r="96" strokeWidth="12" />
        <line x1="160" y1="96" x2="96" y2="160" strokeWidth="12" />
        <line x1="160" y1="160" x2="96" y2="96" strokeWidth="12" />
    </svg>
);
const PhChatDotsLight = ({ className }: { className?: string }) => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" className={className} fill="none" stroke="currentColor" strokeWidth="16" strokeLinecap="round" strokeLinejoin="round">
        <path d="M45.42857,176.99811A96,96,0,1,1,79.00228,210.5717l-33.5737,11.19123a8,8,0,0,1-10.23725-10.23725Z" strokeWidth="12" />
        <circle cx="96" cy="128" r="8" fill="currentColor" stroke="none" />
        <circle cx="128" cy="128" r="8" fill="currentColor" stroke="none" />
        <circle cx="160" cy="128" r="8" fill="currentColor" stroke="none" />
    </svg>
);

interface ChatSidebarProps {
    chats: ChatContact[];
    activeChatId?: string;
    onSelectChat: (chatId: string) => void;
    className?: string;
}

export const ChatSidebar: React.FC<ChatSidebarProps> = ({ chats, activeChatId, onSelectChat, className }) => {
    const [searchQuery, setSearchQuery] = useState('');
    const [filterTab, setFilterTab] = useState<'all' | 'unread'>('all');

    // Dialog State
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
    const [chatToDelete, setChatToDelete] = useState<string | null>(null);

    const filteredChats = chats.filter(chat => {
        // 1. Text Search
        const matchesSearch = (chat.name || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
            (chat.lastMessage || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
            (chat.phoneNumber || '').includes(searchQuery);

        // 2. Tab Filter
        const matchesTab = filterTab === 'all' || (filterTab === 'unread' && chat.unreadCount > 0);

        return matchesSearch && matchesTab;
    });

    const handleAction = async (action: string, chatId: string, e: React.MouseEvent) => {
        e.stopPropagation();
        console.log(`Action: ${action} on chat ${chatId}`);

        try {
            if (action === 'delete') {
                setChatToDelete(chatId);
                setIsDeleteDialogOpen(true);
                return;
            }
            if (action === 'mark_unread') {
                const { error } = await supabase
                    .from('whatsapp_conversations')
                    .update({ unread_count: 1 })
                    .eq('id', chatId);

                if (error) throw error;
                console.log("Marked as unread successfully");
            }
        } catch (error) {
            console.error("Action failed", error);
            alert("Falha ao executar ação: " + error);
        }
    };

    const confirmDelete = async () => {
        if (!chatToDelete) return;
        try {
            await chatService.deleteChat(chatToDelete);
            setIsDeleteDialogOpen(false);
            setChatToDelete(null);
            // Ideally force refresh here
        } catch (delError) {
            console.error("Delete call failed", delError);
            alert("Erro ao apagar conversa. Tente novamente.");
        }
    };

    const getChatColor = (tags: string[]) => {
        const t = tags || [];
        if (t.includes('crm:won')) return 'bg-amber-50 dark:bg-amber-900/10 hover:bg-amber-100 dark:hover:bg-amber-900/20';
        if (t.includes('crm:attended')) return 'bg-emerald-50 dark:bg-emerald-900/10 hover:bg-emerald-100 dark:hover:bg-emerald-900/20';
        if (t.includes('crm:scheduled')) return 'bg-purple-50 dark:bg-purple-900/10 hover:bg-purple-100 dark:hover:bg-purple-900/20';
        if (t.includes('crm:qualifying')) return 'bg-blue-50 dark:bg-blue-900/10 hover:bg-blue-100 dark:hover:bg-blue-900/20';
        if (t.includes('crm:noshow')) return 'bg-red-50 dark:bg-red-900/10 hover:bg-red-100 dark:hover:bg-red-900/20';

        // Default Lead
        return 'bg-indigo-50 dark:bg-indigo-900/10 hover:bg-indigo-100 dark:hover:bg-indigo-900/20';
    };

    return (
        <div className={clsx(
            "flex flex-col h-full bg-white dark:bg-[#111b21]",
            className
        )}>

            {/* 1. HEADER (Profile & Actions) */}
            <div className="h-16 px-4 py-2 bg-[#f0f2f5] dark:bg-[#202c33] flex items-center justify-between border-b border-[#e9edef] dark:border-zinc-800">
                <div className="w-10 h-10 rounded-full bg-slate-300 overflow-hidden cursor-pointer">
                    <img src="https://ui-avatars.com/api/?name=Admin&background=random" alt="Me" />
                </div>
                <div className="flex gap-3 text-[#54656f] dark:text-[#aebac1]">
                    <div className="cursor-pointer p-1 rounded-full active:bg-black/10"><MessageCircle className="w-6 h-6" /></div>
                    <div className="cursor-pointer p-1 rounded-full active:bg-black/10"><MoreVertical className="w-6 h-6" /></div>
                </div>
            </div>

            {/* 2. SEARCH & FILTER */}
            <div className="px-3 py-2 border-b border-[#e9edef] dark:border-zinc-800 bg-white dark:bg-[#111b21]">
                <div className="relative">
                    <div className="absolute left-3 top-2 text-[#54656f] dark:text-[#aebac1]">
                        <Search className="w-5 h-5" />
                    </div>
                    <Input
                        type="text"
                        placeholder="Pesquisar ou começar uma nova conversa"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="pl-12 h-9 bg-[#f0f2f5] dark:bg-[#202c33] border-none rounded-lg text-sm placeholder:text-[#54656f] focus-visible:ring-0"
                    />
                    <Filter className="w-5 h-5 text-[#54656f] dark:text-[#aebac1] absolute right-3 top-2 cursor-pointer" />
                </div>
            </div>

            {/* 3. TABS (All / Unread) */}
            <div className="px-3 flex gap-2 py-2 overflow-x-auto scroller-none bg-white dark:bg-[#111b21]">
                <button
                    onClick={() => setFilterTab('all')}
                    className={clsx(
                        "px-3 py-1 rounded-full text-sm font-medium transition-colors",
                        filterTab === 'all'
                            ? "bg-[#e9edef] dark:bg-[#202c33] text-[#111b21] dark:text-[#e9edef]"
                            : "bg-transparent text-[#54656f] dark:text-[#8696a0] hover:bg-[#f5f6f6]"
                    )}
                >
                    Tudo
                </button>
                <button
                    onClick={() => setFilterTab('unread')}
                    className={clsx(
                        "px-3 py-1 rounded-full text-sm font-medium transition-colors",
                        filterTab === 'unread'
                            ? "bg-[#25d366]/10 text-[#008069]"
                            : "bg-transparent text-[#54656f] dark:text-[#8696a0] hover:bg-[#f5f6f6]"
                    )}
                >
                    Não lidas
                </button>
            </div>


            {/* 4. CHAT LIST */}
            <div className="flex-1 overflow-y-auto bg-white dark:bg-[#111b21]">
                {filteredChats.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-48 text-center text-[#54656f]">
                        <p className="text-sm">Nenhuma conversa encontrada</p>
                    </div>
                ) : (
                    filteredChats.map((chat) => (
                        <div
                            key={chat.id}
                            onClick={() => onSelectChat(chat.id)}
                            className={clsx(
                                "group px-3 py-3 cursor-pointer flex items-center gap-3 transition-colors relative border-b border-[#e9edef] dark:border-zinc-800",
                                activeChatId === chat.id ? "bg-zinc-200 dark:bg-[#2a3942]" : getChatColor(chat.tags)
                            )}
                        >
                            {/* Avatar */}
                            <div className="relative w-12 h-12 flex-shrink-0">
                                <img
                                    src={chat.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(chat.name || 'Desconhecido')}&background=random&size=128`}
                                    alt={chat.name}
                                    className="w-full h-full rounded-full object-cover"
                                />
                            </div>

                            {/* Content */}
                            <div className="flex-1 min-w-0 pr-1 h-full flex flex-col justify-center">
                                <div className="flex justify-between items-center">
                                    <h3 className="text-[17px] text-[#111b21] dark:text-[#e9edef] font-bold truncate">
                                        {chat.name || 'Desconhecido'}
                                    </h3>
                                    <span className={clsx(
                                        "text-xs",
                                        chat.unreadCount > 0 ? "text-[#25d366] font-medium" : "text-[#667781]"
                                    )}>
                                        {chat.lastMessageTime}
                                    </span>
                                </div>
                                <div className="flex justify-between items-center mt-0.5">
                                    <p className="text-[14px] text-[#667781] dark:text-[#8696a0] truncate max-w-[85%] flex items-center gap-1">
                                        <span className="text-indigo-500 dark:text-indigo-400 text-[10px]">✓✓</span>
                                        {chat.lastMessage}
                                    </p>


                                    {/* Action Trigger (Hover) */}
                                    <div className="absolute right-3 top-8 opacity-0 group-hover:opacity-100 transition-opacity duration-200" onClick={(e) => e.stopPropagation()}>
                                        <DropdownMenu modal={false}>
                                            <DropdownMenuTrigger asChild>
                                                <button className="p-1 rounded-full hover:bg-black/10 bg-transparent text-[#54656f] dark:text-[#aebac1]">
                                                    <ChevronDown className="w-5 h-5" />
                                                </button>
                                            </DropdownMenuTrigger>
                                            <DropdownMenuContent align="end" className="w-56 bg-white dark:bg-[#233138] border-none shadow-lg py-2">
                                                <DropdownMenuItem className="cursor-pointer text-[#111b21] dark:text-[#d1d7db] hover:bg-[#f5f6f6] dark:hover:bg-[#111b21] py-2.5" onClick={(e) => handleAction('archive', chat.id, e)}>
                                                    <Archive className="mr-3 h-4 w-4" />
                                                    <span>Arquivar conversa</span>
                                                </DropdownMenuItem>
                                                <DropdownMenuItem className="cursor-pointer text-[#111b21] dark:text-[#d1d7db] hover:bg-[#f5f6f6] dark:hover:bg-[#111b21] py-2.5" onClick={(e) => handleAction('mute', chat.id, e)}>
                                                    <BellOff className="mr-3 h-4 w-4" />
                                                    <span>Silenciar notificações</span>
                                                </DropdownMenuItem>
                                                <DropdownMenuItem className="cursor-pointer text-[#111b21] dark:text-[#d1d7db] hover:bg-[#f5f6f6] dark:hover:bg-[#111b21] py-2.5" onClick={(e) => handleAction('unpin', chat.id, e)}>
                                                    <PinOff className="mr-3 h-4 w-4" />
                                                    <span>Desafixar conversa</span>
                                                </DropdownMenuItem>
                                                <DropdownMenuItem className="cursor-pointer text-[#111b21] dark:text-[#d1d7db] hover:bg-[#f5f6f6] dark:hover:bg-[#111b21] py-2.5" onClick={(e) => handleAction('mark_unread', chat.id, e)}>
                                                    <Mail className="mr-3 h-4 w-4" />
                                                    <span>Marcar como não lida</span>
                                                </DropdownMenuItem>
                                                <DropdownMenuItem className="cursor-pointer text-[#111b21] dark:text-[#d1d7db] hover:bg-[#f5f6f6] dark:hover:bg-[#111b21] py-2.5" onClick={(e) => handleAction('favorite', chat.id, e)}>
                                                    <Heart className="mr-3 h-4 w-4" />
                                                    <span>Adicionar aos favoritos</span>
                                                </DropdownMenuItem>
                                                <DropdownMenuSeparator className="bg-[#e9edef] dark:bg-[#374248]" />
                                                <DropdownMenuItem className="cursor-pointer text-[#111b21] dark:text-[#d1d7db] hover:bg-[#f5f6f6] dark:hover:bg-[#111b21] py-2.5" onClick={(e) => handleAction('block', chat.id, e)}>
                                                    <Ban className="mr-3 h-4 w-4" />
                                                    <span>Bloquear</span>
                                                </DropdownMenuItem>
                                                <DropdownMenuItem className="cursor-pointer text-red-500 hover:bg-[#f5f6f6] dark:hover:bg-[#111b21] py-2.5" onClick={(e) => handleAction('delete', chat.id, e)}>
                                                    <Trash2 className="mr-3 h-4 w-4" />
                                                    <span>Apagar conversa</span>
                                                </DropdownMenuItem>
                                            </DropdownMenuContent>
                                        </DropdownMenu>
                                    </div>

                                    {/* Unread Badge (Hidden if menu open or no unread) */}
                                    {chat.unreadCount > 0 && chat.id !== activeChatId && (
                                        <div className="min-w-[1.25rem] h-5 px-1 bg-[#25d366] text-white text-xs font-medium rounded-full flex items-center justify-center">
                                            {chat.unreadCount}
                                        </div>
                                    )}
                                </div>

                                {/* Dynamic Tags with Phosphor Light Icons */}
                                <div className="flex flex-wrap gap-1 mt-1">
                                    {(!chat.tags || chat.tags.length === 0 || (!chat.tags.some(t => t.startsWith('crm:')) && !chat.tags.includes('financial'))) && (
                                        <span className="bg-zinc-50 text-zinc-500 text-[10px] px-1.5 py-0.5 rounded-md border border-zinc-200 font-medium flex items-center gap-1.5">
                                            <PhUserLight className="w-3 h-3" /> Lead
                                        </span>
                                    )}

                                    {chat.tags && chat.tags.map(tag => {
                                        if (tag === 'crm:won' || tag === 'crm:venda' || tag === 'financial') return (
                                            <span key="won" className="bg-amber-50 text-amber-700 text-[10px] px-1.5 py-0.5 rounded-md border border-amber-200 font-medium flex items-center gap-1.5">
                                                <PhTrendUpLight className="w-3 h-3" /> Venda
                                            </span>
                                        );
                                        if (tag === 'crm:scheduled' || tag === 'crm:agendado') return (
                                            <span key="sched" className="bg-purple-50 text-purple-700 text-[10px] px-1.5 py-0.5 rounded-md border border-purple-200 font-medium flex items-center gap-1.5">
                                                <PhCalendarCheckLight className="w-3 h-3" /> Agendado
                                            </span>
                                        );
                                        if (tag === 'crm:attended' || tag === 'crm:compareceu') return (
                                            <span key="att" className="bg-emerald-50 text-emerald-700 text-[10px] px-1.5 py-0.5 rounded-md border border-emerald-200 font-medium flex items-center gap-1.5">
                                                <PhCheckCircleLight className="w-3 h-3" /> Compareceu
                                            </span>
                                        );
                                        if (tag === 'crm:noshow' || tag === 'crm:faltou') return (
                                            <span key="noshow" className="bg-red-50 text-red-700 text-[10px] px-1.5 py-0.5 rounded-md border border-red-200 font-medium flex items-center gap-1.5">
                                                <PhXCircleLight className="w-3 h-3" /> Faltou
                                            </span>
                                        );
                                        if (tag === 'crm:qualifying' || tag === 'crm:em negociação') return (
                                            <span key="qual" className="bg-blue-50 text-blue-700 text-[10px] px-1.5 py-0.5 rounded-md border border-blue-200 font-medium flex items-center gap-1.5">
                                                <PhChatDotsLight className="w-3 h-3" /> Em Negociação
                                            </span>
                                        );
                                        return null;
                                    })}
                                </div>
                            </div>
                        </div>
                    ))
                )}
            </div>

            {/* Delete Confirmation Dialog */}
            <AlertDialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
                <AlertDialogContent>
                    <AlertDialogHeader>
                        <AlertDialogTitle>Apagar conversa?</AlertDialogTitle>
                        <AlertDialogDescription>
                            Isso apagará o histórico desta conversa no sistema e tentará limpar o histórico no WhatsApp (em alguns casos).
                            Esta ação não pode ser desfeita.
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                        <AlertDialogCancel>Cancelar</AlertDialogCancel>
                        <AlertDialogAction onClick={confirmDelete} className="bg-red-500 hover:bg-red-600 outline-none ring-0">
                            Apagar
                        </AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>
        </div>
    );
};
